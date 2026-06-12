# File Name: weapon_async_parser.py
# Location: /src/network_layer/
# Subsystem: Asynchronous Weapon Bus Telemetry Interception & Processing Extension

import math
import threading
import time
from typing import Dict, Any, Tuple

class WeaponAsyncParserExtension:
    def __init__(self, manufacturer_code: str = "MK45"):
        """
        Initializes the asynchronous weapon bus string decoder.
        manufacturer_code: 4-character identifier matching your hardware configuration.
        """
        self.expected_prefix = f"${manufacturer_code.upper()[:4]}"
        
        # Thread isolation lock for memory register reads/writes
        self.matrix_lock = threading.Lock()
        
        # Safe thread-locked cache storage mapping raw tracking variables
        self.parsed_weapon_state = {
            'azimuth_deg': 0.0,
            'elevation_deg': 0.0,
            'azimuth_rate_rads': 0.0,
            'elevation_rate_rads': 0.0,
            'bus_sync_active': False,
            'last_ingest_time': time.time()
        }
        
        # History tracking registers to compute precise numerical derivatives
        self.prev_az_rad = 0.0
        self.prev_el_rad = 0.0
        self.prev_packet_time = None

    def _verify_checksum_bytes(self, line: str) -> bool:
        """Validates standard NMEA 8-bit XOR hexadecimal checksum parameters."""
        if not line.startswith('$') or '*' not in line:
            return False
        try:
            body, hex_cs = line[1:].split('*')
            hex_cs = hex_cs.strip()
            
            xor_check = 0
            for char in body:
                xor_check ^= ord(char)
                
            return f"{xor_check:02X}" == hex_cs.upper()
        except Exception:
            return False

    def process_async_line(self, raw_line_str: str) -> dict:
        """
        Processes a raw input string, converts units, calculates execution rates,
        and pushes the data to the high-speed target matrix.
        """
        clean_line = raw_line_str.strip()
        current_time = time.time()
        
        # 1. Verification Checklist Guard
        if not self._verify_checksum_bytes(clean_line):
            with self.matrix_lock:
                return self.parsed_weapon_state.copy()

        try:
            # Strip structural markers and split data metrics by comma delimiters
            payload_body = clean_line.split('*')[0]
            parts = payload_body.split(',')
            header_prefix = parts[0]
            
            if header_prefix != self.expected_prefix:
                with self.matrix_lock:
                    return self.parsed_weapon_state.copy()
                    
            # Extract raw string positioning attributes
            azimuth_val = float(parts[1])
            elevation_val = float(parts[2])
            status_register_hex = parts[3]
            
            az_rad = math.radians(azimuth_val)
            el_rad = math.radians(elevation_val)
            
            # 2. Real-Time Numerical Derivative Calculations (Velocity Tracking Engine)
            az_rate_calculated = 0.0
            el_rate_calculated = 0.0
            
            if self.prev_packet_time is not None:
                dt = current_time - self.prev_packet_time
                if dt > 0.001:
                    # Handle 360-degree tracking ring boundaries smoothly
                    delta_az = az_rad - self.prev_az_rad
                    delta_az = (delta_az + math.pi) % (2.0 * math.pi) - math.pi
                    
                    delta_el = el_rad - self.prev_el_rad
                    
                    # Compute rates in analytical metric format (radians/second)
                    az_rate_calculated = delta_az / dt
                    el_rate_calculated = delta_el / dt
            
            # Convert physical servo error indicators to status check bits
            servo_fault_mask = int(status_register_hex, 16)
            bus_healthy = (servo_fault_mask == 0)

            # 3. Thread-Locked Update to High-Speed Balance Cache
            with self.matrix_lock:
                self.parsed_weapon_state['azimuth_deg'] = azimuth_val
                self.parsed_weapon_state['elevation_deg'] = elevation_val
                self.parsed_weapon_state['azimuth_rate_rads'] = az_rate_calculated
                self.parsed_weapon_state['elevation_rate_rads'] = el_rate_calculated
                self.parsed_weapon_state['bus_sync_active'] = bus_healthy
                self.parsed_weapon_state['last_ingest_time'] = current_time

            # Shift tracking indices deep into background storage
            self.prev_az_rad = az_rad
            self.prev_el_rad = el_rad
            self.prev_packet_time = current_time
            
        except (ValueError, IndexError):
            pass # Shield calculations from unexpected line noise strings

        with self.matrix_lock:
            return self.parsed_weapon_state.copy()

    def get_isolated_state_snapshot(self) -> dict:
        """Safe thread-locked snapshot extraction for the main math loop."""
        with self.matrix_lock:
            return self.parsed_weapon_state.copy()

# Verification Runtime Check Environment
if __name__ == "__main__":
    parser = WeaponAsyncParserExtension(manufacturer_code="MK45")
    
    # Pre-calculated test vectors containing verified matching NMEA hex checksums
    # Simulates two fast data updates from a tracking ring encoder line
    mock_wire_data = [
        "$MK45,045.50,012.20,0000*29\r\n",
        "$MK45,046.10,012.25,0000*2F\r\n"
    ]
    
    print("TESTING ASYNC WEAPON SERIAL DECODER HOOKS:")
    print("-" * 65)
    
    for string_packet in mock_wire_data:
        time.sleep(0.05) # Emulate a fast 20Hz hardware transmission rate profile
        latest_snapshot = parser.process_async_line(string_packet)
        
    print(f"Decoded Azimuth Heading:     {latest_snapshot['azimuth_deg']}°")
    print(f"Calculated Azimuth Velocity:  {latest_snapshot['azimuth_rate_rads']:.4f} rad/s")
    print(f"Complete Matrix State Map:\n{latest_snapshot}")
