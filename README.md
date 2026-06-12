# Univac to Aegis Digital Tactical Intermediary Controller (DTIC)

**Description:**
A tactical software bridge and hardware translation layer connecting 1970s UNIVAC mainframes (CP-642B / AN/UYK-7) to modern Aegis Combat System DDS networks via MIL-STD-1397 to Ethernet conversion.

The Digital Tactical Intermediary Controller (DTIC) repository provides the complete software translation layer, protocol bridge, and legacy fallback logic required to integrate 1970s naval computing hardware with modern Aegis open-architecture networks. By capturing asynchronous 32-bit parallel MIL-STD-1397 data and translating it into highly deterministic, DDS-compliant UDP/IP packets, this architecture offloads complex kinematics to the modern network while hardening the legacy mainframe as a secure, real-time actuation terminal.

It also features advanced hydrodynamic state predictors (LQR/EKF) to manage shallow-water squat effects and prevent structural gyroscopic shear on propulsion systems during high-speed Aegis-commanded maneuvers.

**Topics:** `aegis-combat-system`, `univac`, `dds-middleware`, `mil-std-1397`, `cms-2`, `tactical-software`, `legacy-modernization`, `real-time-networking`, `defense-tech`, `fpga-interface`, `cpp17`, `opendds`

## Core Components
- **`NTDS_BRIDGE_PATCH.cms2` & `ACTUATE.CMS`**: Hardened CMS-2Y patches that replace legacy weapon math with hardware input handlers featuring CRC bitmask verification and velocity delta clamps.
- **`main.cpp` & `downlink_driver.cpp`**: Symmetric multiprocessing (SMP) C++ DDS network drivers pinned to isolated CPU cores to handle extreme UDP saturation.
- **`USER_QOS_PROFILES.xml`**: Strict DDS Quality of Service profiles ensuring exclusive ownership and low-latency target delivery using DSCP 46/48 tagging.
- **`hydro_coordinated_predictor.py`**: A high-precision physics module implementing Extended Kalman Filters, Linear-Quadratic Regulators (LQR), and S-Curve limits to protect the physical propeller and rudder from hydrodynamic shear.
- **`dtic_stress_test.py`**: A multicore Numba JIT-compiled fuzzing harness to validate UNIVAC fallback logic under saturated network conditions.

## Build Instructions
1. Install an enterprise DDS distribution (OpenDDS/RTI Connext) and the GNU toolchain.
2. Initialize build directory: `mkdir build && cd build`
3. Configure CMake: `cmake -DCMAKE_BUILD_TYPE=Release ..`
4. Compile binaries: `cmake --build . --config Release -j$(nproc)`
