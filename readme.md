# Localization Manager — Документация

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