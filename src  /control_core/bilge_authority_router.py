# File Name: bilge_authority_router.py
# Location: /src/control_core/
# Subsystem: Tri-State Bilge Control Authority Router & Multiplexer

import time
from typing import Dict, Any

class BilgeControlAuthorityRouter:
    def __init__(self):
        """
        Initializes the tri-state environmental authority routing gate.
        Allowed Modes: 
            "UNIVAC"       (0x01) -> Mainframe has direct pass-through control
            "REPLACEMENT"  (0x02) -> Our core physics loop (Us) commands the valves
            "SEA_MACHINES" (0x03) -> External autonomy layer commands the valves
        """
        self.active_authority_mode = "UNIVAC" # Default safe boot-up mode is the legacy mainframe
        self.last_mode_change_time = time.time()

    def set_control_authority(self, requested_mode: str) -> tuple:
        """
        Changes the global control authority routing state block.
        Ensures strings are validated before altering hardware routing gates.
        """
        sanitized_mode = requested_mode.upper().strip()
        allowed_modes = ["UNIVAC", "REPLACEMENT", "SEA_MACHINES"]
        
        if sanitized_mode in allowed_modes:
            if self.active_authority_mode != sanitized_mode:
                self.active_authority_mode = sanitized_mode
                self.last_mode_change_time = time.time()
                return True, f"AUTHORITY CHANGED ON THE FLY TO: {sanitized_mode}"
            return True, f"Authority already held by: {sanitized_mode}"
        return False, f"REJECTED: Unknown authority mode code requested: '{requested_mode}'"

    def resolve_final_actuator_commands(self, univac_pass_through: dict, our_physics_loop: dict, seamachines_input: dict) -> dict:
        """
        Multiplexes the three incoming control vectors based on the active state.
        Guarantees that only ONE system is talking to the physical hardware wire loop.
        """
        # Resolve vectors based on active routing gates
        if self.active_authority_mode == "UNIVAC":
            final_overboard = univac_pass_through.get('actuator_overboard_valve_open', 0)
            final_recirc = univac_pass_through.get('actuator_recirculation_valve_open', 0)
            routing_source = "UNIVAC_MAINFRAME_PASS_THROUGH"
        elif self.active_authority_mode == "REPLACEMENT":
            final_overboard = our_physics_loop.get('actuator_overboard_valve_open', 0)
            final_recirc = our_physics_loop.get('actuator_recirculation_valve_open', 0)
            routing_source = "OUR_CORE_PHYSICS_LOOP"
        elif self.active_authority_mode == "SEA_MACHINES":
            final_overboard = seamachines_input.get('actuator_overboard_valve_open', 0)
            final_recirc = seamachines_input.get('actuator_recirculation_valve_open', 0)
            routing_source = "SEA_MACHINES_EXTERNAL_AUTONOMY"
        else:
            # Emergency Fail-Safe Default: If the state gets corrupted, close ALL valves instantly
            final_overboard = 0
            final_recirc = 0
            routing_source = "EMERGENCY_ROUTER_FALLBACK_SECURED"

        return {
            "active_authority_mode": self.active_authority_mode,
            "routing_source_string": routing_source,
            "resolved_overboard_valve_open": final_overboard,
            "resolved_recirculation_valve_open": final_recirc,
            "timestamp_resolved": time.time()
        }

# Verification and Diagnostic Execution Environment
if __name__ == "__main__":
    router = BilgeControlAuthorityRouter()
    print("TESTING TRI-STATE DYNAMIC CONTROL LAW ROUTER:")
    print("=" * 72)
    
    # Setup three mock competing data packages arriving simultaneously on the bus
    mock_univac_data = {'actuator_overboard_valve_open': 1, 'actuator_recirculation_valve_open': 0} # Wants to dump clean water
    mock_our_data = {'actuator_overboard_valve_open': 0, 'actuator_recirculation_valve_open': 1}    # Wants to recirculate due to sloshing
    mock_seamachines_data = {'actuator_overboard_valve_open': 0, 'actuator_recirculation_valve_open': 0} # Wants to secure pump entirely
    
    # 1. Default Boot: Verify legacy mainframe pass-through is active
    out_1 = router.resolve_final_actuator_commands(mock_univac_data, mock_our_data, mock_seamachines_data)
    print(f"Default Boot  -> Mode: {out_1['active_authority_mode']} | Overboard: {out_1['resolved_overboard_valve_open']}")
    
    # 2. Shift control on the fly to our Core Physics Loop (Us)
    success, msg = router.set_control_authority("REPLACEMENT")
    print(f"\nCommand Action: {msg}")
    out_2 = router.resolve_final_actuator_commands(mock_univac_data, mock_our_data, mock_seamachines_data)
    print(f"Shift Mode 2  -> Mode: {out_2['active_authority_mode']} | Overboard: {out_2['resolved_overboard_valve_open']}")
    
    # 3. Shift control on the fly to Sea Machines
    success, msg = router.set_control_authority("SEA_MACHINES")
    print(f"\nCommand Action: {msg}")
    out_3 = router.resolve_final_actuator_commands(mock_univac_data, mock_our_data, mock_seamachines_data)
    print(f"Shift Mode 3  -> Mode: {out_3['active_authority_mode']} | Overboard: {out_3['resolved_overboard_valve_open']}")
