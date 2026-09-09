"""
engineering.py

Core engineering classes for the Fluid Flow & Heat Transfer Engineering Suite.

This module contains no Streamlit code -- it is pure calculation logic so it
can be imported, unit tested, and reused independently of the UI.

Classes:
    Fluid          - holds fluid properties (density, viscosity) and exposes
                      a small library of common fluids.
    Pipe           - represents a pipe's geometry and computes flow
                      hydraulics (velocity, Reynolds number, friction factor,
                      pressure drop) for a given Fluid and flow rate.
    HeatExchanger  - performs steady-state conduction and Newton's Law of
                      Cooling (transient) calculations.
"""

from __future__ import annotations
from dataclasses import dataclass
import math


# --------------------------------------------------------------------------- #
# Fluid
# --------------------------------------------------------------------------- #

@dataclass
class Fluid:
    """
    Represents a fluid and its physical properties.

    Attributes:
        name (str): Display name of the fluid.
        density (float): Fluid density in kg/m^3.
        viscosity (float): Dynamic viscosity in Pa.s (kg/m.s).
    """
    name: str
    density: float      # kg/m^3
    viscosity: float     # Pa.s

    # A small built-in library of common fluids at roughly room temperature.
    # Values are approximate and intended for teaching/demo purposes.
    LIBRARY = {
        "Water (20 C)": {"density": 998.0, "viscosity": 1.002e-3},
        "Air (20 C, 1 atm)": {"density": 1.204, "viscosity": 1.825e-5},
        "Crude Oil (medium, 20 C)": {"density": 870.0, "viscosity": 8.0e-3},
    }

    @classmethod
    def from_library(cls, name: str) -> "Fluid":
        """
        Build a Fluid from the built-in property library.

        Args:
            name (str): Key into Fluid.LIBRARY, e.g. "Water (20 C)".

        Returns:
            Fluid: A Fluid instance with the looked-up properties.

        Raises:
            KeyError: If the name is not in the library.
        """
        if name not in cls.LIBRARY:
            raise KeyError(f"Unknown fluid '{name}'. Choose from {list(cls.LIBRARY)}")
        props = cls.LIBRARY[name]
        return cls(name=name, density=props["density"], viscosity=props["viscosity"])

    def validate(self) -> None:
        """Raise ValueError if the fluid properties are physically invalid."""
        if self.density <= 0:
            raise ValueError("Density must be positive.")
        if self.viscosity <= 0:
            raise ValueError("Viscosity must be positive.")


# --------------------------------------------------------------------------- #
# Pipe
# --------------------------------------------------------------------------- #

@dataclass
class Pipe:
    """
    Represents a circular pipe and computes single-phase flow hydraulics.

    Attributes:
        diameter (float): Internal pipe diameter in metres.
        length (float): Pipe length in metres.
        roughness (float): Absolute pipe roughness in metres (e.g. 4.5e-5 for
            commercial steel).
    """
    diameter: float   # m
    length: float     # m
    roughness: float  # m

    def validate(self) -> None:
        """Raise ValueError if the pipe geometry is physically invalid."""
        if self.diameter <= 0:
            raise ValueError("Pipe diameter must be positive.")
        if self.length <= 0:
            raise ValueError("Pipe length must be positive.")
        if self.roughness < 0:
            raise ValueError("Roughness cannot be negative.")

    def area(self) -> float:
        """Cross-sectional flow area in m^2."""
        return math.pi * (self.diameter ** 2) / 4.0

    def velocity(self, flow_rate: float) -> float:
        """
        Mean flow velocity for a given volumetric flow rate.

        Args:
            flow_rate (float): Volumetric flow rate in m^3/s.

        Returns:
            float: Mean velocity in m/s.
        """
        if flow_rate < 0:
            raise ValueError("Flow rate cannot be negative.")
        return flow_rate / self.area()

    def reynolds_number(self, fluid: Fluid, flow_rate: float) -> float:
        """
        Reynolds number Re = rho * v * D / mu.

        Args:
            fluid (Fluid): The flowing fluid.
            flow_rate (float): Volumetric flow rate in m^3/s.

        Returns:
            float: Dimensionless Reynolds number.
        """
        v = self.velocity(flow_rate)
        return fluid.density * v * self.diameter / fluid.viscosity

    def friction_factor(self, fluid: Fluid, flow_rate: float) -> float:
        """
        Darcy friction factor.

        Uses the laminar solution f = 64/Re for Re < 2300, and the
        Swamee-Jain explicit approximation to the Colebrook equation for
        turbulent flow (Re >= 2300). Swamee-Jain is accurate to within
        about 1-2% of Colebrook across the typical engineering range.

        Args:
            fluid (Fluid): The flowing fluid.
            flow_rate (float): Volumetric flow rate in m^3/s.

        Returns:
            float: Dimensionless Darcy friction factor.
        """
        re = self.reynolds_number(fluid, flow_rate)
        if re <= 0:
            return 0.0
        if re < 2300:
            return 64.0 / re
        # Swamee-Jain equation (turbulent, explicit form of Colebrook)
        rel_roughness = self.roughness / self.diameter
        denom = math.log10((rel_roughness / 3.7) + (5.74 / (re ** 0.9)))
        f = 0.25 / (denom ** 2)
        return f

    def pressure_drop(self, fluid: Fluid, flow_rate: float) -> float:
        """
        Pressure drop along the pipe via the Darcy-Weisbach equation:
            dP = f * (L/D) * (rho * v^2 / 2)

        Args:
            fluid (Fluid): The flowing fluid.
            flow_rate (float): Volumetric flow rate in m^3/s.

        Returns:
            float: Pressure drop in Pa.
        """
        fluid.validate()
        self.validate()
        v = self.velocity(flow_rate)
        f = self.friction_factor(fluid, flow_rate)
        return f * (self.length / self.diameter) * (fluid.density * v ** 2 / 2.0)

    def full_report(self, fluid: Fluid, flow_rate: float) -> dict:
        """
        Convenience method returning all key hydraulic results at once.

        Args:
            fluid (Fluid): The flowing fluid.
            flow_rate (float): Volumetric flow rate in m^3/s.

        Returns:
            dict: velocity (m/s), reynolds_number, friction_factor,
                pressure_drop_pa, pressure_drop_kpa.
        """
        v = self.velocity(flow_rate)
        re = self.reynolds_number(fluid, flow_rate)
        f = self.friction_factor(fluid, flow_rate)
        dp = self.pressure_drop(fluid, flow_rate)
        return {
            "velocity_m_s": v,
            "reynolds_number": re,
            "friction_factor": f,
            "pressure_drop_pa": dp,
            "pressure_drop_kpa": dp / 1000.0,
            "flow_regime": "Laminar" if re < 2300 else ("Transitional" if re < 4000 else "Turbulent"),
        }


# --------------------------------------------------------------------------- #
# HeatExchanger
# --------------------------------------------------------------------------- #

@dataclass
class HeatExchanger:
    """
    Performs steady-state conduction and transient (Newton's Law of Cooling)
    heat transfer calculations.
    """

    @staticmethod
    def conduction_flat_wall(k: float, area: float, thickness: float,
                              t_hot: float, t_cold: float) -> dict:
        """
        Steady-state 1D conduction through a single-layer flat wall
        (Fourier's law): q = k * A * (T_hot - T_cold) / L

        Args:
            k (float): Thermal conductivity of the wall material, W/(m.K).
            area (float): Cross-sectional area normal to heat flow, m^2.
            thickness (float): Wall thickness, m.
            t_hot (float): Hot-side surface temperature, K or C (consistent
                units, since only the difference matters).
            t_cold (float): Cold-side surface temperature, same units as
                t_hot.

        Returns:
            dict: heat_rate_w, heat_flux_w_m2, thermal_resistance_k_w.
        """
        if k <= 0:
            raise ValueError("Thermal conductivity must be positive.")
        if area <= 0:
            raise ValueError("Area must be positive.")
        if thickness <= 0:
            raise ValueError("Thickness must be positive.")

        delta_t = t_hot - t_cold
        resistance = thickness / (k * area)  # K/W
        q = delta_t / resistance             # W
        flux = q / area                      # W/m^2

        return {
            "heat_rate_w": q,
            "heat_flux_w_m2": flux,
            "thermal_resistance_k_w": resistance,
            "delta_t": delta_t,
        }

    @staticmethod
    def cooling_time(mass: float, specific_heat: float, h: float, area: float,
                      t0: float, t_target: float, t_inf: float) -> float:
        """
        Time for a lumped body to cool from T0 to T_target in an ambient
        T_inf, via Newton's Law of Cooling (lumped capacitance model):

            T(t) - T_inf = (T0 - T_inf) * exp(-h * A * t / (m * cp))

        Solved for t:
            t = -(m * cp) / (h * A) * ln[(T_target - T_inf) / (T0 - T_inf)]

        Args:
            mass (float): Mass of the body, kg.
            specific_heat (float): Specific heat capacity, J/(kg.K).
            h (float): Convective heat transfer coefficient, W/(m^2.K).
            area (float): Surface area exposed to the ambient, m^2.
            t0 (float): Initial temperature.
            t_target (float): Target temperature to cool to.
            t_inf (float): Ambient (fluid) temperature.

        Returns:
            float: Time in seconds to reach t_target.

        Raises:
            ValueError: For non-physical inputs, e.g. target temperature not
                between T0 and T_inf (cooling is impossible/undefined), or
                target temperature equal to ambient (infinite time).
        """
        if mass <= 0 or specific_heat <= 0 or h <= 0 or area <= 0:
            raise ValueError("mass, specific_heat, h, and area must all be positive.")
        if t0 == t_inf:
            raise ValueError("Initial temperature equals ambient temperature; there is nothing to cool.")

        # Cooling requires T0 to be further from T_inf than T_target, and on
        # the same side of T_inf.
        numerator = t_target - t_inf
        denominator = t0 - t_inf
        ratio = numerator / denominator

        if ratio <= 0:
            raise ValueError(
                "Target temperature must lie strictly between the initial "
                "temperature and the ambient temperature."
            )
        if ratio >= 1:
            raise ValueError(
                "Target temperature must be closer to ambient than the "
                "initial temperature (the body must actually be cooling)."
            )

        tau = (mass * specific_heat) / (h * area)  # time constant, s
        t = -tau * math.log(ratio)
        return t

    @staticmethod
    def cooling_curve(mass: float, specific_heat: float, h: float, area: float,
                       t0: float, t_inf: float, t_max: float, n_points: int = 100) -> dict:
        """
        Generate a temperature-vs-time cooling curve for plotting.

        Args:
            mass, specific_heat, h, area, t0, t_inf: see cooling_time().
            t_max (float): Total duration to simulate, seconds.
            n_points (int): Number of points to generate.

        Returns:
            dict: "time_s" (list) and "temperature" (list), same length.
        """
        if mass <= 0 or specific_heat <= 0 or h <= 0 or area <= 0:
            raise ValueError("mass, specific_heat, h, and area must all be positive.")
        if t_max <= 0:
            raise ValueError("t_max must be positive.")

        tau = (mass * specific_heat) / (h * area)
        times = [t_max * i / (n_points - 1) for i in range(n_points)]
        temps = [t_inf + (t0 - t_inf) * math.exp(-t / tau) for t in times]
        return {"time_s": times, "temperature": temps}
