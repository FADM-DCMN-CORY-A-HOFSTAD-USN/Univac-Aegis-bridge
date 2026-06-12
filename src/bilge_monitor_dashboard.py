
# File Name: bilge_monitor_dashboard.py
# Location: Root source folder
# Subsystem: Independent Environmental Bilge Monitoring and Reporting Console

import tkinter as tk
import math
import time
import random

class BilgeMonitorDashboard:
    def __init__(self, root, router_instance=None):
        """
        Initializes the low-overhead environmental monitoring console.
        router_instance: Optional active BridgeNetworkRouter object to extract live wire telemetry.
        """
        self.root = root
        self.router = router_instance
        
        self.root.title("UNIVAC REPLACEMENT BRIDGE - ENVIRONMENTAL AUDIT CONSOLE")
        self.root.geometry("1000x600")
        self.root.configure(bg="#080d08")
        
        # --- LOCAL DISPLAY FALLBACK STATE REGISTERS ---
        # Used to drive animations if physical network buses are running a simulation layer
        self.current_authority_mode = "UNIVAC"
        self.oil_ppm = 2.4
        self.total_discharged_liters = 142.5
        self.overboard_valve_open = 1
        self.recirc_valve_open = 0
        self.routing_source = "UNIVAC_MAINFRAME_PASS_THROUGH"
        
        # --- BACK-BUFFER MEMORY PIXEL IMAGE ---
        self.img_w = 400
        self.img_h = 400
        self.memory_image_buffer = tk.PhotoImage(width=self.img_w, height=self.img_h)
        
        self._build_interface_layout()
        self._start_blit_refresh_tick()

    def _build_interface_layout(self):
        """Constructs a high-contrast industrial grid layout for tactical monitoring."""
        # Top Environmental Compliance Warning Header Strip
        header_strip = tk.Frame(self.root, bg="#0f2611", height=45, bd=1, relief=tk.SOLID)
        header_strip.pack(fill=tk.X, side=tk.TOP)
        
        lbl_compliance = tk.Label(header_strip, text="MARPOL COMPLIANCE MONITOR: GLOBAL REAL-TIME ENVIRONMENTAL TELEMETRY AUDIT", 
                                  bg="#0f2611", fg="#00ff00", font=('Courier', 11, 'bold'))
        lbl_compliance.pack(side=tk.LEFT, padx=15, pady=10)

        # Workspace Container Split
        workspace = tk.Frame(self.root, bg="#080d08")
        workspace.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Grid: Dynamic Visual Indicator Block (Memory Buffer Map)
        left_grid = tk.Frame(workspace, bg="#080d08")
        left_grid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.screen_label = tk.Label(left_grid, image=self.memory_image_buffer, bg="#000000", bd=2, relief=tk.SUNKEN)
        self.screen_label.pack(padx=10, pady=10)

        # Right Grid: Numerical Report Ledger Text Window
        right_grid = tk.Frame(workspace, bg="#111c11", width=420, bd=1, relief=tk.SOLID)
        right_grid.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        lbl_log_title = tk.Label(right_grid, text="[ RE-RECEIVER TELEMETRY AUDIT LEDGER ]", bg="#111c11", fg="#00ff00", font=('Courier', 11, 'bold'))
        lbl_log_title.pack(anchor=tk.W, padx=15, pady=10)

        self.reporting_ledger_box = tk.Text(right_grid, width=46, height=20, bg="#000000", fg="#00ff00", font=('Courier', 10))
        self.reporting_ledger_box.pack(padx=15, pady=5)

    def _render_environmental_graphics_buffer(self):
        """
        Calculates fluid status variations and blits visual gauges directly 
        onto the memory image frame to eliminate GPU canvas rendering delays.
        """
        # Reset local canvas memory back-buffer frame
        self.memory_image_buffer.blank()
        
        cx, cy = self.img_w // 2, self.img_h // 2
        
        # Determine tracking indicator heights based on live PPM sensor results
        # Normal bounds are mapped between 0.0 PPM and 20.0 PPM scale ceilings
        ppm_bar_height = int(max(0, min(250, (self.oil_ppm / 20.0) * 250)))
        
        # Color transition rules: Green under legal limit, blinking bright red over 14.8 PPM
        if self.oil_ppm >= 14.8:
            status_color = "#ff0000" if (int(time.time() * 2) % 2 == 0) else "#330000"
        else:
            status_color = "#00ff00"

        try:
            # 1. Blit the structural Oil Concentration Gauge Bar (Left Indicator Box)
            # Fills raw pixel coordinates directly in memory
            self.memory_image_buffer.put(status_color, to=(40, 350 - ppm_bar_height, 90, 350))
            # Draw stationary target ceiling indicator outline at the 15 PPM boundary zone
            ceiling_y = 350 - int((15.0 / 20.0) * 250)
            self.memory_image_buffer.put("#ff3333", to=(30, ceiling_y, 100, ceiling_y + 2))

            # 2. Blit the Flow State Piping Diagrams (Right Indicator Maps)
            pipe_color = "#00ff00" if self.overboard_valve_open == 1 else "#003300"
            recirc_color = "#ffcc00" if self.recirc_valve_open == 1 else "#003300"
            
            # Render Overboard Pipe block path mappings
            self.memory_image_buffer.put(pipe_color, to=(150, cy - 15, 350, cy + 15))
            # Render Recirculation Diverter routing block path mappings
            self.memory_image_buffer.put(recirc_color, to=(220, cy + 15, 250, 350))

        except Exception:
            pass # Gracefully shield rendering matrices from runtime division constraints

    def _start_blit_refresh_tick(self):
        """Hard deterministic 20Hz visual refresh loop thread execution window."""
        # 1. Ingest metrics from live data buses or step through local test patterns
        if self.router is not None:
            # Thread-safely extract the multi-variable telemetry block from the shared caches
            sync_data = self.router.get_synchronized_telemetry()
            bilge_telemetry = sync_data.get('upstream_autonomy_telemetry', {}).get('Bilge_Environmental_Status', {})
            authority_telemetry = sync_data.get('upstream_autonomy_telemetry', {}).get('Bilge_Authority_State', {})
            
            self.oil_ppm = float(sync_data.get('oil_content_ppm', 2.4))
            self.current_authority_mode = authority_telemetry.get('active_authority_mode', 'UNIVAC')
            self.routing_source = authority_telemetry.get('routing_source_string', 'UNIVAC_MAINFRAME_PASS_THROUGH')
            self.overboard_valve_open = int(authority_telemetry.get('resolved_overboard_valve_open', 0))
            self.recirc_valve_open = int(authority_telemetry.get('resolved_recirculation_valve_open', 0))
            self.total_discharged_liters = float(bilge_telemetry.get('total_clean_water_discharged_liters', 0.0))
        else:
            # Simulation Mode fallback behavior if run without server wrappers attached
            self.oil_ppm = max(0.5, min(19.0, self.oil_ppm + random.choice([-0.4, 0.0, 0.4])))
            if self.oil_ppm >= 14.8:
                self.current_authority_mode = "REPLACEMENT"
                self.routing_source = "OUR_CORE_PHYSICS_LOOP"
                self.overboard_valve_open = 0
                self.recirc_valve_open = 1
            else:
                # Cycle simulated modes to prove the console reports independent of source
                self.current_authority_mode = random.choice(["UNIVAC", "SEA_MACHINES", "REPLACEMENT"])
                self.routing_source = f"{self.current_authority_mode}_ACTIVE_BUS_LINK"
                self.overboard_valve_open = 1
                self.recirc_valve_open = 0
            self.total_discharged_liters += (5.0 * 0.05) if self.overboard_valve_open == 1 else 0.0

        # 2. Render pixel updates and blit back-buffer frame to screen
        self._render_environmental_graphics_buffer()

        # 3. Reconstruct flat report text parameters in the text window panel
        self.reporting_ledger_box.delete("1.0", tk.END)
        report_text = (
            "============================================\n"
            f"SYSTEM TIME METRIC:     {time.time():.3f}\n"
            f"ACTIVE CONTROL MODE:    {self.current_authority_mode}\n"
            f"BUS ROUTING SOURCE:     {self.routing_source}\n"
            "============================================\n"
            f"OIL CONCENTRATION:      {self.oil_ppm:8.2f} PPM\n"
            f"LEGAL DISCHARGE LIMIT:      15.00 PPM\n"
            f"SAFETY SYSTEM GATING:   {'[ INTERLOCK BLOCKED ]' if self.oil_ppm >= 14.8 else '[ CLEAR / SECURE ]'}\n"
            "--------------------------------------------\n"
            f"OVERBOARD ACCUMULATOR:  {self.overboard_valve_open}\n"
            f"RECIRCULATION RE-ROUTE: {self.recirc_valve_open}\n"
            f"TOTAL AUDITED DISCHARGE: {self.total_discharged_liters:8.1f} L\n"
            "============================================\n"
            "STATUS: Environmental audit logging stream\n" +
            "active. Capturing multi-source parameters\n" +
            "independently of active command node choices."
        )
        self.reporting_ledger_box.insert(tk.END, report_text)

        # Recurse cycle timing thread window (50ms interval)
        self.root.after(50, self._start_visual_blit_tick if hasattr(self, '_start_visual_blit_tick') else self._start_blit_refresh_tick)

# Program Entry Point
if __name__ == "__main__":
    ui_frame = tk.Tk()
    # Run in simulation mode for standalone testing validation
    app = BilgeMonitorDashboard(ui_frame, router_instance=None)
    ui_frame.mainloop()
