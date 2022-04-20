from ...functions import (
    _DEPRECATION_ERROR_ATTRIBUTE,
    _DEPRECATION_ERROR_METHOD,
    DeprecationError,
)


class DataClassDeprecationsMixin:
    """Deprecated attributes and methods for the Data class."""

    def __hash__(self):
        """The built-in function `hash`.

        Deprecated at version TODODASK. Consider using the
        `cf.hash_array` function instead.

        Generating the hash temporarily realizes the entire array in
        memory, which may not be possible for large arrays.

        The hash value is dependent on the data-type and shape of the data
        array. If the array is a masked array then the hash value is
        independent of the fill value and of data array values underlying
        any masked elements.

        The hash value may be different if regenerated after the data
        array has been changed in place.

        The hash value is not guaranteed to be portable across versions of
        Python, numpy and cf.

        :Returns:

            `int`
                The hash value.

        **Examples**

        >>> print(d.array)
        [[0 1 2 3]]
        >>> d.hash()
        -8125230271916303273
        >>> d[1, 0] = numpy.ma.masked
        >>> print(d.array)
        [[0 -- 2 3]]
        >>> hash(d)
        791917586613573563
        >>> d.hardmask = False
        >>> d[0, 1] = 999
        >>> d[0, 1] = numpy.ma.masked
        >>> d.hash()
        791917586613573563
        >>> d.squeeze()
        >>> print(d.array)
        [0 -- 2 3]
        >>> hash(d)
        -7007538450787927902
        >>> d.dtype = float
        >>> print(d.array)
        [0.0 -- 2.0 3.0]
        >>> hash(d)
        -4816859207969696442

        """
        _DEPRECATION_ERROR_METHOD(
            self,
            "__hash__",
            message="Consider using 'cf.hash_array' on the underlying "
            "array instead.",
            version="TODODASK",
            removed_at="5.0.0",
        )

    @property
    def Data(self):
        """Deprecated at version 3.0.0, use attribute `data` instead."""
        _DEPRECATION_ERROR_ATTRIBUTE(
            self, "Data", "Use attribute 'data' instead."
        )  # pragma: no cover

    @property
    def dtvarray(self):
        """Deprecated at version 3.0.0."""
        _DEPRECATION_ERROR_ATTRIBUTE(self, "dtvarray")  # pragma: no cover

    def files(self):
        """Deprecated at version 3.4.0, use method `get_` instead."""
        _DEPRECATION_ERROR_METHOD(
            self,
            "files",
            "Use method `get_filenames` instead.",
            version="3.4.0",
        )  # pragma: no cover

    @property
    def unsafe_array(self):
        """Deprecated at version 3.0.0, use `array` attribute
        instead."""
        _DEPRECATION_ERROR_ATTRIBUTE(
            self, "unsafe_array", "Use 'array' attribute instead."
        )  # pragma: no cover

    def expand_dims(self, position=0, i=False):
        """Deprecated at version 3.0.0, use method `insert_dimension`
        instead."""
        _DEPRECATION_ERROR_METHOD(
            self,
            "expand_dims",
            "Use method 'insert_dimension' instead.",
            version="3.0.0",
        )  # pragma: no cover

    def fits_in_one_chunk_in_memory(self, itemsize):
        """Return True if the master array is small enough to be
        retained in memory.

        Deprecated at version TODODASK.

        :Parameters:

            itemsize: `int`
                The number of bytes per word of the master data array.

        :Returns:

            `bool`

        **Examples**

        >>> print(d.fits_one_chunk_in_memory(8))
        False

        """
        _DEPRECATION_ERROR_METHOD(
            self,
            "fits_in_one_chunk_in_memory",
            version="TODODASK",
            removed_at="5.0.0",
        )  # pragma: no cover

    @property
    def ispartitioned(self):
        """True if the data array is partitioned.

        **Examples:**

        >>> d._pmsize
        1
        >>> d.ispartitioned
        False

        >>> d._pmsize
        2
        >>> d.ispartitioned
        False

        """
        _DEPRECATION_ERROR_METHOD("TODODASK")  # pragma: no cover

    def chunk(self, chunksize=None, total=None, omit_axes=None, pmshape=None):
        """Partition the data array.

        :Parameters:

            chunksize: `int`, optional
                The

            total: sequence of `int`, optional

            omit_axes: sequence of `int`, optional

            pmshape: sequence of `int`, optional

        :Returns:

            `None`

        **Examples:**

        >>> d.chunk()
        >>> d.chunk(100000)
        >>> d.chunk(100000, )
        >>> d.chunk(100000, total=[2])
        >>> d.chunk(100000, omit_axes=[3, 4])

        """
        _DEPRECATION_ERROR_METHOD(
            "TODODASK. Use 'rechunk' instead"
        )  # pragma: no cover

    def HDF_chunks(self, *chunks):
        """Get or set HDF chunk sizes.

        The HDF chunk sizes may be used by external code that allows
        `Data` objects to be written to netCDF files.

        Deprecated at version TODODASK and is no longer available. Use
        the methods `nc_clear_hdf5_chunksizes`, `nc_hdf5_chunksizes`,
        and `nc_set_hdf5_chunksizes` instead.

        .. seealso:: `nc_clear_hdf5_chunksizes`, `nc_hdf5_chunksizes`,
                     `nc_set_hdf5_chunksizes`

        :Parameters:

            chunks: `dict` or `None`, *optional*
                Specify HDF chunk sizes.

                When no positional argument is provided, the HDF chunk
                sizes are unchanged.

                If `None` then the HDF chunk sizes for each dimension
                are cleared, so that the HDF default chunk size value
                will be used when writing data to disk.

                If a `dict` then it defines for a subset of the
                dimensions, defined by their integer positions, the
                corresponding HDF chunk sizes. The HDF chunk sizes are
                set as a number of elements along the dimension.

        :Returns:

            `dict`
                The HDF chunks for each dimension prior to the change,
                or the current HDF chunks if no new values are
                specified. A value of `None` is an indication that the
                default chunk size should be used for that dimension.

        **Examples**

        >>> d = cf.Data(np.arange(30).reshape(5, 6))
        >>> d.HDF_chunks()
        {0: None, 1: None}
        >>> d.HDF_chunks({1: 2})
        {0: None, 1: None}
        >>> d.HDF_chunks()
        {0: None, 1: 2}
        >>> d.HDF_chunks({1:None})
        {0: None, 1: 2}
        >>> d.HDF_chunks()
        {0: None, 1: None}
        >>> d.HDF_chunks({0: 3, 1: 6})
        {0: None, 1: None}
        >>> d.HDF_chunks()
        {0: 3, 1: 6}
        >>> d.HDF_chunks({1: 4})
        {0: 3, 1: 6}
        >>> d.HDF_chunks()
        {0: 3, 1: 4}
        >>> d.HDF_chunks({1: 999})
        {0: 3, 1: 4}
        >>> d.HDF_chunks()
        {0: 3, 1: 999}
        >>> d.HDF_chunks(None)
        {0: 3, 1: 999}
        >>> d.HDF_chunks()
        {0: None, 1: None}

        """
        _DEPRECATION_ERROR_METHOD(
            self,
            "HDF_chunks",
            message="Use the methods 'nc_clear_hdf5_chunksizes', "
            "'nc_hdf5_chunksizes', and 'nc_set_hdf5_chunksizes' "
            "instead.",
            version="TODODASK",
            removed_at="5.0.0",
        )  # pragma: no cover

    @property
    def ismasked(self):
        """True if the data array has any masked values.

        TODODASK

        **Examples:**

        >>> d = cf.Data([[1, 2, 3], [4, 5, 6]])
        >>> print(d.ismasked)
        False
        >>> d[0, ...] = cf.masked
        >>> d.ismasked
        True

        """
        _DEPRECATION_ERROR_METHOD(
            "TODODASK use is_masked instead"
        )  # pragma: no cover

    @property
    def varray(self):
        """A numpy array view the data array.

        Note that making changes to elements of the returned view changes
        the underlying data.

        .. seealso:: `array`, `datetime_array`

        **Examples:**

        >>> a = d.varray
        >>> type(a)
        <type 'numpy.ndarray'>
        >>> a
        array([0, 1, 2, 3, 4])
        >>> a[0] = 999
        >>> d.varray
        array([999, 1, 2, 3, 4])

        """
        _DEPRECATION_ERROR_METHOD("TODODASK")  # pragma: no cover

    def add_partitions(self, extra_boundaries, pdim):
        """Add partition boundaries.

        :Parameters:

            extra_boundaries: `list` of `int`
                The boundaries of the new partitions.

            pdim: `str`
                The name of the axis to have the new partitions.

        :Returns:

            `None`

        **Examples:**

        >>> d.add_partitions(    )

        """
        _DEPRECATION_ERROR_METHOD(
            "TODODASK Consider using rechunk instead"
        )  # pragma: no cover

    @staticmethod
    def mask_fpe(*arg):
        """Masking of floating-point errors in the results of arithmetic
        operations.

        Deprecated at version TODODASK. It is currently not possible
        to control how floating-point errors are handled, due to the
        use of `dask` for handling all array manipulations. This may
        change in the future (see
        https://github.com/dask/dask/issues/3245 for more details).

        If masking is allowed then only floating-point errors which would
        otherwise be raised as `FloatingPointError` exceptions are
        masked. Whether `FloatingPointError` exceptions may be raised is
        determined by `cf.Data.seterr`.

        If called without an argument then the current behaviour is
        returned.

        Note that if the raising of `FloatingPointError` exceptions has
        suppressed then invalid values in the results of arithmetic
        operations may be subsequently converted to masked values with the
        `mask_invalid` method.

        .. seealso:: `cf.Data.seterr`, `mask_invalid`

        :Parameters:

            arg: `bool`, optional
                The new behaviour. True means that `FloatingPointError`
                exceptions are suppressed and replaced with masked
                values. False means that `FloatingPointError` exceptions
                are raised. The default is not to change the current
                behaviour.

        :Returns:

            `bool`
                The behaviour prior to the change, or the current
                behaviour if no new value was specified.

        **Examples:**

        >>> d = cf.Data([0., 1])
        >>> e = cf.Data([1., 2])

        >>> old = cf.Data.mask_fpe(False)
        >>> old = cf.Data.seterr('raise')
        >>> e/d
        FloatingPointError: divide by zero encountered in divide
        >>> e**123456
        FloatingPointError: overflow encountered in power

        >>> old = cf.Data.mask_fpe(True)
        >>> old = cf.Data.seterr('raise')
        >>> e/d
        <CF Data: [--, 2.0] >
        >>> e**123456
        <CF Data: [1.0, --] >

        >>> old = cf.Data.mask_fpe(True)
        >>> old = cf.Data.seterr('ignore')
        >>> e/d
        <CF Data: [inf, 2.0] >
        >>> e**123456
        <CF Data: [1.0, inf] >

        """
        raise DeprecationError(
            "Data method 'mask_fpe' has been deprecated at version TODODASK "
            "and is not available.\n\n"
            "It is currently not possible to control how floating-point errors "
            "are handled, due to the use of `dask` for handling all array "
            "manipulations. This may change in the future (see "
            "https://github.com/dask/dask/issues/3245 for more details)."
        )

    def partition_boundaries(self):
        """Return the partition boundaries for each partition matrix
        dimension.

        :Returns:

            `dict`

        **Examples:**

        """
        _DEPRECATION_ERROR_METHOD(
            "TODODASK - consider using 'chunks' instead"
        )  # pragma: no cover
