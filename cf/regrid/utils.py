"""Worker functions for regridding."""
import numpy as np

from .regrid import Regrid

from ..decorators import _deprecated_kwarg_check


conservative_regridding_methods = (
    "conservative",
    "conservative_1st",
    "conservative_2nd",
)

regridding_methods = (
    "linear",  # prefer over 'bilinear' as of v3.2.0
    "bilinear",  # only for backward compatibility, use & document 'linear'
    "patch",
    "nearest_stod",
    "nearest_dtos",
) + conservative_regridding_methods


def regrid_get_latlong(f, name, axes=None):
    """Retrieve the latitude and longitude coordinates of this field and
       associated information. If 1D lat/long coordinates are found
       then these are returned. Otherwise, 2D lat/long coordinates are
       searched for and if found returned.
    
    :Parameters:

        f: `Field`
            TODO

        name: `str`
            A name to identify the field in error messages. Either
            ``'source'`` or ``'destination'``.

        axes: `dict`, optional
            A dictionary specifying the X and Y axes, with keys
            ``'X'`` and ``'Y'``.

            *Parameter example:*
              ``axes={'X': 'ncdim%x', 'Y': 'ncdim%y'}``

            *Parameter example:*
              ``axes={'X': 1, 'Y': 0}``

    :Returns:

        axis_keys: `list`
            The keys of the x and y dimension coordinates.

        axis_sizes: `list`
            The sizes of the x and y dimension coordinates.

        coord_keys: `list`
            The keys of the x and y coordinate (1D dimension
            coordinate, or 2D auxilliary coordinates).

        coords: `list`
            The x and y coordinates (1D dimension coordinates or 2D
            auxilliary coordinates).

        coords_2D: `bool`
            True if 2D auxiliary coordinates are returned or if 1D X
            and Y coordinates are returned, which are not long/lat.

    """
    data_axes = f.constructs.data_axes()

    if axes is None:
        # Retrieve the field construct's X and Y dimension
        # coordinates
        x_key, x = f.dimension_coordinate(
            "X",
            item=True,
            default=ValueError(
                f"No unique X dimension coordinate found for the {name} "
                "field. If none is present you "
                "may need to specify the axes keyword."
            ),
        )
        y_key, y = f.dimension_coordinate(
            "Y",
            item=True,
            default=ValueError(
                f"No unique Y dimension coordinate found for the {name} "
                "field. If none is present you "
                "may need to specify the axes keyword."
            ),
        )

        x_axis = data_axes[x_key][0]
        y_axis = data_axes[y_key][0]

        x_size = x.size
        y_size = y.size
    else:
        # --------------------------------------------------------
        # Source axes have been provided
        # --------------------------------------------------------
        for key in ("X", "Y"):
            if key not in axes:
                raise ValueError(
                    f"Key {key!r} must be specified for axes of {name} "
                    "field."
                )

        if axes["X"] in (1, 0) and axes["Y"] in (0, 1):
            # Axes specified by integer position in dimensions of
            # lat and lon 2-d auxiliary coordinates
            if axes["X"] == axes["Y"]:
                raise ValueError("TODO 0")

            lon_key, lon = f.auxiliary_coordinate(
                "X", item=True, filter_by_naxes=(2,), default=(None, None)
            )
            lat_key, lat = f.auxiliary_coordinate(
                "Y", item=True, filter_by_naxes=(2,), default=(None, None)
            )
            if lon is None:
                raise ValueError("TODO x")
            if lat is None:
                raise ValueError("TODO y")

            if lat.shape != lon.shape:
                raise ValueError("TODO 222222")

            lon_axes = data_axes[lon_key]
            lat_axes = data_axes[lat_key]
            if lat_axes != lon_axes:
                raise ValueError("TODO 3333333")

            x_axis = lon_axes[axes["X"]]
            y_axis = lat_axes[axes["Y"]]
        else:
            x_axis = f.domain_axis(
                axes["X"],
                key=True,
                default=ValueError(
                    f"'X' axis specified for {name} field not found."
                ),
            )

            y_axis = f.domain_axis(
                axes["Y"],
                key=True,
                default=ValueError(
                    f"'Y' axis specified for {name} field not found."
                ),
            )

        domain_axes = f.domain_axes(todict=True)
        x_size = domain_axes[x_axis].get_size()
        y_size = domain_axes[y_axis].get_size()

    axis_keys = [x_axis, y_axis]
    axis_sizes = [x_size, y_size]

    # If 1-d latitude and longitude coordinates for the field are
    # not found search for 2-d auxiliary coordinates.
    if (
        axes is not None
        or not x.Units.islongitude
        or not y.Units.islatitude
    ):
        lon_found = False
        lat_found = False

        for key, aux in f.auxiliary_coordinates(
            filter_by_naxes=(2,), todict=True
        ).items():
            if aux.Units.islongitude:
                if lon_found:
                    raise ValueError(
                        "The 2-d auxiliary longitude coordinate "
                        f"of the {name} field is not unique."
                    )
                else:
                    lon_found = True
                    x = aux
                    x_key = key

            if aux.Units.islatitude:
                if lat_found:
                    raise ValueError(
                        "The 2-d auxiliary latitude coordinate "
                        f"of the {name} field is not unique."
                    )
                else:
                    lat_found = True
                    y = aux
                    y_key = key

        if not lon_found or not lat_found:
            raise ValueError(
                "Both longitude and latitude coordinates "
                f"were not found for the {name} field."
            )

        if axes is not None:
            if set(axis_keys) != set(data_axes[x_key]):
                raise ValueError(
                    "Axes of longitude do not match "
                    f"those specified for {name} field."
                )

            if set(axis_keys) != set(data_axes[y_key]):
                raise ValueError(
                    "Axes of latitude do not match "
                    f"those specified for {name} field."
                )

        coords_2D = True
    else:
        coords_2D = False
        # Check for size 1 latitude or longitude dimensions
        if x_size == 1 or y_size == 1:
            raise ValueError(
                "Neither the longitude nor latitude dimension coordinates "
                f"of the {name} field can be of size 1."
            )

    coord_keys = [x_key, y_key]
    coords = [x, y]

    return axis_keys, axis_sizes, coord_keys, coords, coords_2D

def regrid_get_cartesian_coords(f, name, axes):
    """Retrieve the specified cartesian dimension coordinates of the
    field and their corresponding keys.

    :Parameters:

        f: `Field`
           TODO

        name: `str`
            A name to identify the field in error messages.

        axes: sequence of `str`
            Specifiers for the dimension coordinates to be
            retrieved. See cf.Field.axes for details.

    :Returns:

        axis_keys: `list`
            A list of the keys of the dimension coordinates
            retrieved.

        coords: `list`
            A list of the dimension coordinates retrieved.

    """
    axis_keys = []
    for axis in axes:
        key = f.domain_axis(axis, key=True)
        axis_keys.append(key)

    coords = []
    for key in axis_keys:
        d = f.dimension_coordinate(filter_by_axis=(key,), default=None)
        if d is None:
            raise ValueError(
                f"No unique {name} dimension coordinate "
                f"matches key {key!r}."
            )

        coords.append(d.copy())

    return axis_keys, coords

@_deprecated_kwarg_check("i")
def regrid_get_axis_indices(f, axis_keys, i=False):
    """Get axis indices and their orders in rank of this field.

   :Parameters:

        f: `Field`
           TODO. The field construct may have size-1 dimensions
           inserted into its data in-place.

       axis_keys: sequence
           A sequence of axis specifiers.

       i: deprecated at version 3.0.0

   :Returns:

       axis_indices: list
           A list of the indices of the specified axes.

       order: `numpy.ndarray`
           A numpy array of the rank order of the axes.

    """
    data_axes = f.get_data_axes()

    # Get the positions of the axes
    axis_indices = []
    for axis_key in axis_keys:
        try:
            axis_index = data_axes.index(axis_key)
        except ValueError:
            f.insert_dimension(axis_key, position=0, inplace=True)
            axis_index = data_axes.index(axis_key)

        axis_indices.append(axis_index)

    # Get the rank order of the positions of the axes
    tmp = np.array(axis_indices)
    tmp = tmp.argsort()
    n = len(tmp)
    order = np.empty((n,), dtype=int)
    order[tmp] = np.arange(n)

    return axis_indices, order

def regrid_get_coord_order(f, axis_keys, coord_keys):
    """Get the ordering of the axes for each N-D auxiliary
    coordinate.

    :Parameters:

         f: `Field`
            TODO.

        axis_keys: sequence
            A sequence of axis keys.

        coord_keys: sequence
            A sequence of keys for each to the N-D auxiliary
            coordinates.

    :Returns:

        `list`
            A list of lists specifying the ordering of the axes for
            each N-D auxiliary coordinate.

    """
    coord_axes = [
        f.get_data_axes(coord_key) for coord_key in coord_keys
    ]
    coord_order = [
        [coord_axis.index(axis_key) for axis_key in axis_keys]
        for coord_axis in coord_axes
    ]
    
    return coord_order

def regrid_get_section_shape(f, axis_sizes, axis_indices):
    """Get the shape of each regridded section.

    :Parameters:

        f: `Field`
            TODO.

        axis_sizes: sequence
            A sequence of the sizes of each axis along which the
            section.  will be taken

        axis_indices: sequence
            A sequence of the same length giving the axis index of
            each axis.

    :Returns:

        shape: `list`
            A list of integers defining the shape of each section.

    """
    shape = [1] * f.ndim
    for i, axis_index in enumerate(axis_indices):
        shape[axis_index] = axis_sizes[i]

    return shape

def regrid_check_bounds(
    src_coords, dst_coords, method, ext_coords=None
):
    """Check the bounds of the coordinates for regridding and reassign the
    regridding method if auto is selected.

    :Parameters:

        src_coords: sequence
            A sequence of the source coordinates.

        dst_coords: sequence
            A sequence of the destination coordinates.

        method: `str`
            A string indicating the regrid method.

        ext_coords: `None` or sequence
            If a sequence of extension coordinates is present these
            are also checked. Only used for cartesian regridding when
            regridding only 1 (only 1!) dimension of a n>2 dimensional
            field. In this case we need to provided the coordinates of
            the dimensions that aren't being regridded (that are the
            same in both src and dst grids) so that we can create a
            sensible ESMF grid object.

    :Returns:

        `None`

    """
    if method not in conservative_regridding_methods:
        return

    for name, coords in zip(
        ("Source", "Destination"), (src_coords, dst_coords)
    ):
        for coord in coords:
            if not coord.has_bounds():
                raise ValueError(
                    f"{name} {coord!r} coordinates must have bounds "
                    "for conservative regridding."
                )

            if not coord.contiguous(overlap=False):
                raise ValueError(
                    f"{name} {coord!r} coordinates must have "
                    "contiguous, non-overlapping bounds "
                    "for conservative regridding."
                )

    if ext_coords is not None:
        for coord in ext_coords:
            if not coord.has_bounds():
                raise ValueError(
                    f"{coord!r} dimension coordinates must have "
                    "bounds for conservative regridding."
                )
            if not coord.contiguous(overlap=False):
                raise ValueError(
                    f"{coord!r} dimension coordinates must have "
                    "contiguous, non-overlapping bounds "
                    "for conservative regridding."
                )

#def regrid_check_dst_Grid_has_corners(regrid, method):
#    """Check the bounds of the coordinates for regridding and reassign the
#    regridding method if auto is selected.
#
#    :Parameters:
#
#        src_coords: sequence
#            A sequence of the source coordinates.
#
#        dst_coords: sequence
#            A sequence of the destination coordinates.
#
#        method: `str`
#            A string indicating the regrid method.
#
#        ext_coords: `None` or sequence
#            If a sequence of extension coordinates is present these
#            are also checked. Only used for cartesian regridding when
#            regridding only 1 (only 1!) dimension of a n>2 dimensional
#            field. In this case we need to provided the coordinates of
#            the dimensions that aren't being regridded (that are the
#            same in both src and dst grids) so that we can create a
#            sensible ESMF grid object.
#
#    :Returns:
#
#        `None`
#
#    """
#    if method not in conservative_regridding_methods:
#        return
#
#    if not regrid.regridSrc2Dst.dstfield.grid.has_corners:
#        raise ValueError(
#            f"cf.{dst.__class__.__name__} {coord!r}  must have destintion "
#            "grid corners for conservative regridding."
#        )
#    for name, coords in zip(
#        ("Source", "Destination"), (src_coords, dst_coords)
#    ):
#        for coord in coords:
#            if not coord.has_bounds():
#                raise ValueError(
#                    f"{name} {coord!r} coordinates must have bounds "
#                    "for conservative regridding."
#                )
#
#            if not coord.contiguous(overlap=False):
#                raise ValueError(
#                    f"{name} {coord!r} coordinates must have "
#                    "contiguous, non-overlapping bounds "
#                    "for conservative regridding."
#                )
#
#    if ext_coords is not None:
#        for coord in ext_coords:
#            if not coord.has_bounds():
#                raise ValueError(
#                    f"{coord!r} dimension coordinates must have "
#                    "bounds for conservative regridding."
#                )
#            if not coord.contiguous(overlap=False):
#                raise ValueError(
#                    f"{coord!r} dimension coordinates must have "
#                    "contiguous, non-overlapping bounds "
#                    "for conservative regridding."
#                )

def regrid_check_method(method):
    """Check the regrid method is valid and if not raise an error.

    :Parameters:

        method: `str`
            The regridding method.

    """
    if method is None:
        raise ValueError("Can't regrid: Must select a regridding method")

    elif method not in regridding_methods:
        raise ValueError(f"Can't regrid: Invalid method: {method!r}")

    elif method == "bilinear":  # TODO use logging.info() once have logging
        print(
            "Note the 'bilinear' method argument has been renamed to "
            "'linear' at version 3.2.0. It is still supported for now "
            "but please use 'linear' in future. "
            "'bilinear' will be removed at version 4.0.0"
        )

def regrid_check_use_src_mask(use_src_mask, method):
    """Check that use_src_mask is True for all methods other than
    nearest_stod and if not raise an error.

    :Parameters:

        use_src_mask: `bool`
            Whether to use the source mask in regridding.

        method: `str`
            The regridding method.

    """
    if not use_src_mask and not method == "nearest_stod":
        raise ValueError(
            "use_src_mask can only be False when using the "
            "nearest_stod method."
        )

def regrid_get_reordered_sections(
    f, axis_order, regrid_axes, regrid_axis_indices
):
    """Get a dictionary of the data sections for regridding and a
    list of its keys reordered if necessary so that they will be
    looped over in the order specified in axis_order.

    :Parameters:

        f: `Field`
            TODO.

        axis_order: `None` or sequence of axes specifiers.
            If `None` then the sections keys will not be reordered. If
            a particular axis is one of the regridding axes or is not
            found then a ValueError will be raised.

        regrid_axes: sequence
            A sequence of the keys of the regridding axes.

        regrid_axis_indices: sequence
            A sequence of the indices of the regridding axes.

    :Returns:

        section_keys: `list`
            An ordered list of the section keys.

        sections: `dict`
            A dictionary of the data sections for regridding.

    """
    # If we had dynamic masking, we wouldn't need this method, we could
    # sdimply replace it in regrid[sc] with a call to
    # Data.section. However, we don't have it, so this allows us to
    # possibibly reduce the number of trasnistions between different masks
    # - each change is slow.
    data_axes = f.get_data_axes()

    axis_indices = []
    if axis_order is not None:
        for axis in axis_order:
            axis_key = f.dimension_coordinate(
                filter_by_axis=(axis,),
                default=None,
                key=True,
            )
            if axis_key is not None:
                if axis_key in regrid_axes:
                    raise ValueError("Cannot loop over regridding axes.")

                try:
                    axis_indices.append(data_axes.index(axis_key))
                except ValueError:
                    # The axis has been squeezed so do nothing
                    pass

            else:
                raise ValueError(f"Axis not found: {axis!r}")

    # Section the data
    sections = f.data.section(regrid_axis_indices)

    # Reorder keys correspondingly if required
    if axis_indices:
        section_keys = sorted(
            sections.keys(), key=itemgetter(*axis_indices)
        )
    else:
        section_keys = sections.keys()

    return section_keys, sections

def regrid_get_destination_mask(
    f, dst_order, axes=("X", "Y"), cartesian=False, coords_ext=None
):
    """Get the mask of the destination field.

    :Parameters:

        f: `Field`
            TODO.

        dst_order: sequence, optional
            The order of the destination axes.

        axes: optional
            The axes the data is to be sectioned along.

        cartesian: `bool`, optional
            Whether the regridding is Cartesian or spherical.

        coords_ext: sequence, optional
            In the case of Cartesian regridding, extension coordinates
            (see _regrid_check_bounds for details).

    :Returns:

        dst_mask: `numpy.ndarray`
            A numpy array with the mask.

    """
    data_axes = f.get_data_axes()

    indices = {axis: [0] for axis in data_axes if axis not in axes}

    g = f.subspace(**indices)
    g = g.squeeze(tuple(indices)).transpose(dst_order)

    dst_mask = g.mask.array

    if cartesian:
        tmp = []
        for coord in coords_ext:
            tmp.append(coord.size)
            dst_mask = np.tile(dst_mask, tmp + [1] * dst_mask.ndim)

    return dst_mask

def regrid_fill_fields(src_data, srcfield, dstfield, fill_value):
    """Fill the source field with data and the destination field
    with fill values.

    :Parameters:

        f: `Field`
            TODO.

        src_data: ndarray
            The data to fill the source field with.

        srcfield: ESMPy Field
            The source field.

        dstfield: ESMPy Field
            The destination field. This get always gets initialised with
            missing values.

    """
    srcfield.data[...] = np.ma.MaskedArray(src_data, copy=False).filled(
        fill_value
    )
    dstfield.data[...] = fill_value

def regrid_compute_field_mass(
    f,
    _compute_field_mass,
    k,
    srcgrid,
    srcfield,
    srcfracfield,
    dstgrid,
    dstfield,
):
    """Compute the field mass for conservative regridding. The mass
    should be the same before and after regridding.

    :Parameters:

        f: `Field`
            TODO.

        _compute_field_mass: `dict`
            A dictionary for the results.

        k: `tuple`
            A key identifying the section of the field being regridded.

        srcgrid: ESMPy grid
            The source grid.

        srcfield: ESMPy grid
            The source field.

        srcfracfield: ESMPy field
            Information about the fraction of each cell of the source
            field used in regridding.

        dstgrid: ESMPy grid
            The destination grid.

        dstfield: ESMPy field
            The destination field.

    """
    if not isinstance(_compute_field_mass, dict):
        raise ValueError(
            "Expected _compute_field_mass to be a dictionary."
        )

    fill_value = f.fill_value(default="netCDF")

    # Calculate the mass of the source field
    srcareafield = Regrid.create_field(srcgrid, "srcareafield")
    srcmass = Regrid.compute_mass_grid(
        srcfield,
        srcareafield,
        dofrac=True,
        fracfield=srcfracfield,
        uninitval=fill_value,
    )

    # Calculate the mass of the destination field
    dstareafield = Regrid.create_field(dstgrid, "dstareafield")
    dstmass = Regrid.compute_mass_grid(
        dstfield, dstareafield, uninitval=fill_value
    )

    # Insert the two masses into the dictionary for comparison
    _compute_field_mass[k] = (srcmass, dstmass)


def regrid_get_regridded_data(
    f, method, fracfield, dstfield, dstfracfield
):
    """Get the regridded data of frac field as a numpy array from
    the ESMPy fields.

    :Parameters:

        f: `Field`
            TODO.

        method: `str`
            The regridding method.

        fracfield: `bool`
            Whether to return the frac field or not in the case of
            conservative regridding.

        dstfield: ESMPy field
            The destination field.

        dstfracfield: ESMPy field
            Information about the fraction of each of the destination
            field cells involved in the regridding. For conservative
            regridding this must be taken into account.

    """
    if method in conservative_regridding_methods:
        frac = dstfracfield.data.copy()
        if fracfield:
            regridded_data = frac
        else:
            frac[frac == 0.0] = 1.0
            regridded_data = np.ma.MaskedArray(
                dstfield.data / frac,
                mask=(dstfield.data == f.fill_value(default="netCDF")),
            )
    else:
        regridded_data = np.ma.MaskedArray(
            dstfield.data.copy(),
            mask=(dstfield.data == f.fill_value(default="netCDF")),
        )

    return regridded_data


def regrid_update_coordinate_references(
    f,
    dst,
    src_axis_keys,
    dst_axis_sizes,
    method,
    use_dst_mask,
    cartesian=False,
    axes=("X", "Y"),
    n_axes=2,
    src_cyclic=False,
    dst_cyclic=False,
):
    """Update the coordinate references of the new field after
    regridding.

    :Parameters:

        f: `Field`
            TODO. Updated in-place.

        dst: `Field` or `dict`
            The object with the destination grid for regridding.

        src_axis_keys: sequence of `str`
            The keys of the source regridding axes.

        dst_axis_sizes: sequence, optional
            The sizes of the destination axes.

        method: `bool`
            The regridding method.

        use_dst_mask: `bool`
            Whether to use the destination mask in regridding.

        i: `bool`
            Whether to do the regridding in place.

        cartesian: `bool`, optional
            Whether to do Cartesian regridding or spherical

        axes: sequence, optional
            Specifiers for the regridding axes.

        n_axes: `int`, optional
            The number of regridding axes.

        src_cyclic: `bool`, optional
            Whether the source longitude is cyclic for spherical
            regridding.

        dst_cyclic: `bool`, optional
            Whether the destination longitude is cyclic for spherical
            regridding.

    """
    domain_ancillaries = f.domain_ancillaries(todict=True)

    # Initialise cached value for domain_axes
    domain_axes = None

    data_axes = f.constructs.data_axes()

    for key, ref in f.coordinate_references(todict=True).items():
        ref_axes = []
        for k in ref.coordinates():
            ref_axes.extend(data_axes[k])

        if set(ref_axes).intersection(src_axis_keys):
            f.del_construct(key)
            continue

        for (
            term,
            value,
        ) in ref.coordinate_conversion.domain_ancillaries().items():
            if value not in domain_ancillaries:
                continue

            key = value

            # If this domain ancillary spans both X and Y axes
            # then regrid it, otherwise remove it
            x = f.domain_axis("X", key=True)
            y = f.domain_axis("Y", key=True)
            if (
                f.domain_ancillary(
                    filter_by_axis=(x, y),
                    axis_mode="exact",
                    key=True,
                    default=None,
                )
                is not None
            ):
                # Convert the domain ancillary into an independent
                # field
                value = f.convert(key)
                try:
                    if cartesian:
                        value.regridc(
                            dst,
                            axes=axes,
                            method=method,
                            use_dst_mask=use_dst_mask,
                            inplace=True,
                        )
                    else:
                        value.regrids(
                            dst,
                            src_cyclic=src_cyclic,
                            dst_cyclic=dst_cyclic,
                            method=method,
                            use_dst_mask=use_dst_mask,
                            inplace=True,
                        )
                except ValueError:
                    ref.coordinate_conversion.set_domain_ancillary(
                        term, None
                    )
                    f.del_construct(key)
                else:
                    ref.coordinate_conversion.set_domain_ancillary(
                        term, key
                    )
                    d_axes = data_axes[key]

                    domain_axes = f.domain_axes(
                        cached=domain_axes, todict=True
                    )

                    for k_s, new_size in zip(
                        src_axis_keys, dst_axis_sizes
                    ):
                        domain_axes[k_s].set_size(new_size)

                    f.set_construct(
                        f._DomainAncillary(source=value),
                        key=key,
                        axes=d_axes,
                        copy=False,
                    )

def regrid_copy_coordinate_references(f, dst, dst_axis_keys):
    """Copy coordinate references from the destination field to the
    new, regridded field.

    :Parameters:

        f: `Field`
            TODO.

        dst: `Field`
            The destination field.

        dst_axis_keys: sequence of `str`
            The keys of the regridding axes in the destination field.

    :Returns:

        `None`

    """
    dst_data_axes = dst.constructs.data_axes()

    for ref in dst.coordinate_references(todict=True).values():
        axes = set()
        for key in ref.coordinates():
            axes.update(dst_data_axes[key])

        if axes and set(axes).issubset(dst_axis_keys):
            # This coordinate reference's coordinates span the X
            # and/or Y axes
            f.set_coordinate_reference(ref, parent=dst, strict=True)

def regrid_use_bounds(method):
    """Returns whether to use the bounds or not in regridding. This
    is only the case for conservative regridding.

    :Parameters:

        method: `str`
            The regridding method

    :Returns:

        `bool`

    """
    return method in conservative_regridding_methods

def regrid_update_coordinates(
    f,
    dst,
    dst_dict,
    dst_coords,
    src_axis_keys,
    dst_axis_keys,
    cartesian=False,
    dst_axis_sizes=None,
    dst_coords_2D=False,
    dst_coord_order=None,
):
    """Update the coordinates of the new field.

    :Parameters:

        f: `Field`
            TODO. Updated in-place.

        dst: Field or `dict`
            The object containing the destination grid.

        dst_dict: `bool`
            Whether dst is a dictionary.

        dst_coords: sequence
            The destination coordinates.

        src_axis_keys: sequence
            The keys of the regridding axes in the source field.

        dst_axis_keys: sequence
            The keys of the regridding axes in the destination field.

        cartesian: `bool`, optional
            Whether regridding is Cartesian of spherical, False by
            default.

        dst_axis_sizes: sequence, optional
            The sizes of the destination axes.

        dst_coords_2D: `bool`, optional
            Whether the destination coordinates are 2D, currently only
            applies to spherical regridding.

        dst_coord_order: `list`, optional
            A list of lists specifying the ordering of the axes for
            each 2D destination coordinate.

    """
    # NOTE: May be common ground between cartesian and shperical that
    # could save some lines of code.

    # Remove the source coordinates of new field
    for key in f.coordinates(
        filter_by_axis=src_axis_keys, axis_mode="or", todict=True
    ):
        f.del_construct(key)

    domain_axes = f.domain_axes(todict=True)

    if cartesian:
        # Insert coordinates from dst into new field
        if dst_dict:
            for k_s, coord in zip(src_axis_keys, dst_coords):
                domain_axes[k_s].set_size(coord.size)
                f.set_construct(coord, axes=[k_s])
        else:
            axis_map = {
                key_d: key_s
                for key_s, key_d in zip(src_axis_keys, dst_axis_keys)
            }

            for key_d in dst_axis_keys:
                dim = dst.dimension_coordinate(filter_by_axis=(key_d,))
                key_s = axis_map[key_d]
                domain_axes[key_s].set_size(dim.size)
                f.set_construct(dim, axes=[key_s])

            dst_data_axes = dst.constructs.data_axes()

            for aux_key, aux in dst.auxiliary_coordinates(
                filter_by_axis=dst_axis_keys,
                axis_mode="subset",
                todict=True,
            ).items():
                aux_axes = [
                    axis_map[key_d] for key_d in dst_data_axes[aux_key]
                ]
                f.set_construct(aux, axes=aux_axes)
    else:
        # Give destination grid latitude and longitude standard names
        dst_coords[0].standard_name = "longitude"
        dst_coords[1].standard_name = "latitude"

        # Insert 'X' and 'Y' coordinates from dst into new field
        for axis_key, axis_size in zip(src_axis_keys, dst_axis_sizes):
            domain_axes[axis_key].set_size(axis_size)

        if dst_dict:
            if dst_coords_2D:
                for coord, coord_order in zip(dst_coords, dst_coord_order):
                    axis_keys = [
                        src_axis_keys[index] for index in coord_order
                    ]
                    f.set_construct(coord, axes=axis_keys)
            else:
                for coord, axis_key in zip(dst_coords, src_axis_keys):
                    f.set_construct(coord, axes=[axis_key])

        else:
            for src_axis_key, dst_axis_key in zip(
                src_axis_keys, dst_axis_keys
            ):
                dim_coord = dst.dimension_coordinate(
                    filter_by_axis=(dst_axis_key,), default=None
                )
                if dim_coord is not None:
                    f.set_construct(dim_coord, axes=[src_axis_key])

                for aux in dst.auxiliary_coordinates(
                    filter_by_axis=(dst_axis_key,),
                    axis_mode="exact",
                    todict=True,
                ).values():
                    f.set_construct(aux, axes=[src_axis_key])

            for aux_key, aux in dst.auxiliary_coordinates(
                filter_by_axis=dst_axis_keys,
                axis_mode="subset",
                todict=True,
            ).items():
                aux_axes = dst.get_data_axes(aux_key)
                if aux_axes == tuple(dst_axis_keys):
                    f.set_construct(aux, axes=src_axis_keys)
                else:
                    f.set_construct(aux, axes=src_axis_keys[::-1])

    # Copy names of dimensions from destination to source field
    if not dst_dict:
        dst_domain_axes = dst.domain_axes(todict=True)
        for src_axis_key, dst_axis_key in zip(
            src_axis_keys, dst_axis_keys
        ):
            ncdim = dst_domain_axes[dst_axis_key].nc_get_dimension(None)
            if ncdim is not None:
                domain_axes[src_axis_key].nc_set_dimension(ncdim)


def regrid_ppp_mask(new_grid, old_grid):
    """Get the regridded data of frac field as a numpy array from
    the ESMPy fields.

    :Parameters:

        new_grid: `ESMF.Grid`
            TODO.

        old_grid: `ESMF.Grid`
            TODO.

    """
    grid_x = new_grid.mask
    regrid_x = old_grid.mask
    
    if len(grid_x) != len(regrid_x):
        return False
    
    for a, b in zip(grid_x, regrid_x):
        if a is None and b is None:
            continue
        
        if a is not None and b is not None:            
            if a.shape != b.shape:
                return False        
            
            if (a != b).any():
                return False
            
        return False

    
def regrid_ppp_coord(new_grid, old_grid):
    """Get the regridded data of frac field as a numpy array from
        the ESMPy fields.
    
    :Parameters:
    
        new_grid: `ESMF.Grid`
            TODO.

        old_grid: `ESMF.Grid`
            TODO.

    """
    grid_x = new_grid.coord
    regrid_x = old_grid.coord
    
    if len(grid_x) != len(regrid_x):
        return False

    for c, d in zip(grid_x, regrid_x):
        if len(c) != len(d):
            return False
        
        for a, b in zip(a, b):
            if a is None and b is None:
                continue
            
            if a is not None and b is not None:            
                if a.shape != b.shape:
                    return False        
                
                if (a != b).any():
                    return False
                
            return False

    return True
