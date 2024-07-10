"""
A module for Milstein discretization algorithm.
"""

from typing import Callable
from dataclasses import dataclass, field
import numpy as np
from sde import SDE
from solver import Solver


@dataclass
class Milstein(Solver):
    """
    Numerical solver for a stochastic differential equation(SDE) using
    the Euler-Maruyama method.

    Consider an SDE of the form :

    dX_t = mu(t,X_t) dt + sigma(t,X_t) dB_t

    with initial condition X_0 = x_0

    The solution to the SDE can be computed using the increments

    X_{n+1} - X_n = mu(n,X_n)(t_{n+1}-t_n) + sigma(n,X_n)(B(n+1)-B(n))
    + 0.5 * sigma(n,X_n) * sigma'(n,X_n) * ((B(n+1) - B(n))**2 - (t_{n+1} - t_n))

    """

    def iterate(self, sde: SDE):
        """
        Generate the next iterate X(n+1)
        """

        mu_n = np.array([sde.drift(self.times[self.iter], x) for x in self.x_curr])
        sigma_n = np.array([sde.vol(self.times[self.iter], x) for x in self.x_curr])
        dvol_dx_n = np.array(
            [sde.dvol_dx(self.times[self.iter], x) for x in self.x_curr]
        )

        d_brownian = self.brownian[:, self.iter + 1] - self.brownian[:, self.iter]

        self.x_curr += (
            mu_n * self.step_size
            + sigma_n * d_brownian
            + 0.5 * sigma_n * dvol_dx_n * (d_brownian**2 - self.step_size)
        )

        return self.x_curr.copy()
