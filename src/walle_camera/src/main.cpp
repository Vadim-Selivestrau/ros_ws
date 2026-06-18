#include "rclcpp/rclcpp.hpp"
#include "stereo_image_splitter/splitter_node.hpp"


int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<stereo_image_splitter::StereoImageSplitter>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}