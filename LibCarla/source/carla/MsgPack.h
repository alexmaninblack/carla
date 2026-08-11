// Copyright (c) 2026 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include "carla/Buffer.h"

// Legacy Apple headers define `nil` as a macro, which collides with
// msgpack's `nil` type declaration. Hide it only while parsing msgpack so
// later Apple framework headers still see their original macro.
#if defined(__APPLE__) && defined(nil)
#  pragma push_macro("nil")
#  undef nil
#  define CARLA_RESTORE_APPLE_NIL_MACRO
#endif

#include <rpc/msgpack.hpp>

#if defined(CARLA_RESTORE_APPLE_NIL_MACRO)
#  pragma pop_macro("nil")
#  undef CARLA_RESTORE_APPLE_NIL_MACRO
#endif

namespace carla {

  class MsgPack {
  public:

    template <typename T>
    static Buffer Pack(const T &obj) {
      namespace mp = ::clmdep_msgpack;
      mp::sbuffer sbuf;
      mp::pack(sbuf, obj);
      return Buffer(
          reinterpret_cast<const unsigned char *>(sbuf.data()),
          static_cast<uint64_t>(sbuf.size()));
    }

    template <typename T>
    static T UnPack(const Buffer &buffer) {
      namespace mp = ::clmdep_msgpack;
      return mp::unpack(reinterpret_cast<const char *>(buffer.data()), buffer.size()).template as<T>();
    }

    template <typename T>
    static T UnPack(const unsigned char *data, size_t size) {
      namespace mp = ::clmdep_msgpack;
      return mp::unpack(reinterpret_cast<const char *>(data), size).template as<T>();
    }
  };

} // namespace carla
