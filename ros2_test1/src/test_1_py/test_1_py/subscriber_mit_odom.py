import os
import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from nav_msgs.msg import Odometry

class MinimalSubscriber(Node):
    inf = float('inf')
    t = 0
    x = 0   
    y = 0
    z = 0
    lx = 0
    ly = 0
    lz = 0
    x_min = inf
    y_min = inf
    z_min = inf
    x_max = -inf
    y_max = -inf
    z_max = -inf
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            'unitree_go2_1/odom',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.t += 1
        self.x += (dx := msg.pose.pose.position.x-self.lx)
        self.y += (dy := msg.pose.pose.position.y-self.ly)
        self.z += (dz := msg.pose.pose.position.z-self.lz)

        lx = msg.pose.pose.position.x
        ly = msg.pose.pose.position.y
        lz = msg.pose.pose.position.z

        self.x_min = min(self.x_min, lx)
        self.y_min = min(self.y_min, ly)
        self.z_min = min(self.z_min, lz)

        self.x_max = max(self.x_max, lx)
        self.y_max = max(self.y_max, ly)
        self.z_max = max(self.z_max, lz)
        
        # self.get_logger().info(f"avg: ({self.x/self.t}, {self.y/self.t}, {self.z/self.t}) min: ({self.x_min}, {self.y_min}, {self.z_min}) max: ({self.x_max}, {self.y_max}, {self.z_max})")

        self.get_logger().info(f"I heard: {msg = }")
        # if not os.path.exists('data/'):
        #     os.makedirs('data/')
        with open('data/mit_lab_data/unitree_go2_1_odom.txt', 'a') as f:
            f.write(f"{msg}\n")

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()