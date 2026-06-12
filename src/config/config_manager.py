# File Name: config_manager.py
# Location: /src/config/
# Subsystem: System Boot Configuration & Parameter Validation Loader

import json
import os
from typing import Dict, Any, Tuple

class VesselConfigManager:
    def __init__(self, config_filename: str = "vessel_config.json"):
        """
        Initializes the configuration loader.
        config_filename: The target JSON parameter file name on the storage disk.
        """
        self.config_path = os.path.join(os.path.dirname(__file__), config_filename)
        
        # --- ROBUST DETERMINISTIC FALLBACK TEMPLATE ---
        # Used if the JSON configuration file is missing, unreadable, or corrupted.
        self.fallback_profile = {
            'diameter': 3.4,
            'inertia_prop': 500.0,
            'inertia_roll': 850000.0,
            'inertia_yaw': 4500000.0,
            'draft': 6.5,
            'rudder_arm_z': 2.8,
            'max_torque': 90000.0,
            'max_rudder_deg': 35.0,
            'hull_length': 45.0,
            'beam': 9.5
        }
        
        # The clean, validated profile cache ready for system-wide execution
        self.active_vessel_profile = {}

    def _generate_default_config_file(self):
        """Creates a fresh default JSON file template on the local file system if none exists."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.fallback_profile, f, indent=4)
            print(f"[CONFIG] Generated a new default specification template at: {self.config_path}")
        except IOError as e:
            print(f"[CONFIG_ERROR] Critical failure writing default specification disk array: {e}")

    def validate_profile_parameters(self, raw_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates that all necessary engineering parameters exist and fit
        within safe structural limits to prevent system calculation errors.
        """
        # Ensure every single key from our fallback definition is accounted for
        for key in self.fallback_profile.keys():
            if key not in raw_data:
                return False, f"Missing critical structural token: '{key}'"
                
        # Numeric sanity checking boundaries to catch misplaced decimal points
        try:
            if not (0.5 <= float(raw_data['diameter']) <= 15.0):
                return False, "Parameter 'diameter' bounds exception [0.5m - 15.0m]"
            if not (1.0 <= float(raw_data['draft']) <= 25.0):
                return False, "Parameter 'draft' bounds exception [1.0m - 25.0m]"
            if not (5.0 <= float(raw_data['max_rudder_deg']) <= 70.0):
                return False, "Parameter 'max_rudder_deg' bounds exception [5.0° - 70.0°]"
            if not (100.0 <= float(raw_data['max_torque']) <= 500000.0):
                return False, "Parameter 'max_torque' bounds exception [100Nm - 500kNm]"
        except (ValueError, TypeError):
            return False, "Type mismatch error: One or more fields contain non-numeric data structures."

        return True, "Profile passed validation gates."

    def load_system_specifications(self) -> Dict[str, Any]:
        """
        Loads, validates, and freezes the hardware profile into memory.
        Falls back safely to default profiles if irregularities are caught at system boot.
        """
        if not os.path.exists(self.config_path):
            print(f"[CONFIG_WARN] Configuration matrix not found at {self.config_path}")
            self._generate_default_config_file()
            self.active_vessel_profile = self.fallback_profile.copy()
            return self.active_vessel_profile

        try:
            with open(self.config_path, 'r') as f:
                loaded_json = json.load(f)
                
            is_valid, validation_msg = self.validate_profile_parameters(loaded_json)
            
            if is_valid:
                print(f"[CONFIG] Safely loaded structural matrix file: {self.config_path}")
                # Enforce clean float conversion for math precision across all inputs
                self.active_vessel_profile = {k: float(v) for k, v in loaded_json.items()}
            else:
                print(f"[CONFIG_ALERT] Validation check failed: {validation_msg}")
                print("[CONFIG] Falling back safely to default hardcoded operational profiles.")
                self.active_vessel_profile = self.fallback_profile.copy()
                
        except (json.JSONDecodeError, IOError) as file_fault:
            print(f"[CONFIG_CRITICAL] File structural breakdown caught: {file_fault}")
            print("[CONFIG] Deploying emergency backup software profiles to prevent boot block.")
            self.active_vessel_profile = self.fallback_profile.copy()

        return self.active_vessel_profile

# Verification and Simulation Test Execution Environment
if __name__ == "__main__":
    print("EXECUTING STORAGE MATRIX LOADER TESTS:")
    print("-" * 65)
    
    manager = VesselConfigManager(config_filename="test_vessel_profile.json")
    
    # Execute the load cycle (Will generate a fresh file on the first run, then parse it)
    active_specifications = manager.load_system_specifications()
    
    print(f"\nFinal Verified Boot Spec Cache: \n{active_specifications}")
    
    # Cleanup verification artifact safely
    if os.path.exists(manager.config_path):
        os.remove(manager.config_path)
