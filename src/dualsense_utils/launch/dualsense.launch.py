from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='dualsense_utils',
            executable='handler_node',
            name='dualsense_handler',
            output='screen'
        )
    ])
