import cfdm

from .query import Query


class Constructs(cfdm.Constructs):
    """A container for metadata constructs.

    The following metadata constructs can be included:

    * auxiliary coordinate constructs
    * coordinate reference constructs
    * cell measure constructs
    * dimension coordinate constructs
    * domain ancillary constructs
    * domain axis constructs
    * cell method constructs
    * field ancillary constructs

    The container may be used by `Field` and `Domain` instances. In
    the latter case cell method and field ancillary constructs must be
    flagged as "ignored" (see the *_ignore* parameter).

    The container is like a dictionary in many ways, in that it stores
    key/value pairs where the key is the unique construct key with
    corresponding metadata construct value, and provides some of the
    usual dictionary methods.

    **Calling**

    Calling a `Constructs` instance selects metadata constructs by
    identity and is an alias for the `filter_by_identity` method. For
    example, to select constructs that have an identity of
    'air_temperature': ``d = c('air_temperature')``.

    .. versionadded:: 3.0.0

    """

    def __repr__(self):
        """Called by the `repr` built-in function.

        x.__repr__() <==> repr(x)

        """
        return super().__repr__().replace("<", "<CF ", 1)

    @classmethod
    def _matching_values(cls, value0, construct, value1, basic=False):
        """Whether two values match according to equality on a given
        construct.

        The definition of "match" depends on the types of *value0* and
        *value1*.

        :Parameters:

            value0:
                The first value to be matched.

            construct:
                The construct whose `_equals` method is used to
                determine whether values can be considered to match.

            value1:
                The second value to be matched.

            basic: `bool`
                If True then value0 and value1 will be compared with
                the basic ``==`` operator.

        :Returns:

            `bool`
                Whether or not the two values match.

        """
        if isinstance(value0, Query):
            return value0.evaluate(value1)

        return super()._matching_values(value0, construct, value1, basic=basic)

    #     def domain_axis_key(self, identity, default=ValueError()):
    #         '''Return the key of the domain axis construct that is spanned by 1-d
    # coordinate constructs.
    #
    # .. versionadded:: 3.0.0
    #
    # :Parameters:
    #
    #     identity:
    #
    #         Select the 1-d coordinate constructs that have the given
    #         identity.
    #
    #         An identity is specified by a string (e.g. ``'latitude'``,
    #         ``'long_name=time'``, etc.); or a compiled regular expression
    #         (e.g. ``re.compile('^atmosphere')``), for which all constructs
    #         whose identities match (via `re.search`) are selected.
    #
    #         Each coordinate construct has a number of identities, and is
    #         selected if any of them match any of those provided. A
    #         construct's identities are those returned by its `!identities`
    #         method. In the following example, the construct ``x`` has four
    #         identities:
    #
    #            >>> x.identities()
    #            ['time', 'long_name=Time', 'foo=bar', 'ncvar%T']
    #
    #         In addition, each construct also has an identity based its
    #         construct key (e.g. ``'key%dimensioncoordinate2'``)
    #
    #         Note that in the output of a `print` call or `!dump` method, a
    #         construct is always described by one of its identities, and so
    #         this description may always be used as an *identity* argument.
    #
    #     default: optional
    #         Return the value of the *default* parameter if a domain axis
    #         construct can not be found. If set to an `Exception` instance
    #         then it will be raised instead.
    #
    # :Returns:
    #
    #     `str`
    #         The key of the domain axis construct that is spanned by the
    #         data of the selected 1-d coordinate constructs.
    #
    # **Examples:**
    #
    # TODO
    #
    #         '''
    #         # Try for index
    #         try:
    #             da_key = self.get_data_axes(default=None)[identity]
    #         except TypeError:
    #             pass
    #         except IndexError:
    #             return self._default(
    #                 default,
    #                 "Index does not exist for field construct data dimenions")
    #         else:
    #             identity = da_key
    #
    #         domain_axes = self.domain_axes(identity)
    #         if len(domain_axes) == 1:
    #             # identity is a unique domain axis construct identity
    #             da_key = domain_axes.key()
    #         else:
    #             # identity is not a unique domain axis construct identity
    #             da_key = self.domain_axis_key(identity, default=default)
    #
    #         if key:
    #             return da_key
    #
    #         return self.constructs[da_key]

#    def filter_by_identity(self, *identities, view=False,
#                           todict=False, cache=None, **identities_kwargs):
#        """Select metadata constructs by identity.
#
#        .. versionadded:: 3.0.0
#
#        .. seealso:: `filter_by_axis`, `filter_by_data`, `filter_by_key`,
#                     `filter_by_measure`, `filter_by_method`,
#                     `filter_by_naxes`, `filter_by_ncdim`,
#                     `filter_by_ncvar`, `filter_by_property`,
#                     `filter_by_size`, `filter_by_type`,
#                     `filters_applied`, `inverse_filter`, `unfilter`
#
#        :Parameters:
#
#            identities: optional
#                Select constructs that have any of the given identities or
#                construct keys.
#
#                An identity is specified by a string (e.g. ``'latitude'``,
#                ``'long_name=time'``, etc.); or a compiled regular
#                expression (e.g. ``re.compile('^atmosphere')``), for which
#                all constructs whose identities match (via `re.search`)
#                are selected.
#
#                If no identities are provided then all constructs are selected.
#
#                Each construct has a number of identities, and is selected
#                if any of them match any of those provided. A construct's
#                identities are those returned by its `!identities`
#                method. In the following example, the construct ``x`` has
#                five identities:
#
#                   >>> x.identities()
#                   ['time', 'long_name=Time', 'foo=bar', 'T', 'ncvar%t']
#
#                A construct key may optionally have the ``'key%'``
#                prefix. For example ``'dimensioncoordinate2'`` and
#                ``'key%dimensioncoordinate2'`` are both acceptable keys.
#
#                Note that the identifiers of a metadata construct in the
#                output of a `print` or `!dump` call are always one of its
#                identities, and so may always be used as an *identities*
#                argument.
#
#                Domain axis constructs may also be identified by their
#                position in the field construct's data array. Positions
#                are specified by either integers.
#
#                .. note:: This is an extension to the functionality of
#                          `cfdm.Constucts.filter_by_identity`.
#
#            {{view: `bool`, optional}}
#
#            {{todict: `bool`, optional}}
#
#            {{cache: optional}}
#
#            identities_kwargs: optional
#                Additional parameters for configuring each construct's
#                `identities` method. By default ``generator=True`` is
#                passed by default, and ``ctype`` is inferred from the
#                *identities* parameter.
#
#                .. versionadded:: 3.9.0
#
#        :Returns:
#
#            `Constructs`
#                The selected constructs and their construct keys.
#
#        **Examples:**
#
#        Select constructs that have a "standard_name" property of
#        'latitude':
#
#        >>> d = c.filter_by_identity('latitude')
#
#        Select constructs that have a "long_name" property of 'Height':
#
#        >>> d = c.filter_by_identity('long_name=Height')
#
#        Select constructs that have a "standard_name" property of
#        'latitude' or a "foo" property of 'bar':
#
#        >>> d = c.filter_by_identity('latitude', 'foo=bar')
#
#        Select constructs that have a netCDF variable name of 'time':
#
#        >>> d = c.filter_by_identity('ncvar%time')
#
#        """
#        if cache is not None:
#            return cache
#            
#        # Allow keys without the 'key%' prefix
#        for n, identity in enumerate(identities):
#            if identity in self:
#                identities = list(identities)
#                identities[n] = "key%" + identity
#                break
#
#        ctype = [i for i in "XTYZ" if i in identities]
#
#        return super().filter_by_identity(
#            identities, todict=todict,
#            _config={"identities_kwargs": {"ctype": ctype},
#             "bypass": lambda x: x in ctype}
#        )
    
    @classmethod
    def _filter_by_identity(cls, self, *identities, todict=False,
                            _config={}):
        """TODO.

        """
        # Allow keys without the 'key%' prefix
        for n, identity in enumerate(identities):
            if identity in self:
                identities = list(identities)
                identities[n] = "key%" + identity
                break

        ctype = [i              for i in "XTYZ"      if i in identities]
        
        config = {    "identities_kwargs": {"ctype": ctype}}

        if ctype:
            # Exclude a ctype from the short circuit test
            config["short_circuit_test"] = (
                lambda x: (
                    x not in ctype
                    and "=" not in x
                    and ":" not in x
                    and "%" not in x
                )
            )
                
        config.update(_config)

        return super()._filter_by_identity(
            self,
            *identities,
            todict=todict,
            cache=cache,
            _config=config
        )
