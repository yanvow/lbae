###### IMPORT MODULES ######

# Official modules
import pickle
import warnings

###### DEFINE MaldiData CLASS ######


class MaldiData:
    __slots__ = ["dic_slices", "hdf5_getter"]

    def __init__(self, hdf5_getter, path_dictionnary_data="lbae/data/whole_dataset/slices.pickle"):

        # Load the dictionnary containing small-size data for all slices
        with open(path_dictionnary_data, "rb") as handle:
            self.dic_slices = pickle.load(handle)

        # Set the accesser to the HDF5 dataset
        self.hdf5_getter = hdf5_getter

    def get_image_shape(self, slice_index):
        return self.dic_slices["s" + str(slice_index)]["image_shape"]

    def get_divider_lookup(self, slice_index):
        return self.dic_slices["s" + str(slice_index)]["divider_lookup"]

    def get_array_avg_intensity_downsampled(self, slice_index):
        # Previously called array_averaged_mz_intensity_low_res
        return self.dic_slices["s" + str(slice_index)]["array_avg_intensity_downsampled"]

    def get_array_lookup_pixels(self, slice_index):
        # Previously called array_pixel_indexes_high_res
        return self.dic_slices["s" + str(slice_index)]["array_lookup_pixels"]

    def get_array_lookup_mz_avg(self, slice_index):
        # Previously called lookup_table_averaged_spectrum_high_res
        return self.dic_slices["s" + str(slice_index)]["array_lookup_mz_avg"]

    def get_array_spectra(self, slice_index):
        # Previously called array_spectra_high_res
        warnings.warn(
            "A large slice dataset is being loaded in memory. "
            + "That's a time and memory costly operation that you might want to avoid "
            + "by calling get_partial_array_spectra() instead."
        )
        return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][:]

    def get_array_mz(self, slice_index):
        # Previously called array_spectra_high_res
        warnings.warn(
            "A large slice dataset is being loaded in memory. "
            + "That's a time and memory costly operation that you might want to avoid "
            + "by calling get_partial_array_mz() instead."
        )
        return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][0, :]

    def get_array_intensity(self, slice_index):
        # Previously called array_spectra_high_res
        warnings.warn(
            "A large slice dataset is being loaded in memory. "
            + "That's a time and memory costly operation that you might want to avoid "
            + "by calling get_partial_array_intensity() instead."
        )
        return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][1, :]

    def get_array_avg_spectrum(self, slice_index):
        # Previously called array_averaged_mz_intensity_high_res

        warnings.warn(
            "get_array_avg_spectrum()is a time costly function that you might want to avoid "
            + "by calling get_partial_array_avg_spectrum() instead."
        )
        return self.hdf5_getter.root["s" + str(slice_index)]["array_avg_intensity"][:]

    def get_array_lookup_mz(self, slice_index):
        # Previously called lookup_table_spectra_high_res

        warnings.warn(
            "get_array_lookup_mz()is a time costly function that you might want to avoid "
            + "by calling get_lookup_mz() instead."
        )
        return self.hdf5_getter.root["s" + str(slice_index)]["array_lookup_mz"][:]

    def get_array_cumulated_lookup_mz_image(self, slice_index):
        # Previously called cumulated_image_lookup_table_high_res

        warnings.warn(
            "get_array_cumulated_lookup_mz_image()is a time costly function that you might want to avoid "
            + "by calling get_cumulated_lookup_mz_image() instead."
        )
        return self.hdf5_getter.root["s" + str(slice_index)]["array_cumulated_lookup_mz_image"][:]

    def get_partial_array_spectra(self, slice_index, lb=None, hb=None, index=None):

        # If not specific index has been provided, it returns a range
        if index is None:

            # Start with most likely case
            if hb is not None and lb is not None:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][:, lb:hb]

            # Second most likely case : full slice
            elif lb is None and hb is None:
                return self.get_array_intensity(slice_index)

            # Most likely the remaining cases won't be used
            elif lb is None:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][:, :hb]
            else:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][:, lb:]

        # Else, it returns the required index
        else:
            if lb is not None or hb is not None:
                warnings.warn(
                    "Both one or several boundaries and one index have been specified when calling array_spectra. "
                    + "Only the index request will be satisfied."
                )
            return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][:, index]

    def get_partial_array_mz(self, slice_index, lb=None, hb=None, index=None):

        # If not specific index has been provided, it returns a range
        if index is None:

            # Start with most likely case
            if hb is not None and lb is not None:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][0, lb:hb]

            # Second most likely case : full slice
            elif lb is None and hb is None:
                return self.get_array_mz(slice_index)

            # Most likely the remaining cases won't be used
            elif lb is None:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][0, :hb]

            else:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][0, lb:]

        # Else, it returns the required index
        else:
            if lb is not None or hb is not None:
                warnings.warn(
                    "Both one or several boundaries and one index have been specified when calling array_spectra. "
                    + "Only the index request will be satisfied."
                )
            return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][0, tuple(index)]

    def get_partial_array_intensity(self, slice_index, lb=None, hb=None, index=None):

        # If not specific index has been provided, it returns a range
        if index is None:

            # Start with most likely case
            if hb is not None and lb is not None:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][1, lb:hb]

            # Second most likely case : full slice
            elif lb is None and hb is None:
                return self.get_array_intensity(slice_index)

            # Most likely the remaining cases won't be used
            elif lb is None:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][1, :hb]

            else:
                return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][1, lb:]

        # Else, it returns the required index
        else:
            if lb is not None or hb is not None:
                warnings.warn(
                    "Both one or several boundaries and one index have been specified when calling array_spectra. "
                    + "Only the index request will be satisfied."
                )
            return self.hdf5_getter.root["s" + str(slice_index)]["array_spectra"][1, index]

    def get_partial_array_avg_spectrum(self, slice_index, lb=None, hb=None):

        # Start with most likely case
        if hb is not None and lb is not None:
            return self.hdf5_getter.root["s" + str(slice_index)]["array_avg_intensity"][:, lb:hb]

        # Second most likely case : full slice
        elif lb is None and hb is None:
            return self.get_array_avg_spectrum(slice_index)

        # Most likely the remaining cases won't be used
        elif lb is None:
            return self.hdf5_getter.root["s" + str(slice_index)]["array_avg_intensity"][:, :hb]
        else:
            return self.hdf5_getter.root["s" + str(slice_index)]["array_avg_intensity"][:, lb:]

    def get_lookup_mz(self, slice_index, index):
        # Just return the (one) required lookup to go faster
        return self.hdf5_getter.root["s" + str(slice_index)]["array_lookup_mz"][index]

    def get_cumulated_lookup_mz_image(self, slice_index, index):
        # Just return the (one) required lookup to go faster
        return self.hdf5_getter.root["s" + str(slice_index)]["array_cumulated_lookup_mz_image"][index]
