# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: product-service.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'product-service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15product-service.proto\x12\x0eproductService\"V\n\x07Product\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\r\n\x05price\x18\x03 \x01(\x02\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\x12\r\n\x05image\x18\x05 \x01(\t\"8\n\x0bProductList\x12)\n\x08products\x18\x01 \x03(\x0b\x32\x17.productService.Product\"\x1c\n\x0eProductRequest\x12\n\n\x02id\x18\x01 \x01(\x05\"\x07\n\x05\x45mpty\"X\n\x0eProductMessage\x12\x0e\n\x06sucess\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x12\n\nerror_code\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\t2\xf9\x02\n\x0eProductService\x12\x41\n\x0bGetProducts\x12\x15.productService.Empty\x1a\x1b.productService.ProductList\x12I\n\x0eGetProductById\x12\x1e.productService.ProductRequest\x1a\x17.productService.Product\x12\x45\n\nAddProduct\x12\x17.productService.Product\x1a\x1e.productService.ProductMessage\x12H\n\rUpdateProduct\x12\x17.productService.Product\x1a\x1e.productService.ProductMessage\x12H\n\rDeleteProduct\x12\x17.productService.Product\x1a\x1e.productService.ProductMessageB$\n\x13productService.gRPCB\x0b\x61lternativeP\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'product_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\023productService.gRPCB\013alternativeP\001'
  _globals['_PRODUCT']._serialized_start=41
  _globals['_PRODUCT']._serialized_end=127
  _globals['_PRODUCTLIST']._serialized_start=129
  _globals['_PRODUCTLIST']._serialized_end=185
  _globals['_PRODUCTREQUEST']._serialized_start=187
  _globals['_PRODUCTREQUEST']._serialized_end=215
  _globals['_EMPTY']._serialized_start=217
  _globals['_EMPTY']._serialized_end=224
  _globals['_PRODUCTMESSAGE']._serialized_start=226
  _globals['_PRODUCTMESSAGE']._serialized_end=314
  _globals['_PRODUCTSERVICE']._serialized_start=317
  _globals['_PRODUCTSERVICE']._serialized_end=694
# @@protoc_insertion_point(module_scope)
