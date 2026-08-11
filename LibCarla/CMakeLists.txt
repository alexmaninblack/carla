project (
  libcarla
  LANGUAGES
    CXX
  VERSION
    ${CARLA_VERSION}
)

set (
  LIBCARLA_SOURCE_PATH
  ${CARLA_WORKSPACE_PATH}/LibCarla/source
)

carla_two_step_configure_file (
  ${LIBCARLA_SOURCE_PATH}/carla/Version.h
  ${LIBCARLA_SOURCE_PATH}/carla/Version.h.in
)

if (WIN32)

  set (
    WINNT_MACRO_PATH
    ${LIBCARLA_SOURCE_PATH}/util/winnt-macros.txt
  )

  file (
    STRINGS
    ${WINNT_MACRO_PATH}
    WINDOWS_MACRO_LIST
  )

  set (
    GUARD_BEGIN_FILE_TEXT
    ""
  )

  set (
    GUARD_END_FILE_TEXT
    ""
  )

  foreach (WINDOWS_MACRO ${WINDOWS_MACRO_LIST})
    string (
      APPEND
      GUARD_BEGIN_FILE_TEXT
      "#pragma push_macro(\"${WINDOWS_MACRO}\")\n"
      "#undef ${WINDOWS_MACRO}\n"
    )
    string (
      APPEND
      GUARD_END_FILE_TEXT
      "#pragma pop_macro(\"${WINDOWS_MACRO}\")\n"
    )
  endforeach ()

  file (
    WRITE
    ${LIBCARLA_SOURCE_PATH}/util/ue-header-guard-begin.h
    ${GUARD_BEGIN_FILE_TEXT}
  )

  file (
    WRITE
    ${LIBCARLA_SOURCE_PATH}/util/ue-header-guard-end.h
    ${GUARD_END_FILE_TEXT}
  )

  set_directory_properties(
    PROPERTIES
    CMAKE_CONFIGURE_DEPENDS
    ${WINNT_MACRO_PATH}
  )

else ()

  file (
    WRITE
    ${LIBCARLA_SOURCE_PATH}/util/ue-header-guard-begin.h
    ""
  )

  file (
    WRITE
    ${LIBCARLA_SOURCE_PATH}/util/ue-header-guard-end.h
    ""
  )

endif ()



if (BUILD_CARLA_SERVER)

  file (
    GLOB
    LIBCARLA_SERVER_SOURCES
    ${LIBCARLA_SOURCE_PATH}/carla/Buffer.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/Exception.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/geom/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/parser/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/element/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/general/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/object/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/signal/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/rpc/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/s11n/SensorHeaderSerializer.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/tcp/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/multigpu/*.cpp
  )

  if (ENABLE_ROS2)
    file (
      GLOB
      LIBCARLA_SERVER_SOURCES_ROS2
      ${LIBCARLA_SOURCE_PATH}/carla/ros2/*.cpp
    )
    list (
      APPEND
      LIBCARLA_SERVER_SOURCES
      ${LIBCARLA_SERVER_SOURCES_ROS2}
    )
  endif ()

  file (
    GLOB
    LIBCARLA_SERVER_SOURCES_THIRD_PARTY
    ${LIBCARLA_SOURCE_PATH}/third-party/odrSpiral/*.cpp
    ${LIBCARLA_SOURCE_PATH}/third-party/moodycamel/*.cpp
    ${LIBCARLA_SOURCE_PATH}/third-party/pugixml/*.cpp
  )

  file (
    GLOB
    LIBCARLA_SERVER_HEADERS
    ${LIBCARLA_SOURCE_PATH}/carla/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/geom/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/parser/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/element/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/general/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/object/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/signal/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/rpc/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/s11n/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/low_level/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/multigpu/*.h
    ${LIBCARLA_SOURCE_PATH}/util/*.h
  )
  
  list (
    APPEND
    LIBCARLA_SERVER_HEADERS
    ${LIBCARLA_SOURCE_PATH}/util/winnt-macros.txt
  )

  if (ENABLE_ROS2)
    file (
      GLOB
      LIBCARLA_SERVER_HEADERS_ROS2
      ${LIBCARLA_SOURCE_PATH}/carla/ros2/*.h
    )
    list (
      APPEND
      LIBCARLA_SERVER_HEADERS
      ${LIBCARLA_SERVER_HEADERS_ROS2}
    )
    set (CARLA_ROS2_DEFINITIONS WITH_ROS2)
  endif ()

  if (ENABLE_ROS2_DEMO)
    set (CARLA_ROS2_DEFINITIONS ${CARLA_ROS2_DEFINITIONS} WITH_ROS2_DEMO)
  endif ()

  file (
    GLOB
    LIBCARLA_SERVER_HEADERS_THIRD_PARTY
    ${LIBCARLA_SOURCE_PATH}/third-party/odrSpiral/*.h
    ${LIBCARLA_SOURCE_PATH}/third-party/moodycamel/*.h
    ${LIBCARLA_SOURCE_PATH}/third-party/pugixml/*.hpp
  )

  # glibc 2.38+ compat shim (compiled as C11 to avoid __isoc23_strtol redirect)
  set (GLIBC_COMPAT_SOURCE ${LIBCARLA_SOURCE_PATH}/carla/GlibcCompat.c)
  set_source_files_properties (${GLIBC_COMPAT_SOURCE} PROPERTIES LANGUAGE C)

  carla_add_library (
    carla-server
    "Build the CARLA server."
    ${LIBCARLA_SERVER_HEADERS}
    ${LIBCARLA_SERVER_SOURCES}
    ${LIBCARLA_SERVER_HEADERS_THIRD_PARTY}
    ${LIBCARLA_SERVER_SOURCES_THIRD_PARTY}
    ${GLIBC_COMPAT_SOURCE}
  )

  target_link_libraries (
    carla-server PUBLIC
    Boost::asio
    Boost::geometry
    Boost::algorithm
    Boost::assert
    Boost::gil
    RecastNavigation::Recast
    RecastNavigation::Detour
    RecastNavigation::DetourCrowd
    png_static
    zlibstatic
    rpc
  )
  
  target_include_directories (
    carla-server PUBLIC
    ${LIBCARLA_SOURCE_PATH}
  )

  target_compile_definitions (
    carla-server PUBLIC
    ${CARLA_COMMON_DEFINITIONS}
    ${CARLA_EXCEPTION_DEFINITIONS}
    ${CARLA_RTTI_DEFINITIONS}
    ${CARLA_ROS2_DEFINITIONS}
  )

  if (ENABLE_ROS2)
    add_dependencies (carla-server carla-ros2-native)
  endif ()

endif ()



if (BUILD_CARLA_CLIENT)

  file (
    GLOB
    LIBCARLA_CLIENT_HEADERS
    ${LIBCARLA_SOURCE_PATH}/carla/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/client/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/client/detail/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/geom/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/image/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/nav/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/parser/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/pointcloud/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/profiler/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/element/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/general/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/object/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/road/signal/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/rpc/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/data/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/s11n/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/tcp/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/low_level/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/multigpu/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/trafficmanager/*.h
    ${LIBCARLA_SOURCE_PATH}/carla/agents/navigation/*.h
    ${LIBCARLA_SOURCE_PATH}/util/*.h
  )

  list (
    APPEND
    LIBCARLA_CLIENT_HEADERS
    ${LIBCARLA_SOURCE_PATH}/util/winnt-macros.txt
  )

  if (ENABLE_RSS)
    file (
      GLOB
      LIBCARLA_CLIENT_HEADERS_RSS
      ${LIBCARLA_SOURCE_PATH}/carla/rss/*.h
    )
    list (
      APPEND
      LIBCARLA_CLIENT_HEADERS
      ${LIBCARLA_CLIENT_HEADERS_RSS}
    )
  endif ()

  file (
    GLOB
    LIBCARLA_CLIENT_HEADERS_THIRD_PARTY
    ${LIBCARLA_SOURCE_PATH}/third-party/odrSpiral/*.h
    ${LIBCARLA_SOURCE_PATH}/third-party/moodycamel/*.h
    ${LIBCARLA_SOURCE_PATH}/third-party/pugixml/*.hpp
    ${LIBCARLA_SOURCE_PATH}/third-party/pugixml/*.h
  )

  file (
    GLOB
    LIBCARLA_CLIENT_SOURCES
    ${LIBCARLA_SOURCE_PATH}/carla/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/client/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/client/detail/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/geom/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/image/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/nav/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/opendrive/parser/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/pointcloud/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/element/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/general/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/object/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/road/signal/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/rpc/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/data/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/sensor/s11n/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/detail/tcp/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/streaming/low_level/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/multigpu/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/trafficmanager/*.cpp
    ${LIBCARLA_SOURCE_PATH}/carla/agents/navigation/*.cpp
  )

  if (ENABLE_RSS)
    file (
      GLOB
      LIBCARLA_CLIENT_SOURCES_RSS
      ${LIBCARLA_SOURCE_PATH}/carla/rss/*.cpp
    )
    list (
      APPEND
      LIBCARLA_CLIENT_SOURCES
      ${LIBCARLA_CLIENT_SOURCES_RSS}
    )
  endif ()

  file (
    GLOB
    LIBCARLA_CLIENT_SOURCES_THIRD_PARTY
    ${LIBCARLA_SOURCE_PATH}/third-party/odrSpiral/*.cpp
    ${LIBCARLA_SOURCE_PATH}/third-party/pugixml/*.cpp
  )

  carla_add_library (
    carla-client
    "Build the CARLA client."
    ${LIBCARLA_CLIENT_HEADERS}
    ${LIBCARLA_CLIENT_SOURCES}
    ${LIBCARLA_CLIENT_HEADERS_THIRD_PARTY}
    ${LIBCARLA_CLIENT_SOURCES_THIRD_PARTY}
  )

  target_link_libraries (
    carla-client PUBLIC
    Boost::asio
    Boost::algorithm
    Boost::geometry
    Boost::assert
    Boost::gil
    RecastNavigation::Recast
    RecastNavigation::Detour
    RecastNavigation::DetourCrowd
    png_static
    zlibstatic
    rpc
  )
  target_include_directories (
    carla-client PUBLIC
    ${LIBCARLA_SOURCE_PATH}
  )

  target_compile_definitions (
    carla-client PUBLIC
    ${CARLA_COMMON_DEFINITIONS}
    ${CARLA_EXCEPTION_DEFINITIONS}
    ${CARLA_RTTI_DEFINITIONS}
  )

  # Install + find_package(Carla) integration — closes #6091.
  #
  # LibCarla's public headers expose Boost, rpclib, and Recast types, while its
  # static archive depends on their static libraries plus libpng and zlib. A
  # usable standalone package must therefore install the exact dependency
  # headers and archives used for this build. The hand-written package config
  # below attaches those archives transitively to Carla::carla-client.
  include (GNUInstallDirs)
  include (CMakePackageConfigHelpers)

  install (
    TARGETS carla-client
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  )

  install (
    DIRECTORY   ${LIBCARLA_SOURCE_PATH}/carla
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING
      PATTERN "*.h"
      PATTERN "*.hpp"
      PATTERN "*.inl"
  )

  # Boost's CMake distribution keeps public headers in one include directory
  # per module. Install all module include trees into one conventional prefix;
  # overlapping directories are intentional and contain different headers.
  file (GLOB CARLA_BOOST_PUBLIC_INCLUDE_DIRS
    LIST_DIRECTORIES true
    "${boost_SOURCE_DIR}/libs/*/include"
    "${boost_SOURCE_DIR}/libs/*/*/include"
  )
  foreach (CARLA_BOOST_INCLUDE_DIR IN LISTS CARLA_BOOST_PUBLIC_INCLUDE_DIRS)
    install (
      DIRECTORY "${CARLA_BOOST_INCLUDE_DIR}/"
      DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )
  endforeach ()

  install (
    DIRECTORY ${rpclib_SOURCE_DIR}/include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )
  install (
    DIRECTORY
      ${recastnavigation_SOURCE_DIR}/Recast/Include/
      ${recastnavigation_SOURCE_DIR}/Detour/Include/
      ${recastnavigation_SOURCE_DIR}/DetourCrowd/Include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )
  install (
    FILES
      ${libpng_SOURCE_DIR}/png.h
      ${libpng_SOURCE_DIR}/pngconf.h
      ${libpng_BINARY_DIR}/pnglibconf.h
      ${zlib_SOURCE_DIR}/zlib.h
      ${zlib_BINARY_DIR}/zconf.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )

  set (CARLA_CLIENT_STATIC_DEPENDENCY_TARGETS
    boost_context
    boost_graph
    boost_random
    boost_serialization
    boost_thread
    boost_date_time
    boost_container
    boost_atomic
    boost_chrono
    boost_filesystem
    Recast
    DetourCrowd
    Detour
    png_static
    zlibstatic
    rpc
  )
  foreach (CARLA_DEPENDENCY_TARGET IN LISTS CARLA_CLIENT_STATIC_DEPENDENCY_TARGETS)
    install (
      FILES $<TARGET_FILE:${CARLA_DEPENDENCY_TARGET}>
      DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
  endforeach ()

  install (
    FILES ${boost_SOURCE_DIR}/LICENSE_1_0.txt
    DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/Carla
    RENAME Boost-LICENSE_1_0.txt
  )
  install (
    FILES ${rpclib_SOURCE_DIR}/LICENSE.md
    DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/Carla
    RENAME rpclib-LICENSE.md
  )
  install (
    FILES ${recastnavigation_SOURCE_DIR}/License.txt
    DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/Carla
    RENAME RecastNavigation-License.txt
  )
  install (
    FILES ${libpng_SOURCE_DIR}/LICENSE
    DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/Carla
    RENAME libpng-LICENSE
  )
  install (
    FILES ${zlib_SOURCE_DIR}/LICENSE
    DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/Carla
    RENAME zlib-LICENSE
  )

  write_basic_package_version_file (
    ${CMAKE_CURRENT_BINARY_DIR}/CarlaConfigVersion.cmake
    VERSION       ${CARLA_VERSION}
    COMPATIBILITY SameMajorVersion
  )

  set (CARLA_EXPORTED_DEFINITIONS
    ${CARLA_COMMON_DEFINITIONS}
    ${CARLA_EXCEPTION_DEFINITIONS}
    ${CARLA_RTTI_DEFINITIONS}
    BOOST_ALL_NO_LIB
    RPCLIB_MSGPACK=clmdep_msgpack
  )
  if (APPLE)
    list (APPEND CARLA_EXPORTED_DEFINITIONS RPCLIB_MAC)
  endif ()

  configure_package_config_file (
    ${CARLA_WORKSPACE_PATH}/CMake/CarlaConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/CarlaConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Carla
    PATH_VARS CMAKE_INSTALL_INCLUDEDIR CMAKE_INSTALL_LIBDIR
  )

  install (
    FILES
      ${CMAKE_CURRENT_BINARY_DIR}/CarlaConfig.cmake
      ${CMAKE_CURRENT_BINARY_DIR}/CarlaConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Carla
  )

endif ()



if (BUILD_LIBCARLA_TESTS)

  set (
    LIBCARLA_TEST_HARNESS_SOURCES
    ${LIBCARLA_SOURCE_PATH}/test/test.cpp
    ${LIBCARLA_SOURCE_PATH}/test/test.h
    ${LIBCARLA_SOURCE_PATH}/test/Buffer.cpp
    ${LIBCARLA_SOURCE_PATH}/test/Buffer.h
    ${LIBCARLA_SOURCE_PATH}/test/Random.h
  )

  file (
    GLOB
    LIBCARLA_TEST_COMMON_SOURCES
    ${LIBCARLA_SOURCE_PATH}/test/common/*.cpp
  )

  if (BUILD_CARLA_SERVER)

    file (
      GLOB
      LIBCARLA_TEST_SERVER_SOURCES
      ${LIBCARLA_SOURCE_PATH}/test/server/*.cpp
    )

    carla_add_executable (
      libcarla_test_server
      "Build the LibCarla server-side gtest suite."
      ${LIBCARLA_TEST_HARNESS_SOURCES}
      ${LIBCARLA_TEST_COMMON_SOURCES}
      ${LIBCARLA_TEST_SERVER_SOURCES}
    )

    target_link_libraries (
      libcarla_test_server PRIVATE
      carla-server
      GTest::gtest
      GTest::gtest_main
    )

    target_include_directories (
      libcarla_test_server PRIVATE
      ${LIBCARLA_SOURCE_PATH}
      ${LIBCARLA_SOURCE_PATH}/test
      ${LIBCARLA_SOURCE_PATH}/third-party
    )

    target_compile_definitions (
      libcarla_test_server PRIVATE
      LIBCARLA_WITH_GTEST
      LIBCARLA_TEST_CONTENT_FOLDER="${CARLA_WORKSPACE_PATH}/Build/test-content"
    )

  endif ()

  if (BUILD_CARLA_CLIENT)

    file (
      GLOB
      LIBCARLA_TEST_CLIENT_SOURCES
      ${LIBCARLA_SOURCE_PATH}/test/client/*.cpp
    )

    carla_add_executable (
      libcarla_test_client
      "Build the LibCarla client-side gtest suite."
      ${LIBCARLA_TEST_HARNESS_SOURCES}
      ${LIBCARLA_TEST_COMMON_SOURCES}
      ${LIBCARLA_TEST_CLIENT_SOURCES}
    )

    target_link_libraries (
      libcarla_test_client PRIVATE
      carla-client
      GTest::gtest
      GTest::gtest_main
    )

    target_include_directories (
      libcarla_test_client PRIVATE
      ${LIBCARLA_SOURCE_PATH}
      ${LIBCARLA_SOURCE_PATH}/test
      ${LIBCARLA_SOURCE_PATH}/third-party
    )

    target_compile_definitions (
      libcarla_test_client PRIVATE
      LIBCARLA_WITH_GTEST
      LIBCARLA_TEST_CONTENT_FOLDER="${CARLA_WORKSPACE_PATH}/Build/test-content"
    )

  endif ()

endif ()
