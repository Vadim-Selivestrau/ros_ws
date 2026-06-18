#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion

class FakeIMU(Node):
    def __init__(self):
        super().__init__("fake_imu_publisher")

        # === 1. Параметры узла ===
        self.declare_parameter("imu_topic", "/fake_imu")
        self.declare_parameter("odom_topic", "/odom_fixed")
        self.declare_parameter("frame_id", "base_link")
        self.declare_parameter("linear_covariance", 0.001)
        self.declare_parameter("angular_covariance", 0.001)

        self.imu_topic = self.get_parameter("imu_topic").get_parameter_value().string_value
        self.odom_topic = self.get_parameter("odom_topic").get_parameter_value().string_value
        self.frame_id = self.get_parameter("frame_id").get_parameter_value().string_value
        self.linear_cov = self.get_parameter("linear_covariance").get_parameter_value().double_value
        self.angular_cov = self.get_parameter("angular_covariance").get_parameter_value().double_value

        # === 2. Издатели ===
        self.imu_publisher_ = self.create_publisher(Imu, self.imu_topic, 10)

        # === 3. Подписчики ===
        self.odom_subscriber_ = self.create_subscription(
            Odometry, self.odom_topic, self.odom_callback, 10
        )

        # === 4. Внутренние переменные ===
        self.prev_time_sec = None
        self.prev_linear_vel = 0.0
        self.prev_angular_vel = 0.0

        # Раздельные матрицы ковариации
        self.lin_cov_matrix = [0.0] * 9
        self.lin_cov_matrix[0] = self.linear_cov
        self.lin_cov_matrix[4] = self.linear_cov
        self.lin_cov_matrix[8] = self.linear_cov

        self.ang_cov_matrix = [0.0] * 9
        self.ang_cov_matrix[0] = self.angular_cov
        self.ang_cov_matrix[4] = self.angular_cov
        self.ang_cov_matrix[8] = self.angular_cov

        self.get_logger().info(f"FakeIMU узел запущен. Ожидает одометрию из {self.odom_topic}")

    def odom_callback(self, msg: Odometry):
        current_stamp = msg.header.stamp
        current_time_sec = current_stamp.sec + current_stamp.nanosec * 1e-9

        current_linear_vel = msg.twist.twist.linear.x
        current_angular_vel = msg.twist.twist.angular.z

        if self.prev_time_sec is None:
            self.prev_time_sec = current_time_sec
            self.prev_linear_vel = current_linear_vel
            self.prev_angular_vel = current_angular_vel
            return

        dt = current_time_sec - self.prev_time_sec
        
        if dt <= 0.0:
            self.get_logger().warn("dt <= 0, пропускаю сообщение")
            # Обновляем время, чтобы не застрять в бесконечном пропуске
            self.prev_time_sec = current_time_sec 
            return

        # Вычисление ускорений
        linear_acc = (current_linear_vel - self.prev_linear_vel) / dt

        # Формируем IMU-сообщение
        imu_msg = Imu()
        imu_msg.header = msg.header
        imu_msg.header.frame_id = self.frame_id

        # Линейное ускорение + гравитация по Z
        imu_msg.linear_acceleration.x = linear_acc
        imu_msg.linear_acceleration.y = 0.0
        imu_msg.linear_acceleration.z = 9.80665 

        # Угловая скорость
        imu_msg.angular_velocity.x = 0.0
        imu_msg.angular_velocity.y = 0.0
        imu_msg.angular_velocity.z = current_angular_vel

        # Берем реальную ориентацию из одометрии, чтобы не было конфликтов данных
        imu_msg.orientation = msg.pose.pose.orientation

        # Ковариации
        imu_msg.linear_acceleration_covariance = self.lin_cov_matrix
        imu_msg.angular_velocity_covariance = self.ang_cov_matrix
        
        # Ковариацию ориентации можно скопировать из одометрии (угловую часть вокруг Z)
        # или оставить дефолтной, раз мы её транслируем
        imu_msg.orientation_covariance = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001]

        self.imu_publisher_.publish(imu_msg)

        # Сохраняем состояние для следующего шага
        self.prev_time_sec = current_time_sec
        self.prev_linear_vel = current_linear_vel
        self.prev_angular_vel = current_angular_vel

def main(args=None):
    rclpy.init(args=args)
    node = FakeIMU()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()