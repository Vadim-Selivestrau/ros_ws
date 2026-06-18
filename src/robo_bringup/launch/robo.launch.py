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
    joy_launch = os.path.join(
        get_package_share_directory('robo_bringup'), 'launch', 'joy.launch.py'
    )
    dualsense_launch = os.path.join(
        get_package_share_directory('dualsense_utils'), 'launch', 'dualsense.launch.py'
    )
    slam_launch = os.path.join(
        get_package_share_directory('robo_bringup'), 'launch', 'slam.launch.py'
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


    rf2o = os.path.join(
        get_package_share_directory('rf2o_laser_odometry'), 'launch', 'rf2o_laser_odometry.launch.py'
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
    global_localizator_node = Node(
        package='robo_bringup',
        executable='global_localizator.py',
        name='global_localizator_fix',
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

    mjpeg_proxy_cmd = ExecuteProcess(
        cmd=['python3', 'mjpeg_proxy.py'],
        cwd='/home/jetson/ros2_ws/www',
        output='screen'
    )





    # Запуск сервера карт
    map_server_cmd = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': '/home/jetson/ros2_ws/ofice_map/map_1781274690.yaml'}, 
                    {'use_sim_time': False}]
    )

    # Запуск навигационного стека
    nav2_bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py'
        )),
        launch_arguments={
            'map': '/home/jetson/ros2_ws/ofice_map/map_1781274690.yaml',
            'params_file': '/home/jetson/ros2_ws/src/robo_bringup/config/nav2/nav2_params.yaml',
            'use_sim_time': 'False'
        }.items()
    )



    return LaunchDescription([
        odom_fixer_node,
        IncludeLaunchDescription(PythonLaunchDescriptionSource(urdf_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(micro_ros_docker_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(lidar_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(camera_launch)),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(rtsp_launch)),
        # IncludeLaunchDescription(PythonLaunchDescriptionSource(rf2o)),
        
        vslam_fixer_node,
        ekf_node,

        # IncludeLaunchDescription(PythonLaunchDescriptionSource(slam_launch)),
        IncludeLaunchDescription(XMLLaunchDescriptionSource(rosbridge_launch)),
        http_server_cmd,
        # map_server_cmd,
        # nav2_bringup_cmd,
        # global_localizator_node,
    ])
