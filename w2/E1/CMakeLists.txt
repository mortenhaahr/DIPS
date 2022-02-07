cmake_minimum_required(VERSION 3.16)
project(JSON)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_FLAGS -Wall)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

file(GLOB all_SRCS
	"${PROJECT_SOURCE_DIR}/*.cpp"
	"${PROJECT_SOURCE_DIR}/*.hpp"
	"${PROJECT_SOURCE_DIR}/JSON/*.cpp"
	"${PROJECT_SOURCE_DIR}/JSON/*.hpp"
)

add_executable(JSON ${all_SRCS})

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
target_link_libraries(JSON PRIVATE Threads::Threads)