import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz_config = LaunchConfiguration('rviz_config')
    publish_default_joints = LaunchConfiguration('publish_default_joints')

    webots_share_dir = get_package_share_directory('webots_rosconfr')
    car_share_dir = get_package_share_directory('car_rosconfr')

    robot_description_path = os.path.join(
        webots_share_dir,
        'resource',
        'TT02_jaune.urdf',
    )
    default_rviz_config_path = os.path.join(
        car_share_dir,
        'rviz',
        'rviz2_car.rviz',
    )

    with open(robot_description_path, 'r', encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time},
        ],
        output='screen',
    )

    laser_alias_tf_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'laser_link',
            '--child-frame-id', 'laser',
        ],
        output='screen',
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time},
        ],
        condition=IfCondition(publish_default_joints),
        output='screen',
    )

    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Utiliser l horloge /clock si elle est disponible.',
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=default_rviz_config_path,
            description='Chemin vers le fichier de configuration RViz2.',
        ),
        DeclareLaunchArgument(
            'publish_default_joints',
            default_value='true',
            description='Publier des joint_states par defaut pour completer les TF du modele.',
        ),
        joint_state_publisher,
        robot_state_publisher,
        laser_alias_tf_publisher,
        rviz2,
    ])
