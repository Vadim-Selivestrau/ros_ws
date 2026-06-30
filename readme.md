# Camera utils 
сплиттер для стереокамеры, в данный момент не используется

# Dualsense utils 
нода для отправки команд на cmd_vel посредством dualsense, в данный момент не используется

# fake imu 
имитация инерциального датчика, принимающего одометрию, в данный момент не используется

# robo bringup
launch-файл, который запускает все необходимые узлы и компоненты робота: лидар, стереокамеру, трансформации, RTSP-потоки, одометрию, EKF, rosbridge и веб-интерфейс.

| Компонент | Тип запуска | Источник | Назначение |
|-----------|-------------|----------|------------|
| **Лидар** | IncludeLaunch | `ydlidar_ros2_driver/launch/ydlidar_launch.py` | Запуск драйвера 2D-лидара |
| **Стереокамера** | IncludeLaunch | `camera_utils/launch/stereo_proc.launch.py` | Обработка стереоизображений |
| **Micro-ROS Agent** | IncludeLaunch | `robo_bringup/launch/micro_ros_agent_docker.launch.py` | Связь с микроконтроллером (STM32/ESP32) |
| **Трансформации (URDF)** | IncludeLaunch | `transforms_urdf/launch/transforms.launch.py` | Публикация tf-фреймов робота |
| **RTSP-потоки** | IncludeLaunch | `rtsp_streamer/launch/stream.launch.py` | Трансляция видео по RTSP |
| **odom_fixer** | Node | `robo_bringup/odom_fixer.py` | Фильтрация и коррекция одометрии с гусениц |
| **vslam_fixer** | Node | `robo_bringup/vslam_fixer.py` | Фильтрация одометрии от V-SLAM |
| **EKF (robot_localization)** | Node | `robot_localization/ekf_node` | Слияние данных сенсоров (одометрия + IMU) |
| **Rosbridge** | IncludeLaunch (XML) | `rosbridge_server/launch/rosbridge_websocket_launch.xml` | WebSocket-мост для внешних приложений |
| **HTTP-сервер** | ExecuteProcess | `python3 -m http.server 8000` | Веб-интерфейс (./www) |

# rtsp streamer
Узел rtsp_multi_streamer транслирует три RTSP-потока (панорама, левая, правая камеры) из ROS-топиков с изображениями.
|Поток|	URL|	ROS-топик|
|-----|----|-------------|
|Панорама|	rtsp://<IP>:8554/stream	/camera/image_raw|
|Левый|	rtsp://<IP>:8554/stream_left	/camera/left/image_raw|
|Правый|	rtsp://<IP>:8554/stream_right	/camera/right/image_raw|

# transforms urdf
описывает структуру, визуализацию и системы координат робота
| Фрейм | Описание | Родитель |
|-------|----------|----------|
| `base_footprint` | Проекция центра робота на пол | – |
| `base_link` | центр робота | `base_footprint` |
| `laser_frame` | Лидар | `base_link` |
| `camera_link` | корпус камеры | `base_link` |
| `left_optical_frame` | Оптический центр левой камеры  | `camera_link` |
| `right_optical_frame` | Оптический центр правой камеры | `camera_link` |

# Localization Manager 

Узел `localization_manager` управляет конечным автоматом для локализации, маппинга и исследования робота. Он координирует работу AMCL, SlamToolbox и explore_lite, автоматически переключаясь между режимами.

## Назначение

- Запускает Nav2 со стартовой картой.
- Пытается локализоваться (вращение + AMCL).
- При неудаче — переключается в маппинг (SlamToolbox + explore_lite).
- Завершает исследование по фронтирам или таймауту.
- Сохраняет построенную карту и перезапускает Nav2 с ней.

## Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `amcl_threshold` | float | `0.4` | Порог суммы ковариаций (x, y, yaw) для перехода в `LOCALIZED` |
| `exploration_timeout` | int | `300` | Максимальное время исследования (сек) |

## Состояния (FSM)

| Состояние | Описание |
|-----------|----------|
| `INIT` | Начальное состояние. Запускается Nav2, затем переход в `LOCALIZATION`. |
| `LOCALIZATION` | Активная локализация. Робот вращается, AMCL разбрасывает частицы. |
| `LOCALIZED` | Успешная локализация. Робот готов к навигации. |
| `MAPPING` | Режим построения карты. SlamToolbox + explore_lite активны. |

**Переходы:**
- `INIT` → `LOCALIZATION` (автоматически)
- `LOCALIZATION` → `LOCALIZED` (ковариация < `amcl_threshold`)
- `LOCALIZATION` → `MAPPING` (таймаут локализации 5 сек)
- `MAPPING` → `LOCALIZED` (фронтиры == 0 ИЛИ таймаут исследования)

##  Карты

| Карта | Путь | Назначение |
|-------|------|------------|
| Стартовая | `/home/jetson/ros2_ws/ofice_map/map_1781274690.yaml` | Локализация при старте |
| Новая (сохраняемая) | `/home/jetson/ros2_ws/maps/current_map.yaml` | Сохраняется при завершении маппинга |

## Топики и сервисы

**Подписки:**

| Топик | Тип | Описание |
|-------|-----|----------|
| `/amcl_pose` | `PoseWithCovarianceStamped` | Ковариация для проверки локализации |
| `/explore/frontiers` | `MarkerArray` | Фронтиры для завершения исследования |

**Публикации:**

| Топик | Тип | Описание |
|-------|-----|----------|
| `/cmd_vel` | `Twist` | Управление движением (вращение) |
| `/explore/resume` | `Bool` | Управление паузой исследования |

**Сервисы:**

| Сервис | Тип | Назначение |
|--------|-----|------------|
| `/reinitialize_global_localization` | `Empty` | Перезапуск AMCL (разброс частиц) |
| `/slam_toolbox/save_map` | `SaveMap` | Сохранение построенной карты |
| `/amcl/set_parameters` | `SetParameters` | Управление параметром `tf_broadcast` |


## Описание методов

- `start_nav2(map_path)` — запускает Nav2 с указанной картой через `subprocess`.
- `stop_nav2()` — останавливает Nav2 (принудительно через 5 сек).
- `check_state()` — таймер 0.5 с. Обрабатывает переходы между состояниями FSM.
- `spin_timer_callback()` — таймер 0.1 с. Публикует вращение в `LOCALIZATION`.
- `start_localization()` — переключает в `LOCALIZATION`, вызывает `global_reinitialize()`, начинает вращение.
- `global_reinitialize()` — вызывает сервис AMCL `/reinitialize_global_localization`.
- `amcl_callback(msg)` — обновляет `cov_sum` = covariance[0] + covariance[7] + covariance[35].
- `mapping()` — переключает в `MAPPING`, отключает `tf_broadcast` AMCL, запускает SlamToolbox и explore_lite.
- `start_slam_mapping()` — запускает `slam.launch.py` через `subprocess`.
- `start_explore()` — запускает explore_lite с параметрами из YAML.
- `frontiers_callback(msg)` — считает фронтиры из `/explore/frontiers`.
- `finish_mapping()` — сохраняет карту, останавливает explore и slam, перезапускает Nav2 с новой картой, вызывает реинициализацию AMCL.
- `save_map()` — сохраняет карту через сервис `/slam_toolbox/save_map` в `/home/jetson/ros2_ws/maps/current_map`.
- `set_amcl_tf_broadcast(enable)` — включает/отключает публикацию трансформа `map→odom` у AMCL.
- `stop_rotation()` — публикует нулевой Twist.
- `localization()` — заглушка.



# внешние зависимости
m-explore-ros2
rf2o-laser odometry
ydlidar driver

порядок запуска
ros2 launch walle_camera camera.launch.py camera_ns:=camera
ros2 launch robo_bringup robo.launch.py
ros2 run localization_manager localization_manager