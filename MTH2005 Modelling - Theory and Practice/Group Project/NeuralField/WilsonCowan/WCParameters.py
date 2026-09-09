from dataclasses import dataclass


@dataclass
class WCParamaters:
    # Time constants
    tau_E: float = 1.0
    tau_I: float = 2.0

    # Sigmoid slope/threshold
    beta: float = 5.0
    theta: float = 0.0

    # Coupling strengths
    strength_EE: float = 15.0
    strength_EI: float = 25.0
    strength_IE: float = 5.0
    strength_II: float = 10.0

    # Spatial locality
    sigma_EE: float = 1.3
    sigma_EI: float = 3.2
    sigma_IE: float = 1.3
    sigma_II: float = 3.2

    # External inputs
    P0: float = 0.0
    Q0: float = 0.0

    # Integration settings
    dt: float = 0.1
    total_time: float = 50.0
    periodic: bool = True