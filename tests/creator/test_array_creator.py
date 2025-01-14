# Copyright 2021 TileDB Inc.
# Licensed under the MIT License.
import numpy as np
import pytest

import tiledb
from tiledb.cf.creator import ArrayCreator, DataspaceRegistry, SharedDim


class TestArrayCreatorSparseExample1:
    @pytest.fixture
    def array_creator(self):
        registry = DataspaceRegistry()
        SharedDim(registry, "row", (0, 63), np.uint32)
        SharedDim(registry, "col", (0, 31), np.uint32)
        creator = ArrayCreator(
            registry,
            "array",
            ("row", "col"),
            sparse=True,
            coords_filters=tiledb.FilterList([tiledb.ZstdFilter(level=6)]),
            offsets_filters=tiledb.FilterList([tiledb.Bzip2Filter()]),
            tiles=(32, 16),
            dim_filters={
                "row": tiledb.FilterList([tiledb.ZstdFilter(level=1)]),
                "col": tiledb.FilterList([tiledb.GzipFilter(level=5)]),
            },
        )
        attr_filters = tiledb.FilterList([tiledb.ZstdFilter(level=7)])
        creator.add_attr_creator("enthalpy", np.dtype("float64"), filters=attr_filters)
        return creator

    def test_repr(self, array_creator):
        assert isinstance(repr(array_creator), str)

    def test_create(self, tmpdir, array_creator):
        uri = str(tmpdir.mkdir("output").join("sparse_example_1"))
        array_creator.create(uri)
        assert tiledb.object_type(uri) == "array"

    def test_dim_filters(self, array_creator):
        filters = {
            dim_creator.name: dim_creator.filters
            for dim_creator in array_creator.domain_creator
        }
        assert filters == {
            "row": tiledb.FilterList([tiledb.ZstdFilter(level=1)]),
            "col": tiledb.FilterList([tiledb.GzipFilter(level=5)]),
        }

    def test_tiles(self, array_creator):
        tiles = tuple(dim_creator.tile for dim_creator in array_creator.domain_creator)
        assert tiles == (32, 16)

    def test_nattr(self, array_creator):
        nattr = array_creator.nattr
        assert nattr == 1


class TestArrayCreatorDense1:
    @pytest.fixture
    def array_creator(self):
        registry = DataspaceRegistry()
        SharedDim(registry, "row", (0, 63), np.uint32)
        creator = ArrayCreator(registry, "array", "row")
        attr_filters = tiledb.FilterList([tiledb.ZstdFilter(level=7)])
        creator.add_attr_creator("enthalpy", np.dtype("float64"), filters=attr_filters)
        return creator

    def test_repr(self, array_creator):
        assert isinstance(repr(array_creator), str)

    def test_create(self, tmpdir, array_creator):
        uri = str(tmpdir.mkdir("output").join("dense_example_1"))
        array_creator.create(uri)
        assert tiledb.object_type(uri) == "array"

    def test_dim_filters(self, array_creator):
        filters = {
            dim_creator.name: dim_creator.filters
            for dim_creator in array_creator.domain_creator
        }
        assert filters == {"row": None}

    def test_tiles(self, array_creator):
        tiles = tuple(dim_creator.tile for dim_creator in array_creator.domain_creator)
        assert tiles == (None,)

    def test_nattr(self, array_creator):
        nattr = array_creator.nattr
        assert nattr == 1


def test_rename_attr():
    registry = DataspaceRegistry()
    SharedDim(registry, "pressure", (0.0, 1000.0), np.float64)
    SharedDim(registry, "temperature", (-200.0, 200.0), np.float64)
    array_creator = ArrayCreator(
        registry, "array", ("pressure", "temperature"), sparse=True
    )
    array_creator.add_attr_creator("enthalp", np.dtype("float64"))
    attr_names = tuple(attr_creator.name for attr_creator in array_creator)
    assert attr_names == ("enthalp",)
    array_creator.attr_creator("enthalp").name = "enthalpy"
    attr_names = tuple(attr_creator.name for attr_creator in array_creator)
    assert attr_names == ("enthalpy",)


def test_array_no_dim_error():
    with pytest.raises(ValueError):
        ArrayCreator(DataspaceRegistry(), "array", [])


def test_repeating_name_error():
    with pytest.raises(ValueError):
        registry = DataspaceRegistry()
        SharedDim(registry, "x", (1, 4), np.int32)
        ArrayCreator(registry, "array", ["x", "x"])


def test_name_exists_error():
    registry = DataspaceRegistry()
    SharedDim(registry, "pressure", (0.0, 1000.0), np.float64)
    SharedDim(registry, "temperature", (-200.0, 200.0), np.float64)
    creator = ArrayCreator(registry, "array", ("pressure", "temperature"), sparse=True)
    creator.add_attr_creator("enthalpy", np.float64)
    with pytest.raises(ValueError):
        creator.add_attr_creator("enthalpy", np.float64)


def test_dim_name_exists_error():
    registry = DataspaceRegistry()
    SharedDim(registry, "pressure", (0.0, 1000.0), np.float64)
    SharedDim(registry, "temperature", (-200.0, 200.0), np.float64)
    creator = ArrayCreator(registry, "array", ("pressure", "temperature"), sparse=True)
    creator.add_attr_creator("enthalpy", np.float64)
    with pytest.raises(ValueError):
        creator.add_attr_creator("pressure", np.float64)


def test_bad_tiles_error():
    registry = DataspaceRegistry()
    SharedDim(registry, "row", (0, 63), np.uint32)
    SharedDim(registry, "col", (0, 31), np.uint32)
    with pytest.raises(ValueError):
        ArrayCreator(registry, "array", ("row", "col"), tiles=(4,))


def test_to_schema_no_attrs_error():
    registry = DataspaceRegistry()
    SharedDim(registry, "row", (0, 63), np.uint32)
    SharedDim(registry, "col", (0, 31), np.uint32)
    creator = ArrayCreator(registry, "array", ("row", "col"))
    with pytest.raises(ValueError):
        creator.to_schema()
