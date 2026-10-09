import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped


class NodeCenter(Node):

    def __init__(self):
        super().__init__('node_centered')

        self.scan_sub = self.create_subscription(LaserScan, '/lidar', self.scan_callback, 10)
        self.vel_pub = self.create_publisher(TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 10)

        self.stopped = False
        self.get_logger().info('Node Centering started succesfully')

    def scan_callback(self, msg: LaserScan):
        """ runs when a new lidar scan arrives """

        if not msg.ranges:
            return

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'

        total_beams = len(msg.ranges)
        right_distance = msg.ranges[int(total_beams * 0.25)]
        left_distance = msg.ranges[int(total_beams * 0.75)]
        front_distance = msg.ranges[total_beams // 2]

        if self.stopped or (math.isfinite(front_distance) and front_distance < 1.5):
            if not self.stopped:
                self.get_logger().info('End of corridor, stopping')
            self.stopped = True
            self.vel_pub.publish(cmd)
            return

        if not (math.isfinite(left_distance) and math.isfinite(right_distance)):
            return

        gain = 0.5
        error_total = left_distance - right_distance
        velocity = max(min(gain * error_total, 0.5), -0.5)

        self.get_logger().info(f'L : {left_distance:.2f} | R : {right_distance:.2f} | Error : {error_total:.2f} | Velocity : {velocity:.2f}')

        cmd.twist.linear.x = 0.3
        cmd.twist.linear.y = velocity
        self.vel_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = NodeCenter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()