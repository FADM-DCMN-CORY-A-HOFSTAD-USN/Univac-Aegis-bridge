# File Name: actuator_telemetry_receiver.py
# Location: /src/network_layer/

import math
from typing import Dict, Any, Tuple

class ActuatorTelemetryReceiverNode:
    def __init__(self, manufacturer_code: str = "UNVC"):
        """
        Initializes the feedback telemetry receiver node.
        manufacturer_code: 4-character identifier matching your hardware bus.
        """
        self.expected_prefix = f"P{manufacturer_code.upper()[:4]}AK"
        
        # Tracking states for linkage deviation verification
        self.consecutive_error_seconds = 0.0
        self.tracking_error_threshold_deg = 2.5  # Allowed alignment deviation limit
        self.max_error_time_allowed_sec = 1.5    # Duration before declaring a physical jam
        
        # Decoded status cache registers
        self.latest_status = {
            'measured_rudder_deg': 0.0,
            'actuator_temperature_c': 25.0,
            'hardware_faults_active': False,
            'fault_flags': [],
            'linkage_tracking_jammed': False
        }

    def _validate_checksum(self, sentence: str) -> bool:
        """Validates standard NMEA 8-bit XOR hexadecimal checksums."""
        if not sentence.startswith('$') or '*' not in sentence:
            return False
        try:
            data_body, hex_checksum = sentence[1:].split('*')
            hex_checksum = hex_checksum.strip()
            
            calculated_xor = 0
            for char in data_body:
                calculated_xor ^= ord(char)
                
            return f"{calculated_xor:02X}" == hex_checksum.upper()
        except Exception:
            return False

    def decode_status_flags(self, hex_string: str) -> Tuple[bool, list]:
        """
        Parses the 16-bit hardware bitmask to isolate physical errors.
        Bit 0: Hydraulic pressure drop
        Bit 1: High motor current (Overload)
        Bit 2: Thermal warning
        Bit 3: Feedback sensor open/short circuit
        """
        try:
            mask = int(hex_string, 16)
        except ValueError:
            return True, ["MALFORMED_BITMASK_ERROR"]
            
        faults = []
        if mask & (1 << 0): faults.append("HYDRAULIC_PRESSURE_DROP")
        if mask & (1 << 1): faults.append("MOTOR_CURRENT_OVERLOAD")
        if mask & (1 << 2): faults.append("ACTUATOR_THERMAL_CRITICAL")
        if mask & (1 << 3): faults.append("FEEDBACK_SENSOR_FAULT")
        
        is_faulted = len(faults) > 0
        return is_faulted, faults

    def process_hardware_feedback(self, raw_sentence: str, ordered_rudder_deg: float, dt: float) -> dict:
        """
        Parses raw serial strings returned by the steering gear, isolates faults, 
        and verifies that physical linkages are responding to commands.
        """
        clean_str = raw_sentence.strip()
        
        # 1. Structural Checksum Validation
        if not self._validate_checksum(clean_str):
            # If line noise corrupts the sentence, flag it and rely on the previous status cache
            if "LINE_NOISE_CORRUPTION" not in self.latest_status['fault_flags']:
                self.latest_status['fault_flags'].append("LINE_NOISE_CORRUPTION")
            return self.latest_status

        # Clean string array split components
        try:
            parts = clean_str.split('*')[0].split(',')
            message_header = parts[0][1:] # Strip '$'
            
            if message_header != self.expected_prefix:
                return self.latest_status # Ignore unrelated sentences on the serial bus
                
            measured_deg = float(parts[1])
            status_hex = parts[2]
            temp_c = float(parts[3])
            
            # 2. Extract hardware register codes
            is_faulted, active_faults = self.decode_status_flags(status_hex)
            
            # 3. Linkage Verification Engine: Check if physical mechanism tracks commands
            tracking_deviation = abs(ordered_rudder_deg - measured_deg)
            
            if tracking_deviation > self.tracking_error_threshold_deg:
                # Accumulate time while the linkage is falling behind or unresponsive
                self.consecutive_error_seconds += dt
                if self.consecutive_error_seconds >= self.max_error_time_allowed_sec:
                    active_faults.append("MECHANICAL_LINKAGE_JAM")
                    linkage_jammed = True
                else:
                    linkage_jammed = False
            else:
                # Reset tracking clock if the rudder returns within acceptable tolerances
                self.consecutive_error_seconds = 0.0
                linkage_jammed = False

            # Update cache registry values
            self.latest_status = {
                'measured_rudder_deg': measured_deg,
                'actuator_temperature_c': temp_c,
                'hardware_faults_active': is_faulted or linkage_jammed,
                'fault_flags': active_faults,
                'linkage_tracking_jammed': linkage_jammed
            }
            
        except (ValueError, IndexError):
            if "PARSING_PAYLOAD_EXCEPTION" not in self.latest_status['fault_flags']:
                self.latest_status['fault_flags'].append("PARSING_PAYLOAD_EXCEPTION")

        return self.latest_status

# Local Simulation and Diagnostic Environment
if __name__ == "__main__":
    receiver = ActuatorTelemetryReceiverNode(manufacturer_code="UNVC")
    dt = 0.2 # 200ms processing loop intervals
    
    # Ordered target rudder position sent by the bridge core engine
    commanded_position = -15.0 
    
    # Scenario A: Hardware responds normally with no active faults (Status mask: 0000)
    normal_sentence = "$PUNVCAK,-14.80,0000,32.5*24\r\n"
    print("SCENARIO A: NOMINAL FEEDBACK PACKET")
    status_a = receiver.process_hardware_feedback(normal_sentence, commanded_position, dt)
    print(status_a)
    print("-" * 80)
    
    # Scenario B: Hardware sends a hydraulic fault code and falls behind command vector
    # Mask '0003' -> Bit 0 (Pressure Drop) + Bit 1 (Current Overload) are active
    fault_sentence = "$PUNVCAK,-2.10,0003,58.0*20\r\n"
    print("SCENARIO B: CRITICAL FAULT WITH ACCUMULATING MECHANICAL TRAILING ERROR")
    
    # Simulate step-by-step passage of time under stuck conditions to trigger the jam flag
    for step in range(9):
        time_elapsed = step * dt
        status_b = receiver.process_hardware_feedback(fault_sentence, commanded_position, dt)
        if status_b['linkage_tracking_jammed']:
            print(f"-> Time: {time_elapsed:.1f}s | INTERLOCK ENGAGED: {status_b['fault_flags']}")
            break
