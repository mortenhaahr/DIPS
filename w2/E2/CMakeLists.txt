cmake_minimum_required(VERSION 3.21)
project(E2)

set(CMAKE_CXX_STANDARD 20)

add_executable(E2 main.cpp)
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
target_link_libraries(E2 PRIVATE Threads::Threads)