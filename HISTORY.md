# History

## Unreleased

### Bug fixes

### Breaking Behavior

* `NetCDF4ConverterEngine.add_array_converter` adds a `NetCDF4ArrayConverter` and `NetCDF4ConverterEngine.add_array` inherits from `DataspaceCreator`.

### New Features

* Add `create_array` to `DataspaceCreator` for dataspaces with 1 array.
* Add `convert_to_array` and `copy_to_array` to `NetCDF4ConverterEngine` for converters with 1 array.

### Improvements

### Deprecation

* Deprecate `Group.create_virtual` in favor of `VirtualGroup.create`.
* Deprecate `NetCDF4ConverterEngine.add_scalar_dim_converter` in favor of `NetCDF4ConverterEngine.add_scalar_to_dim_converter`.

## TileDB-CF-Py Release 0.3.0

### Breaking Behavior

* Makes `NetCDF4ConverterEngine` methods `add_ncvar_to_attr` and `add_ncdim_to_dim` private.
* Renames method `create` in `DataspaceConverter` to `create_group` and changes method parameters.
* Renames method `convert` in `NetCDF4ConverterEngine` to `convert_to_group` and changes method parameters.
* Renames method `copy` in `NetCDF4ConverterEninge` to `copy_group` and changes method parameters.
* Adds `use_virtual_groups` parameter to `from_netcdf` and `from_netcdf_group` functions.I
* Replaces parameter `tiles` with `tiles_by_dims` and `tiles_by_var` in `from_netcdf` and `from_netcdf_group` functions.
* Renames method `get_all_attr_arrays` in `GroupSchema` to `arrays_with_attr`.
* Removes methods `get_attr_array` and `set_default_metadata_schema` from `GroupSchema` class.
* Change `from_group` and `from_file` in `NetCDF4ConverterEngine` to default to convertering NetCDF coordinates to dimensions.
* Update TileDB-CF standard to version 0.2.0 and implement changes in `DataspaceCreator` class.
* Remove support for arrays with no dimensions in `DataspaceCreator.add_array` method.
* Increase minimum TileDB-Py version to 0.9.3.

### New Features

* Adds the parameter `is_virtual` to classmethod `Group.create` for flagging if the created group should be a virtual group.
* Adds the classmethod `Group.create_virtual` that creates a virtual group from a mapping of array names to URIs.
* Adds a classmethod `GroupSchema.load_virtual` for loading a virtual group defined by a mapping from array names to URIs.
* Adds method `create_virtual_group` to `DataspaceConverter`.
* Adds method `convert_to_virtual_group` in `NetCDF4ConverterEngine`.
* Adds method `copy_to_virtual_group` in `NetCDF4ConverterEngine`.
* Adds TileDB backend engine for xarray (previously in TileDB-xarray package).
* Adds methods to convert NetCDF group where all attributes are stored in separate arrays.
* Adds parameter to set default metadata schema in `GroupSchema` instance in not otherwise specified.
* Adds ability to convert NetCDF coordinates to TileDB dimensions.

### Bug fixes

* Fixes detection of tiles from NetCDF variables with matching chunk sizes.
* Fixes ouput in NetCDF4ConverterEngine and GroupSchema `__repr__` methods.
* Fixes build error when installing with `python setup.py install`.

## TileDB-CF-Py Release 0.2.0

The TileDB-CF-Py v0.2.0 release is the initial release of TileDB-CF-Py.

### New Features

* Initial release of the [TileDB CF dataspace specification](tiledb-cf-spec.md) for defining a data model compatible with the NetCDF data model.
* Adds a `Group` class for reading and writing to arrays in a TileDB group.
* Adds a `GroupSchema` class for loading the array schemas for ararys in a TileDB group.
* Adds `AttrMetadata` and `ArrayMetadata` class for managing attribute specific metadata.
* Adds a `DataspaceCreator` class for creating groups compatible with the TileDB CF dataspace specification.
* Adds a `NetCDF4ConverterEngine` for converting NetCDF files to TileDB with the `netCDF4` library.
* Adds functions and a command-line interface for converting NetCDF files to TileDB.
