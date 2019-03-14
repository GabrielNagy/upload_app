cmake_minimum_required (VERSION 2.6)
set (CMAKE_CXX_STANDARD 11)
project (TEMPLATE)
enable_testing()

add_subdirectory (googletest/googletest)
add_subdirectory (src) 

add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure)
