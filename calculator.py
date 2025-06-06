def calculate_fluid_requirement(weight_kg: float) -> str:
    if weight_kg <= 10:
        fluid = weight_kg * 100
    elif weight_kg <= 20:
        fluid = 1000 + (weight_kg - 10) * 50
    else:
        fluid = 1500 + (weight_kg - 20) * 20
    return f"Estimated daily fluid requirement: {fluid:.0f} mL/day"


def calculate_min_systolic_bp(age_years: int) -> str:
    if age_years <= 10:
        bp = 70 + (age_years * 2)
    else:
        bp = 90
    return f"Estimated minimum systolic BP: {bp} mmHg"

