# File Name: hardware_watchdog.py
# Location: /src/network_layer/
# Subsystem: Asynchronous Co-Processor Thread Health & Serial Link Watchdog

import threading
import time
from typing import Dict, Any

class AsynchronousHardwareWatchdog:
    def __init__(self, critical_timeout_sec: float = 1.0):
        """
        Initializes the standalone thread safety monitor.
        critical_timeout_sec: Max allowed delay before declaring a thread frozen or dead.
        """
        self.timeout = critical_timeout_sec
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Central register tracking the live timestamp updates of background nodes
        self.thread_heartbeats = {
            'NMEA_SERIAL_IN': time.time(),
            'WEAPON_BUS_IN': time.time(),
            'TCP_COMMAND_IN': time.time(),
            'MAIN_CORE_MATH': time.time()
        }
        
        # System health status flags
        self.system_faulted = False
        self.tripped_subsystems = []

    def poke_watchdog(self, thread_name: str):
        """
        Call this function inside the active loops of your background threads 
        at each cycle iteration to register a fresh, healthy heartbeat.
        """
        with self.lock:
            if thread_name in self.thread_heartbeats:
                self.thread_heartbeats[thread_name] = time.time()

    def _execute_monitor_loop(self):
        """Thread-isolated background monitoring wheel checking time stamps."""
        print(f"[WATCHDOG] Active thread check routine deployed. Timeout ceiling: {self.timeout}s")
        
        while self.is_monitoring:
            current_time = time.time()
            local_faults = []
            
            with self.lock:
                for thread_name, last_heartbeat in self.thread_heartbeats.items():
                    time_delta = current_time - last_heartbeat
                    
                    if time_delta > self.timeout:
                        local_faults.append(thread_name)
            
            # Evaluate systemic health parameters
            if local_faults:
                self.system_faulted = True
                self.tripped_subsystems = local_faults
                self._trigger_emergency_safe_mode()
            else:
                self.system_faulted = False
                self.tripped_subsystems.clear()
                
            # Run checks at a steady 10Hz frequency cadence (Every 100ms)
            time.sleep(0.1)

    def _trigger_emergency_safe_mode(self):
        """
        CRITICAL HARDWARE PROTECTION GATING:
        Executed instantly if any core serial links or math wheels stall.
        """
        print(f"\n[CRITICAL_WATCHDOG_TRIP] THREAD FREEZE DETECTED: {self.tripped_subsystems}")
        print("[WATCHDOG] FORCE-DROPPING ACTUATOR DISPATCH TO ZERO TORQUE STATE.")
        # This flag is consumed directly by the main router matrix to kill power commands

    def get_watchdog_diagnostics(self) -> dict:
        """Safe thread-locked interface to pass telemetry flags up to the router or UI."""
        current_time = time.time()
        diagnostics = {}
        
        with self.lock:
            for name, last_hb in self.thread_heartbeats.items():
                diagnostics[f"delay_{name.lower()}_sec"] = round(current_time - last_hb, 3)
                
        diagnostics['watchdog_system_faulted'] = self.system_faulted
        diagnostics['watchdog_tripped_subsystems'] = self.tripped_subsystems
        return diagnostics

    def start_watchdog(self):
        """Spins up the isolated software-defined tracking inspector thread."""
        if self.is_monitoring:
            return
        self.is_monitoring = True
        
        # Pre-seed heartbeats to current boot time to prevent instant false trips
        with self.lock:
            boot_now = time.time()
            for key in self.thread_heartbeats.keys():
                self.thread_heartbeats[key] = boot_now
                
        self.monitor_thread = threading.Thread(target=self._execute_monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_watchdog(self):
        """Gracefully secures the monitoring thread context."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        print("[WATCHDOG] Safety monitoring thread secured safely.")

# Verification Simulation Environment
if __name__ == "__main__":
    print("VERIFYING WATCHDOG THREAD INTERVENTION SCHEMAS:")
    print("=" * 65)
    
    # Initialize a watchdog with a fast 0.5-second trip limit
    wd = AsynchronousHardwareWatchdog(critical_timeout_sec=0.5)
    wd.start_watchdog()
    
    # Simulate healthy processing cycles poking the monitor
    wd.poke_watchdog('MAIN_CORE_MATH')
    wd.poke_watchdog('NMEA_SERIAL_IN')
    wd.poke_watchdog('WEAPON_BUS_IN')
    wd.poke_watchdog('TCP_COMMAND_IN')
    
    print("Simulating a physical serial cable sever or thread lock up (waiting 0.7s)...")
    time.sleep(0.7)
    
    # Check health parameters after the simulated link loss window
    stats = wd.get_watchdog_diagnostics()
    print(f"Watchdog Status Code State Flag: {stats['watchdog_system_faulted']}")
    print(f"Tripped Network Subsystems:      {stats['watchdog_tripped_subsystems']}")
    
    wd.stop_watchdog()
