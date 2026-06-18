from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import os


def generate_launch_description():
    
    pkg_share = get_package_share_directory('robo_bringup')
    slam_config_path = os.path.join(pkg_share, 'config/slam/', 'mapper_params_online_async.yaml')


    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            parameters=[
                slam_config_path,
                {
                'use_sim_time': False,
                'odom_frame': 'odom',        
                'base_frame': 'base_footprint',  
                'scan_topic': '/scan',       
                'mode': 'mapping' #'localization'            
            }],

            remappings=[
                ('scan', '/scan'),
                ('/odom', '/odometry/filtered'),
            ],
            output='screen'

        )
    ])
