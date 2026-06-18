
from launch import LaunchDescription
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    left_rectify_node = ComposableNode(
        name='left_rectify_node',
        package='isaac_ros_image_proc',
        plugin='nvidia::isaac_ros::image_proc::RectifyNode',
        parameters=[{
            'output_width': 640, #1280,
            'output_height': 480, #720,
        }],
        remappings=[
            ('image_raw', 'camera/left/image_raw'),
            ('camera_info', 'camera/left/camera_info'),
            ('image_rect', 'camera/left/image_rect'),
            ('camera_info_rect', 'camera/left/camera_info_rect')
        ]
    )
    

    right_rectify_node = ComposableNode(
        name='right_rectify_node',
        package='isaac_ros_image_proc',
        plugin='nvidia::isaac_ros::image_proc::RectifyNode',
        parameters=[{
            'output_width': 640, #1280,
            'output_height': 480, #720,
        }],
        remappings=[
            ('image_raw', 'camera/right/image_raw'),
            ('camera_info', 'camera/right/camera_info'),
            ('image_rect', 'camera/right/image_rect'),
            ('camera_info_rect', 'camera/right/camera_info_rect')
        ]
    )

    left_resize_node = ComposableNode(
        name='left_resize',
        package='isaac_ros_image_proc',
        plugin='nvidia::isaac_ros::image_proc::ResizeNode',
        parameters=[{
            'output_width': 960,
            'output_height': 576,
            'keep_aspect_ratio': False,
        }],
        remappings=[
            ('camera_info', 'camera/left/camera_info_rect'),
            ('image', 'camera/left/image_rect'),
            ('resize/camera_info', 'camera/left/camera_info_resize'),
            ('resize/image', 'camera/left/image_resize')
        ]
    )

    right_resize_node = ComposableNode(
        name='right_resize',
        package='isaac_ros_image_proc',
        plugin='nvidia::isaac_ros::image_proc::ResizeNode',
        parameters=[{
            'output_width': 960,
            'output_height': 576,
            'keep_aspect_ratio': False,
        }],
        remappings=[
            ('camera_info', 'camera/right/camera_info_rect'),
            ('image', 'camera/right/image_rect'),
            ('resize/camera_info', 'camera/right/camera_info_resize'),
            ('resize/image', 'camera/right/image_resize')
        ]
    )

    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'tracking_mode': 0, # 0 = Multicamera (Visual only, no IMU)
            'num_cameras': 2,

            'rectified_images': True,
            'base_frame': 'base_footprint',

            'camera_optical_frames': [
                'left_optical_frame',
                'right_optical_frame'
            ],
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,


            'publish_map_to_odom_tf': False,
            'publish_odom_to_base_tf': False,

            # for 2D Mode
            'enable_planar_mode': True,

            'enable_ground_constraint_in_odometry': True,
            'enable_ground_constraint_in_slam': True,
            'force_planar_mode': True,
            'enable_localization_n_mapping': False,

            #IMU SETTINGS
            # 'enable_imu_fusion': True,
            # 'imu_frame': 'base_link',

            #MASK SETTINGS
            'img_mask_bottom': int(480 * 0.25),
            # 'img_mask_up': int(480 * 0.1),
        }],
        remappings=[
            ('visual_slam/image_0', 'camera/left/image_rect'),
            ('visual_slam/camera_info_0', 'camera/left/camera_info_rect'),
            ('visual_slam/image_1', 'camera/right/image_rect'),
            ('visual_slam/camera_info_1', 'camera/right/camera_info_rect'),
            # ('visual_slam/imu', 'fake_imu')
        ]
    )
    
    ess_disparity_node = ComposableNode(
        name='ess_disparity',
        package='isaac_ros_ess',
        plugin='nvidia::isaac_ros::dnn_stereo_depth::ESSDisparityNode',
        parameters=[{
            'engine_file_path': '/home/jetson/ros2_ws/isaac_ros-dev/isaac_ros_assets/models/dnn_stereo_disparity/dnn_stereo_disparity_v4.1.0_onnx/ess.engine',
            'threshold': 0.4,
            'input_layer_width': 960,
            'input_layer_height': 576,
        }],
        remappings=[
            ('left/image_rect', 'camera/left/image_resize'),
            ('right/image_rect', 'camera/right/image_resize'),
            ('left/camera_info', 'camera/left/camera_info_resize'),
            ('right/camera_info', 'camera/right/camera_info_resize'),
            ('disparity', 'camera/disparity')
        ]
    )

    disparity_to_depth_node = ComposableNode(
        name='disparity_to_depth_node',
        package='isaac_ros_stereo_image_proc',
        plugin='nvidia::isaac_ros::stereo_image_proc::DisparityToDepthNode',
        remappings=[
            ('disparity', 'camera/disparity'),
            ('depth', 'camera/depth/image_rect_raw')
        ]
    )

    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        parameters=[{
            'global_frame': 'odom',
            'voxel_size': 0.05,         # Resolution of the 3D map (meters)
            'esdf_mode': '2d',          # Generates a 2D slice for navigation
        }],
        remappings=[
            ('camera_0/depth/image', 'camera/depth/image_rect_raw'),
            ('camera_0/depth/camera_info', 'camera/left/camera_info_rect'),
            ('camera_0/color/image', 'camera/left/image_rect'),
            ('camera_0/color/camera_info', 'camera/left/camera_info_rect'),
        ]
    )
    
    container = ComposableNodeContainer(
        name='visual_slam_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[

            left_rectify_node, 
            right_rectify_node, 
            visual_slam_node,
            left_resize_node,
            right_resize_node,
            # ess_disparity_node,
            # disparity_to_depth_node,
            
            # nvblox_node
        ],
        output='screen'
    )

    return LaunchDescription([container])
