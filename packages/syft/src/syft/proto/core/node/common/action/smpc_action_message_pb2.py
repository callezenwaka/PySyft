# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/core/node/common/action/smpc_action_message.proto
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
from syft.proto.core.io import address_pb2 as proto_dot_core_dot_io_dot_address__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n7proto/core/node/common/action/smpc_action_message.proto\x12\x1csyft.core.node.common.action\x1a%proto/core/common/common_object.proto\x1a\x1bproto/core/io/address.proto"\x8c\x04\n\x11SMPCActionMessage\x12\x13\n\x0bname_action\x18\x01 \x01(\t\x12&\n\x07self_id\x18\x02 \x01(\x0b\x32\x15.syft.core.common.UID\x12&\n\x07\x61rgs_id\x18\x03 \x03(\x0b\x32\x15.syft.core.common.UID\x12P\n\tkwargs_id\x18\x04 \x03(\x0b\x32=.syft.core.node.common.action.SMPCActionMessage.KwargsIdEntry\x12K\n\x06kwargs\x18\x05 \x03(\x0b\x32;.syft.core.node.common.action.SMPCActionMessage.KwargsEntry\x12-\n\x0eid_at_location\x18\x06 \x01(\x0b\x32\x15.syft.core.common.UID\x12&\n\x07\x61\x64\x64ress\x18\x07 \x01(\x0b\x32\x15.syft.core.io.Address\x12%\n\x06msg_id\x18\x08 \x01(\x0b\x32\x15.syft.core.common.UID\x1a\x46\n\rKwargsIdEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12$\n\x05value\x18\x02 \x01(\x0b\x32\x15.syft.core.common.UID:\x02\x38\x01\x1a-\n\x0bKwargsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x0c:\x02\x38\x01\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "proto.core.node.common.action.smpc_action_message_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _SMPCACTIONMESSAGE_KWARGSIDENTRY._options = None
    _SMPCACTIONMESSAGE_KWARGSIDENTRY._serialized_options = b"8\001"
    _SMPCACTIONMESSAGE_KWARGSENTRY._options = None
    _SMPCACTIONMESSAGE_KWARGSENTRY._serialized_options = b"8\001"
    _SMPCACTIONMESSAGE._serialized_start = 158
    _SMPCACTIONMESSAGE._serialized_end = 682
    _SMPCACTIONMESSAGE_KWARGSIDENTRY._serialized_start = 565
    _SMPCACTIONMESSAGE_KWARGSIDENTRY._serialized_end = 635
    _SMPCACTIONMESSAGE_KWARGSENTRY._serialized_start = 637
    _SMPCACTIONMESSAGE_KWARGSENTRY._serialized_end = 682
# @@protoc_insertion_point(module_scope)
