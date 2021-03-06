###############################################################################
#                                                                             #
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
from os import getcwd, sep
import re

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.dispersion.variables import MODEL_R2EFF, MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1

#########################################
#### Setup
# The pipe names.
if not (hasattr(ds, 'pipe_name') and hasattr(ds, 'pipe_bundle') and hasattr(ds, 'pipe_type')):
    # Set pipe name, bundle and type.
    ds.pipe_name = 'base pipe'
    ds.pipe_bundle = 'relax_disp'
    ds.pipe_type = 'relax_disp'

# The data path
if not hasattr(ds, 'data_path'):
    ds.data_path = getcwd()

# The models to analyse.
if not hasattr(ds, 'models'):
    #ds.models = [MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1, MODEL_TP02_FIT_R1, MODEL_TAP03_FIT_R1, MODEL_MP05_FIT_R1]
    ds.models = [MODEL_NOREX_R1RHO_FIT_R1, MODEL_DPL94_FIT_R1]

# The number of increments per parameter, to split up the search interval in grid search.
if not hasattr(ds, 'grid_inc'):
    ds.grid_inc = 10

# The number of Monte-Carlo simulations for estimating the error of the parameters of the fitted models.
if not hasattr(ds, 'mc_sim_num'):
    ds.mc_sim_num = 10

# The model selection technique. Either: 'AIC', 'AICc', 'BIC'
if not hasattr(ds, 'modsel'):
    ds.modsel = 'AIC'

# The previous result directory with R2eff values.
if not hasattr(ds, 'pre_run_dir'):
    ds.pre_run_dir = getcwd() + sep + 'results_R2eff' + sep + 'R2eff'

# The result directory.
if not hasattr(ds, 'results_dir'):
    ds.results_dir = getcwd() + sep + 'results_models'

## The optimisation function tolerance.
## This is set to the standard value, and should not be changed.
#if not hasattr(ds, 'opt_func_tol'):
#    ds.opt_func_tol = 1e-25
#Relax_disp.opt_func_tol = ds.opt_func_tol

#if not hasattr(ds, 'opt_max_iterations'):
#    ds.opt_max_iterations = int(1e7)
#Relax_disp.opt_max_iterations = ds.opt_max_iteration

#########################################
# Create the data pipe.
pipe.create(pipe_name=ds.pipe_name, bundle=ds.pipe_bundle, pipe_type=ds.pipe_type)

# Load the previous results into the base pipe.
results.read(file='results', dir=ds.pre_run_dir)

# Run the analysis.
Relax_disp(pipe_name=ds.pipe_name, pipe_bundle=ds.pipe_bundle, results_dir=ds.results_dir, models=ds.models, grid_inc=ds.grid_inc, mc_sim_num=ds.mc_sim_num, modsel=ds.modsel)
