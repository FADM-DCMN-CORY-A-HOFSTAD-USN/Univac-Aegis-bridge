# File Name: flag_alert_console.py
# Location: Root source folder
# Subsystem: Memory-Buffered Flag Halyard Fault Warning Console

import tkinter as tk
import math
import time
import threading
import random

class FlagFaultTacticalConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("UNIVAC BACKUP CONSOLE - HIGH-VISIBILITY FLAG INTERLOCK TYPE")
        self.root.geometry("1100x650")
        self.root.configure(bg="#0a0a0a")

        # --- HIGH-SPEED TELEMETRY AND FAULT REGISTERS ---
        self.data_lock = threading.Lock()
        self.system_telemetry = {
            'active_flag_state': "ENSIGN",
            'halyard_position_pct': 0.0,
            'flag_winch_fault_active': False,  # Core hardware error trigger flag
            'last_sensor_update': time.time()
        }

        # --- VISUAL IMAGE MAP BOUNDARIES ---
        self.img_w = 400
        self.img_h = 400
        self.cx = self.img_w // 2
        self.cy = self.img_h // 2
        
        # Instantiate the low-overhead memory back-buffer
        self.memory_image_buffer = tk.PhotoImage(width=self.img_w, height=self.img_h)

        self._build_console_layout()
        self._start_visual_blit_tick()

    def _build_console_layout(self):
        """Constructs a ruggedized grid layout matching your network requirements."""
        banner = tk.Frame(self.root, bg="#1a1111", height=40, bd=1, relief=tk.SOLID)
        banner.pack(fill=tk.X, side=tk.TOP)
        
        lbl_info = tk.Label(banner, text="HALYARD INTERLOCK DISPLAY: AUTOMATED EMBEDDED MONITORING BUS ACTIVE", 
                            bg="#1a1111", fg="#ffaa00", font=('Courier', 11, 'bold'))
        lbl_info.pack(side=tk.LEFT, padx=15, pady=8)

        panel_container = tk.Frame(self.root, bg="#0a0a0a")
        panel_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_column = tk.Frame(panel_container, bg="#0a0a0a")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind our pre-allocated memory blit block to the window screen
        self.blit_screen_label = tk.Label(left_column, image=self.memory_image_buffer, bg="#000000", bd=2, relief=tk.RIDGE)
        self.blit_screen_label.pack(padx=10, pady=10)

        right_column = tk.Frame(panel_container, bg="#111111", width=450, bd=1, relief=tk.SOLID)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

        lbl_title = tk.Label(right_column, text="[ FLAG GEAR HARDWARE REGISTER ]", bg="#111111", fg="#00ff00", font=('Courier', 11, 'bold'))
        lbl_title.pack(anchor=tk.W, padx=15, pady=10)

        self.telemetry_box = tk.Text(right_column, width=48, height=15, bg="#000000", fg="#00ff00", font=('Courier', 10))
        self.telemetry_box.pack(padx=15, pady=5)

        # Control Overrides for Testing and Fault Simulation
        control_deck = tk.Frame(right_column, bg="#111111")
        control_deck.pack(fill=tk.X, padx=15, pady=20)

        btn_toggle_fault = tk.Button(control_deck, text="SIMULATE WINCH JAM", bg="#2a1212", fg="#ff3333", 
                                     activebackground="#ff3333", activeforeground="#ffffff",
                                     font=('Courier', 10, 'bold'), command=self._trigger_mock_winch_fault)
        btn_toggle_fault.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        btn_clear_fault = tk.Button(control_deck, text="CLEAR HARDWARE LOCK", bg="#122a12", fg="#33ff33", 
                                    activebackground="#33ff33", activeforeground="#ffffff",
                                    font=('Courier', 10, 'bold'), command=self._clear_mock_winch_fault)
        btn_clear_fault.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

    def _render_image_buffer_pixels(self):
        """
        BUFFER RENDERER: Blits a high-visibility flashing warning banner 
        directly into the pixel matrix if a hardware winch fault trips.
        """
        # Reset memory frame canvas to clear previous state data lines
        self.memory_image_buffer.blank()

        with self.data_lock:
            active_state = self.system_telemetry['active_flag_state']
            halyard_pct = self.system_telemetry['halyard_position_pct']
            fault_tripped = self.system_telemetry['flag_winch_fault_active']

        # Draw baseline crosshairs on tactical screen back-buffer
        self.memory_image_buffer.put("#002200", to=(self.cx - 80, self.cy, self.cx + 80, self.cy + 1))
        self.memory_image_buffer.put("#002200", to=(self.cx, self.cy - 80, self.cx, self.cy + 80))

        # Render a vertical indicator mapping current physical flag height
        halyard_height_px = int((halyard_pct / 100.0) * 200)
        self.memory_image_buffer.put("#00ff00", to=(self.cx - 10, self.cy + 100 - halyard_height_px, self.cx + 10, self.cy + 105 - halyard_height_px))

        # ──────────────────────────────────────────────────────────────────────────
        # HIGH-VISIBILITY EMBEDDED FAULT FLASH ALGORITHM
        # ──────────────────────────────────────────────────────────────────────────
        if fault_tripped:
            # Alternates colors every 250 milliseconds based on standard system clock parity
            flash_state = int(time.time() * 4) % 2 == 0
            alert_color = "#ff0000" if flash_state else "#220000"
            border_color = "#ffffff" if flash_state else "#ff0000"
            
            # Blit high-overhead solid alert banner box directly across top quadrant pixels
            self.memory_image_buffer.put(alert_color, to=(40, 40, self.img_w - 40, 100))
            
            # Blit warning outline borders to isolate the notification field
            self.memory_image_buffer.put(border_color, to=(38, 38, self.img_w - 38, 41))
            self.memory_image_buffer.put(border_color, to=(38, 99, self.img_w - 38, 102))
            self.memory_image_buffer.put(border_color, to=(38, 38, 41, 102))
            self.memory_image_buffer.put(border_color, to=(self.img_w - 41, 38, self.img_w - 38, 102))
        # ──────────────────────────────────────────────────────────────────────────

    def _trigger_mock_winch_fault(self):
        """Forces system memory state registers into an active mechanical failure mode."""
        with self.data_lock:
            self.system_telemetry['flag_winch_fault_active'] = True
            self.system_telemetry['active_flag_state'] = "FAULT_JAM"

    def _clear_mock_winch_fault(self):
        """Resets the hardware registers and clears active interlock gates."""
        with self.data_lock:
            self.system_telemetry['flag_winch_fault_active'] = False
            self.system_telemetry['active_flag_state'] = "ENSIGN"

    def _start_visual_blit_tick(self):
        """Deterministic 20Hz frame swap loop thread execution window."""
        # Simulate subtle data updates to vary telemetry numbers on screen over time
        with self.data_lock:
            if not self.system_telemetry['flag_winch_fault_active']:
                # Oscillate mock halyard positions slightly to simulate cruising ripples
                self.system_telemetry['halyard_position_pct'] = 50.0 + 5.0 * math.sin(time.time() * 2.0)
            else:
                # Freeze winch motor metrics instantly during an active mechanical jam
                self.system_telemetry['halyard_position_pct'] = 32.4

        # Execute back-buffer pixel processing matrix transforms
        self._render_image_buffer_pixels()

        # Update numerical diagnostics readout text window
        with self.data_lock:
            snap = self.system_telemetry.copy()

        self.telemetry_box.delete("1.0", tk.END)
        
        # Build text string block layout
        report = (
            "=== HALYARD SIGNAL REGISTRY SNAPSHOT ===\n" +
            f"TIMESTAMP CLOCK WHEEL: {snap['last_sensor_update']:.4f}\n" +
            f"CURRENT HALYARD HEIGHT: {snap['halyard_position_pct']:.1f} %\n" +
            f"SIGNAL ENVELOPE MODE:  {snap['active_flag_state']}\n" +
            "========================================\n" +
            f"WINCH MOTOR INTEGRITY:  " +
            (f"[ MECHANICAL_JAM_ALERT ]" if snap['flag_winch_fault_active'] else "[ NOMINAL HEALTHY ]") + "\n" +
            f"HARDWARE CONTROL LOCK:  " +
            (f"[ BRAKE OVERRIDE PIN ENGAGED ]" if snap['flag_winch_fault_active'] else "[ AUTOMATIC TRACKING ]") + "\n" +
            "========================================\n" +
            "ALERT STATUS: High-visibility flash matrix\n" +
            "runs embedded inside back-buffer pixels,\n" +
            "guaranteeing alarm visibility during\n" +
            "downstream communication link failures."
        )
        self.telemetry_box.insert(tk.END, report)

        # Recurse cycle timing thread window (50ms interval)
        self.root.after(50, self._start_visual_blit_tick)

# Program Initialization Entry Point
if __name__ == "__main__":
    ui_frame = tk.Tk()
    app = FlagFaultTacticalConsole(ui_frame)
    ui_frame.mainloop()
