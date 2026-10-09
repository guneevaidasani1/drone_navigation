## idea is to keep distance of drone from left wall same as the distance to right wall

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped


class NodeCenter(Node):

    def __init__(self):

        super().__init__('node_centered')

        self.scan_sub = self.create_subscription(LaserScan,'/scan',self.scan_callback,10)

        self.vel_pub = self.create_publisher(TwistStamped,'/mavros/setpoint_velocity/cmd_vel',10)

        self.get_logger().info('Node Centering started succesfully')


    def scan_callback(self, msg : LaserScan):
        """ runs when a new lidar scan arrives """

        if not msg.ranges:
            return

        total_beams = len(msg.ranges)

        left_index = int(total_beams * 0.25)
        right_index = int(total_beams * 0.75)

        left_distance = msg.ranges[left_index]
        right_distance = msg.ranges[right_index]

        if left_distance < msg.range_min or left_distance > msg.range_max:
            left_distance = 1.0
        if right_distance < msg.range_min or right_distance > msg.range_max:
            right_distance = 1.0

        gain = 0.5
        error_total = right_distance - left_distance
        velocity = gain * error_total

        velocity = max(min(velocity , 0.5),-0.5)

        self.get_logger().info(f'L : {left_distance} | R : {right_distance} | Error : {error_total} | Velocity : {velocity}')

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'

        cmd.twist.linear.x = 0.3
        cmd.twist.linear.y = velocity
        self.vel_pub.publish(cmd)

def main(args = None):
    rclpy.init(args = args)
    node = NodeCenter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass 
    finally:
        node.destroy_node()
        rclpy.shutdown()


