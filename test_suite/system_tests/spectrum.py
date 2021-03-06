###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
# Copyright (C) 2008 Sebastien Morin                                          #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
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
from os import sep
from os.path import basename, dirname
from tempfile import mkdtemp, NamedTemporaryFile

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Spectrum(SystemTestCase):
    """TestCase class for the functional tests for the support of different spectrum intensity calculation or errors, signal to noise and plotting."""


    def setUp(self):
        """Set up for all the functional tests."""

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()
        self.tmpdir = ds.tmpdir

    def setup_signal_noise_ratio(self):
        """Setup intensity data.

        This uses the data from paper at U{http://dx.doi.org/10.1073/pnas.0509100103}.  This is CPMG data with a fixed relaxation time period.  Experiment in 0.48 M GuHCl (guanidine hydrochloride).
        """

        # Set pipe name, bundle and type.
        pipe_name = 'base pipe'
        pipe_bundle = 'relax_disp'
        pipe_type = 'relax_disp'

        # Create the data pipe.
        self.interpreter.pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type=pipe_type)

        data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'KTeilum_FMPoulsen_MAkke_2006'+sep+'bug_neg_int_acbp_cpmg_disp_048MGuHCl_40C_041223'

        # Create the spins
        self.interpreter.spectrum.read_spins(file="peaks_list_max_standard.ser", dir=data_path)

        # Name the isotope for field strength scaling.
        self.interpreter.spin.isotope(isotope='15N')

        # Read the spectrum from NMRSeriesTab file. The "auto" will generate spectrum name of form: Z_A{i}
        self.interpreter.spectrum.read_intensities(file="peaks_list_max_standard.ser", dir=data_path, spectrum_id='auto', int_method='height')

        # Loop over the spectra settings.
        ncycfile=open(data_path + sep + 'ncyc.txt', 'r')

        # Make empty ncyclist
        ncyclist = []

        i = 0
        for line in ncycfile:
            ncyc = line.split()[0]
            time_T2 = float(line.split()[1])
            vcpmg = line.split()[2]
            set_sfrq = float(line.split()[3])
            rmsd_err = float(line.split()[4])

            # Test if spectrum is a reference
            if float(vcpmg) == 0.0:
                vcpmg = None
            else:
                vcpmg = round(float(vcpmg), 3)

            # Add ncyc to list
            ncyclist.append(int(ncyc))

            # Set the current spectrum id
            current_id = "Z_A%s"%(i)

            # Set the current experiment type.
            self.interpreter.relax_disp.exp_type(spectrum_id=current_id, exp_type='SQ CPMG')

            # Set the peak intensity errors, as defined as the baseplane RMSD.
            self.interpreter.spectrum.baseplane_rmsd(error=rmsd_err, spectrum_id=current_id)

            # Set the NMR field strength of the spectrum.
            self.interpreter.spectrometer.frequency(id=current_id, frq=set_sfrq, units='MHz')

            # Relaxation dispersion CPMG constant time delay T (in s).
            self.interpreter.relax_disp.relax_time(spectrum_id=current_id, time=time_T2)

            # Set the relaxation dispersion CPMG frequencies.
            self.interpreter.relax_disp.cpmg_setup(spectrum_id=current_id, cpmg_frq=vcpmg)

            i += 1

        # Perform the error analysis.
        self.interpreter.spectrum.error_analysis_per_field()

        # Store the reference intensities and RMSD.
        ds.data = [
        [1, 1711.104, 3040.110, 8.514, 121.681, +5.586445e+05, 'A3N-HN', 1.0000, 1.7492, 0.9997, 1.0075, 1.0081, 0.8991, 1.0205, 0.9893, 1.0145, 1.0078, 1.0133, 1.0020, 0.9995, 1.0020, 1.0249, 1.7571, 1.0016],
        [2, 2011.491, 4112.494, 8.025, 117.805, +6.213668e+05, 'E4N-HN', 1.0000, 1.6032, -0.8322, 0.9920, 0.9951, 0.8300, 0.9458, 0.9689, 0.9246, 0.9936, 0.9914, 0.9842, 1.0011, 0.8529, 0.9727, 1.5845, 0.9822],
        [3, 1974.019, 2629.250, 8.086, 123.166, +4.592940e+05, 'F5N-HN', 1.0000, 1.8235, 0.8614, 1.0135, 1.0134, 0.8825, 0.9332, 0.9772, 0.9273, 0.9803, 0.9986, 1.0000, 1.0012, 0.8923, 0.9421, 1.8102, 1.0062],
        [4, 1608.518, 3683.374, 8.681, 119.356, +5.293190e+05, 'D6N-HN', 1.0000, 1.6865, 0.8531, 1.0052, 1.0065, 0.8530, 0.9280, 0.9594, 0.8989, 0.9914, 1.0115, 0.9743, 1.0063, 0.8177, 0.9264, 1.6855, 0.9981],
        ]

        ds.rmsd = [2.47e+03, 2.34e+03, 2.41e+03, 2.42e+03, 2.45e+03, 2.42e+03, 2.42e+03, 2.44e+03, 2.39e+03, 2.4e+03, 2.42e+03, 2.46e+03, 2.41e+03, 2.45e+03, 2.45e+03, 2.39e+03, 2.45e+03]


    def test_signal_noise_ratio(self):
        """Test calculation of signal to noise ratio.
        """


        # Setup data.
        self.setup_signal_noise_ratio()

        # Test the signal to noise ratio calculation.
        self.interpreter.spectrum.sn_ratio()

        # Assign counter
        i = 0
        for cur_spin, cur_spin_id in spin_loop(return_id=True, skip_desel=True):
            # Test assignment.
            self.assertEqual(cur_spin_id, ":%s@N"%ds.data[i][6][1])

            # Loop over intensity columns.
            for j in range(17):
                # Test intensity.
                data_int = ds.data[i][j+7] * ds.data[i][5]
                pint = cur_spin.peak_intensity['Z_A%i'%j]
                self.assertEqual(pint, data_int)

                # Test baseplane_rmsd.
                data_rmsd = ds.rmsd[j]
                self.assertEqual(cur_spin.baseplane_rmsd['Z_A%i'%j], data_rmsd)

                # Test the calculated peak_intensity_err.
                # Since we have measured intensity height, and have not specified replications, this is the same as rmsd.
                pint_err = cur_spin.peak_intensity_err['Z_A%i'%j]
                self.assertEqual(pint_err, ds.rmsd[j])

                # Test the signal to noise ratio.
                sn_ratio = data_int / data_rmsd
                self.assertEqual(cur_spin.sn_ratio['Z_A%i'%j], sn_ratio)
                self.assertEqual(cur_spin.sn_ratio['Z_A%i'%j], pint/pint_err)

            # Add to counter
            i += 1


    def test_grace_int(self):
        """Test grace plotting function for plotting the intensities per residue.
        """


        # Setup data.
        self.setup_signal_noise_ratio()

        # Deselect spin with negative intensity.
        self.interpreter.deselect.spin(spin_id=':4@N', boolean='AND', change_all=False)

        # Test show grace. If showing, the temporary directory created, should not be deleted.
        show_grace = False
        if show_grace:
            outfile= NamedTemporaryFile(delete=False).name
            filedir = dirname(outfile)
        else:
            filedir = self.tmpdir
        outfile = 'int.agr'

        self.interpreter.grace.write(x_data_type='res_num', y_data_type='peak_intensity', file=outfile, dir=filedir, force=True)

        # View the plotting.
        if show_grace:
            self.interpreter.grace.view(file=outfile, dir=filedir, grace_exe='xmgrace')


    def test_grace_sn_ratio(self):
        """Test grace plotting function for plotting the signal to noise ratio per residue.
        """

        # Setup data.
        self.setup_signal_noise_ratio()

        # Calculate the signal to noise ratio calculation.
        self.interpreter.spectrum.sn_ratio()

        # Deselect spin with negative intensity.
        self.interpreter.deselect.spin(spin_id=':4@N', boolean='AND', change_all=False)

        # Test show grace. If showing, the temporary directory created, should not be deleted.
        show_grace = False
        if show_grace:
            outfile= NamedTemporaryFile(delete=False).name
            filedir = dirname(outfile)
        else:
            filedir = self.tmpdir
        outfile = 'int_sn.agr'

        self.interpreter.grace.write(x_data_type='res_num', y_data_type='sn_ratio', file=outfile, dir=filedir, force=True)

        # View the plotting.
        if show_grace:
            self.interpreter.grace.view(file=outfile, dir=filedir, grace_exe='xmgrace')


    def test_deselect_sn_ratio_all(self):
        """Test the deselect.sn_ratio for signal to noise ratios, where all ID should evaluate to True.
        """

        # Setup data.
        self.setup_signal_noise_ratio()

        # Calculate the signal to noise ratio calculation.
        self.interpreter.spectrum.sn_ratio()

        # deselect spins.
        self.interpreter.deselect.sn_ratio(ratio=400.0, operation='<', all_sn=True)

        # Test
        spin_ids_sel = []
        spin_ids_desel = []

        # Collect spin ids which are selected.
        for cur_spin, cur_spin_id in spin_loop(return_id=True, skip_desel=False):
            if cur_spin.select:
                spin_ids_sel.append(cur_spin_id)
            else:
                spin_ids_desel.append(cur_spin_id)

        # Make the test:
        self.assertEqual(spin_ids_sel, [':3@N', ':4@N'])
        self.assertEqual(spin_ids_desel, [':5@N', ':6@N'])


    def test_deselect_sn_ratio_any(self):
        """Test the deselect.sn_ratio for signal to noise ratios, where any ID should evaluate to True.
        """

        # Setup data.
        self.setup_signal_noise_ratio()

        # Calculate the signal to noise ratio calculation.
        self.interpreter.spectrum.sn_ratio()

        # Deselect spins.
        self.interpreter.deselect.sn_ratio(ratio=200.0, operation='<', all_sn=False)

        # Test
        spin_ids_sel = []
        spin_ids_desel = []

        # Collect spin ids which are selected.
        for cur_spin, cur_spin_id in spin_loop(return_id=True, skip_desel=False):
            if cur_spin.select:
                spin_ids_sel.append(cur_spin_id)
            else:
                spin_ids_desel.append(cur_spin_id)

        # Make the test:
        self.assertEqual(spin_ids_sel, [':3@N'])
        self.assertEqual(spin_ids_desel, [':4@N', ':5@N', ':6@N'])


    def test_select_sn_ratio_all(self):
        """Test the select.sn_ratio for signal to noise ratios, where all ID should evaluate to True.
        """

        # Setup data.
        self.setup_signal_noise_ratio()

        # Calculate the signal to noise ratio calculation.
        self.interpreter.spectrum.sn_ratio()

        # First deselect all spins.
        self.interpreter.deselect.all()

        # Select spins.
        self.interpreter.select.sn_ratio(ratio=400.0, operation='<', all_sn=True)

        # Test
        spin_ids_sel = []
        spin_ids_desel = []

        # Collect spin ids which are selected.
        for cur_spin, cur_spin_id in spin_loop(return_id=True, skip_desel=False):
            if cur_spin.select:
                spin_ids_sel.append(cur_spin_id)
            else:
                spin_ids_desel.append(cur_spin_id)

        # Make the test:
        self.assertEqual(spin_ids_sel, [':5@N', ':6@N'])
        self.assertEqual(spin_ids_desel, [':3@N', ':4@N'])


    def test_select_sn_ratio_any(self):
        """Test the select.sn_ratio for signal to noise ratios, where any ID should evaluate to True.
        """

        # Setup data.
        self.setup_signal_noise_ratio()

        # Calculate the signal to noise ratio calculation.
        self.interpreter.spectrum.sn_ratio()

        # First deselect all spins.
        self.interpreter.deselect.all()

        # Select spins.
        self.interpreter.select.sn_ratio(ratio=200.0, operation='<', all_sn=False)

        # Test
        spin_ids_sel = []
        spin_ids_desel = []

        # Collect spin ids which are selected.
        for cur_spin, cur_spin_id in spin_loop(return_id=True, skip_desel=False):
            if cur_spin.select:
                spin_ids_sel.append(cur_spin_id)
            else:
                spin_ids_desel.append(cur_spin_id)

        # Make the test:
        self.assertEqual(spin_ids_sel, [':4@N', ':5@N', ':6@N'])
        self.assertEqual(spin_ids_desel, [':3@N'])
