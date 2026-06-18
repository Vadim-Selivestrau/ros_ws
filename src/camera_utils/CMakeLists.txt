cmake_minimum_required(VERSION 3.8)
project(camera_utils)   # Имя вашего пакета

# Включаем стандарт C++17 и строгую компиляцию
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()
set(CMAKE_CXX_STANDARD 17)

# Ищем зависимости (rclcpp для C++ и ament_cmake_python для интеграции Python)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(OpenCV REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(yaml_cpp_vendor REQUIRED)
find_package(ament_cmake_python REQUIRED)     
find_package(image_transport REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  camera_utils/status_node.py
  DESTINATION lib/${PROJECT_NAME}
)

include_directories(include)

add_library(cpp_splitter SHARED
  src/cpp_splitter.cpp   # Путь к вашему .cpp файлу
)

target_link_libraries(cpp_splitter
  ${OpenCV_LIBRARIES}
  yaml-cpp  # Измененная строка
)

ament_target_dependencies(cpp_splitter
  rclcpp
  rclcpp_components
  cv_bridge
  sensor_msgs
)

rclcpp_components_register_node(cpp_splitter
  PLUGIN "camera_utils::StereoSplitter"   
  EXECUTABLE stereo_splitter_component_node 
)

install(TARGETS cpp_splitter
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()