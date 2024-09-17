import h5py
import numpy as np
from numpy import arange

#Here is the example code to convert the data from Yell 1.0 format to the newly proposed nexus file
def yell2ds(inp_filename, out_filename):
    inp = h5py.File(inp_filename,'r')

    inp_data = inp['data'] #Diffuse scattering data array

    lower_limits = inp['lower_limits'][()] #lowest index for h, k and l
    step_sizes = inp['step_sizes'][()] #step size along h, k and l directions
    unit_cell = inp['unit_cell'][()] #Unit cell dimensiona a, b, c, alpha, beta, gamma

    #Nexus below asks to explicitely provide indices as 1d vector arrays
    indices = [lower_limits[i]+step_sizes[i]*arange(0, inp_data.shape[i]) for i in range(3)]
    h_indices, k_indices, l_indices = indices

    write_diffuse_scattering(out_filename,
                            inp_data[()],
                            h_indices,
                            k_indices,
                            l_indices,
                            unit_cell)

def ds2yell(inp_filename, out_filename):
    # Open the diffuse scattering nexus file
    inp = h5py.File(inp_filename, 'r')

    # Access the dataset group containing the scattering data
    scattering = inp['scattering/data']

    # Read the data from the nexus file
    inp_data = scattering['data'][()]  # Diffuse scattering data
    h_indices = scattering['h'][()]  # h indices
    k_indices = scattering['k'][()]  # k indices
    l_indices = scattering['l'][()]  # l indices
    unit_cell = scattering['unit_cell'][()]  # Unit cell parameters

    # Calculate the lower_limits and step_sizes
    lower_limits = np.array([h_indices[0], k_indices[0], l_indices[0]])
    step_sizes = np.array([
        h_indices[1] - h_indices[0],  # Step size along h
        k_indices[1] - k_indices[0],  # Step size along k
        l_indices[1] - l_indices[0]  # Step size along l
    ])

    is_direct = scattering.attrs['space']=='reciprocal'

    # Write back to the Yell 1.0 format
    with h5py.File(out_filename, 'w') as out:
        # Write the data and metadata in Yell format
        out['data'] = inp_data
        out['lower_limits'] = lower_limits
        out['step_sizes'] = step_sizes
        out['unit_cell'] = unit_cell
        out['format'] = b'Yell 1.0'  # Format string
        out['is_direct'] = is_direct


def write_diffuse_scattering(outfile, inp_data, h_indices, k_indices, l_indices, unit_cell):
    with h5py.File(outfile, 'w') as out:
        # our format string containing version
        out.attrs['format'] = "Disorder scattering 1.0"

        out.attrs['default'] = "scattering"
        scattering = out.create_group('scattering')
        scattering.attrs["NX_class"] = 'NXentry'
        scattering.attrs['default'] = 'data'

        # If more than one dataset is present, this name can be more reasonable,
        # for instance background, clean, averaged etc.
        data = scattering.create_group('data')
        data.attrs['NX_class'] = 'NXdata'
        data.attrs['signal'] = 'data'
        data.attrs['axes'] = ["h", "k", "l"]  # or "u", "v", "w" for PDF, or "x", "y", "z" for scattering density map
        data.attrs['h_indices'] = 0
        data.attrs['k_indices'] = 1
        data.attrs['l_indices'] = 2

        data.attrs['radiation'] = 'x-ray'  # or neutrons or electrons

        # this flag will be required for chosing the correct metric tensor for the affine transform
        data.attrs['space'] = 'reciprocal'  # or 'direct' for PDF reconstruction

        data['h'] = h_indices
        data['k'] = k_indices
        data['l'] = l_indices

        # the data array of scattering is written here
        data['data'] = inp_data
        data['unit_cell'] = unit_cell

        #   Possible : attribute on whether the data was calculated or experimental


def read_diffuse_scattering(infile):
    print(" ")
    with h5py.File(infile, 'r') as inp:
        # List (and check) required keys and attributes
        print("Input file Keys: ",list(inp.keys()))
        print("Input file Attr: ",list(inp.attrs))
        for name in inp.attrs:
            print("           Attr: ",name, " = ", inp.attrs[name] )
        print(" ")

        dset = inp['scattering']
        print("Scattering Keys: ",list(dset.keys()))
        print("Scattering Attr: ",list(dset.attrs))
        for name in dset.attrs:
            print("           Attr: ",name, " = ", dset.attrs[name] )
        print(" ")

        print(" ")
        data = dset['data']
        print("Data       Keys: ",list(data.keys()))
        print("Data       Attr: ",list(data.attrs))
        for name in data.attrs:
            print("           Attr: ",name, " = ", data.attrs[name] )
        print(" ")

        outp_data = np.array(data['data'])
        h_indices = np.array(data['h'])
        k_indices = np.array(data['k'])
        l_indices = np.array(data['l'])
        unit_cell = np.array(data['unit_cell'])

        print("qvalues   : ", outp_data.ndim)
        print("qvalues   : ", outp_data.shape, outp_data.shape[0], \
                              outp_data.shape[1], outp_data.shape[2])

        # Reporting H indices
        print("H indices : ", h_indices.ndim)
        print("H indices : ", h_indices.shape, h_indices.shape[0])
        print("H indices : ", h_indices[0], " to ", h_indices[-1])

        # Reporting K indices
        print("K indices : ", k_indices.ndim)
        print("K indices : ", k_indices.shape, k_indices.shape[0])
        print("K indices : ", k_indices[0], " to ", k_indices[-1])

        # Reporting L indices
        print("L indices : ", l_indices.ndim)
        print("L indices : ", l_indices.shape, l_indices.shape[0])
        print("L indices : ", l_indices[0], " to ", l_indices[-1])

        # Reporting Unit Cell
        print("Unit Cell : ", unit_cell)

    return outp_data, h_indices, k_indices, l_indices, unit_cell

