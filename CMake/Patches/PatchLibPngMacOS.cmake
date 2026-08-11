#[[
  libpng versions used by CARLA include <fp.h> whenever TARGET_OS_MAC is
  defined. Modern Apple SDKs define that macro but no longer provide fp.h;
  math.h supplies the required declarations instead.

  This is the upstream libpng fix from commit 893b8113f04d408cc6177c6de19c9889a48faa24.
]]

set (PNG_PRIVATE_HEADER "${SOURCE_DIR}/pngpriv.h")

if (NOT EXISTS "${PNG_PRIVATE_HEADER}")
  message (FATAL_ERROR "Could not find libpng private header at ${PNG_PRIVATE_HEADER}.")
endif ()

file (READ "${PNG_PRIVATE_HEADER}" PNG_PRIVATE_HEADER_CONTENT)

set (PNG_FP_HEADER_BLOCK [=[#  if (defined(__MWERKS__) && defined(macintosh)) || defined(applec) || \
    defined(THINK_C) || defined(__SC__) || defined(TARGET_OS_MAC)
   /* We need to check that <math.h> hasn't already been included earlier
    * as it seems it doesn't agree with <fp.h>, yet we should really use
    * <fp.h> if possible.
    */
#    if !defined(__MATH_H__) && !defined(__MATH_H) && !defined(__cmath__)
#      include <fp.h>
#    endif
#  else
#    include <math.h>
#  endif]=])

string (FIND "${PNG_PRIVATE_HEADER_CONTENT}" "${PNG_FP_HEADER_BLOCK}" PNG_FP_HEADER_BLOCK_OFFSET)

if (NOT PNG_FP_HEADER_BLOCK_OFFSET EQUAL -1)
  string (
    REPLACE
    "${PNG_FP_HEADER_BLOCK}"
    "#  include <math.h>"
    PNG_PRIVATE_HEADER_CONTENT
    "${PNG_PRIVATE_HEADER_CONTENT}"
  )
  file (WRITE "${PNG_PRIVATE_HEADER}" "${PNG_PRIVATE_HEADER_CONTENT}")
elseif (NOT PNG_PRIVATE_HEADER_CONTENT MATCHES "#  include <math.h>")
  message (FATAL_ERROR "Could not locate the expected floating-point header block in ${PNG_PRIVATE_HEADER}.")
endif ()
