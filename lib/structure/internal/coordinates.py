###############################################################################
#                                                                             #
# Copyright (C) 2014-2015 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module for handling atomic coordinate information."""

# Python module imports.
from numpy import array, float64, int16, zeros

# relax module imports.
from lib.errors import RelaxFault
from lib.sequence_alignment.align_protein import align_pairwise


def assemble_coord_array(objects=None, object_names=None, molecules=None, models=None, atom_id=None, algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=1.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0, seq_info_flag=False):
    """Assemble the atomic coordinates 
 
    @keyword objects:                   The list of internal structural objects to assemble the coordinates from.
    @type objects:                      list of str
    @keyword object_names:              The list of names for each structural object to use in printouts.
    @type object_names:                 list of str
    @keyword models:                    The list of models for each structural object.  The number of elements must match the objects argument.  If set to None, then all models will be used.
    @type models:                       None or list of lists of int
    @keyword molecules:                 The list of molecules for each structural object.  The number of elements must match the objects argument.  If set to None, then all molecules will be used.
    @type molecules:                    None or list of lists of str
    @keyword atom_id:                   The molecule, residue, and atom identifier string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:                      None or str
    @keyword algorithm:                 The pairwise sequence alignment algorithm to use.  If set to None, then no alignment will be performed.
    @type algorithm:                    str or None
    @keyword matrix:                    The substitution matrix to use.
    @type matrix:                       str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    @keyword seq_info_flag:             A flag which if True will cause the atomic sequence information to be assembled and returned.  This includes the molecule names, residue names, residue numbers, atom names, and elements.
    @type seq_info_flag:                bool
    @return:                            The array of atomic coordinates (first dimension is the model and/or molecule, the second are the atoms, and the third are the coordinates); a list of unique IDs for each structural object, model, and molecule; the common list of molecule names (if the seq_info_flag is set); the common list of residue names (if the seq_info_flag is set); the common list of residue numbers (if the seq_info_flag is set); the common list of atom names (if the seq_info_flag is set); the common list of element names (if the seq_info_flag is set).
    @rtype:                             numpy rank-3 float64 array, list of str, list of str, list of str, list of int, list of str, list of str
    """

    # Assemble the atomic coordinates of all structures.
    print("Assembling all atomic coordinates:")
    ids = []
    atom_pos = []
    mol_names = []
    res_names = []
    res_nums = []
    atom_names = []
    elements = []
    one_letter_codes = []
    for struct_index in range(len(objects)):
        # Printout.
        print("    Data pipe: %s" % object_names[struct_index])

        # Validate the models.
        objects[struct_index].validate_models(verbosity=0)

        # The number of models.
        num_models = objects[struct_index].num_models()

        # The selection object.
        selection = objects[struct_index].selection(atom_id=atom_id)

        # Loop over the models.
        for model in objects[struct_index].model_loop():
            # No model match.
            if models != None and model.num not in models[struct_index]:
                continue

            # Printout.
            print("        Model: %s" % model.num)

            # Add all coordinates and elements.
            current_mol = ''
            current_res = None
            for mol_name, res_num, res_name, atom_name, elem, pos in objects[struct_index].atom_loop(selection=selection, model_num=model.num, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True, element_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[struct_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:
                    # Printout.
                    print("            Molecule: %s" % mol_name)

                    # Change the current molecule name and residue number.
                    current_mol = mol_name
                    current_res = None

                    # Store the one letter codes for sequence alignment.
                    one_letter_codes.append(objects[struct_index].one_letter_codes(mol_name=mol_name))

                    # Extend the lists.
                    atom_names.append([])
                    atom_pos.append([])
                    if seq_info_flag:
                        mol_names.append([])
                        res_names.append([])
                        res_nums.append([])
                        elements.append([])

                    # Create a new structure ID.
                    if len(object_names) > 1 and num_models > 1:
                        ids.append('%s, model %i, %s' % (object_names[struct_index], model.num, mol_name))
                    elif len(object_names) > 1:
                        ids.append('%s, %s' % (object_names[struct_index], mol_name))
                    elif num_models > 1:
                        ids.append('model %i, %s' % (model.num, mol_name))
                    else:
                        ids.append('%s' % mol_name)

                # A new residue.
                if res_num != current_res:
                    # Change the current residue
                    current_res = res_num

                    # Extend the lists.
                    atom_names[-1].append([])
                    atom_pos[-1].append({})
                    if seq_info_flag:
                        mol_names[-1].append({})
                        res_names[-1].append({})
                        res_nums[-1].append({})
                        elements[-1].append({})

                # Store the per-structure ID and coordinate.
                atom_names[-1][-1].append(atom_name)
                atom_pos[-1][-1][atom_name] = pos[0]

                # Store the per-structure sequence information.
                if seq_info_flag:
                    mol_names[-1][-1][atom_name] = mol_name
                    res_names[-1][-1][atom_name] = res_name
                    res_nums[-1][-1][atom_name] = res_num
                    elements[-1][-1][atom_name] = elem

    # The total number of molecules.
    num_mols = len(atom_names)

    # Sequence alignment.
    if algorithm == 'NW70':
        print("\nPairwise sequence alignment to the first molecule:\n")
        gap_matrices = []
        for mol_index in range(1, num_mols):
            print("Molecules 1-%i" % (mol_index+1))
            align1, align2, gaps = align_pairwise(one_letter_codes[0], one_letter_codes[mol_index], algorithm=algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)
            gap_matrices.append(gaps)

        # Determine the residues in common.
        skip = common_residues(gap_matrices=gap_matrices, one_letter_codes=one_letter_codes)

    # No alignment, so create an empty residue skipping data structure.
    else:
        # Create
        skip = []
        for mol_index in range(num_mols):
            skip.append([])
            for res_index in range(len(one_letter_codes[mol_index])):
                skip[mol_index].append(0)

    # Set up the structures for common coordinates.
    coord = []
    mol_name_common = []
    res_name_common = []
    res_num_common = []
    atom_name_common = []
    element_common = []
    for mol_index in range(num_mols):
        coord.append([])

    # Find the common atoms and create the coordinate data structure.
    res_indices = [-1]*num_mols
    max_res = -1
    for mol_index in range(num_mols):
        if len(one_letter_codes[mol_index]) > max_res:
            max_res = len(one_letter_codes[mol_index])
    while 1:
        # Move to the next non-skipped residues in each molecule.
        for mol_index in range(num_mols):
            terminate = False
            while 1:
                res_indices[mol_index] += 1
                if res_indices[mol_index] >= len(skip[mol_index]):
                    terminate = True
                    break
                if not skip[mol_index][res_indices[mol_index]]:
                    break

        # Termination.
        for mol_index in range(num_mols):
            if res_indices[0] >= len(atom_names[0]):
                terminate = True
            if res_indices[mol_index] >= len(atom_names[0]):
                terminate = True
        if terminate:
            break

        # Loop over the residue atoms in the first molecule.
        for atom_name in atom_names[0][res_indices[0]]:
            # Is the atom ID present in all other structures?
            present = True
            for mol_index in range(1, num_mols):
                if atom_name not in atom_names[mol_index][res_indices[mol_index]]:
                    present = False
                    break

            # Not present, so skip the atom.
            if not present:
                continue

            # Add the atomic position to the coordinate list and the element to the element list.
            for mol_index in range(num_mols):
                coord[mol_index].append(atom_pos[mol_index][res_indices[mol_index]][atom_name])

            # The common sequence information.
            if seq_info_flag:
                mol_name_common.append(mol_names[0][res_indices[0]][atom_name])
                res_name_common.append(res_names[0][res_indices[0]][atom_name])
                res_num_common.append(res_nums[0][res_indices[0]][atom_name])
                atom_name_common.append(atom_name)
                element_common.append(elements[0][res_indices[0]][atom_name])

    # Convert to a numpy array.
    coord = array(coord, float64)

    # Return the information.
    if seq_info_flag:
        return coord, ids, mol_name_common, res_name_common, res_num_common, atom_name_common, element_common
    else:
        return coord, ids


def common_residues(gap_matrices=None, one_letter_codes=None, seq=False):
    """Determine the common residues between all the pairwise alignments.

    @keyword gap_matrices:      The list of gap matrices from the pairwise alignments.
    @type gap_matrices:         list of numpy rank-2 arrays.
    @keyword one_letter_codes:  The list of strings of one letter residue codes for each molecule.
    @type one_letter_codes:     list of str
    @keyword seq:               A flag which if True will cause the gapped sequence strings to be returned.
    @type seq:                  bool
    @return:                    The residue skipping data structure and the optional gapped sequence strings.  For the skipping structure, the first dimension corresponds to the molecule and the second to the residue.  A one means the residue should be skipped, whereas zero means keep the residue.
    @rtype:                     list of list of int
    """

    # The number of molecules.
    num_mols = len(gap_matrices) + 1

    # Initialise the residue skipping structures.
    skip = []
    skip_counts = zeros(num_mols, int16)
    res_counts = zeros(num_mols, int16)
    for mol_index in range(num_mols):
        res_counts[mol_index] = len(one_letter_codes[mol_index])
        skip.append([])
        for j in range(res_counts[mol_index]):
            skip[mol_index].append(0)

    # Update the residue skipping structures for the first molecule.
    for mol_index in range(num_mols-1):
        # Loop over the residues of alignment i.
        seq_index = -1
        for j in range(len(gap_matrices[mol_index][0])):
            # Increment the sequence index.
            if not gap_matrices[mol_index][0, j]:
                seq_index += 1

            # A gap in the second sequence, so skip the residue.
            if gap_matrices[mol_index][1, j]:
                skip[0][seq_index] = 1

    # Initialise the gapped strings data structure for the first molecule.
    gapped_strings = ['']
    string_length = max(res_counts)
    offsets = zeros((num_mols-1), int16)
    prev_offsets = zeros((num_mols-1), int16)
    for seq_index in range(res_counts[0]):
        # Increment the offsets indices.
        for mol_index in range(1, num_mols):
            while gap_matrices[mol_index-1][0, seq_index+offsets[mol_index-1]]:
                offsets[mol_index-1] += 1

        # A gap.
        for i in range(max(offsets - prev_offsets)):
            gapped_strings[0] += "-"

        # Missing in one of the other molecule.
        missing = False
        for mol_index in range(1, num_mols):
            if gap_matrices[mol_index-1][1, seq_index+offsets[mol_index-1]]:
                missing = True
        if missing:
            gapped_strings[0] += "-"

        # Keep the residue.
        else:
            gapped_strings[0] += one_letter_codes[0][seq_index]

        # Store the old offsets.
        prev_offsets = offsets * 1

    # Final padding.
    for j in range(max(res_counts) - res_counts[0] - 1):
        gapped_strings[0] += "-"

    # Update the first molecule skip counts.
    skip_counts[0] = sum(skip[0])

    # Update the residue skipping structures for all other molecules.
    for mol_index in range(1, num_mols):
        # Loop over the residues of alignment mol_index.
        seq1_index = -1
        seq2_index = -1
        gapped_strings.append('')
        for j in range(len(gap_matrices[mol_index-1][0])):
            # Increment the sequence indices.
            if not gap_matrices[mol_index-1][0, j]:
                seq1_index += 1
            if not gap_matrices[mol_index-1][1, j]:
                seq2_index += 1

            # End condition for the first molecule.
            if seq1_index >= res_counts[0]:
                # Skip the rest of the second molecule.
                for k in range(seq2_index, res_counts[mol_index]):
                    skip[mol_index][k] = 1
                    skip_counts[mol_index] += 1
                    gapped_strings[mol_index] += "-"

                # Terminate the loop.
                break

            # A gap in the first sequence, so skip the residue.
            if gap_matrices[mol_index-1][0, j]:
                skip[mol_index][seq2_index] = 1
                skip_counts[mol_index] += 1
                gapped_strings[mol_index] += "-"

            # Already skipped in the first molecule.
            elif skip[0][seq1_index] and not gap_matrices[mol_index-1][1, j]:
                skip[mol_index][seq2_index] = 1
                skip_counts[mol_index] += 1
                gapped_strings[mol_index] += "-"

            # Skipped in the second molecule.
            elif gap_matrices[mol_index-1][1, j]:
                gapped_strings[mol_index] += "-"

            # Print out the one letter code.
            else:
                gapped_strings[mol_index] += one_letter_codes[mol_index][seq2_index]

    # Printout.
    print("Shared residues:")
    for mol_index in range(num_mols):
        print("Molecule %3i:  %s" % (mol_index, gapped_strings[mol_index]))

    # Sanity checks.
    total = res_counts[0] - skip_counts[0]
    for mol_index in range(1, num_mols):
        if total != res_counts[mol_index] - skip_counts[mol_index]:
            print("\nThe total shared residue counts between molcule 1 and %i of %i and %i respectively do not match." % ((mol_index+1), total, res_counts[mol_index] - skip_counts[mol_index]))
            raise RelaxFault

    # Return the skipping data structure.
    if seq:
        return skip, gapped_strings
    else:
        return skip


def loop_coord_structures(objects=None, molecules=None, models=None, atom_id=None):
    """Generator function for looping over all internal structural objects, models and molecules.
 
    @keyword objects:       The list of internal structural objects to loop over.
    @type objects:          list of str
    @keyword models:        The list of models for each structural object.  The number of elements must match the objects argument.  If set to None, then all models will be used.
    @type models:           None or list of lists of int
    @keyword molecules:     The list of molecules for each structural object.  The number of elements must match the objects argument.  If set to None, then all molecules will be used.
    @type molecules:        None or list of lists of str
    @keyword atom_id:       The molecule, residue, and atom identifier string of the coordinates of interest.  This matches the spin ID string format.
    @type atom_id:          None or str
    @return:                The structural object index, model number, and molecule name.
    @rtype:                 int, int or None, str
    """

    # Loop over all structural objects.
    for struct_index in range(len(objects)):
        # Validate the models.
        objects[struct_index].validate_models(verbosity=0)

        # The number of models.
        num_models = objects[struct_index].num_models()

        # The selection object.
        selection = objects[struct_index].selection(atom_id=atom_id)

        # Loop over the models.
        for model in objects[struct_index].model_loop():
            # No model match.
            if models != None and model.num not in models[struct_index]:
                continue

            # Coordinate loop.
            current_mol = ''
            for mol_name, res_num, res_name, atom_name, elem, pos in objects[struct_index].atom_loop(selection=selection, model_num=model.num, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_name_flag=True, pos_flag=True, element_flag=True):
                # No molecule match, so skip.
                if molecules != None and mol_name not in molecules[struct_index]:
                    continue

                # A new molecule.
                if mol_name != current_mol:
                    # Change the current molecule name.
                    current_mol = mol_name

                    # Yield the data.
                    yield struct_index, model.num, mol_name
