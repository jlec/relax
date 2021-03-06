###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from numpy import array, float64, int16, ones, pi, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.ns_cpmg_2site_expanded import r2eff_ns_cpmg_2site_expanded


class Test_ns_cpmg_2site_expanded(TestCase):
    """Unit tests for the lib.dispersion.ns_cpmg_2site_expanded relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.r20 = 2.0
        self.pA = 0.95
        self.dw = 0.5
        self.kex = 100.0

        # Required data structures.
        self.num_points = 3
        self.tcp = array([0.1, 0.2, 0.3], float64)
        self.num_cpmg = array([1, 2, 3], int16)
        self.R2eff = zeros(self.num_points, float64)

        # The spin Larmor frequencies.
        self.sfrq = 200. * 1E6


    def calc_r2eff(self):
        """Calculate and check the R2eff values."""

        # Parameter conversions.
        k_AB, k_BA, dw_frq = self.param_conversion(pA=self.pA, kex=self.kex, dw=self.dw, sfrq=self.sfrq)

        a = ones([self.num_points])

        # Calculate the R2eff values.
        r2eff_ns_cpmg_2site_expanded(r20=self.r20*a, pA=self.pA, dw=dw_frq*a, dw_orig=dw_frq*a, kex=self.kex, relax_time=0.3, inv_relax_time=1/0.3, tcp=self.tcp, back_calc=self.R2eff, num_cpmg=self.num_cpmg)

        # Check all R2eff values.
        if self.kex >= 1.e5:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R2eff[i], self.r20, 5)
        else:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R2eff[i], self.r20)


    def param_conversion(self, pA=None, kex=None, dw=None, sfrq=None):
        """Convert the parameters.

        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @keyword dw:    The chemical exchange difference between states A and B in ppm.
        @type dw:       float
        @keyword sfrq:  The spin Larmor frequencies in Hz.
        @type sfrq:     float
        @return:        The parameters {k_AB, k_BA, dw_frq}.
        @rtype:         tuple of float
        """

        # Calculate pB.
        pB = 1.0 - pA

        # Exchange rates.
        k_BA = pA * kex
        k_AB = pB * kex

        # Calculate spin Larmor frequencies in 2pi.
        frqs = sfrq * 2 * pi

        # Convert dw from ppm to rad/s.
        dw_frq = dw * frqs / 1.e6

        # Return all values.
        return k_AB, k_BA, dw_frq


    def test_ns_cpmg_2site_expanded_no_rex1(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when dw = 0.0."""

        # Parameter reset.
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_expanded_no_rex2(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_expanded_no_rex3(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_expanded_no_rex4(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when dw = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_expanded_no_rex5(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when dw = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_expanded_no_rex6(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_expanded_no_rex7(self):
        """Test the r2eff_ns_cpmg_2site_expanded() function for no exchange when dw = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()

