import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Process,pool

class MinimalSubscriber(Node):

    def __init__(self,topic_name,path):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            topic_name,
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.path = path
        

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
        with open(self.path,'a') as f:
            f.write(msg.data)
            f.write('\n')


def create_topic(topic_name,path):


    print(f"{topic_name = }")
    
    print(f"topic: {topic_name} create")
    rclpy.init(args=None)
    minimal_publisher = MinimalSubscriber(topic_name,path)
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
        p = Process(target=create_topic,args=(f"topic_{num}",f'multi_node_datas/topic_{num}.txt',))
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
