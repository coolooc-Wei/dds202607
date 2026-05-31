import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Process,pool

class MinimalPublisher(Node):

    def __init__(self,nums):
        super().__init__('minimal_publisher')
        self.publishers_ = []
        for i in range(nums):
            publisher = self.create_publisher(String, f"topic_{i}", 100)
            self.publishers_.append(publisher)
        timer_period = 0.5  # seconds
        self.i_s = []
        for i in range(nums):
            self.i_s.append(0)

        self.timers_ = []
        for i in range(nums):
            timer = self.create_timer(timer_period, lambda num=i, topic_name=f"topic_{i}": self.timer_callback(num, topic_name))
            self.timers_.append(timer)

    def timer_callback(self, num, topic_name):
        msg = String()
        msg.data = f'{topic_name} Hello World: {self.i_s[num]}'
        self.publishers_[num].publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i_s[num] += 1
        subscription_count = self.publishers_[num].get_subscription_count()
        self.get_logger().info(f'Matched subscriptions count: {subscription_count}')


def main(args=None):
    print(sys.argv)
    if len(sys.argv) != 2:
        print("need topic num")
        exit(-100)
    # rclpy.init(args=args)

    nums = int(sys.argv[1])
    rclpy.init(args=None)
    minimal_publisher = MinimalPublisher(nums)
    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # minimal_publisher.destroy_node()
    # rclpy.shutdown()

if __name__ == "__main__":
    main()
