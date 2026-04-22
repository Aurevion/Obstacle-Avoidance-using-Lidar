import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class SafetyNode(Node):
    def __init__(self):
        super().__init__('safety_node')

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.threshold = 0.2

    def scan_callback(self, msg):
        valid_ranges = [r for r in msg.ranges if 0.1 < r < 100.0]  # Filter noise
        if not valid_ranges:
            return

        min_dist = min(valid_ranges)
        print(f"Min distance: {min_dist}")

        cmd = Twist()

        if min_dist < self.threshold:
            cmd.linear.x = 0.0
        else:
            cmd.linear.x = 0.2

        self.pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = SafetyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()