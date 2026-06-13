# File Name: cray_gray_code_parser.py
# Location: /src/network_layer/
# Subsystem: Cray Supercomputing High-Speed Gray-Code Serial Decoder

import threading
import time
from typing import Dict, Any

class CrayGrayCodeParserExtension:
    def __init__(self):
        """Initializes the thread-safe Gray code decoding register."""
        self.lock = threading.Lock()
        self.latest_decoded_telemetry = {
            'raw_gray_word': 0,
            'decoded_binary_integer': 0,
            'calibrated_shaft_angle_deg': 0.0,
            'last_decode_timestamp': time.time()
        }

    def decode_cray_gray_word(self, raw_gray_word: int, bits_resolution: int = 12) -> dict:
        """
        Performs hard-deterministic bitwise Gray-to-Binary transformation.
        Maps the results directly to physical engineering units (degrees).
        """
        # Apply word-width boundary truncation to protect against register bleed
        mask = (1 << bits_resolution) - 1
        clean_gray = raw_gray_word & mask
        
        # --- BITWISE GRAY-TO-BINARY CONVERSION LOOP ---
        binary_integer = clean_gray
        shift_register = clean_gray
        while shift_register >> 1:
            shift_register >>= 1
            binary_integer ^= shift_register
        # ──────────────────────────────────────────────
        
        # Convert the standard binary integer to a precise 360-degree geometric angle
        max_counts = 1 << bits_resolution
        angle_deg = (binary_integer / max_counts) * 360.0

        with self.lock:
            self.latest_decoded_telemetry['raw_gray_word'] = clean_gray
            self.latest_decoded_telemetry['decoded_binary_integer'] = binary_integer
            self.latest_decoded_telemetry['calibrated_shaft_angle_deg'] = round(angle_deg, 2)
            self.latest_decoded_telemetry['last_sync_timestamp'] = time.time()

        return self.latest_decoded_telemetry.copy()

# Verification Verification Run Environment
if __name__ == "__main__":
    parser = CrayGrayCodeParserExtension()
    print("VERIFYING BITWISE GRAY-TO-BINARY DECODER LOGIC:")
    print("=" * 65)
    
    # Test Scenario: Optical shaft encoder sits at a true physical count of 7.
    # Standard Binary 7 = 0111 | Matching Gray Code 7 = 0100 (Decimal 4 representation)
    mock_gray_input = 0b0100 
    
    res = parser.decode_cray_gray_word(raw_gray_word=mock_gray_input, bits_resolution=4)
    print(f"Input Gray String:  {bin(mock_gray_input)}")
    print(f"Decoded Binary Output: {bin(res['decoded_binary_integer'])} (Decimal {res['decoded_binary_integer']})")
    print(f"Computed Shaft Axis:   {res['calibrated_shaft_angle_deg']}°")
