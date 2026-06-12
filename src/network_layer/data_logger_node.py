# File Name: data_logger_node.py
# Location: /src/network_layer/
# Subsystem: Asynchronous Asymmetric Telemetry & Mission Param Disk Logger

import os
import csv
import queue
import threading
import time
from typing import Dict, Any

class AutomatedMissionDataLogger:
    def __init__(self, log_directory: str = "logs", file_prefix: str = "mission_telemetry"):
        """
        Initializes the thread-isolated asynchronous mission parameter logger.
        log_directory: Absolute or relative directory path where CSV files will be stored.
        file_prefix: Base naming convention for generated telemetry spreadsheets.
        """
        self.log_dir = os.path.join(os.path.dirname(__file__), "..", log_directory)
        self.file_prefix = file_prefix
        self.log_file_path = ""
        
        # High-speed RAM thread-safe FIFO queue to offload I/O blocking from the math core
        self.log_queue = queue.Queue(maxsize=5000)
        self.is_logging = False
        self.worker_thread = None
        
        # Exact explicit structural header schema row for maritime telemetry audits
        self.csv_headers = [
            "timestamp_epoch", "vessel_speed_ms", "water_depth_m", "shaft_rpm", 
            "command_torque_nm", "command_rudder_deg", "structural_load_pct", 
            "ventilation_index", "roll_angle_deg", "roll_rate_degs", 
            "weapon_azimuth_deg", "weapon_elevation_deg", "computer_temp_c"
        ]

    def _initialize_log_file(self):
        """Creates the directory matrix and initializes a fresh time-stamped CSV spreadsheet file."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
            
        # Format filename using precise system time definitions
        time_str = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.file_prefix}_{time_str}.csv"
        self.log_file_path = os.path.join(self.log_dir, filename)
        
        # Write structural system column headers to disk immediately on boot layout
        try:
            with open(self.log_file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_headers)
            print(f"[LOGGER] New mission telemetry spreadsheet initialized at: {self.log_file_path}")
        except IOError as e:
            print(f"[LOGGER_ERROR] Severe storage array write restriction caught during header build: {e}")

    def log_snapshot(self, engine_commands: Dict[str, Any], live_telemetry: Dict[str, Any]):
        """
        Non-blocking high-speed RAM entry point. Call this directly inside your 50Hz 
        main calculation loop to cache snapshot states instantly.
        """
        if not self.is_logging:
            return
            
        # Isolate and flatten nested dictionary properties into a structural array matching headers
        try:
            insight_link = engine_commands.get('upstream_autonomy_telemetry', {}).get('UNIVAC_Water_Insight_Link', {})
            weapon_link = engine_commands.get('upstream_autonomy_telemetry', {}).get('Weapon_Balance_Metrics', {})
            
            snapshot_row = [
                time.time(),
                live_telemetry.get('speed_ms', 0.0),
                live_telemetry.get('depth', 50.0),
                live_telemetry.get('rpm', 0.0),
                engine_commands.get('command_motor_torque_nm', 0.0),
                engine_commands.get('command_rudder_angle_deg', 0.0),
                insight_link.get('structural_fatigue_load_percentage', 0.0),
                insight_link.get('subsurface_ventilation_index', 1.0),
                math.degrees(live_telemetry.get('roll_angle_rad', 0.0)) if 'math' in globals() else live_telemetry.get('roll_angle_rad', 0.0) * 57.2958,
                math.degrees(live_telemetry.get('roll_rate_rads', 0.0)) if 'math' in globals() else live_telemetry.get('roll_rate_rads', 0.0) * 57.2958,
                weapon_link.get('weapon_azimuth_deg', 0.0),
                weapon_link.get('weapon_elevation_deg', 0.0),
                live_telemetry.get('computer_temperature_c', 25.0)
            ]
            
            # Non-blocking injection into memory queue. If full, drop frame to protect calculation clock.
            self.log_queue.put_nowait(snapshot_row)
        except queue.Full:
            # Indicates disk subsystem is severely backed up or completely frozen
            pass 
        except Exception as e:
            pass

    def _io_writer_worker_loop(self):
        """Asynchronous disk I/O worker thread loop."""
        self._initialize_log_file()
        
        # Open resource and append lines progressively over long voyages
        while self.is_logging or not self.log_queue.empty():
            try:
                # Block thread until data is queued, timing out every 1.0s to check state gates
                row_data = self.log_queue.get(timeout=1.0)
                
                with open(self.log_file_path, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(row_data)
                    
                self.log_queue.task_done()
            except queue.Empty:
                continue # Recycle listening checks if loop queue goes quiet at the pier
            except IOError as disk_fault:
                print(f"[LOGGER_ERROR] Asynchronous flash storage write-access delayed: {disk_fault}")
                time.sleep(1.0) # Back off thread to clear operating system storage pipelines

    def start_logging_services(self):
        """Spins up the isolated disk-writing worker background thread context."""
        if self.is_logging:
            return
        self.is_logging = True
        self.worker_thread = threading.Thread(target=self._io_writer_worker_loop, daemon=True)
        self.worker_thread.start()
        print("[LOGGER] Automated mission parameter recording thread successfully spawned.")

    def stop_logging_services(self):
        """Gracefully flushes remaining memory cache rows out to disk and secures file locks."""
        print(f"[LOGGER] Securing data pipes... Flushing {self.log_queue.qsize()} cached data frames to storage.")
        self.is_logging = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        print("[LOGGER] Mission telemetry file closed and locked safely on hardware storage.")

# Verification Integration Runtime
if __name__ == "__main__":
    logger = AutomatedMissionDataLogger(log_directory="test_logs")
    logger.start_logging_services()
    
    # Generate dummy testing matrix variables mimicking a fast-paced tracking calculation frame
    dummy_commands = {
        'command_motor_torque_nm': 45000.0, 'command_rudder_angle_deg': -5.4,
        'upstream_autonomy_telemetry': {
            'UNIVAC_Water_Insight_Link': {'structural_fatigue_load_percentage': 12.5, 'subsurface_ventilation_index': 0.98},
            'Weapon_Balance_Metrics': {'weapon_azimuth_deg': 90.0, 'weapon_elevation_deg': 15.0}
        }
    }
    dummy_telemetry = {'speed_ms': 8.2, 'depth': 12.4, 'rpm': 510.0, 'roll_angle_rad': 0.02, 'roll_rate_rads': 0.05, 'computer_temperature_c': 18.5}
    
    print("\nCaching tracking data snapshots into RAM buffer memory structures...")
    for _ in range(5):
        logger.log_snapshot(dummy_commands, dummy_telemetry)
        time.sleep(0.02) # Emulate a 50Hz calculation cycle pace
        
    time.sleep(0.5) # Allow background I/O thread to pick up and clear the queues
    logger.stop_logging_services()
    
    # Cleanup verification file paths upon diagnostic validation end
    if os.path.exists(logger.log_file_path):
        os.remove(logger.log_file_path)
        os.rmdir(logger.log_dir)
