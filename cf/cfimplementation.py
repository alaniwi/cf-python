import cfdm

from . import (
    AuxiliaryCoordinate,
    Bounds,
    CellMeasure,
    CellMethod,
    CoordinateConversion,
    CoordinateReference,
    Count,
    Datum,
    DimensionCoordinate,
    Domain,
    DomainAncillary,
    DomainAxis,
    Field,
    FieldAncillary,
    Index,
    InteriorRing,
    List,
    NodeCountProperties,
    PartNodeCountProperties,
)
from .data import (
    Data,
    GatheredArray,
    NetCDFArray,
    RaggedContiguousArray,
    RaggedIndexedArray,
    RaggedIndexedContiguousArray,
)
from .functions import CF


class CFImplementation(cfdm.CFDMImplementation):
    """A container for the CF data model implementation for `cf`.

    .. versionadded:: 3.0.0

    """

    def set_construct(self, parent, construct, axes=None, copy=True, **kwargs):
        """Insert a construct into a field or domain.

        Does not attempt to conform cell method nor coordinate
        reference constructs, as that has been handled by `cfdm`.

        .. versionadded:: TODODASKVER

        :Parameters:

            parent: `Field` or `Domain`
               On what to set the construct

            construct:
                The construct to set.

            axes: `tuple` or `None`, optional
                The construct domain axes, if applicable.

            copy: `bool`, optional
                Whether or not to set a copy of *construct*.

            kwargs: optional
                Additional parameters to the `set_construct` method of
                *parent*.

        :Returns:

            `str`
                The construct identifier.

        """
        kwargs.setdefault("conform", False)
        return super().set_construct(
            parent, construct, axes=axes, copy=copy, **kwargs
        )


_implementation = CFImplementation(
    cf_version=CF(),
    AuxiliaryCoordinate=AuxiliaryCoordinate,
    CellMeasure=CellMeasure,
    CellMethod=CellMethod,
    CoordinateReference=CoordinateReference,
    DimensionCoordinate=DimensionCoordinate,
    Domain=Domain,
    DomainAncillary=DomainAncillary,
    DomainAxis=DomainAxis,
    Field=Field,
    FieldAncillary=FieldAncillary,
    Bounds=Bounds,
    InteriorRing=InteriorRing,
    CoordinateConversion=CoordinateConversion,
    Datum=Datum,
    List=List,
    Index=Index,
    Count=Count,
    NodeCountProperties=NodeCountProperties,
    PartNodeCountProperties=PartNodeCountProperties,
    Data=Data,
    GatheredArray=GatheredArray,
    NetCDFArray=NetCDFArray,
    RaggedContiguousArray=RaggedContiguousArray,
    RaggedIndexedArray=RaggedIndexedArray,
    RaggedIndexedContiguousArray=RaggedIndexedContiguousArray,
)


def implementation():
    """Return a container for the CF data model implementation.

    .. versionadded:: 3.1.0

    .. seealso:: `cf.example_field`, `cf.read`, `cf.write`

    :Returns:

        `CFImplementation`
            A container for the CF data model implementation.

    **Examples**

    >>> i = cf.implementation()
    >>> i
    <CFDMImplementation: >
    >>> i.classes()
    {'AuxiliaryCoordinate': cf.auxiliarycoordinate.AuxiliaryCoordinate,
     'CellMeasure': cf.cellmeasure.CellMeasure,
     'CellMethod': cf.cellmethod.CellMethod,
     'CoordinateReference': cf.coordinatereference.CoordinateReference,
     'DimensionCoordinate': cf.dimensioncoordinate.DimensionCoordinate,
     'Domain': cf.domain.Domain,
     'DomainAncillary': cf.domainancillary.DomainAncillary,
     'DomainAxis': cf.domainaxis.DomainAxis,
     'Field': cf.field.Field,
     'FieldAncillary': cf.fieldancillary.FieldAncillary,
     'Bounds': cf.bounds.Bounds,
     'InteriorRing': cf.interiorring.InteriorRing,
     'CoordinateConversion': cf.coordinateconversion.CoordinateConversion,
     'Datum': cf.datum.Datum,
     'Data': cf.data.data.Data,
     'GatheredArray': cf.data.gatheredarray.GatheredArray,
     'NetCDFArray': cf.data.netcdfarray.NetCDFArray,
     'RaggedContiguousArray': cf.data.raggedcontiguousarray.RaggedContiguousArray,
     'RaggedIndexedArray': cf.data.raggedindexedarray.RaggedIndexedArray,
     'RaggedIndexedContiguousArray': cf.data.raggedindexedcontiguousarray.RaggedIndexedContiguousArray,
     'List': cf.list.List,
     'Count': cf.count.Count,
     'Index': cf.index.Index,
     'NodeCountProperties': cf.nodecountproperties.NodeCountProperties,
     'PartNodeCountProperties': cf.partnodecountproperties.PartNodeCountProperties}

    """
    return _implementation.copy()
