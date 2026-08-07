cmake_minimum_required(VERSION 3.20)
project(NexusAI_Shell LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS 
    Widgets
    Core
    Network
    WebSockets)

if (MSVC)
    # MSVC does not report the real C++ standard via __cplusplus unless
    # this is set explicitly. Qt's headers check __cplusplus directly to
    # detect C++17/20 support, so without this flag they see the legacy
    # value (199711L) and fail with "Qt requires a C++17 compiler".
    add_compile_options(/Zc:__cplusplus /permissive-)
endif()

add_executable(NexusAI_Shell
    backend/WebsocketClient.cpp
    backend/WebSocketClient.h
    main.cpp
    DynamicIslandWindow.h
    DynamicIslandWindow.cpp
)

target_link_libraries(NexusAI_Shell PRIVATE Qt6::Widgets
    Qt6::Core
    Qt6::Network
    Qt6::WebSockets)

if (WIN32)
    target_link_libraries(NexusAI_Shell PRIVATE dwmapi user32)
    # Suppress the console window in release builds; comment out while
    # debugging if you want stdout/stderr visible.
    # set_target_properties(NexusAI_Shell PROPERTIES WIN32_EXECUTABLE TRUE)
endif()