# Copyright 2024 Walter Lucetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###########################################################################

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    
    node_name = LaunchConfiguration('node_name')

    # Launch arguments
    declare_node_name_cmd = DeclareLaunchArgument(
        'node_name',
        default_value='ldlidar_node',
        description='Name of the node'
    )

    # RVIZ2 settings
    rviz2_config = os.path.join(
        get_package_share_directory('ldlidar_node'),
        'config',
        'both_lidar_simple.rviz'  # Using simple config to avoid potential segfault issues
    )

    # RVIZ2 node
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[["-d"], [rviz2_config]]
    )

    # Note: `robot_state_publisher` is launched inside each bringup include
    # (ldlidar_bringup.launch.py). Do not start an additional global rsp here
    # to avoid duplicate node names and TF conflicts.


    # Include LDLidar with lifecycle manager launch
    ldlidar_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('ldlidar_node'),
            '/launch/ldlidar_with_mgr.launch.py'
        ]),
        launch_arguments={
            'node_namespace': '',
            'node_name': node_name
        }.items()
    )

    # Include LDLidar with lifecycle manager launch
    ldlidar2_launch = IncludeLaunchDescription(
        launch_description_source=PythonLaunchDescriptionSource([
            get_package_share_directory('ldlidar_node'),
            '/launch/ldlidar2_with_mgr.launch.py'
        ]),
        launch_arguments={
            'node_namespace': 'ldlidar2',
            'node_name': 'ldlidar2_node'
        }.items()
    )

    # Define LaunchDescription variable
    ld = LaunchDescription()

    # Launch arguments
    ld.add_action(declare_node_name_cmd)

    # Call LDLidar launch first
    ld.add_action(ldlidar_launch)
    ld.add_action(ldlidar2_launch)

    # Launch odom_puller which reads odometry and broadcasts odom -> ldlidar_base
    odom_puller_node = Node(
        package='py_pubsub',
        executable='odom_puller',
        name='odom_puller',
        output='screen'
    )
    ld.add_action(odom_puller_node)

    # Delay RViz2 start to allow lidar nodes to initialize properly
    # Increase this delay if frames still aren't ready
    ld.add_action(TimerAction(period=5.0, actions=[rviz2_node]))


    return ld
