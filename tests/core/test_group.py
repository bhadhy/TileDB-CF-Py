# Copyright 2021 TileDB Inc.
# Licensed under the MIT License.
import numpy as np
import pytest

import tiledb
from tiledb.cf import ArrayMetadata, AttrMetadata, Group, GroupSchema

_row = tiledb.Dim(name="rows", domain=(1, 4), tile=4, dtype=np.uint64)
_col = tiledb.Dim(name="cols", domain=(1, 4), tile=4, dtype=np.uint64)


_attr_a = tiledb.Attr(name="a", dtype=np.uint64)
_attr_b = tiledb.Attr(name="b", dtype=np.float64)
_attr_c = tiledb.Attr(name="c", dtype=np.dtype("U"))
_array_schema_1 = tiledb.ArraySchema(
    domain=tiledb.Domain(_row, _col),
    attrs=[_attr_a],
)
_array_schema_2 = tiledb.ArraySchema(
    domain=tiledb.Domain(_row),
    sparse=True,
    attrs=[_attr_b, _attr_c],
)
_array_schema_3 = tiledb.ArraySchema(
    domain=tiledb.Domain(_row, _col),
    attrs=[_attr_c],
)


class TestCreateGroup:

    _metadata_schema = _array_schema_1
    _array_schemas = [
        ("A1", _array_schema_1),
        ("A2", _array_schema_2),
    ]
    _group_schema = GroupSchema(_array_schemas, _metadata_schema)
    _key = None

    @pytest.fixture(scope="class")
    def group_uri(self, tmpdir_factory):
        """Creates a TileDB Group from GroupSchema and returns scenario dict."""
        uri = str(tmpdir_factory.mktemp("group1"))
        ctx = None
        Group.create(uri, self._group_schema, self._key, ctx)
        return uri

    def test_array_schemas(self, group_uri):
        uri = group_uri
        assert tiledb.object_type(uri) == "group"
        for name, schema in self._array_schemas:
            array_uri = group_uri + "/" + name
            assert tiledb.ArraySchema.load(array_uri, key=self._key) == schema


class TestCreateVirtualGroup:

    _metadata_schema = _array_schema_1
    _array_schemas = [
        ("A1", _array_schema_1),
        ("A2", _array_schema_2),
    ]
    _group_schema = GroupSchema(_array_schemas, _metadata_schema)
    _key = None

    @pytest.fixture(scope="class")
    def group_uri(self, tmpdir_factory):
        """Creates a TileDB Group from GroupSchema and returns scenario dict."""
        uri = str(tmpdir_factory.mktemp("group1"))
        ctx = None
        with pytest.deprecated_call():
            Group.create_virtual(uri, self._group_schema, self._key, ctx)
        return uri

    def test_array_schemas(self, group_uri):
        uri = group_uri
        assert tiledb.ArraySchema.load(uri, key=self._key) == self._metadata_schema
        for name, schema in self._array_schemas:
            array_uri = group_uri + "_" + name
            assert tiledb.ArraySchema.load(array_uri, key=self._key) == schema


class TestNotTileDBURI:
    @pytest.fixture(scope="class")
    def empty_uri(self, tmpdir_factory):
        """Create an empty directory and return URI."""
        return str(tmpdir_factory.mktemp("empty"))

    def test_not_group_exception(self, empty_uri):
        with pytest.raises(ValueError):
            Group(empty_uri)


class TestSimpleGroup:

    _metadata_schema = tiledb.ArraySchema(
        domain=tiledb.Domain(
            tiledb.Dim(name="rows", domain=(1, 4), tile=2, dtype=np.uint64)
        ),
        attrs=[tiledb.Attr(name="a", dtype=np.uint64)],
        sparse=True,
    )

    @pytest.fixture(scope="class")
    def group_uri(self, tmpdir_factory):
        uri = str(tmpdir_factory.mktemp("group1"))
        Group.create(uri, GroupSchema(None, self._metadata_schema))
        return uri

    def test_has_metadata(self, group_uri):
        with Group(group_uri) as group:
            assert isinstance(group, Group)
            assert group.has_metadata_array
            assert group.meta is not None


class TestGroupWithArrays:

    _metadata_schema = tiledb.ArraySchema(
        domain=tiledb.Domain(
            tiledb.Dim(name="rows", domain=(1, 4), tile=2, dtype=np.uint64)
        ),
        attrs=[tiledb.Attr(name="a", dtype=np.uint64)],
        sparse=True,
    )

    _A1_data = np.array(
        ([1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]), dtype=np.uint64
    )

    @pytest.fixture(scope="class")
    def group_uri(self, tmpdir_factory):
        uri = str(tmpdir_factory.mktemp("simple_group"))
        tiledb.group_create(uri)
        tiledb.Array.create(uri + "/A1", _array_schema_1)
        with tiledb.DenseArray(uri + "/A1", mode="w") as array:
            array[:] = self._A1_data
        tiledb.Array.create(uri + "/A2", _array_schema_2)
        tiledb.Array.create(uri + "/A3", _array_schema_3)
        filesystem = tiledb.VFS()
        filesystem.create_dir(uri + "/empty_dir")
        return uri

    def test_open_array_from_group(self, group_uri):
        with Group(group_uri, array="A1") as group:
            array = group.array
            assert isinstance(array, tiledb.Array)
            assert array.mode == "r"
            assert np.array_equal(array[:, :]["a"], self._A1_data)

    def test_array_metadata(self, group_uri):
        with Group(group_uri, array="A1") as group:
            isinstance(group.array_metadata, ArrayMetadata)

    def test_attr_metadata_with_attr(self, group_uri):
        with Group(group_uri, attr="a") as group:
            isinstance(group.attr_metadata, AttrMetadata)

    def test_attr_metadata_with_single_attr_array(self, group_uri):
        with Group(group_uri, array="A3") as group:
            isinstance(group.attr_metadata, AttrMetadata)

    def test_get_attr_metadata(self, group_uri):
        with Group(group_uri, array="A2") as group:
            isinstance(group.get_attr_metadata("b"), AttrMetadata)

    def test_open_attr(self, group_uri):
        with Group(group_uri, attr="a") as group:
            array = group.array
            assert isinstance(array, tiledb.Array)
            assert array.mode == "r"
            assert np.array_equal(array[:, :], self._A1_data)

    def test_ambiguous_metadata_attr_exception(self, group_uri):
        with Group(group_uri, array="A2") as group:
            with pytest.raises(RuntimeError):
                isinstance(group.attr_metadata, AttrMetadata)

    def test_no_array_execption(self, group_uri):
        with Group(group_uri) as group:
            with pytest.raises(RuntimeError):
                _ = group.array

    def test_no_array_metadata_execption(self, group_uri):
        with Group(group_uri) as group:
            with pytest.raises(RuntimeError):
                _ = group.array_metadata

    def test_no_attr_metadata_execption(self, group_uri):
        with Group(group_uri) as group:
            with pytest.raises(RuntimeError):
                _ = group.attr_metadata

    def test_no_get_attr_metadata_execption(self, group_uri):
        with Group(group_uri) as group:
            with pytest.raises(RuntimeError):
                _ = group.get_attr_metadata("a")

    def test_no_array_with_attr_exception(self, group_uri):
        with pytest.raises(KeyError):
            with Group(group_uri, attr="bad_name"):
                pass

    def test_ambiguous_array_exception(self, group_uri):
        with pytest.raises(ValueError):
            with Group(group_uri, attr="c"):
                pass


class TestNoMetadataArray:
    @pytest.fixture(scope="class")
    def group_uri(self, tmpdir_factory):
        """Creates a TileDB group and return URI."""
        uri = str(tmpdir_factory.mktemp("empty_group"))
        tiledb.group_create(uri)
        return uri

    def test_no_metadata_array_exception(self, group_uri):
        with Group(group_uri) as group:
            assert group.meta is None
