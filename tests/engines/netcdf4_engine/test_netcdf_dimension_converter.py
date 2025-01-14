# Copyright 2021 TileDB Inc.
# Licensed under the MIT License.
import numpy as np
import pytest

from tiledb.cf.creator import DataspaceRegistry
from tiledb.cf.engines.netcdf4_engine import (
    NetCDF4CoordToDimConverter,
    NetCDF4DimToDimConverter,
    NetCDF4ScalarToDimConverter,
)

netCDF4 = pytest.importorskip("netCDF4")


class TestNetCDFCoordToDimConverterUnlimCoord:
    """This class tests the NetCDFCoordToDimConverter class for a simple NetCDF
    coordinate.

    This test use an example NetCDF file with the following root group:

    Dimensions:
      value(unlim)

    Variables:
      float64 value(value)
    """

    def test_class_properties(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dataset.createDimension("value")
            var = dataset.createVariable("value", np.float64, ("value",))
            var[:] = np.random.rand((8))
            registry = DataspaceRegistry()
            converter = NetCDF4CoordToDimConverter.from_netcdf(registry, var)
            assert converter.name == var.name
            assert converter.domain is None
            assert converter.dtype == np.dtype(np.float64)
            assert isinstance(repr(converter), str)
            assert converter.input_name == var.name
            assert converter.input_dtype == np.dtype(np.float64)

    def test_get_values(self):
        data = np.random.rand((8))
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dataset.createDimension("value")
            var = dataset.createVariable("value", np.float64, ("value",))
            var[:] = data
            registry = DataspaceRegistry()
            converter = NetCDF4CoordToDimConverter.from_netcdf(registry, var)
            result = converter.get_values(dataset, sparse=True)
        assert np.array_equal(result, data)

    def test_get_values_no_data(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dataset.createDimension("value")
            var = dataset.createVariable("value", np.float64, ("value",))
            registry = DataspaceRegistry()
            converter = NetCDF4CoordToDimConverter.from_netcdf(registry, var)
            result = converter.get_values(dataset, sparse=True)
            assert result is None

    def test_get_values_dense_error(self):
        data = np.random.rand((8))
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dataset.createDimension("value")
            var = dataset.createVariable("value", np.float64, ("value",))
            var[:] = data
            registry = DataspaceRegistry()
            converter = NetCDF4CoordToDimConverter.from_netcdf(registry, var)
            with pytest.raises(NotImplementedError):
                converter.get_values(dataset, sparse=False)

    def test_get_value_no_variable_error(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dataset.createDimension("value")
            var = dataset.createVariable("value", np.float64, ("value",))
            registry = DataspaceRegistry()
            converter = NetCDF4CoordToDimConverter.from_netcdf(registry, var)
            group = dataset.createGroup("group1")
            with pytest.raises(KeyError):
                converter.get_values(group, sparse=True)

    def test_get_value_wrong_ndim_error(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dataset.createDimension("value")
            var = dataset.createVariable("value", np.float64, ("value",))
            registry = DataspaceRegistry()
            converter = NetCDF4CoordToDimConverter.from_netcdf(registry, var)
            group = dataset.createGroup("group1")
            group.createVariable("value", np.float64, tuple())
            with pytest.raises(ValueError):
                converter.get_values(group, sparse=True)


class TestNetCDFDimToDimConverterSimpleDim:
    """This class tests the NetCDFDimToDimConverter class for a simple NetCDF
    dimension.

    This test uses an example NetCDF file with a dimension row(8) in the root
    group.
    """

    def test_class_properties(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", 8)
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 1000, np.uint64
            )
            assert isinstance(repr(converter), str)
            assert converter.input_name == dim.name
            assert converter.input_size == dim.size
            assert not converter.is_unlimited
            assert converter.name == dim.name
            assert converter.domain == (0, dim.size - 1)
            assert converter.dtype == np.uint64

    @pytest.mark.parametrize(
        "sparse,values", [(True, np.arange(0, 8)), (False, slice(8))]
    )
    def test_get_values(self, sparse, values):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", 8)
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 1000, np.uint64
            )
            result = converter.get_values(dataset, sparse=sparse)
            assert np.array_equal(result, values)

    @pytest.mark.parametrize(
        "sparse,values", [(True, np.arange(0, 8)), (False, slice(8))]
    )
    def test_get_values_from_subgroup(self, sparse, values):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", 8)
            group = dataset.createGroup("group1")
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 1000, np.uint64
            )
            result = converter.get_values(group, sparse=sparse)
            assert np.array_equal(result, values)

    def test_no_dim_error(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", 8)
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 1000, np.uint64
            )
        with netCDF4.Dataset("no_dims.nc", mode="w", diskless=True) as dataset:
            group = dataset.createGroup("group")
            with pytest.raises(KeyError):
                converter.get_values(group, sparse=False)


class TestNetCDFDimToDimConverterUnlimitedDim:
    """This class tests the NetCDFDimToDimConverter class for an unlimited
    NetCDF dimension."""

    def test_class_properties(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", None)
            max_size = 100
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, max_size, np.uint64
            )
            assert isinstance(repr(converter), str)
            assert converter.input_name == dim.name
            assert converter.input_size == dim.size
            assert converter.is_unlimited
            assert converter.name == dim.name
            assert converter.domain == (0, max_size - 1)
            assert converter.dtype == np.uint64

    @pytest.mark.parametrize("sparse", [True, False])
    def test_get_values_no_data(self, sparse):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", None)
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 100, np.uint64
            )
            with pytest.raises(ValueError):
                converter.get_values(dataset, sparse=sparse)

    @pytest.mark.parametrize(
        "sparse,values", [(True, np.arange(0, 10)), (False, slice(10))]
    )
    def test_get_values(self, sparse, values):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", None)
            var = dataset.createVariable("data", np.int32, ("row",))
            size = 10
            var[:] = np.arange(size)
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 100, np.uint64
            )
            result = converter.get_values(dataset, sparse=sparse)
            assert np.array_equal(result, values)

    def test_data_too_large_error(self):
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            dim = dataset.createDimension("row", None)
            var = dataset.createVariable("data", np.int32, ("row",))
            size = 11
            var[:] = np.arange(size)
            registry = DataspaceRegistry()
            converter = NetCDF4DimToDimConverter.from_netcdf(
                registry, dim, 10, np.uint64
            )
            with pytest.raises(IndexError):
                converter.get_values(dataset, sparse=True)


class TestNetCDFScalarToDimConverter:
    def test_class_properties(self):
        registry = DataspaceRegistry()
        converter = NetCDF4ScalarToDimConverter.create(registry, "__scalars", np.uint32)
        assert converter.name == "__scalars"
        assert converter.domain == (0, 0)
        assert converter.dtype == np.dtype(np.uint32)

    def test_repr(self):
        registry = DataspaceRegistry()
        converter = NetCDF4ScalarToDimConverter.create(registry, "__scalars", np.uint32)
        isinstance(repr(converter), str)

    @pytest.mark.parametrize(
        "sparse,values", [(True, np.arange(0, 1)), (False, slice(1))]
    )
    def test_ret_values(self, sparse, values):
        registry = DataspaceRegistry()
        converter = NetCDF4ScalarToDimConverter.create(registry, "__scalars", np.uint32)
        with netCDF4.Dataset("example.nc", mode="w", diskless=True) as dataset:
            result = converter.get_values(dataset, sparse=sparse)
            assert np.array_equal(result, values)
