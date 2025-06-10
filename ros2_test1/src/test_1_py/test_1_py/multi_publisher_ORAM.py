import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Process,pool
import sys
import os
from test_1_py.pathORAM_test import ORAM

class MinimalPublisher(Node):

    def __init__(self,topic_name):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, topic_name, 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1
        
        subscription_count = self.publisher_.get_subscription_count()
        self.get_logger().info(f'Matched subscriptions count: {subscription_count}')

def create_topic(topic_name):


    print(f"{topic_name = }")
    
    print(f"topic: {topic_name} create")
    rclpy.init(args=None)
    minimal_publisher = MinimalPublisher(topic_name)
    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()

def main(args=None):

    oram = ORAM(7, debug_mode=True)

    print(sys.argv)
    if len(sys.argv)!=3:
        print("need 2 topic name")
        exit(-100)
    # rclpy.init(args=args)

    for i in range(2):
        p = Process(target=create_topic,args={sys.argv[1+i],})
        p.start()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # minimal_publisher.destroy_node()
    # rclpy.shutdown()

if __name__ == "__main__":
    # main()

    oram = ORAM(7, debug_mode=True)
