#ifndef STEREO_IMAGE_SPLITTER__SPLITTER_NODE_HPP_
#define STEREO_IMAGE_SPLITTER__SPLITTER_NODE_HPP_

#include <string>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "sensor_msgs/msg/camera_info.hpp"
#include "camera_info_manager/camera_info_manager.hpp"
#include "sensor_msgs/msg/image.hpp"
//#include "image_transport/image_transport.hpp"

namespace stereo_image_splitter
{

class StereoImageSplitter : public rclcpp::Node
{
public:
  explicit StereoImageSplitter(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
  void image_callback(const sensor_msgs::msg::Image::ConstSharedPtr & msg);

  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;

  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr left_image_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr right_image_pub_;
  //image_transport::Publisher left_image_pub_;
  //image_transport::Publisher right_image_pub_;

  std::unique_ptr<camera_info_manager::CameraInfoManager> left_cam_info_;
  std::unique_ptr<camera_info_manager::CameraInfoManager> right_cam_info_;

  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr left_cam_info_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr right_cam_info_pub_;

  std::string camera_ns_;
  std::string left_frame_id_;
  std::string right_frame_id_;
};

}  // namespace stereo_image_splitter

#endif  // STEREO_IMAGE_SPLITTER__SPLITTER_NODE_HPP_