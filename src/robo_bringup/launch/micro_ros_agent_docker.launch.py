#docker run -it --rm -v /dev:/dev --privileged --net=host microros/micro-ros-agent:humble serial --dev /dev/ttyACM0


from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        ExecuteProcess(
            cmd=[
                'docker', 'run',
                '--rm',
                '--net=host',
                '--privileged',
                '-v', '/dev:/dev',
                'microros/micro-ros-agent:humble',
                'serial', '--dev', '/dev/ttyACM0', '-b', '115200'
            ],
            output='screen'
        )
    ])
