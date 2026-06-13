# File Name: univac_architecture_hal.py
# Location: /src/network_layer/
# Subsystem: Unified UNIVAC Multi-Model Hardware Abstraction Layer (HAL)

import sys
from typing import Dict, Any, Tuple

class UnivacArchitectureHAL:
    def __init__(self):
        """
        Initializes the dynamic bit-masking registers for all requested
        UNIVAC military and scientific mainframe computing architectures.
        """
        # Exact architectural word-mask blueprints matching native hardware limits
        self.model_registry = {
            '1219':       {'bits': 18, 'mask': 0x0003FFFF, 'protocol': 'MIL_STD_1397_A'},
            'AN/UYK-43':  {'bits': 32, 'mask': 0xFFFFFFFF, 'protocol': 'NTDS_SERIAL_E'},
            'AN/UYK-20':  {'bits': 16, 'mask': 0x0000FFFF, 'protocol': 'NTDS_PARALLEL_C'},
            'AN/AYK-14':  {'bits': 16, 'mask': 0x0000FFFF, 'protocol': 'MIL_STD_1553B'},
            '490':        {'bits': 30, 'mask': 0x3FFFFFFF, 'protocol': 'NTDS_PARALLEL_A'},
            '494':        {'bits': 30, 'mask': 0x3FFFFFFF, 'protocol': 'NTDS_PARALLEL_B'},
            '1107':       {'bits': 36, 'mask': 0xFFAAAAAA, 'protocol': 'SCIENTIFIC_PARALLEL'},
            '1108':       {'bits': 36, 'mask': 0xFFAAAAAA, 'protocol': 'SCIENTIFIC_EXTENDED'}
        }
        
        self.active_target_model = 'AN/UYK-43' # Default fallback target baseline

    def clear_interlocks_for_model(self, target_model: str) -> bool:
        """
        Locks the target hardware profile into active memory registers.
        Ensures strict bit-width compliance during subsequent serial loop steps.
        """
        sanitized = target_model.upper().strip()
        # Handle lazy numerical naming formats seamlessly (e.g., '43' -> 'AN/UYK-43')
        if sanitized == '43': sanitized = 'AN/UYK-43'
        if sanitized == '20': sanitized = 'AN/UYK-20'
        if sanitized == '14': sanitized = 'AN/AYK-14'
        
        if sanitized in self.model_registry:
            self.active_target_model = sanitized
            print(f"[BOOT_HAL] UNIVAC target architecture changed to: {self.active_target_model} ({self.model_registry[sanitized]['bits']}-Bit Matrix Activated)")
            return True
            
        print(f"[BOOT_HAL_ERROR] Request denied. Model '{target_model}' not found in compliance matrix.")
        return False

    def pack_native_word_to_64bit(self, raw_input_word: int) -> int:
        """
        Applies model-specific bitmasks to the raw data stream.
        Prevents high-order register overflow or data leakage across system lines.
        """
        cfg = self.model_registry[self.active_target_model]
        # Force strict bitwise truncation against the selected native hardware blueprint mask
        clean_word = raw_input_word & cfg['mask']
        return clean_word

    def unpack_64bit_to_native_bytes(self, system_word: int) -> Tuple[bytes, str]:
        """
        Serializes data words into native byte sequences matching the target 
        UNIVAC computer's word boundaries for transmission over RS-422 wires.
        """
        cfg = self.model_registry[self.active_target_model]
        bit_width = cfg['bits']
        clean_word = system_word & cfg['mask']
        
        # Calculate exactly how many 8-bit bytes are needed to contain the word width
        byte_count = (bit_width + 7) // 8
        
        # Convert integer to big-endian binary byte blocks for the serial wire pipelines
        binary_payload = clean_word.to_bytes(byte_count, byteorder='big')
        return binary_payload, cfg['protocol']

# Verification and Integration Run Profile
if __name__ == "__main__":
    hal = UnivacArchitectureHAL()
    print("EXECUTING MULTI-MODEL DYNAMIC BIT-WIDTH INITIALIZATION TESTS:")
    print("=" * 72)
    
    # Large test variable containing data bits across higher registers
    dirty_test_word = 0xFFFFFFFFFFFFFFFF 
    
    # Test Loop 1: Verify the 18-Bit UNIVAC 1219 architecture mask constraints
    hal.clear_interlocks_for_model('1219')
    clean_1219 = hal.pack_native_word_to_64bit(dirty_test_word)
    bytes_1219, proto_1219 = hal.unpack_64bit_to_native_bytes(clean_1219)
    print(f"UNIVAC 1219 -> Cleansed Word: 0x{clean_1219:05X} | Wire Bytes: {bytes_1219.hex().upper()} | Protocol: {proto_1219}")
    
    # Test Loop 2: Verify the 36-Bit UNIVAC 1108 scientific architecture mask constraints
    hal.clear_interlocks_for_model('1108')
    clean_1108 = hal.pack_native_word_to_64bit(dirty_test_word)
    bytes_1108, proto_1108 = hal.unpack_64bit_to_native_bytes(clean_1108)
    print(f"UNIVAC 1108 -> Cleansed Word: 0x{clean_1108:09X} | Wire Bytes: {bytes_1108.hex().upper()} | Protocol: {proto_1108}")
    
    # Test Loop 3: Verify the 30-Bit UNIVAC 494 high-speed real-time mask constraints
    hal.clear_interlocks_for_model('494')
    clean_494 = hal.pack_native_word_to_64bit(dirty_test_word)
    bytes_494, proto_494 = hal.unpack_64bit_to_native_bytes(clean_494)
    print(f"UNIVAC 494  -> Cleansed Word: 0x{clean_494:08X} | Wire Bytes: {bytes_494.hex().upper()} | Protocol: {proto_494}")
