include_directories (${TEMPLATE_SOURCE_DIR}/src)
include_directories (${TEMPLATE_SOURCE_DIR}/googletest/googletest/include)


add_library (template templateSrc.cc) 


add_executable (templateTest templateTest.cc)
target_link_libraries (templateTest template gtest_main)  

add_test (templateTest templateTest)
