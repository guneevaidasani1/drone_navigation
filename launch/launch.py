import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('corridor_navigation')
    world = os.path.join(pkg, 'worlds', 'corridor_world.sdf')  

    gz = ExecuteProcess(cmd=['gz', 'sim', '-v4', '-r', world], output='screen')

    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=['/lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                   '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen')

    mavros = ExecuteProcess(
        cmd=['ros2', 'launch', 'mavros', 'apm.launch',
             'fcu_url:=udp://127.0.0.1:14551@'],
        output='screen')

    centering = Node(
        package='corridor_navigation', executable='centering_node',
        output='screen')

    return LaunchDescription([gz, bridge, mavros])