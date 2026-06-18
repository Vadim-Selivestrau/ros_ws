from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rtsp_streamer',
            executable='stream_node',
            name='rtsp_streamer'
        )
    ])
