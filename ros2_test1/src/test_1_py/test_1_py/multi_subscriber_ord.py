import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from multiprocessing import Process,pool,Queue
import os
import base64
import pickle

class MinimalSubscriber(Node):

    def __init__(self,topic_name):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            topic_name,
            self.listener_callback,
            10000)
        self.subscription  # prevent unused variable warning
        

    def listener_callback(self, msg):
        data = pickle.loads(base64.b64decode(msg.data))
        self.get_logger().info(f'data: {data}')
        # self.queue.put(msg)


def create_topic(topic_name):


    print(f"{topic_name = }")
    
    print(f"topic: {topic_name} create")
    rclpy.init(args=None)
    minimal_publisher = MinimalSubscriber(topic_name)
    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()


def main(args=None):
    print(sys.argv)
    if len(sys.argv)!=2:
        print("need 1 topic numbers")
        exit(-100)
    # rclpy.init(args=args)

    topic_num = int(sys.argv[1])

    subscriber_list = []

    for num in range(topic_num):
        print(f"{num = }")
        p = Process(target=create_topic,args=(f"topic_{num}",))
        subscriber_list.append(p)


    for p in subscriber_list:
        p.start()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # minimal_publisher.destroy_node()
    # rclpy.shutdown()

if __name__ == "__main__":
    main()
