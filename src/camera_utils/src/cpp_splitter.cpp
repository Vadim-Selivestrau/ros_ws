#include "camera_utils/cpp_splitter.hpp"

#include <opencv2/opencv.hpp>
#include <yaml-cpp/yaml.h>
#include <cv_bridge/cv_bridge.h>
#include <rclcpp_components/register_node_macro.hpp>
#include <algorithm>
#include <vector>
#include <string>

namespace camera_utils
{

StereoSplitter::StereoSplitter(const rclcpp::NodeOptions & options)
: Node("stereo_splitter", options)
{
  // Load calibration files
  loadCameraInfo("/home/jetson/ros2_ws/src/robo_bringup/config/calibration/left.yaml", left_info_);
  loadCameraInfo("/home/jetson/ros2_ws/src/robo_bringup/config/calibration/right.yaml", right_info_);

  // Subscription to wide stereo image (left+right side‑by‑side)
  subscription_ = this->create_subscription<sensor_msgs::msg::Image>(
    "/image_raw", 1,
    std::bind(&StereoSplitter::listenerCallback, this, std::placeholders::_1));

  // Publishers for left and right images and camera info
  left_img_pub_ = this->create_publisher<sensor_msgs::msg::Image>("/left/image_raw", 1);
  right_img_pub_ = this->create_publisher<sensor_msgs::msg::Image>("/right/image_raw", 1);
  left_info_pub_ = this->create_publisher<sensor_msgs::msg::CameraInfo>("/left/camera_info", 1);
  right_info_pub_ = this->create_publisher<sensor_msgs::msg::CameraInfo>("/right/camera_info", 1);

  RCLCPP_INFO(this->get_logger(), "Stereo splitter component started");
}

void StereoSplitter::loadCameraInfo(const std::string & yaml_path,
                                    sensor_msgs::msg::CameraInfo & msg)
{
  try {
    YAML::Node config = YAML::LoadFile(yaml_path);

    msg.width = config["image_width"].as<int>();
    msg.height = config["image_height"].as<int>();
    msg.distortion_model = config["distortion_model"].as<std::string>();

    // Camera matrix K (9 elements)
    auto k_node = config["camera_matrix"]["data"];
    if (k_node && k_node.size() == 9) {
      for (size_t i = 0; i < 9; ++i) {
        msg.k[i] = k_node[i].as<double>();
      }
    }

    // Distortion coefficients D (variable size)
    auto d_node = config["distortion_coefficients"]["data"];
    if (d_node) {
      msg.d.clear();
      for (size_t i = 0; i < d_node.size(); ++i) {
        msg.d.push_back(d_node[i].as<double>());
      }
    }

    // Rectification matrix R (9 elements)
    auto r_node = config["rectification_matrix"]["data"];
    if (r_node && r_node.size() == 9) {
      for (size_t i = 0; i < 9; ++i) {
        msg.r[i] = r_node[i].as<double>();
      }
    }

    // Projection matrix P (12 elements)
    auto p_node = config["projection_matrix"]["data"];
    if (p_node && p_node.size() == 12) {
      for (size_t i = 0; i < 12; ++i) {
        msg.p[i] = p_node[i].as<double>();
      }
    }

    RCLCPP_INFO(this->get_logger(), "Loaded calibration from %s", yaml_path.c_str());
  } catch (const std::exception & e) {
    RCLCPP_ERROR(this->get_logger(), "Failed to load calibration from %s: %s",
                 yaml_path.c_str(), e.what());
  }
}

void StereoSplitter::listenerCallback(const sensor_msgs::msg::Image::SharedPtr msg)
{
  // Convert ROS Image to OpenCV Mat (bgr8)
  cv_bridge::CvImagePtr cv_ptr;
  try {
    cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
  } catch (cv_bridge::Exception & e) {
    RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
    return;
  }

  cv::Mat full_image = cv_ptr->image;
  int height = full_image.rows;
  int width = full_image.cols;
  int mid = width / 2;   // assume exactly two images side by side

  // Extract left and right halves
  cv::Mat left_bgr = full_image(cv::Rect(0, 0, mid, height));
  cv::Mat right_bgr = full_image(cv::Rect(mid, 0, mid, height));

  // Convert BGR to RGB
  cv::Mat left_rgb, right_rgb;
  cv::cvtColor(left_bgr, left_rgb, cv::COLOR_BGR2RGB);
  cv::cvtColor(right_bgr, right_rgb, cv::COLOR_BGR2RGB);

  // Create Image messages using cv_bridge
  auto left_img_msg = cv_bridge::CvImage(msg->header, "rgb8", left_rgb).toImageMsg();
  auto right_img_msg = cv_bridge::CvImage(msg->header, "rgb8", right_rgb).toImageMsg();

  // Set proper frame_ids
  left_img_msg->header.frame_id = "left_camera_optical_frame";
  right_img_msg->header.frame_id = "right_camera_optical_frame";

  // Update CameraInfo width/height and timestamp
  left_info_.header = msg->header;
  left_info_.header.frame_id = left_img_msg->header.frame_id;
  left_info_.width = mid;
  left_info_.height = height;

  right_info_.header = msg->header;
  right_info_.header.frame_id = right_img_msg->header.frame_id;
  right_info_.width = mid;
  right_info_.height = height;

  // Publish (Разыменовываем shared_ptr с помощью '*')
  left_img_pub_->publish(*left_img_msg);
  right_img_pub_->publish(*right_img_msg);
  left_info_pub_->publish(left_info_);
  right_info_pub_->publish(right_info_);
}

}  // namespace camera_utils

RCLCPP_COMPONENTS_REGISTER_NODE(camera_utils::StereoSplitter)
