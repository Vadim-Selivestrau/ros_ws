import os

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    launch_args = [
        DeclareLaunchArgument('camera_ns', default_value='elp'),
    ]

    walle_camera_dir = os.path.join(
        get_package_share_directory("walle_camera"), "config"
    )
    usb_cam_node = Node(
        package="usb_cam",
        executable="usb_cam_node_exe",
        output="screen",
        namespace=LaunchConfiguration("camera_ns"),
        parameters=[os.path.join(walle_camera_dir, "elp_stereo_camera_params.yaml")]
    )

    split_sync_images_node = Node(
        package="walle_camera",
        executable="stereo_image_splitter_node",
        name="stereo_image_splitter",
        parameters=[{
            "camera_ns": LaunchConfiguration("camera_ns"),
            "input_topic": "image_raw",
            "left_image_topic": "left/image_raw",
            "right_image_topic": "right/image_raw",
            "left_camera_info_topic": "left/camera_info",
            "right_camera_info_topic": "right/camera_info",
            "left_frame_id": "left_optical_frame",
            "right_frame_id": "right_optical_frame"
        }]
    )

    return LaunchDescription(
        [
            usb_cam_node,
            split_sync_images_node
        ]
    )
