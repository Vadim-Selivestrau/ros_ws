cmake_minimum_required(VERSION 3.8)
project(walle_camera)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
#find_package(image_transport REQUIRED)
find_package(camera_info_manager REQUIRED)

add_library(splitter_node SHARED
  src/splitter_node.cpp
)
target_include_directories(splitter_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(splitter_node
  rclcpp
  rclcpp_components
  sensor_msgs
  #image_transport
  cv_bridge
  camera_info_manager
  OpenCV
)
rclcpp_components_register_node(splitter_node
  PLUGIN "stereo_image_splitter::StereoImageSplitter"
  EXECUTABLE splitter_node_exe
)


add_executable(stereo_image_splitter_node
  src/main.cpp
)
target_link_libraries(stereo_image_splitter_node splitter_node)
ament_target_dependencies(stereo_image_splitter_node
  rclcpp
  sensor_msgs
  #image_transport
  cv_bridge
  camera_info_manager
)

install(TARGETS splitter_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(TARGETS stereo_image_splitter_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

install(DIRECTORY calibration/
  DESTINATION share/${PROJECT_NAME}/calibration
)

ament_package()
