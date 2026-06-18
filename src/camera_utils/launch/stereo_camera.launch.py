from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            name='usb_cam',
            parameters=[
                {'video_device': '/dev/video0'},
                {'image_width': 1280},#1280/480          3840/1080 #2560/720
                {'image_height': 480},
                {'pixel_format': 'mjpeg2rgb'},
                {'io_method': 'mmap'},
                {'framerate': 60.0},
                {'image_transport': 'ffmpeg'},
            ]
        ),

        Node(
            package='camera_utils',
            executable='splitter',
            name='stereo_splitter',
            output='screen'
        ),
    ])
