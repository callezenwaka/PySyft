# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/core/io/route.proto
"""Generated protocol buffer code."""
# third party
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


# syft absolute
from syft.proto.core.common import (
    common_object_pb2 as proto_dot_core_dot_common_dot_common__object__pb2,
)
from syft.proto.core.io import (
    connection_pb2 as proto_dot_core_dot_io_dot_connection__pb2,
)
from syft.proto.core.io import location_pb2 as proto_dot_core_dot_io_dot_location__pb2
from syft.proto.grid.connections import (
    http_connection_pb2 as proto_dot_grid_dot_connections_dot_http__connection__pb2,
)

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x19proto/core/io/route.proto\x12\x0csyft.core.io\x1a%proto/core/common/common_object.proto\x1a\x1cproto/core/io/location.proto\x1a\x1eproto/core/io/connection.proto\x1a,proto/grid/connections/http_connection.proto"\xfc\x01\n\tSoloRoute\x12!\n\x02id\x18\x01 \x01(\x0b\x32\x15.syft.core.common.UID\x12\x33\n\x0b\x64\x65stination\x18\x02 \x01(\x0b\x32\x1e.syft.core.io.SpecificLocation\x12\x43\n\x12virtual_connection\x18\x03 \x01(\x0b\x32%.syft.core.io.VirtualClientConnectionH\x00\x12\x44\n\x0fgrid_connection\x18\x04 \x01(\x0b\x32).syft.grid.connections.GridHTTPConnectionH\x00\x42\x0c\n\nconnectionb\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "proto.core.io.route_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _SOLOROUTE._serialized_start = 191
    _SOLOROUTE._serialized_end = 443
# @@protoc_insertion_point(module_scope)
