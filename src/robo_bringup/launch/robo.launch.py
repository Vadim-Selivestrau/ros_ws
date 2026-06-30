from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():
    lidar_launch = os.path.join(
        get_package_share_directory('ydlidar_ros2_driver'), 'launch', 'ydlidar_launch.py'
    )
    camera_launch = os.path.join(
        get_package_share_directory('camera_utils'), 'launch', 'stereo_proc.launch.py'
    )
    micro_ros_docker_launch = os.path.join(
        get_package_share_directory('robo_bringup'), 'launch', 'micro_ros_agent_docker.launch.py'
    )
    urdf_launch = os.path.join(
        get_package_share_directory('transhorms_urdf'), 'launch', 'transforms.launch.py'
    )
    rtsp_launch = os.path.join(
        get_package_share_directory('rtsp_streamer'), 'launch', 'stream.launch.py'
    )
    
    rosbridge_launch = os.path.join(
        get_package_share_directory('rosbridge_server'), 'launch', 'rosbridge_websocket_launch.xml'
    )






    vslam_fixer_node = Node(
        package='robo_bringup',
        executable='vslam_fixer.py',
        name='vslam_fixer_fix',
        output='screen'
    )


    odom_fixer_node = Node(
        package='robo_bringup',
        executable='odom_fixer.py',
        name='odom_fixer_fix',
        output='screen'
    )
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            '/home/jetson/ros2_ws/src/robo_bringup/config/ekf/ekf.yaml'
        ]
    )

    http_server_cmd = ExecuteProcess(
        cmd=['python3', '-m', 'http.server', '8000'],
        cwd='/home/jetson/ros2_ws/www',
        output='screen'
    )


    return LaunchDescription([
        odom_fixer_node,
        IncludeLaunchDescription(PythonLaunchDescriptionSource(urdf_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(micro_ros_docker_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(lidar_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(camera_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(rtsp_launch)),
        
        vslam_fixer_node,
        ekf_node,

        IncludeLaunchDescription(XMLLaunchDescriptionSource(rosbridge_launch)),
        http_server_cmd,
        
    ])