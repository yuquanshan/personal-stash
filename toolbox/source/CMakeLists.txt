cmake_minimum_required (VERSION 2.6)
set (CMAKE_CXX_STANDARD 14)
project (toolbox)

set (LOCAL_HEADERS "/usr/local/include/")
include_directories ("${LOCAL_HEADERS}")

find_library(FOLLY folly)

add_executable(count_bits count_bits.cpp)
target_link_libraries(count_bits ${FOLLY})
install (TARGETS count_bits DESTINATION /usr/local/bin)