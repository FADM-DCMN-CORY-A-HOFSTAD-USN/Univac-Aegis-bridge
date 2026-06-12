# Operator Pre-Sail Diagnostic Checklist (diagnostics.md)

## 1. Functional Overview
This document outlines the mandatory sequential verification sequences required before underway operations. These tests must be performed **after** cargo configurations have been locked via the API (`cargo_load` payload) and **before** the main propulsion interlocks are cleared for open-water navigation. 

This checklist cross-validates serial telemetry lines, sensor integrity, weapon-ring mass tracking balances, and the Sea Machines thermal verification interface.

---

## 2. Phase 1: Static Power & File Integrity Checks
Verify the underlying operating system environment, file structures, and localized hardware profiles prior to loop execution.

*   [ ] **1.1 Asset Configuration Verification**: Confirm that `vessel_config.json` exists in the local root storage array and matches the current hull specification profile.
*   [ ] **1.2 Structural Parameter Validation**: Run the `config_manager.py` diagnostic module to ensure all numeric boundaries pass the validation gates:
    ```bash
    python /src/config/config_manager.py
    ```
    *Verification: Command terminal window returns: `[CONFIG] Profile passed validation gates.`*
*   [ ] **1.3 Storage Array Integrity Check**: Confirm that all log directories are clear of write-locks and possess adequate space for continuous mission tracking logs.

---

## 3. Phase 2: Asynchronous Network & Serial Ingestion Checks
Verify that the copper differential RS-422 and TCP network links are streaming error-free frames into the central memory cache registers.

*   [ ] **2.1 True Heading Compass Link ($HEHDT)**: Observe the standard system terminal output for clean serial packet reception on `/dev/ttyUSB0` (or `COM3`).
    *   *Verification: Telemetry data frame `yaw_rate_rads` stabilizes at $0.00$ at the pier.*
*   [ ] **2.2 Echo Sounder / Depth Link ($SDDBT)**: Verify that the transducer output matches known harbor depth records.
    *   *Verification: `live_telemetry['depth']` displays a consistent meter parameter without dropouts or noise values.*
*   [ ] **2.3 Network Terminal Server Port Binding**: Connect a testing workstation to TCP Port 7000 and broadcast a standard test heartbeat frame:
    ```json
    {"msg_type": "motion_setpoint", "rpm": 0.0, "target_yaw_rate": 0.0}
    ```
    *Verification: Server returns socket string: `{"status": "OK", "message": "ACCEPTED: Targets updated successfully"}`*

---

## 4. Phase 3: High-Speed Weapon Bus & Balance Matrix Verification
Verify that the weapon ring encoder interfaces are streaming true positions and that the cross-coupling hydrostatic calculations are dynamically modifying the hull balance baselines.

*   [ ] **3.1 Weapon Ring Encoder Ingestion ($PMK45)**: Command the gun mount to train $90.0^\circ$ out to the starboard beam.
    *   *Verification: Terminal outputs a matching `$PMK45,090.00,...` string.*
*   [ ] **3.2 Hydrostatic Roll List Cross-Correction**: Observe the computed telemetry packet to check the simulated weight impact:
    *   *Verification: `induced_roll_list_angle_deg` calculates a precise heeling shift based on the weapon mass profile, and `live_telemetry['roll_angle_rad']` automatically updates to pre-compensate for the mass transition.*
*   [ ] **3.3 Dynamic Gyroscopic Precession Interlock**: Execute a sudden, high-speed automated slew check in both azimuth and elevation axes simultaneously.
    *   *Verification: `induced_gyro_torque_nm` updates matching the cross-axis velocity rate derivatives without triggering a `MOTOR_CURRENT_OVERLOAD` fault code (`0x0002`).*

---

## 5. Phase 4: Sea Machines Thermal Interface & Interlock Checklist
Verify that the Sea Machines thermal verification sensor correctly interfaces with the software's multi-variable status logic.

*   [ ] **4.1 Thermal State Ingestion**: Inspect the live sensor value coming from the computer's enclosure thermometer.
    *   *Verification: Temperature reflects actual local ambient or idle operating parameters (e.g., $16.5^\circ\text{C}$).*
*   [ ] **4.2 Multi-Variable Status Override Gate**: Confirm that despite a low core temperature reading, the system remains locked in an `ONLINE` operational mode due to the presence of active network packets on the wire.
    *   *Verification: `System_Status_Matrix.configured_status` reads `"ONLINE"`. The `force_abort` flag must evaluate to `False`.*
*   [ ] **4.3 Heartbeat Timeout Interlock Protection**: Temporarily disconnect the main sensor network switch array to mimic a hardware data dropout while running cool.
    *   *Verification: Within $1.0\text{ second}$, the system must register a true timeout fault, overwrite the status register to `"OFFLINE"`, trip the interlock gates, and drive the motor torque output directly down to $0.0\text{ Nm}$ to protect the ship.*

## 6. Pre-Sail Certification Sign-Off
Once all four verification phases are successfully executed without triggering hard faults or mechanical linkage jam interlocks, clear the bridge console error display rings. The replacement bridge cognitive matrix is now certified as **Fully Operational and Ready for Underway Navigation**.

## 7. Phase 5: Asymmetric Port/Starboard Actuator Calibration
This field protocol verifies electrical decoupling tolerances across dual independent hydraulic control loops (PUNVCPRT and PUNVCSTB) before underway operations.

*   [ ] **5.1 Channel Isolation Verification**: Ensure the asymmetric matrix outputs split differential commands cleanly when a lateral bias is active.
    *   *Field Test*: Manually inject an artificial 5-degree port hull list via the diagnostic override console while holding a straight heading.
    *   *Verification*: Port control loop signal must shift to a protective negative potential (e.g., -1.43 VDC) while the Starboard loop tracks a counter-acting positive bias (+1.43 VDC).
*   [ ] **5.2 Voltage Balance Field Measurement**: Hook an isolated digital multimeter to the differential breakout pins on the main RS-422 interface terminal strip.
    *   *Verification*: Zero-point cross-talk check. With the hull sitting flat at the pier (0.0° roll, 0.0 rad/s roll rate), the differential reading between Port (Pin 3/4) and Starboard (Pin 7/8) loops must sit within 0.00 VDC ± 15mV. If the variance exceeds 15mV, re-null the amplifier trim-pots before clearing the steering interlock.
*   [ ] **5.3 Combat-Lock Bit Step-Response**: Force the weapon parser to simulate an active storm-firing trajectory state flag.
    *   *Verification*: Observe the oscilloscope on the steering gear PLC interface. The 4th tracking data field (Combat Lock Bit) must snap instantaneously from `0` to `1`, signaling the valves to open their high-flow hydraulic bypass paths.

## 8. Modular System Expansion Guide (For Future Generations)
To preserve the hard-deterministic execution profiles of this platform, all newly developed software plugins, hardware interfaces, or sensor processing layers must conform to the strict "Co-Processor Architecture Pattern."

### A. Architectural Golden Rules
1. **Never Block the Loop**: Any new module requiring physical I/O over serial, USB, Ethernet, or file storage MUST manage its data transport arrays inside an isolated background execution thread. 
2. **Interface via Caches Only**: New modules must read inputs from a thread-safe snapshot dict and dump their calculated results into a locked memory register. Never allow an unvalidated external data stream to directly alter active control law states.
3. **Keep the Core Plant Pure**: The core calculation loop inside `main.py` should only handle math transformations (dt = 0.02). It should never manage string connections, parse serial bytes, or open disk file blocks.

### B. Standard Code Block Template for New Subsystem Modules
When constructing a new prediction or sensor processing layer, utilize this structural template to ensure uniform compilation and thread safety across generations:

```python
# File Template Name: generic_expansion_module.py
# Location: /src/control_core/ or /src/network_layer/

import threading
import time

class GenericUnivacExpansionModule:
    def __init__(self, physical_bounds: dict):
        """Initializes state vectors and establishes hardware memory protection locks."""
        self.lock = threading.Lock()
        self.module_active = False
        
        # Load static variables out of the boot profile
        self.safety_limit = float(physical_bounds.get('generic_limit_value', 100.0))
        
        # Local calculation memory register
        self.latest_processed_output = 0.0

    def compute_deterministic_math_step(self, live_telemetry: dict, dt: float) -> float:
        """
        Calculates values synchronously inside the 50Hz main timing wheel.
        This function MUST be highly optimized and completely free of I/O operations.
        """
        raw_input = float(live_telemetry.get('target_sensor_variable', 0.0))
        
        # Execute your algebraic or differential control matrix step
        calculated_result = raw_input * 0.145 * dt
        
        with self.lock:
            self.latest_processed_output = max(-self.safety_limit, min(self.safety_limit, calculated_result))
            return self.latest_processed_output

    def get_thread_safe_snapshot(self) -> float:
        """Extracts values cleanly for external telemetry logging or UI blitting layers."""
        with self.lock:
            return self.latest_processed_output
```
