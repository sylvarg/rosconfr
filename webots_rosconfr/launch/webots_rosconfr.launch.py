import os
import launch
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from ament_index_python.packages import get_package_share_directory
from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController


def generate_launch_description():
    package_dir = get_package_share_directory('webots_rosconfr')
    robot_description_path = os.path.join(
        package_dir, 'resource', 'TT02_jaune.urdf')
    with open(robot_description_path, 'r') as file:
        robot_description = file.read()

    webots = WebotsLauncher(
        world=os.path.join(package_dir, 'worlds',
                           'Piste_CoVAPSy_2025a.wbt'),
        mode='realtime',
        gui=True
    )

    robot_name = 'yellow_car' # must match the robot name in world file
    webots_bridge = WebotsController(
        robot_name=robot_name,  
        parameters=[{'robot_description': robot_description_path},],
        remappings=[
            ('__node', 'webots_bridge'),  # Change node name
        ],
        respawn=True,  # Respawn robot after simulation reset in Webots
        # respawn_delay=1.0
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=robot_name,
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True},
        ],
        output='screen',
    )

    # CoVAPSy_conduite = Node(
    #     package='monPaquetCoVAPSy',
    #     executable='CoVAPSy_conduite',
    # )

    shutdown_on_webots_exit = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=webots,
            on_exit=[
                EmitEvent(event=launch.events.Shutdown())
            ],
        )
    )

    return LaunchDescription([
        webots,
        webots_bridge,
        robot_state_publisher,
        # CoVAPSy_conduite,
        shutdown_on_webots_exit
    ])
