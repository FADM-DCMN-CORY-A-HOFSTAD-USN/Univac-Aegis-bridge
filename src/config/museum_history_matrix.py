# System Math Formulas Catalog Matrix (For Museum Interactive Simulations)

# 1. HOSPITAL: Blood Bank Inventory Decay (Poisson Probability Distribution)
# Predicts stockouts of rare blood types based on daily base usage rate (lam)
def equation_hospital_blood_decay(lam: float, k: int) -> float:
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

# 2. ELECTRICITY: Generator Phase Synchronization Angle Delta
# Calculates phase drift between base power and incoming generator lines
def equation_power_phase_sync(voltage_a: float, voltage_b: float, angle_rad: float) -> float:
    return voltage_a * voltage_b * math.sin(angle_rad)

# 3. PUBLIC UTILITY: Overboard Hydraulic Fluid Reynolds Number
# Calculates flow state to prevent valve cavitations inside sump pump drains
def equation_utility_reynolds_number(velocity: float, pipe_diameter: float, viscosity: float) -> float:
    return (velocity * pipe_diameter) / viscosity

# 4. GYM: Anthropometric Physical Readiness Scaling Index
# Calculates normalized lean body mass parameters for troop deployment readiness
def equation_gym_readiness_index(weight_kg: float, height_meters: float) -> float:
    return weight_kg / (height_meters ** 2)

# 5. LAB: Radar Cross-Section (RCS) Geometric Target Echo Factor
# Calculates reflective area parameters of incoming air contacts based on aspect angle
def equation_lab_radar_cross_section(radius: float, wavelength: float) -> float:
    return (math.pi * (radius ** 4)) / (4 * (wavelength ** 2))

# 6. ENGINEERING: Crane Hook Torsional Cable Deflection
# Calculates structural twisting strain when hoisting heavy weapon turrets
def equation_engineering_cable_twist(torque: float, length: float, shear_modulus: float, polar_inertia: float) -> float:
    return (torque * length) / (shear_modulus * polar_inertia)

# 7. PATENT: Magnetic Core Memory Inductive Flux Matrix
# Calculates the electrical potential required to flip a core memory bit from 0 to 1
def equation_patent_core_flux(turns: int, current_amps: float, reluctance: float) -> float:
    return (turns * current_amps) / reluctance

# 8. CLOTHING: Logistic Reorder Optimization Bound (Wilson EOQ Formula)
# Calculates the ideal raw material order size to minimize base warehousing expenses
def equation_clothing_reorder_size(demand_rate: float, setup_cost: float, holding_cost: float) -> float:
    return math.sqrt((2.0 * demand_rate * setup_cost) / holding_cost)

# 9. EDUCATION: Operator Visual Clutter Reaction Degradation Curve
# Predicts tracking performance drops as targets increase on the radar canvas
def equation_education_operator_lag(number_of_targets: int) -> float:
    return 0.15 * math.log(max(1, number_of_targets)) + 0.05

# 10. ACTIVE FIRING PLANT: Target Intercept Angle Correction Formula
# Used by your core engine to align weapons based on target vector changes
def equation_firing_intercept_angle(v_target: float, v_bullet: float, approach_angle_rad: float) -> float:
    return math.asin((v_target * math.sin(approach_angle_rad)) / v_bullet)
