import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from multiprocessing import Process,pool,Queue
import os

class MinimalSubscriber(Node):

    def __init__(self,topic_name,queue):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            topic_name,
            self.listener_callback,
            10000)
        self.subscription  # prevent unused variable warning
        self.queue = queue
        

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg)
        self.queue.put(msg)


def create_topic(topic_name,path):


    print(f"{topic_name = }")
    
    print(f"topic: {topic_name} create")
    rclpy.init(args=None)
    minimal_publisher = MinimalSubscriber(topic_name,path)
    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()

def create_file_saver(path,queue):
    
    with open(path,'a') as f:
        print(f"file saver create: {path}")
        while True:
            if not queue.empty():
                data = queue.get()
                print(f"file saver {path = } writing {data = }")
                f.write(data)
                f.write('\n')

def main(args=None):
    print(sys.argv)
    if len(sys.argv)!=2:
        print("need 1 topic numbers")
        exit(-100)
    # rclpy.init(args=args)

    topic_num = int(sys.argv[1])

    subscriber_list = []
    file_saver_list = []

    for num in range(topic_num):
        print(f"{num = }")
        q = Queue()
        p = Process(target=create_topic,args=(f"topic_{num}",q,))
        subscriber_list.append(p)
        p = Process(target=create_file_saver, args=(f'multi_node_datas/ord/topic_{num}.txt', q,))
        file_saver_list.append(p)

    for p in file_saver_list:
        p.start()

    for p in subscriber_list:
        p.start()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # minimal_publisher.destroy_node()
    # rclpy.shutdown()

if __name__ == "__main__":
    main()
