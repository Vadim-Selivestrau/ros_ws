from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
from visualization_msgs.msg import MarkerArray
import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from lifecycle_msgs.srv import ChangeState
import pdb
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterType
import subprocess
import os
from ament_index_python.packages import get_package_share_directory

class LocalizationManager(Node):
    def __init__(self):
        super().__init__('localization_manager')
        

        self.declare_parameter('amcl_threshold', 0.4)
        
        self.create_timer(0.5, self.check_state)
        self.state = 'INIT' # MAPPING LOCALIZATION LOCALIZED
        self.cov_sum = float('inf')
        self.start_time = None
        self.timeout = 5.0 
        self.amcl_threshold = self.get_parameter('amcl_threshold').value
        self.cli = self.create_client(Empty, '/reinitialize_global_localization')
        self.spin_timer = self.create_timer(0.1, self.spin_timer_callback)


        self.set_param_client = self.create_client(SetParameters, '/amcl/set_parameters')

        self.frontiers_sub = self.create_subscription(
            MarkerArray,
            '/explore/frontiers',
            self.frontiers_callback,
            10
        )

        self.amcl_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

    def check_state(self):
        # pdb.set_trace()
        self.get_logger().info(f'мы в чек стейте со стейтом {self.state}')

        if self.state == 'INIT':
            self.get_logger().info('мы в ините')
            self.start_localization()
        elif self.state == 'LOCALIZATION':
            if self.start_time is None: return
            now = self.get_clock().now().seconds_nanoseconds()[0]
            self.get_logger().info(f'{now - self.start_time}\t{self.timeout}\t{self.cov_sum}\t{self.amcl_threshold}')
            if now - self.start_time > self.timeout:
                self.get_logger().info('мы в маппинге')
                self.stop_rotation()
                self.state = 'MAPPING'
                self.mapping()
            elif self.cov_sum < self.amcl_threshold:
                self.get_logger().info('мы локализованЫЫЫ')
                self.stop_rotation()
                self.state = 'LOCALIZED'
                self.localization()
            else:
                self.get_logger().info('хммм')

    def spin_timer_callback(self):
        if self.state == 'LOCALIZATION':
            twist = Twist()
            twist.angular.z = 0.66
            self.cmd_pub.publish(twist)
        else:
            pass

    def stop_rotation(self):
        self.get_logger().info('СТОПНУТО')

        twist = Twist()
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)


    def start_localization(self):

        self.state = 'LOCALIZATION'
        self.get_logger().info('мы локализуемся')
        self.start_time = self.get_clock().now().seconds_nanoseconds()[0]

        req = Empty.Request()
        self.future = self.cli.call_async(req)
        self.get_logger().info('Called /global_localization')

        twist = Twist()
        twist.angular.z = 0.66
        self.get_logger().info('мы крутимся')
        self.cmd_pub.publish(twist)


            
    def localization(self):
        pass
    
    def start_slam_mapping(self):
        if hasattr(self, 'slam_process') and self.slam_process.poll() is None:
            self.get_logger().warn('SlamToolbox already running')
            return
        slam_launch = os.path.join(
            get_package_share_directory('robo_bringup'), 'launch', 'slam.launch.py'
        )
        self.slam_process = subprocess.Popen(
            ['ros2', 'launch', 'robo_bringup', 'slam.launch.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.get_logger().info('SlamToolbox mapping process started')

    def mapping(self):
        self.set_amcl_tf_broadcast(False)

        self.start_slam_mapping()
        self.start_explore()
        if self.count == 0:
            self.get_logger().info('эксплоринг закончен')
        # self.state = 'MAPPING'

    def frontiers_callback(self, msg):
        self.count = 0
        for marker in msg.markers:
            if marker.type == 2 and marker.color.g == 1.0:
                count += 1
        self.get_logger().info(f'Frontier centers: {count}')


    def amcl_callback(self, msg):
        self.cov_sum = msg.pose.covariance[0] + msg.pose.covariance[7] + msg.pose.covariance[35] # x, y, yaw
        

    def set_amcl_tf_broadcast(self, enable: bool):
        if not self.set_param_client.service_is_ready():
            self.get_logger().warn('set_parameters service not ready')
            return
        req = SetParameters.Request()
        param = Parameter()
        param.name = 'tf_broadcast'
        param.value.type = ParameterType.PARAMETER_BOOL
        param.value.bool_value = enable
        req.parameters = [param]
        future = self.set_param_client.call_async(req)
        future.add_done_callback(
            lambda f: self.get_logger().info(f'tf_broadcast set to {enable}')
        )

    def start_explore(self):
        if hasattr(self, 'explore_process') and self.explore_process.poll() is None:
            self.get_logger().warn('Explore already running')
            return
        self.explore_process = subprocess.Popen(
            [
                'ros2', 'run', 'explore_lite', 'explore',
                '--ros-args', '--params-file',
                '/home/jetson/ros2_ws/src/m-explore-ros2/explore/config/params.yaml'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )   
        self.get_logger().info('Explore lite started')

def main(args=None):
    rclpy.init(args=args)
    node = LocalizationManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()