import math
import json
from typing import Dict, Any

class ModernizedRFResonanceTuner:
    def __init__(self):
        self.c = 299792458.0 # Speed of light (m/s)
        
    def tune_microwave_horn(self, h, w):
        """Calculates TE10 mode cutoff for horns (e.g., Space Needle, AN/SPS-39)."""
        f_cutoff = self.c / (2.0 * max(h, w))
        f_opt = f_cutoff * 1.35
        return {"opt_freq_mhz": round(f_opt / 1e6, 2), "gain_dbi": round(10*math.log10((4*math.pi*h*w)/(self.c/f_opt)**2), 2)}

    def tune_biconical_hourglass(self, length, angle_deg):
        """Calculates resonance for Telecloche Omni Arrays."""
        f_res = self.c / (4.0 * length)
        z0 = 120.0 * math.log(1.0 / math.tan(math.radians(angle_deg) / 4.0))
        return {"res_freq_mhz": round(f_res / 1e6, 2), "z0_ohms": round(z0, 2)}

    def tune_log_periodic(self, l_max, l_min):
        """Calculates bandwidth for Arrowhead matrices."""
        f_low = self.c / (2.0 * l_max)
        f_high = self.c / (2.0 * l_min)
        return {"f_low_mhz": round(f_low / 1e6, 2), "f_high_mhz": round(f_high / 1e6, 2)}

    def tune_helical_coil(self, dia, pitch, turns):
        """Calculates axial mode for satellite/OE-82 coils."""
        circ = math.pi * dia
        f_opt = self.c / circ
        z0 = 140.0 * (circ / circ) # Axial mode ~140 Ohm
        return {"center_freq_mhz": round(f_opt / 1e6, 2), "z0_ohms": 140.0, "pol": "RHCP"}

# Example Usage:
# tuner = ModernizedRFResonanceTuner()
# horn_profile = tuner.tune_microwave_horn(1.8, 1.2)
