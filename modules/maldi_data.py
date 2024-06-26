# Copyright (c) 2022, Colas Droin. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

""" This class is used to access the data coming from acquisitions (MALDI), essentially in the form 
of memory maps, and annotations."""

# ==================================================================================================
# --- Imports
# ==================================================================================================

# Standard modules
import logging
import pickle
import time
import numpy as np
import pandas as pd
import os
from skimage import io
import lzma

# LBAE imports
from modules.tools.misc import logmem


# ==================================================================================================
# --- Class
# ==================================================================================================


class MaldiData:
    """A class to access the various arrays in the dataset from two dictionnaries, lightweight
    (always kept in ram), and memmap (remains on disk). It uses the special attribute __slots__ for
    faster access to the attributes. If _sample_data is True, all the dataset is stored in the
    lightweight dictionnary, and the memmap dictionnary is empty.

    Attributes:
        _sample_data (bool): if True, use the sampled dataset. Else use the whole dataset.
        _dic_lightweight (dictionnary): a dictionnary containing the following lightweights arrays,
            which remain in memory as long as the app is running, as well as the shape of thoses
            stored in memory maps:
            - image_shape: a tuple of integers, indicating the vertical and horizontal sizes of the
                corresponding slice.
            - divider_lookup: integer that sets the resolution of the lookup tables.
            - array_avg_spectrum_downsampled: bidimensional, it contains the low-resolution spectrum
                averaged over all pixels. First row contains the m/z values, while second row
                contains the corresponding intensities.
            - array_lookup_pixels: bidimensional, it maps each pixel to two array_spectra_high_res
            indices, delimiting the corresponding spectrum.
            - array_lookup_mz_avg: unidimensional, it maps m/z values to indexes in the averaged
                array_spectra for each pixel.
            - array_peaks_transformed_lipids: bidimensional, it contains the peak annotations
                (min peak, max peak, average value of the peak), sorted by min_mz, for the lipids
                that have been transformed.
            In addition, it contains the shape of all the arrays stored in the numpy memory maps.
            Dictionnary indices start at 1.
        _n_slices (int): number of slices present in the dataset.
        _l_slices (list): list of slices indices in the dataset. Indices start at 1.
        _l_slices_brain_1 (list): list of slices indices belonging to brain 1.
        _l_slices_brain_2 (list): list of slices indices belonging to brain 2.
        _dic_memmap (dictionnary): a dictionnary containing numpy memory maps allowing to access the
            heavyweights arrays of the datasets, without saturating the disk (ONLY IF _sample_data
            IS FALSE. ELSE ALL THE DATASET IS STORED IN _dic_lightweight). The arrays in the
            dictionnary are:
            - array_spectra: bidimensional, it contains the concatenated spectra of each pixel.
                First row contains the m/z values, while second row contains the corresponding
                intensities.
            - array_avg_spectrum: bidimensional, it contains the high-resolution spectrum averaged
                over all pixels. First row contains the m/z values, while second row contains the
                corresponding intensities.
            - array_avg_spectrum_after_standardization: Same as array_avg_spectrum, but after MAIA
                standardization.
            - array_lookup_mz: bidimensional, it maps m/z values to indexes in array_spectra for
                each pixel.
            - array_cumulated_lookup_mz_image: bidimensional, it maps m/z values to the cumulated
                spectrum until the corresponding m/z value for each pixel.
            - array_corrective_factors: three-dimensional, it contains the MAIA corrective factor
                used for lipid (first dimension) and each pixel (second and third dimension).
        _path_data (str): path were the data files are stored.
        _df_annotations (pd.dataframe): a dataframe containing for each slice and each annotated
            peak the name of the lipid in between the two annotated peak boundaries. Columns are
            'slice', 'name', 'structure', 'cation', 'theoretical m/z', 'min', 'max', 'num_pixels',
            and	'mz_estimated'.
        _df_annotations_MAIA_transformed_lipids_brain_1 (pd.dataframe): a dataframe containing the
            average m/z value of each MAIA transformed lipid. Columns are 'name', 'structure',
            'cation', 'estimated_mz', for brain 1.
        _df_annotations_MAIA_transformed_lipids_brain_2 (pd.dataframe): Same as
            _df_annotations_MAIA_transformed_lipids_brain_1 for brain 2.

    Methods:
        __init__(path_data="data/whole_dataset/", path_annotations="data/annotations/"): Initialize
            the class MaldiData.
        get_annotations(): Getter for the lipid annotation of each slice, contained in a pandas
            dataframe.
        get_annotations_MAIA_transformed_lipids(brain_1=True): Getter for the MAIA transformed
            lipid annotation, contained in a pandas dataframe.
        get_slice_number(): Getter for the number of slice present in the dataset.
        get_slice_list(indices="all"): Getter for the list of slice indices in the dataset.
        get_image_shape(slice_index): Getter for image_shape, which indicates the shape of the image
            corresponding to the acquisition indexed by slice_index.
        get_divider_lookup(slice_index): Getter for divider_lookup, which sets the resolution of the
            lookup of the acquisition indexed by slice_index.
        get_array_avg_spectrum_downsampled(slice_index): Getter for array_avg_spectrum_downsampled,
            which is a low resolution version of average spectrum of the acquisition indexed by
            slice_index.
        get_array_lookup_pixels(slice_index): Getter for array_lookup_pixels, which is a lookup
            table that maps pixel value to the corresponding spectrum indices in the corresponding
            spectrum data.
        get_array_lookup_mz_avg(slice_index): Getter for array_lookup_mz_avg, which is a lookup
            table that maps m/z values to the corresponding indices in the averaged sectral data.
        get_array_peaks_transformed_lipids(slice_index): Getter for array_peaks_transformed_lipids,
            which is a lookup table for the indices of the peaks of the transformed lipids in the
            spectral data.
        get_array_corrective_factors(slice_index): Getter for array_corrective_factors, which is a
            numpy array containing the MAIA corrective factors for each pixel of the requested
            acquired slice.
        get_array_spectra(slice_index): Getter for array_spectra, which is a (memmaped) numpy array
            containing the spectral data of slice indexed by slice_index.
        get_array_mz(slice_index): Getter for array_mz, which corresponds to the first row of
            array_spectra, i.e. the m/z values of the spectral data.
        get_array_intensity(slice_index): Getter for array_intensity, which corresponds to the
            second row of array_spectra, i.e. the intensity values of the spectral data.
        get_array_avg_spectrum(slice_index, standardization=True): Getter for array_avg_spectrum,
            which is a (memmaped) numpy array containing the (high resolution) averaged spectral
            data of slice indexed by slice_index.
        get_array_lookup_mz(slice_index): Getter for array_lookup_mz, which is a lookup table
            that maps m/z values to the corresponding indices in the spectral data.
        get_array_cumulated_lookup_mz_image(slice_index): Getter for
            array_cumulated_lookup_mz_image, which is a lookup table that maps m/z values to the
            cumulated spectrum until the corresponding m/z value for each pixel.
        get_partial_array_spectra(slice_index, lb=None, hb=None, index=None): Getter for
            partial_array_spectra, which is a (memmaped) numpy array containing the spectral data
            of slice indexed by slice_index, between lb and hb m/z values.
        get_partial_array_mz(slice_index, lb=None, hb=None, index=None): Getter for
            partial_array_mz, which corresponds to the first row of partial_array_spectra, i.e.
            the m/z values of the spectral data, between lb and hb.
        get_partial_array_intensity(slice_index, lb=None, hb=None, index=None): Getter for
            partial_array_intensity, which corresponds to the second row of partial_array_spectra,
            i.e. the intensity values of the spectral data, between lb and hb.
        get_partial_array_avg_spectrum(slice_index, lb=None, hb=None, standardization=True): Getter
            for partial_array_avg_spectrum, which is a (memmaped) numpy array containing the
            (high resolution) averaged spectral data of slice indexed by slice_index, between lb
            and hb m/z values.
        get_lookup_mz(slice_index, index): Returns the m/z value corresponding to the index in the
            spectral data of slice indexed by slice_index.
        get_cumulated_lookup_mz_image(slice_index, index): Returns the cumulated spectrum until
            the corresponding m/z value for the pixel corresponding to the index in the spectral
            data of slice indexed by slice_index.
        is_brain_1(self, slice_index): Returns True if the slice indexed by slice_index is from
            brain 1, False otherwise.
        clean_memory(slice_index=None, array=None, cache=None): Cleans the memory (reset the
            memory-mapped arrays) of the app.
        compute_l_labels(slice_index): Computes and returns the labels of the lipids in the dataset
            for the requested slice.
        return_lipid_options(): Computes and returns the list of lipid names, structures and cation.
        compute_padded_original_images(): Pads the original slice images of the dataset so that they
            all have the same size.
        return_lipizones_options(): Computes and returns the list of lipizones.
    """

    __slots__ = [
        "_dic_lightweight",
        "_dic_memmap",
        "_l_slices",
        "_n_slices",
        "_l_slices_brain_1",
        "_l_slices_brain_2",
        "_sample_data",
        "_df_annotations",
        "_df_lipizones",
        "_df_annotations_MAIA_transformed_lipids_brain_1",
        "_df_annotations_MAIA_transformed_lipids_brain_2",
        "_path_data",
    ]

    # ==============================================================================================
    # --- Constructor
    # ==============================================================================================

    def __init__(
        self,
        path_data="data/whole_dataset/",
        path_annotations="data/annotations/",
        path_lipizones="data/lipizones/",
        sample_data=False,
    ):
        """Initialize the class MaldiData.

        Args:
            path_data (str): Path used to load the files containing the MALDI data.
            path_annotations (str): Path used to load the files containing the annotations.
        """

        logging.info("Initializing MaldiData object" + logmem())

        # Set if use the sampled dataset or not
        self._sample_data = sample_data

        # Load the dictionnary containing small-size data for all slices
        if self._sample_data:
            with lzma.open(path_data + "light_arrays.pickle", "rb") as handle:
                self._dic_lightweight = pickle.load(handle)
        else:
            with open(path_data + "light_arrays.pickle", "rb") as handle:
                self._dic_lightweight = pickle.load(handle)

        # Simple variable to get the number of slices
        self._n_slices = len(self._dic_lightweight)
        self._l_slices = sorted(list(self._dic_lightweight.keys()))
        self._l_slices_brain_1 = sorted(
            [slice_idx for slice_idx, val in self._dic_lightweight.items() if val["is_brain_1"]]
        )
        self._l_slices_brain_2 = sorted(
            [slice_idx for slice_idx, val in self._dic_lightweight.items() if not val["is_brain_1"]]
        )

        # Set the accesser to the mmap files
        self._dic_memmap = {}
        if not self._sample_data:
            for slice_index in self._l_slices:
                self._dic_memmap[slice_index] = {}
                for array_name in [
                    "array_spectra",
                    "array_avg_spectrum",
                    "array_avg_spectrum_after_standardization",
                    "array_lookup_mz",
                    "array_cumulated_lookup_mz_image",
                    "array_corrective_factors",
                ]:
                    self._dic_memmap[slice_index][array_name] = np.memmap(
                        path_data + array_name + "_" + str(slice_index) + ".mmap",
                        dtype="float32" if array_name != "array_lookup_mz" else "int32",
                        mode="r",
                        shape=self._dic_lightweight[slice_index][array_name + "_shape"],
                    )

        # Save path_data for cleaning memmap in case
        self._path_data = path_data

        # Load lipid annotation (not user-session specific)
        self._df_annotations = pd.read_csv(path_annotations + "lipid_annotation.csv")

        # Load lipid annotations of MAIA-transformed lipids for brain 1
        self._df_annotations_MAIA_transformed_lipids_brain_1 = pd.read_csv(
            path_annotations + "transformed_lipids_brain_1.csv"
        )

        # Load lipizones for brain 2
        self._df_lipizones = pd.read_csv(path_lipizones + "coordinates_and_lipizones.csv")
        self._df_lipizones.rename(columns={'Unnamed: 0':'id'}, inplace=True)
        self._df_lipizones["level"] = self._df_lipizones.lipotype.apply(lambda x: x.split("_")[1])
        self._df_lipizones["value"] = self._df_lipizones.lipotype.apply(lambda x: x.split("_")[2])

        # Brain 2 is not contained in the sampled dataset
        if not self._sample_data:
            # Load lipid annotations of MAIA-transformed lipids for brain 2
            self._df_annotations_MAIA_transformed_lipids_brain_2 = pd.read_csv(
                path_annotations + "transformed_lipids_brain_2.csv"
            )
        else:
            self._df_annotations_MAIA_transformed_lipids_brain_2 = None

        logging.info("MaldiData object instantiated" + logmem())

    # ==============================================================================================
    # --- Methods
    # ==============================================================================================

    def get_annotations(self):
        """Getter for the lipid annotation of each slice, contained in a pandas
            dataframe.

        Returns:
            (pd.DataFrame): A dataframe of annotations.
        """
        return self._df_annotations
    
    def get_lipizones(self):
        """Getter for the lipizones annotation of each slice, contained in a pandas
            dataframe.

        Returns:
            (pd.DataFrame): A dataframe of lipizones.
        """
        return self._df_lipizones

    def get_annotations_MAIA_transformed_lipids(self, brain_1=True):
        """Getter for the MAIA transformed lipid annotation, contained in a pandas dataframe.

        Args:
            brain_1 (bool, optional): If True, return the lipid annotions for brain 1. Else for
                brain 2. Defaults to True.

        Returns:
            (pd.DataFrame): A dataframe of lipid annotations for the MAIA transformed lipids.
        """
        if brain_1:
            return self._df_annotations_MAIA_transformed_lipids_brain_1
        else:
            return self._df_annotations_MAIA_transformed_lipids_brain_2

    def get_slice_number(self):
        """Getter for the number of slice present in the dataset.

        Returns:
            (int): The number of slices in the dataset.
        """
        return self._n_slices

    def get_slice_list(self, indices="all"):
        """Getter for the list of slice indices.

        Args:
            indices (str, optional): If "all", return the list of all slice indices. If "brain_1",
                return the list of slice indices for brain 1. If "brain_2", return the list of
                slice indices for brain 2. Defaults to "all". Indices start at 1.

        Returns:
            (list): The list of requested slice indices.
        """
        if indices == "all":
            return self._l_slices
        elif indices == "brain_1":
            return self._l_slices_brain_1
        elif indices == "brain_2":
            return self._l_slices_brain_2
        else:
            raise ValueError("Invalid string for indices")

    def get_image_shape(self, slice_index):
        """Getter for image_shape, which indicates the shape of the image corresponding to the
        acquisition indexed by slice_index.

        Args:
            slice_index (int): Index of the slice whose shape is requested.

        Returns:
            (np.ndarray): The shape of the requested slice image.
        """
        return self._dic_lightweight[slice_index]["image_shape"]

    def get_divider_lookup(self, slice_index):
        """Getter for divider_lookup, which sets the resolution of the lookup of the acquisition
        indexed by slice_index.

        Args:
            slice_index (int): Index of the slice whose divider lookup value is requested.

        Returns:
            (int): The divider lookup value for the requested slice.
        """
        return self._dic_lightweight[slice_index]["divider_lookup"]

    def get_array_avg_spectrum_downsampled(self, slice_index):
        """Getter for array_avg_spectrum_downsampled, which is a low-resolution version of the
        average spectrum of the acquisition indexed by slice_index.

        Args:
            slice_index (int): Index of the slice whose spectrum data is requested.

        Returns:
            (np.ndarray): A low-resolution version of the average spectrum of the acquisition indexed
                by slice_index.
        """
        # Previously called array_averaged_mz_intensity_low_res
        return self._dic_lightweight[slice_index]["array_avg_spectrum_downsampled"]

    def get_array_lookup_pixels(self, slice_index):
        """Getter for array_lookup_pixels, which is a lookup table that maps pixel value to the
        corresponding spectrum indices in the corresponding spectrum data.

        Args:
            slice_index (int): Index of the slice whose pixel lookup table is requested.

        Returns:
            (np.ndarray): The requested lookup table.
        """
        # Previously called array_pixel_indexes_high_res
        return self._dic_lightweight[slice_index]["array_lookup_pixels"]

    def get_array_lookup_mz_avg(self, slice_index):
        """Getter for array_lookup_mz_avg, which is a lookup table that maps m/z values to the
        corresponding indices in the averaged sectral data.

        Args:
            slice_index (int): Index of the slice for which the lookup table is requested.

        Returns:
            (np.ndarray): The requested lookup table.
        """
        # Previously called lookup_table_averaged_spectrum_high_res
        return self._dic_lightweight[slice_index]["array_lookup_mz_avg"]

    def get_array_peaks_transformed_lipids(self, slice_index):
        """Getter for array_peaks_transformed_lipids, which is a lookup table for the indices of the
        peaks of the transformed lipids in the spectral data.

        Args:
            slice_index (int): Index of the slice for which the peaks lookup table is requested.

        Returns:
            (np.ndarray): Bidimensional array of peak annotations for the requested slice.
        """
        return self._dic_lightweight[slice_index]["array_peaks_transformed_lipids"]

    def get_array_corrective_factors(self, slice_index):
        """Getter for array_corrective_factors, which is a numpy array containing the MAIA
        corrective factors for each pixel of the requested acquired slice.

        Args:
            slice_index (int): Index of the slice for which the corrective factors are requested.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): Three-dimensional array containing the MAIA
                corrective factor used for lipids and each pixel.
        """
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_corrective_factors"]
        else:
            return self._dic_memmap[slice_index]["array_corrective_factors"]

    def get_array_spectra(self, slice_index):
        """Getter for array_spectra, which is a numpy array containing the spectral data
        of slice indexed by slice_index.

        Args:
            slice_index (int): Index of the slice for which the spectral data is requested.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): Spectral data of the requested slice.
        """
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_spectra"]
        else:
            return self._dic_memmap[slice_index]["array_spectra"]

    def get_array_mz(self, slice_index):
        """Getter for array_mz, which corresponds to the first row of array_spectra, i.e. the m/z
        values of the spectral data.

        Args:
            slice_index (int): Index of the slice for which the m/z values are requested.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): m/z values of the spectral data of the
                requested slice.
        """
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_spectra"][0, :]
        else:
            return self._dic_memmap[slice_index]["array_spectra"][0, :]

    def get_array_intensity(self, slice_index):
        """Getter for array_intensity, which corresponds to the second row of array_spectra, i.e.
        the intensity values of the spectral data.

        Args:
            slice_index (int): Index of the slice for which the intensity values are requested.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): Intensity values of the spectral data of the
                requested slice.
        """
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_spectra"][1, :]
        else:
            return self._dic_memmap[slice_index]["array_spectra"][1, :]

    def get_array_avg_spectrum(self, slice_index, standardization=True):
        """Getter for array_avg_spectrum, which is a numpy array containing the (high
        resolution) averaged spectral data of slice indexed by slice_index.

        Args:
            slice_index (int): Index of the slice for which the average spectrum is requested.
            standardization (bool): If True, the average spectrum is standardized with MAIA.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): The requested average spectrum.
        """

        if not standardization:
            if self._sample_data:
                return self._dic_lightweight[slice_index]["array_avg_spectrum"]
            else:
                return self._dic_memmap[slice_index]["array_avg_spectrum"]
        else:
            if self._sample_data:
                return self._dic_lightweight[slice_index][
                    "array_avg_spectrum_after_standardization"
                ]
            else:
                return self._dic_memmap[slice_index]["array_avg_spectrum_after_standardization"]

    def get_array_lookup_mz(self, slice_index):
        """Getter for array_lookup_mz, which is a lookup table that maps m/z values to the
        corresponding indices in the spectral data.

        Args:
            slice_index (int): Index of the slice for which the lookup table is requested.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): The requested lookup table.
        """
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_lookup_mz"]
        else:
            return self._dic_memmap[slice_index]["array_lookup_mz"]

    def get_array_cumulated_lookup_mz_image(self, slice_index):
        """Getter for array_cumulated_lookup_mz_image, which is a lookup table that maps m/z values
        to the corresponding indices in the spectral data.

        Args:
            slice_index (int): Index of the slice for which the lookup table is requested.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): The requested lookup table.
        """
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_cumulated_lookup_mz_image"]
        else:
            return self._dic_memmap[slice_index]["array_cumulated_lookup_mz_image"]

    def get_partial_array_spectra(self, slice_index, lb=None, hb=None, index=None):
        """Getter for partial_array_spectra, which is a numpy array containing the
        spectral data of slice indexed by slice_index.

        Args:
            slice_index (int): Index of the slice for which the spectral data is requested.
            lb (int): Lower bound of the requested spectrum.
            hb (int): Upper bound of the requested spectrum.
            index (int): Index of the requested spectrum.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): Spectral data of the requested slice.
        """

        # As there are many possibilities, define new dic depending if sampled data or not
        if self._sample_data:
            dic = self._dic_lightweight[slice_index]
        else:
            dic = self._dic_memmap[slice_index]

        if lb is None and hb is None and index is None:
            # Previously called array_spectra_high_res.
            return dic["array_spectra"]
        elif lb is not None and hb is not None:
            return dic["array_spectra"][:, lb:hb]
        elif index is not None:
            return dic["array_spectra"][:, index]

        # If not specific index has been provided, it returns a range
        if index is None:
            # Start with most likely case
            if hb is not None and lb is not None:
                return dic["array_spectra"][:, lb:hb]

            # Second most likely case : full slice
            elif lb is None and hb is None:
                return self.get_array_intensity(slice_index)

            # Most likely the remaining cases won't be used
            elif lb is None:
                return dic["array_spectra"][:, :hb]
            else:
                return dic["array_spectra"][:, lb:]

        # Else, it returns the required index
        else:
            if lb is not None or hb is not None:
                logging.warning(
                    "Both one or several boundaries and one index have been specified"
                    + " when calling array_spectra. "
                    + "Only the index request will be satisfied."
                )
            return dic["array_spectra"][:, index]

    def get_partial_array_mz(self, slice_index, lb=None, hb=None, index=None):
        """Getter for partial_array_mz, which corresponds to the first row of partial_array_spectra,
        i.e. the m/z values of the spectral data, between lb and hb.

        Args:
            slice_index (int): Index of the slice for which the m/z values are requested.
            lb (int): Lower bound of the requested spectrum.
            hb (int): Upper bound of the requested spectrum.
            index (int): Index of the slice of the requested spectrum.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): m/z values of the spectral data of the
                requested slice between lb and hb.
        """

        # As there are many possibilities, define new dic depending if sampled data or not
        if self._sample_data:
            dic = self._dic_lightweight[slice_index]
        else:
            dic = self._dic_memmap[slice_index]

        if lb is None and hb is None and index is None:
            # Previously called array_spectra_high_res
            return dic["array_spectra"][0, :]
        elif lb is not None and hb is not None:
            return dic["array_spectra"][0, lb:hb]
        elif index is not None:
            return dic["array_spectra"][0, index]

        # If not specific index has been provided, it returns a range
        if index is None:
            # Start with most likely case
            if hb is not None and lb is not None:
                return dic["array_spectra"][0, lb:hb]

            # Second most likely case : full slice
            elif lb is None and hb is None:
                return self.get_array_mz(slice_index)

            # Most likely the remaining cases won't be used
            elif lb is None:
                return dic["array_spectra"][0, :hb]

            else:
                return dic["array_spectra"][0, lb:]

        # Else, it returns the required index
        else:
            if lb is not None or hb is not None:
                logging.warning(
                    "Both one or several boundaries and one index have been specified"
                    + " when calling array_spectra. "
                    + "Only the index request will be satisfied."
                )
            return dic["array_spectra"][0, index]

    def get_partial_array_intensity(self, slice_index, lb=None, hb=None, index=None):
        """Getter for partial_array_intensity, which corresponds to the second row of
        partial_array_spectra, i.e. the intensity values of the spectral data, between lb and hb.

        Args:
            slice_index (int): Index of the slice for which the intensity values are requested.
            lb (int): Lower bound of the requested spectrum.
            hb (int): Upper bound of the requested spectrum.
            index (int): Index of the slice of the requested spectrum.

        Returns:
            (np.ndarray, mmaped if not sampled dataset): Intensity values of the spectral data of the
                requested slice between lb and hb.
        """
        # As there are many possibilities, define new dic depending if sampled data or not
        if self._sample_data:
            dic = self._dic_lightweight[slice_index]
        else:
            dic = self._dic_memmap[slice_index]

        if lb is None and hb is None and index is None:
            # Previously called array_spectra_high_res
            return dic["array_spectra"][1, :]
        elif lb is not None and hb is not None:
            return dic["array_spectra"][1, lb:hb]
        elif index is not None:
            return dic["array_spectra"][1, index]

        # If not specific index has been provided, it returns a range
        if index is None:
            # Start with most likely case
            if hb is not None and lb is not None:
                return dic["array_spectra"][1, lb:hb]

            # Second most likely case : full slice
            elif lb is None and hb is None:
                return self.get_array_intensity(slice_index)

            # Most likely the remaining cases won't be used
            elif lb is None:
                return dic["array_spectra"][1, :hb]

            else:
                return dic["array_spectra"][1, lb:]

        # Else, it returns the required index
        else:
            if lb is not None or hb is not None:
                logging.warning(
                    "Both one or several boundaries and one index have been specified"
                    + " when calling array_spectra. "
                    + "Only the index request will be satisfied."
                )
            return dic["array_spectra"][1, index]

    def get_partial_array_avg_spectrum(self, slice_index, lb=None, hb=None, standardization=True):
        """Getter for partial_array_avg_spectrum, which corresponds to the average spectrum of the
        spectral data, between lb and hb.

        Args:
            slice_index (int): Index of the slice for which the average spectrum is requested.
            lb (int): Lower bound of the requested spectrum.
            hb (int): Upper bound of the requested spectrum.
            standardization (bool): If True, the average spectrum is normalized.

        Returns:
            (np.ndarray, mmaped if not sampled dataset)): Average spectrum of the spectral data of the
                requested slice between lb and hb.
        """
        # As there are many possibilities, define new dic depending if sampled data or not
        if self._sample_data:
            dic = self._dic_lightweight[slice_index]
        else:
            dic = self._dic_memmap[slice_index]

        # Start with most likely case
        if hb is not None and lb is not None:
            if standardization:
                return dic[slice_index]["array_avg_spectrum"][:, lb:hb]
            else:
                return dic[slice_index]["array_avg_spectrum_before_standardization"][:, lb:hb]

        # Second most likely case : full slice
        elif lb is None and hb is None:
            return self.get_array_avg_spectrum(slice_index, standardization)

        # Most likely the remaining cases won't be used
        elif lb is None:
            if standardization:
                return dic[slice_index]["array_avg_spectrum"][:, :hb]
            else:
                return dic[slice_index]["array_avg_spectrum_before_standardization"][:, :hb]
        else:
            if standardization:
                return dic[slice_index]["array_avg_spectrum"][:, lb:]
            else:
                return dic[slice_index]["array_avg_spectrum_before_standardization"][:, lb:]

    def get_lookup_mz(self, slice_index, index):
        """Returns the m/z value corresponding to the index in the spectral data of the slice
        indexed by slice_index.

        Args:
            slice_index (int): Index of the slice for which the m/z value is requested.
            index (int): Index of the slice of the requested spectrum.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): m/z value of the spectral data of the
                requested slice and requested   lookup.
        """
        # Just return the (one) required lookup to go faster
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_lookup_mz"][index]
        else:
            return self._dic_memmap[slice_index]["array_lookup_mz"][index]

    def get_cumulated_lookup_mz_image(self, slice_index, index):
        """Returns the cumulated spectrum until the corresponding m/z value for the pixel
        corresponding to the index in the spectral data of slice indexed by slice_index.

        Args:
            slice_index (int): Index of the slice for which the m/z value is requested.
            index (int): Index of the slice of the requested spectrum.

        Returns:
            (np.ndarray (mmaped if not sampled dataset)): Cumulated m/z value of the spectral data of
                the requested slice and requested lookup.
        """
        # Just return the (one) required lookup to go faster
        if self._sample_data:
            return self._dic_lightweight[slice_index]["array_cumulated_lookup_mz_image"][index]
        else:
            return self._dic_memmap[slice_index]["array_cumulated_lookup_mz_image"][index]

    def is_brain_1(self, slice_index):
        """Returns True if the slice indexed by slice_index is a brain 1. Else, returns False.

        Args:
            slice_index (int): Index of the slice for which the status is requested.

        Returns:
            (bool): True if the slice indexed by slice_index is a brain 1. Else, returns False.
        """
        return self._dic_lightweight[slice_index]["is_brain_1"]

    def clean_memory(self, slice_index=None, array=None, cache=None):
        """Cleans the memory (reset the memory-mapped arrays) of the app. slice_index and array
        allow for a more fine-grained cleaning. If "cache" is provided, it will be used to lock the
        dataset while cleaning. Overall, this function takes about 5ms to run on all memmaps, and
        1ms on a given slice.

        Args:
            slice_index (int, optional): Index of the slice whose corresponding mmap must be
                cleaned. Defaults to None.
            array (str, optional): Name of the array whose corresponding mmap must be cleaned.
                Defaults to None.
            cache (flask_caching.Cache, optional): Cache of the database. Defaults to None.
        """
        if self._sample_data:
            logging.warning(
                "Cleaning memory-mapped dictionnary has been requested, but the sample dataset if"
                " currently being used."
            )
            return None

        # Wait for memory to be released before taking action
        if cache is not None:
            while cache.get("locked-reading") or cache.get("locked-cleaning"):
                time.sleep(0.05)

            # Lock memory to prevent other processes from accessing it
            cache.set("locked-cleaning", True)

        # Case no array name has been provided
        if array is None:
            l_array_names = [
                "array_spectra",
                "array_avg_spectrum",
                "array_avg_spectrum_after_standardization",
                "array_lookup_mz",
                "array_cumulated_lookup_mz_image",
                "array_corrective_factors",
            ]

            # Clean all memmaps if no slice index have been given
            if slice_index is None:
                for index in self._l_slices:
                    for array_name in l_array_names:
                        self._dic_memmap[index][array_name] = np.memmap(
                            self._path_data + array_name + "_" + str(index) + ".mmap",
                            dtype="float32" if array_name != "array_lookup_mz" else "int32",
                            mode="r",
                            shape=self._dic_lightweight[index][array_name + "_shape"],
                        )

            # Else clean all memmaps of a given slice index
            else:
                for array_name in l_array_names:
                    self._dic_memmap[slice_index][array_name] = np.memmap(
                        self._path_data + array_name + "_" + str(slice_index) + ".mmap",
                        dtype="float32" if array_name != "array_lookup_mz" else "int32",
                        mode="r",
                        shape=self._dic_lightweight[slice_index][array_name + "_shape"],
                    )
        # Case an array name has been provided
        else:
            # Clean all memmaps corresponding to the current array if no slice_index have been given
            if slice_index is None:
                for index in self._l_slices:
                    self._dic_memmap[index][array] = np.memmap(
                        self._path_data + array + "_" + str(index) + ".mmap",
                        dtype="float32" if array != "array_lookup_mz" else "int32",
                        mode="r",
                        shape=self._dic_lightweight[index][array + "_shape"],
                    )

            # Else clean the memap of the given slice index
            else:
                self._dic_memmap[slice_index][array] = np.memmap(
                    self._path_data + array + "_" + str(slice_index) + ".mmap",
                    dtype="float32" if array != "array_lookup_mz" else "int32",
                    mode="r",
                    shape=self._dic_lightweight[slice_index][array + "_shape"],
                )

        # Release memory
        if cache is not None:
            cache.set("locked-cleaning", False)

        logging.info("Memory cleaned")

    def compute_l_labels(self, slice_index = None):
        """Computes the list of labels of the dataset (for the whole dataset, or a given slice).

        Args:
            slice_index (int, optional): Index of the slice for which the list of labels must be
                computed. Defaults to None.

        Returns:
            (list): List of labels of the dataset.
        """

        if slice_index is None:
            l_labels = (
                self._df_annotations["name"]
                + "_"
                + self._df_annotations["structure"]
                + "_"
                + self._df_annotations["cation"]
            ).to_list()

        else:
            df_slice = self._df_annotations[self._df_annotations["slice"] == slice_index]
            l_labels = (
                df_slice["name"] + "_" + df_slice["structure"] + "_" + df_slice["cation"]
            ).to_list()
        return l_labels

    def return_lipid_options(self):
        """Computes and returns the list of lipid names, structures and cation.

        Returns:
            (list): List of lipid names, structures and cations.
        """

        return [
            {
                "label": name + " " + structure + " " + cation,
                "value": name + " " + structure + " " + cation,
                "group": name,
            }
            for name in sorted(self.get_annotations().name.unique())
            for structure in sorted(
                self.get_annotations()[(self.get_annotations()["name"] == name)].structure.unique()
            )
            for cation in sorted(
                self.get_annotations()[
                    (self.get_annotations()["name"] == name)
                    & (self.get_annotations()["structure"] == structure)
                ].cation.unique()
            )
        ]
    
    def return_lipizones_options(self):
        """Computes and returns the list of lipizones.

        Returns:
            (list): List of lipizones.
        """

        return [            
            {       
                "label": "level " + level + " " + lipotype,
                "value": "level " + level + " " + lipotype,
                "group": "level " + level,
            }
            for level in sorted(self.get_lipizones().level.unique(), key=lambda x: int(x))
            for lipotype in sorted(self.get_lipizones().value.unique(), key=lambda x: float(x))
        ]

    def compute_padded_original_images(self):
        """Pads the original images of the dataset so that they are all the same size.

        Returns:
            (np.ndarray): A 3D numpy array, where the first dimension corresponds to the slice index,
                and the second and third dimensions correspond to the padded images.
        """
        # Compute number of slices from the original acquisition are present in the folder
        if self._sample_data:
            path = "data_sample/tiff_files/original_data/"
        else:
            path = "data/tiff_files/original_data/"
        n_slices = len([x for x in os.listdir(path) if "slice_" in x])
        if n_slices != self.get_slice_number():
            logging.warning(
                "The number of slices computed from the original tiff files is different from"
                + " the number of slice "
                + "recorded in the MaldiData object."
            )

        # Store them as arrays in a list
        l_array_slices = []
        for i in range(n_slices):
            filename = path + "slice_" + str(i + 1) + ".tiff"
            if self._sample_data:
                l_array_slices.append(np.array(io.imread(filename), dtype=np.int16))
            else:
                l_array_slices.append(np.array(io.imread(filename), dtype=np.int16)[:, :, 2])

        # Find the size of the biggest image
        max_size = (
            np.max([array_slice.shape[0] for array_slice in l_array_slices]),
            np.max([array_slice.shape[1] for array_slice in l_array_slices]),
        )

        # Pad the images with zeros (we add +-0.1 in case we need to round above or below 0.5
        # if odd dimension)
        l_array_slices = [
            np.pad(
                array_slice,
                (
                    (
                        int(round(max_size[0] - array_slice.shape[0] / 2 - 0.1)),
                        int(round(max_size[0] - array_slice.shape[0] / 2 + 0.1)),
                    ),
                    (
                        int(round(max_size[1] - array_slice.shape[1] / 2 - 0.1)),
                        int(round(max_size[1] - array_slice.shape[1] / 2 + 0.1)),
                    ),
                ),
            )
            for array_slice in l_array_slices
        ]

        return np.array(l_array_slices)
