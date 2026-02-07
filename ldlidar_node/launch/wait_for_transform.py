#!/usr/bin/env python3
"""
Helper script to wait for a transform to be published before exiting.
This allows launch files to wait for frames rather than using arbitrary delays.
"""

import sys
import time
import rclpy
from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener


def wait_for_transform(source_frame: str, target_frame: str, timeout: float = 30.0) -> bool:
    """
    Wait for a transform to be published.
    
    Args:
        source_frame: Source frame name
        target_frame: Target/fixed frame name
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if transform found, False if timeout
    """
    rclpy.init()
    node = rclpy.create_node('wait_for_transform_node')
    
    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node)
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            tf_buffer.lookup_transform(target_frame, source_frame, rclpy.time.Time())
            node.get_logger().info(f"Transform from {source_frame} to {target_frame} found!")
            rclpy.shutdown()
            return True
        except TransformException as e:
            node.get_logger().debug(f"Waiting for transform: {e}")
            time.sleep(0.1)
    
    node.get_logger().error(f"Timeout waiting for transform from {source_frame} to {target_frame}")
    rclpy.shutdown()
    return False


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <source_frame> <target_frame> <timeout_seconds>")
        sys.exit(1)
    
    source = sys.argv[1]
    target = sys.argv[2]
    timeout = float(sys.argv[3])
    
    success = wait_for_transform(source, target, timeout)
    sys.exit(0 if success else 1)
