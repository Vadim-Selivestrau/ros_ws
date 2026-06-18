#include "stereo_image_splitter/splitter_node.hpp"

#include "sensor_msgs/image_encodings.hpp"
#include "cv_bridge/cv_bridge.h"
#include "opencv2/imgproc/imgproc.hpp"

namespace stereo_image_splitter
{

StereoImageSplitter::StereoImageSplitter(const rclcpp::NodeOptions& options)
  : Node("split_sync_image_node", options)
  {
    this->declare_parameter<std::string>("camera_ns", "elp");
    this->declare_parameter<std::string>("input_topic", "image_raw");
    this->declare_parameter<std::string>("left_image_topic", "left/image_raw");
    this->declare_parameter<std::string>("right_image_topic", "right/image_raw");
    this->declare_parameter<std::string>("left_camera_info_topic", "left/camera_info");
    this->declare_parameter<std::string>("right_camera_info_topic", "right/camera_info");
    this->declare_parameter<std::string>("left_frame_id", "left_optical_frame");
    this->declare_parameter<std::string>("right_frame_id", "right_optical_frame");

    camera_ns_ = this->get_parameter("camera_ns").as_string();
    const auto input_topic = camera_ns_ + "/" + this->get_parameter("input_topic").as_string();
    const auto left_image_topic = camera_ns_ + "/" + this->get_parameter("left_image_topic").as_string();
    const auto right_image_topic = camera_ns_ + "/" + this->get_parameter("right_image_topic").as_string();
    const auto left_camera_info_topic = camera_ns_ + "/" + this->get_parameter("left_camera_info_topic").as_string();
    const auto right_camera_info_topic = camera_ns_ + "/" + this->get_parameter("right_camera_info_topic").as_string();
    left_frame_id_ = camera_ns_ + "/" + this->get_parameter("left_frame_id").as_string();
    right_frame_id_ = camera_ns_ + "/" + this->get_parameter("right_frame_id").as_string();

    left_image_pub_ = this->create_publisher<sensor_msgs::msg::Image>(left_image_topic, 3);
    left_cam_info_pub_ = this->create_publisher<sensor_msgs::msg::CameraInfo>(left_camera_info_topic, 3);
    right_image_pub_ = this->create_publisher<sensor_msgs::msg::Image>(right_image_topic, 3);
    right_cam_info_pub_ = this->create_publisher<sensor_msgs::msg::CameraInfo>(right_camera_info_topic, 3);

    //left_image_pub_ = image_transport::create_publisher(this, left_image_topic);
    //right_image_pub_ = image_transport::create_publisher(this, right_image_topic);

    sub_ = this->create_subscription<sensor_msgs::msg::Image>(
      input_topic, 1,
      std::bind(&StereoImageSplitter::image_callback, this, std::placeholders::_1));

    std::string left_calib_url = "file:///home/jetson/ros2_ws/src/robo_bringup/config/calibration/04.06.2026_1280X480/left.yaml";
    std::string right_calib_url = "file:///home/jetson/ros2_ws/src/robo_bringup/config/calibration/04.06.2026_1280X480/right.yaml";
    
    left_cam_info_ = std::make_unique<camera_info_manager::CameraInfoManager>(this, "left", left_calib_url);
    right_cam_info_ = std::make_unique<camera_info_manager::CameraInfoManager>(this, "right", right_calib_url);

    RCLCPP_INFO(this->get_logger(), "Split synchronized elp image node initialized.");
  }

void StereoImageSplitter::image_callback(const sensor_msgs::msg::Image::ConstSharedPtr& msg)
{
  if (left_image_pub_->get_subscription_count() == 0 &&
  right_image_pub_->get_subscription_count() == 0)
    {
      return;
    }

  cv_bridge::CvImageConstPtr cv_ptr;

  try {
    cv_ptr = cv_bridge::toCvShare(msg);
  } catch (cv_bridge::Exception& e) {
    RCLCPP_ERROR(this->get_logger(), "cv_bridge exception: %s", e.what());
    return;
  }

  int combined_rows = cv_ptr->image.rows; 
  int combined_cols = cv_ptr->image.cols;

  int image_cols = combined_cols / 2;
  int image_rows = combined_rows;

  cv::Rect leftROI(0, 0, image_cols, image_rows);
  cv::Rect rightROI(image_cols, 0, image_cols, image_rows);

  cv_bridge::CvImage cv_ptr_left(msg->header, msg->encoding, cv_ptr->image(leftROI).clone());
  cv_bridge::CvImage cv_ptr_right(msg->header, msg->encoding, cv_ptr->image(rightROI).clone());
  cv_ptr_left.header.frame_id = left_frame_id_;
  cv_ptr_right.header.frame_id = right_frame_id_;

  auto ci_left = left_cam_info_->getCameraInfo();
  auto ci_right = right_cam_info_->getCameraInfo();

  ci_left.header = cv_ptr_left.header;
  ci_right.header = cv_ptr_right.header;

  left_image_pub_->publish(*cv_ptr_left.toImageMsg());
  left_cam_info_pub_->publish(ci_left);
  right_image_pub_->publish(*cv_ptr_right.toImageMsg());
  right_cam_info_pub_->publish(ci_right);
}

}
