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

---

## 6. Pre-Sail Certification Sign-Off
Once all four verification phases are successfully executed without triggering hard faults or mechanical linkage jam interlocks, clear the bridge console error display rings. The replacement bridge cognitive matrix is now certified as **Fully Operational and Ready for Underway Navigation**.
