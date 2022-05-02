###### IMPORT MODULES ######

# Standard modules
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from bg_atlasapi import BrainGlobeAtlas
from PIL import Image
import base64
from io import BytesIO
from matplotlib import cm
import plotly.express as px
import skimage
import warnings
import logging
import io
from imageio import imread

# Homemade functions
from modules.tools.atlas import (
    project_atlas_mask,
    get_array_rows_from_atlas_mask,
    fill_array_projection,
    solve_plane_equation,
    compute_simplified_atlas_annotation,
    compute_array_images_atlas,
)
from modules.tools.spectra import compute_spectrum_per_row_selection, compute_thread_safe_function
from modules.atlas_labels import Labels
from modules.tools.storage import (
    return_shelved_object,
    dump_shelved_object,
    load_shelved_object,
    check_shelved_object,
)
from modules.tools.misc import logmem


#! Overall, see if I can memmap all the objects in this class

###### Atlas Class ######
class Atlas:
    def __init__(self, maldi_data, resolution=25, sample=False):

        logging.info("Initializing Atlas object" + logmem())

        # Resolution of the atlas, to be chosen among 10um, 25um or 100um
        if resolution in (10, 25, 100):
            self.resolution = resolution
        else:
            logging.warning("The resolution you chose is not available, using the default of 25um")
            self.resolution = 25

        # Load our data
        self.data = maldi_data

        # Load or download the atlas if it's the first time BrainGlobeAtlas is used
        brainglobe_dir = "data/atlas/"
        os.makedirs(brainglobe_dir, exist_ok=True)
        self.bg_atlas = BrainGlobeAtlas(
            "allen_mouse_" + str(resolution) + "um",
            brainglobe_dir=brainglobe_dir,
            check_latest=False,
        )

        # When computing an array of figures with a slider to explore the atlas, subsample in the
        # longitudinal direction, otherwise it's too heavy
        self.subsampling_block = 20

        # Load string annotation for contour plot, for each voxel.
        # These objects are heavy as they force the loading of annotations from the core Atlas
        # class. But they shouldn't be memory-mapped as they are called when hovering and require
        # very fast response from the server
        self.labels = Labels(self.bg_atlas, force_init=True)

        # Compute a dictionnary that associates to each structure (acronym) the set of ids (int) of
        # all of its children. Used only in page_4_plot_graph_volume, but it's very light so no
        # problem using it as an attribute
        self.dic_acronym_children_id = return_shelved_object(
            "atlas/atlas_objects",
            "dic_acronym_children_id",
            force_update=False,
            compute_function=self.compute_dic_acronym_children_id,
        )

        # Load array of coordinates for warped data (can't be load on the fly from shelve as used
        # with hovering)
        self.array_coordinates_warped_data = np.array(
            skimage.io.imread("data/tiff_files/coordinates_warped_data.tif"), dtype=np.float32
        )

        # Record shape of the warped data
        self.image_shape = list(self.array_coordinates_warped_data.shape[1:-1])

        # Record dict that associate brain region (complete string) to specific id (short label),
        # along with graph of structures. Although the treemap graph is precomputed, the two dics of
        # name and acronyms are relatively lightweight and are used in many different place, so
        # they shouldn't be used a properties
        (
            self.l_nodes,
            self.l_parents,
            self.dic_name_acronym,
            self.dic_acronym_name,
        ) = return_shelved_object(
            "atlas/atlas_objects",
            "hierarchy",
            force_update=False,
            compute_function=self.compute_hierarchy_list,
        )

        # Array_projection_corrected is used a lot, as it encodes the warping transformation of the
        # data. Therefore it shouldn't be used a as a property
        self.array_projection_correspondence_corrected = return_shelved_object(
            "atlas/atlas_objects",
            "arrays_projection_corrected",
            force_update=False,
            compute_function=self.compute_array_projection,
            nearest_neighbour_correction=True,
            atlas_correction=True,
        )[1]

        # Dictionnary of existing masks per slice, which associates slice index (key) to a set of
        # masks acronyms
        if check_shelved_object("atlas/atlas_objects", "dic_existing_masks"):
            self.dic_existing_masks = load_shelved_object(
                "atlas/atlas_objects", "dic_existing_masks"
            )
        else:
            logging.info(
                "The dictionnary of available mask per slice has not been computed yet. "
                + "Doing it now, this may take several hours."
            )
            # Since this function is called at startup, no data locking is needed
            self.save_all_projected_masks_and_spectra(cache_flask=None, sample=sample)

        # Properties
        self._array_projection_corrected = None
        self._l_original_coor = None
        self._list_projected_atlas_borders_arrays = None

    # Load arrays of images using atlas projection. It's a property to save memory as it is only
    # used with objects that should also be precomputed.
    @property
    def array_projection_corrected(self):
        if self._array_projection_corrected is None:
            self._array_projection_corrected = return_shelved_object(
                "atlas/atlas_objects",
                "arrays_projection_corrected",
                force_update=False,
                compute_function=self.compute_array_projection,
                nearest_neighbour_correction=True,
                atlas_correction=True,
            )[0]
        return self._array_projection_corrected

    # Load arrays of original images coordinates. It's a property to save memory as it is only used
    # with objects that should also be precomputed.
    @property
    def l_original_coor(self):
        if self._l_original_coor is None:
            self._l_original_coor = return_shelved_object(
                "atlas/atlas_objects",
                "arrays_projection_corrected",
                force_update=False,
                compute_function=self.compute_array_projection,
                nearest_neighbour_correction=True,
                atlas_correction=True,
            )[2]
        return self._l_original_coor

    # Load array of projected atlas borders (i.e. image of atlas annotations). It's a property to
    # save memory as it is only used with objects that should also be precomputed.
    @property
    def list_projected_atlas_borders_arrays(self):
        if self._list_projected_atlas_borders_arrays is None:
            self._list_projected_atlas_borders_arrays = return_shelved_object(
                "atlas/atlas_objects",
                "list_projected_atlas_borders_arrays",
                force_update=False,
                compute_function=self.compute_list_projected_atlas_borders_figures,
            )
        return self._list_projected_atlas_borders_arrays

    # Compute a dictionnary that associate to each structure (acronym) the set of ids (int) of all
    # of its children
    def compute_dic_acronym_children_id(self):
        def fill_dic_acronym_children_id(dic_acronym_children_id, l_id_leaves):
            older_leave_id = l_id_leaves[0]
            acronym = self.bg_atlas.structures[older_leave_id]["acronym"]
            for id_leave in l_id_leaves:
                # fill dic with current acronym and id
                if acronym in dic_acronym_children_id:
                    dic_acronym_children_id[acronym].add(id_leave)
                else:
                    dic_acronym_children_id[acronym] = set([id_leave])
            # while root is not reached, climb back the ancestor tree
            if len(self.bg_atlas.structures[older_leave_id]["structure_id_path"]) >= 2:
                id_parent = self.bg_atlas.structures[older_leave_id]["structure_id_path"][-2]
                dic_acronym_children_id = fill_dic_acronym_children_id(
                    dic_acronym_children_id, [id_parent] + l_id_leaves
                )
            return dic_acronym_children_id

        dic_acronym_children_id = {}
        for id in set(self.bg_atlas.annotation.flatten()):
            if id != 0:
                dic_acronym_children_id = fill_dic_acronym_children_id(
                    dic_acronym_children_id, [id]
                )
        return dic_acronym_children_id

    def compute_hierarchy_list(self):

        # Create a list of parents for all ancestors
        l_nodes = []
        l_parents = []
        dic_name_acronym = {}
        dic_acronym_name = {}
        idx = 0
        for x, v in self.bg_atlas.structures.items():
            if len(self.bg_atlas.get_structure_ancestors(v["acronym"])) > 0:
                ancestor_acronym = self.bg_atlas.get_structure_ancestors(v["acronym"])[-1]
                ancestor_name = self.bg_atlas.structures[ancestor_acronym]["name"]
            else:
                ancestor_name = ""
            current_name = self.bg_atlas.structures[x]["name"]

            l_nodes.append(current_name)
            l_parents.append(ancestor_name)
            dic_name_acronym[current_name] = v["acronym"]
            dic_acronym_name[v["acronym"]] = current_name

        return l_nodes, l_parents, dic_name_acronym, dic_acronym_name

    def compute_array_projection(self, nearest_neighbour_correction=False, atlas_correction=False):

        array_projection = np.zeros(self.array_coordinates_warped_data.shape[:-1], dtype=np.int16)
        array_projection_filling = np.zeros(array_projection.shape, dtype=np.int16)

        # This array makes the correspondence between the original data coordinates and the new ones
        array_projection_correspondence = np.zeros(array_projection.shape + (2,), dtype=np.int16)
        array_projection_correspondence.fill(-1)

        # list of orginal coordinates
        l_original_coor = []
        l_transform_parameters = return_shelved_object(
            "atlas/atlas_objects",
            "l_transform_parameters",
            force_update=False,
            compute_function=self.compute_projection_parameters,
        )
        for i in range(array_projection.shape[0]):
            # print("slice " + str(i) + " getting processed")
            a, u, v = l_transform_parameters[i]

            # load corresponding slice and coor
            path = "data/tiff_files/coordinates_original_data/"
            filename = (
                path
                + [
                    x
                    for x in os.listdir(path)
                    if str(i + 1) == x.split("slice_")[1].split(".tiff")[0]
                ][0]
            )
            original_coor = np.array(skimage.io.imread(filename), dtype=np.float32)
            l_original_coor.append(original_coor)

            path = "data/tiff_files/original_data/"
            filename = (
                path
                + [
                    x
                    for x in os.listdir(path)
                    if str(i + 1) == x.split("slice_")[1].split(".tiff")[0]
                ][0]
            )
            original_slice = np.array(skimage.io.imread(filename), dtype=np.int16)

            # map back the pixel from the atlas coordinates
            array_projection, array_projection_correspondence = fill_array_projection(
                i,
                array_projection,
                array_projection_filling,
                array_projection_correspondence,
                original_coor,
                self.resolution,
                a,
                u,
                v,
                original_slice,
                self.array_coordinates_warped_data,
                self.bg_atlas.annotation,
                nearest_neighbour_correction=nearest_neighbour_correction,
                atlas_correction=atlas_correction,
            )

        return array_projection, array_projection_correspondence, l_original_coor

    def compute_projection_parameters(self):
        l_transform_parameters = []
        for slice_index in range(self.array_coordinates_warped_data.shape[0]):
            a_atlas, u_atlas, v_atlas = solve_plane_equation(
                slice_index, self.array_coordinates_warped_data
            )
            l_transform_parameters.append((a_atlas, u_atlas, v_atlas))
        return l_transform_parameters

    def compute_list_projected_atlas_borders_figures(self):
        l_array_images = []
        # Load array of atlas images corresponding to our data and how it is projected
        array_projected_images_atlas, array_projected_simplified_id = return_shelved_object(
            "atlas/atlas_objects",
            "array_images_atlas",
            force_update=False,
            compute_function=self.prepare_and_compute_array_images_atlas,
            zero_out_of_annotation=True,
        )

        for slice_index in range(array_projected_simplified_id.shape[0]):

            contours = (
                array_projected_simplified_id[slice_index, 1:, 1:]
                - array_projected_simplified_id[slice_index, :-1, :-1]
            )
            contours = np.clip(contours ** 2, 0, 1)
            contours = np.pad(contours, ((1, 0), (1, 0)))
            # do some cleaning on the sides
            contours[:, :10] = 0
            contours[:, -10:] = 0
            contours[:10, :] = 0
            contours[-10:, :] = 0

            fig = plt.figure(frameon=False)
            dpi = 100
            fig.set_size_inches(contours.shape[1] / dpi, contours.shape[0] / dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")
            prefix = "data:image/png;base64,"
            plt.contour(contours, colors="orange", antialiased=True, linewidths=0.2, origin="image")
            with BytesIO() as stream:
                plt.savefig(stream, format="png", dpi=dpi)
                plt.close()
                img = imread(io.BytesIO(stream.getvalue()))
                l_array_images.append(img)

        return l_array_images

    # * This is quite long to execute (~10mn)
    # ! Delete this comment if it's not long anymore
    def prepare_and_compute_array_images_atlas(self, zero_out_of_annotation=False):

        # Compute an array of simplified structures ids
        simplified_atlas_annotation = compute_simplified_atlas_annotation(self.bg_atlas.annotation)

        return compute_array_images_atlas(
            self.array_coordinates_warped_data,
            simplified_atlas_annotation,
            self.bg_atlas.reference,
            self.resolution,
            zero_out_of_annotation=zero_out_of_annotation,
        )

    def get_atlas_mask(self, structure):

        logging.info('Getting mask for structure "{}"'.format(structure))

        # Get id of the parent structure
        structure_id = self.bg_atlas.structures[structure]["id"]

        # Get list of descendants
        descendants = self.bg_atlas.get_structure_descendants(structure)

        # Build empty mask for 3D array of atlas annotations
        mask_stack = np.zeros(self.bg_atlas.shape, self.bg_atlas.annotation.dtype)

        # Compute a list of ids (parents + children) we want to keep in the final annotation
        l_id = [self.bg_atlas.structures[descendant]["id"] for descendant in descendants] + [
            structure_id
        ]

        # Do the masking
        mask_stack[np.isin(self.bg_atlas.annotation, l_id)] = structure_id

        logging.info('Mask computed for structure "{}"'.format(structure))
        return mask_stack

    def compute_spectrum_data(
        self,
        slice_index,
        projected_mask=None,
        mask_name=None,
        slice_coor_rescaled=None,
        MAIA_correction=False,
        cache_flask=None,
    ):
        if projected_mask is None and mask_name is None:
            print("Either a mask or a mask name must be provided")
            return None
        elif mask_name is not None:
            if slice_coor_rescaled is None:
                slice_coor_rescaled = np.asarray(
                    (
                        self.array_coordinates_warped_data[slice_index, :, :]
                        * 1000
                        / self.resolution
                    ).round(0),
                    dtype=np.int16,
                )
            stack_mask = self.get_atlas_mask(self.dic_name_acronym[mask_name])
            projected_mask = project_atlas_mask(
                stack_mask, slice_coor_rescaled, self.bg_atlas.reference.shape
            )

        # get the list of rows containing the pixels to average
        original_shape = self.data.get_image_shape(slice_index + 1)
        mask_remapped = np.zeros(original_shape, dtype=np.uint8)
        list_index_bound_rows, list_index_bound_column_per_row = get_array_rows_from_atlas_mask(
            projected_mask,
            mask_remapped,
            self.array_projection_correspondence_corrected[slice_index],
        )
        if np.sum(list_index_bound_rows) == 0:
            print("No selection could be found for current mask")
            grah_scattergl_data = None
        else:
            # do the average
            grah_scattergl_data = compute_thread_safe_function(
                compute_spectrum_per_row_selection,
                cache_flask,
                list_index_bound_rows,
                list_index_bound_column_per_row,
                self.data.get_array_spectra(slice_index + 1),
                self.data.get_array_lookup_pixels(slice_index + 1),
                original_shape,
                self.data.get_array_peaks_transformed_lipids(slice_index + 1),
                self.data.get_array_corrective_factors(slice_index + 1),
                zeros_extend=False,
                apply_correction=MAIA_correction,
            )
        return grah_scattergl_data

    def save_all_projected_masks_and_spectra(
        self, force_update=False, cache_flask=None, sample=False
    ):

        # Path atlas for shelving
        path_atlas = "atlas/atlas_objects"

        if sample:
            logging.warning("Only a sample of the masks and spectra will be computed!")

        # Define a dictionnary that contains all the masks that exist for every slice
        dic_existing_masks = {}

        # Define a dictionnary to save the result of the function slice by slice
        if check_shelved_object(path_atlas, "dic_processed_temp"):
            dic_processed_temp = load_shelved_object(path_atlas, "dic_processed_temp",)
        else:
            dic_processed_temp = {}

        for slice_index in range(self.data.get_slice_number()):

            # Break the loop after the first slice if sample is True
            if sample and slice_index > 1:
                break

            logging.info("Starting slice " + str(slice_index))
            slice_coor_rescaled = np.asarray(
                (
                    self.array_coordinates_warped_data[slice_index, :, :] * 1000 / self.resolution
                ).round(0),
                dtype=np.int16,
            )

            dic_existing_masks[slice_index] = set([])

            # Check if the slice has already been processed
            if slice_index not in dic_processed_temp:
                dic_processed_temp[slice_index] = set([])

            # Get hierarchical tree of brain structures
            n_computed = 0
            for mask_name, id_mask in self.dic_name_acronym.items():
                if id_mask not in dic_processed_temp[slice_index]:

                    # Break the loop after a few computations if sample is True
                    if sample and n_computed > 1:
                        break

                    if (
                        not (
                            check_shelved_object(
                                path_atlas,
                                "mask_and_spectrum_"
                                + str(slice_index)
                                + "_"
                                + str(id_mask).replace("/", ""),
                            )
                            and check_shelved_object(
                                path_atlas,
                                "mask_and_spectrum_MAIA_corrected_"
                                + str(slice_index)
                                + "_"
                                + str(id_mask).replace("/", ""),
                            )
                        )
                        or force_update
                    ):
                        # get the array corresponding to the projected mask
                        stack_mask = self.get_atlas_mask(id_mask)

                        # Project the mask onto high resolution data
                        projected_mask = project_atlas_mask(
                            stack_mask, slice_coor_rescaled, self.bg_atlas.reference.shape
                        )
                        if np.sum(projected_mask) == 0:
                            logging.info(
                                "The structure "
                                + mask_name
                                + " is not present in slice "
                                + str(slice_index)
                            )
                            # Mask doesn't exist, so it considered processed
                            dic_processed_temp[slice_index].add(id_mask)
                            continue

                        # Compute average spectrum in the mask
                        grah_scattergl_data = self.compute_spectrum_data(
                            slice_index,
                            projected_mask,
                            MAIA_correction=False,
                            cache_flask=cache_flask,
                        )

                        # Add mask to the list of existing masks
                        dic_existing_masks[slice_index].add(id_mask)
                        dic_processed_temp[slice_index].add(id_mask)

                        # Dump the mask and data with shelve
                        dump_shelved_object(
                            path_atlas,
                            "mask_and_spectrum_"
                            + str(slice_index)
                            + "_"
                            + str(id_mask).replace("/", ""),
                            (projected_mask, grah_scattergl_data),
                        )

                        # Same with MAIA corrected data
                        grah_scattergl_data = self.compute_spectrum_data(
                            slice_index,
                            projected_mask,
                            MAIA_correction=True,
                            cache_flask=cache_flask,
                        )

                        dump_shelved_object(
                            path_atlas,
                            "mask_and_spectrum_MAIA_corrected_"
                            + str(slice_index)
                            + "_"
                            + str(id_mask).replace("/", ""),
                            (projected_mask, grah_scattergl_data),
                        )

                    else:
                        dic_existing_masks[slice_index].add(id_mask)
                        dic_processed_temp[slice_index].add(id_mask)

                    n_computed += 1

                else:
                    n_computed += 1
                    logging.info('Mask "' + mask_name + '" already processed')

            # Dump the dictionnary of processed masks with shelve after every slice
            dump_shelved_object(
                path_atlas, "dic_processed_temp", dic_processed_temp,
            )

        if not sample:
            # Dump the dictionnary of existing masks with shelve
            dump_shelved_object(
                path_atlas, "dic_existing_masks", dic_existing_masks,
            )

        logging.info("Projected masks and spectra have all been computed.")
        self.dic_existing_masks = dic_existing_masks

    def get_projected_mask_and_spectrum(self, slice_index, mask_name, MAIA_correction=False):
        id_mask = self.dic_name_acronym[mask_name]
        if MAIA_correction:
            filename = (
                "mask_and_spectrum_MAIA_corrected_"
                + str(slice_index)
                + "_"
                + str(id_mask).replace("/", "")
            )
        else:
            filename = "mask_and_spectrum_" + str(slice_index) + "_" + str(id_mask).replace("/", "")

        logging.info(
            "Loading " + mask_name + " for slice " + str(slice_index) + " from shelve file."
        )
        try:
            return load_shelved_object("atlas/atlas_objects", filename)
        except:
            logging.warning(
                "The mask and spectrum data could not be found for "
                + mask_name
                + " for slice "
                + str(slice_index)
                + ". Make sure the files have been precomputed and that you checked the mask"
                + " was present in self.dic_existing_masks"
            )
            return None
