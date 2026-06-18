#ifndef CAMERA_UTILS__STEREO_SPLITTER_COMPONENT_HPP_
#define CAMERA_UTILS__STEREO_SPLITTER_COMPONENT_HPP_

#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "sensor_msgs/msg/camera_info.hpp"
#include "cv_bridge/cv_bridge.h"

namespace camera_utils
{

class StereoSplitter : public rclcpp::Node
{
public:
  explicit StereoSplitter(const rclcpp::NodeOptions & options);

private:
  void loadCameraInfo(const std::string & yaml_path, sensor_msgs::msg::CameraInfo & msg);
  void listenerCallback(const sensor_msgs::msg::Image::SharedPtr msg);

  // Standard ROS 2 Publishers
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr left_img_pub_;   
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr right_img_pub_;  
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr left_info_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr right_info_pub_;

  // Subscription
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr subscription_;

  // CameraInfo messages (loaded from YAML and reused)
  sensor_msgs::msg::CameraInfo left_info_;
  sensor_msgs::msg::CameraInfo right_info_;

  // CvBridge helper
  cv_bridge::CvImagePtr cv_ptr_;
};

}  // namespace camera_utils

#endif  // CAMERA_UTILS__STEREO_SPLITTER_COMPONENT_HPP_
