#!/bin/bash
source /opt/ros/humble/setup.bash
cd /home/jetson/ros2_ws
source install/setup.bash


ros2 launch walle_camera camera.launch.py camera_ns:=camera > /home/jetson/ros2_ws/launch_logs/camera.log 2>&1 &
PID_CAM=$!

ros2 launch robo_bringup robo.launch.py > /home/jetson/ros2_ws/launch_logs/bringup.log 2>&1 &
PID_ROBO=$!

# ros2 launch nav2_bringup bringup_launch.py \
#   use_sim_time:=False \
#   map:=/home/jetson/ros2_ws/ofice_map/map_1781274690.yaml \
#   params_file:=/home/jetson/ros2_ws/src/robo_bringup/config/nav2/nav2_params.yaml \
#   slam:=False > /home/jetson/ros2_ws/launch_logs/nav2.log 2>&1 &
# PID_NAV=$!

# echo "Ожидание появления сервиса локализации..."
# until ros2 service list 2>/dev/null | grep "/reinitialize_global_localization" > /dev/null; do
#     sleep 1
# done

# ros2 service call /reinitialize_global_localization std_srvs/srv/Empty {}

# echo "Старт цикла проверки amcl_pose..."
# while true; do
#   POSE=$(ros2 topic echo --once /amcl_pose geometry_msgs/msg/PoseWithCovarianceStamped 2>/dev/null)
#   X=$(echo "$POSE" | grep -A 3 "position:" | grep "x:" | awk '{print $2}')
  
#   if [ ! -z "$X" ]; then
#     echo "Текущий X: $X"
#     if (( $(echo "$X < 1.5" | bc -l) )); then
#       echo "Порог достигнут ($X < 1.5). Остановка вращения."
#       for i in {1..3}; do
#         ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
#         sleep 0.1
#       done
#       break
#     fi
#   fi
  
#   ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.5}}"
#   sleep 0.1
# done


wait $PID_CAM $PID_ROBO # $PID_NAV
