import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Process,pool,Queue
import os
from test_1_py.pathORAM_test import ORAM
import json
import time

class MinimalPublisher(Node):

    def __init__(self,topic_name,sender_name,q,path):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, topic_name, 10000)
        self.topic_name = topic_name
        self.sender_name = sender_name
        self.q = q
        self.path = path
        print(f"publisher {self.topic_name = } {self.sender_name = } created")

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):

        if self.q.empty():
            return

        
        msg = String()
        msg.data = f"{self.q.get()} from {self.sender_name}"
        self.publisher_.publish(msg)
        self.get_logger().info(f'{self.topic_name} {self.sender_name} send: {msg.data}')
        print(f"{self.topic_name} {self.sender_name} send: {msg.data}")
        with open(self.path,'a') as f:
            f.write(f'{self.topic_name} send: {msg.data}')
            f.write('\n')

class ORAM_Node():

    def __init__(self,id):
        self.id = id
        self.data = None
        with open(f'multi_node_datas/test_data_{self.id}.json', 'r') as f:
            self.data = json.load(f)
        print(f"{self.data}")
        self.q_list = []
        self.p_list = []
        self.id_list = self.data['id_list'].copy()
        self.ORAM = ORAM(len(self.id_list))
        self.ROS_node_to_ORAM_node = {}

        for ORAM_node,ROS_node in enumerate(self.id_list):
            print(ORAM_node,ROS_node)
            self.ROS_node_to_ORAM_node[ROS_node] = ORAM_node
        print(self.ROS_node_to_ORAM_node)

        self.create_node()  
        self.start_process()
        self.test_process()
        


    def create_topic(self,topic_name,sender_name,q):


        print(f"{topic_name = }")
        
        print(f"topic: {topic_name} create")
        rclpy.init(args=None)
        minimal_publisher = MinimalPublisher(topic_name,sender_name,q,f'multi_node_datas/sender_{sender_name}.txt')
        rclpy.spin(minimal_publisher)

        minimal_publisher.destroy_node()
        rclpy.shutdown()

    def create_node(self):

        id_list = self.data['id_list']

        print(f"{id_list}")

        for id in id_list:
            q = Queue()
            print(f"{id=} {q = }")
            p = Process(target=self.create_topic,args=(f"topic_{id}",self.id,q,))    
            self.q_list.append(q)
            self.p_list.append(p)
    
    def start_process(self):
        for p in self.p_list:
            p.start()

    def test_process(self):
        for t,i in enumerate(self.data['sends']):
            if i is not None:
                ORAM_node = self.ROS_node_to_ORAM_node[i]
                paths = self.ORAM.random_choose_two_path(ORAM_node)
                nodes = self.ORAM.get_ros_node_from_path(paths[0],paths[1])
                for node in nodes:
                    if node == ORAM_node:
                        self.q_list[node].put(f"{t} real")
                    else:
                        self.q_list[node].put(f"{t} fake")

def start_oram(num):
    ORAM_Node(num)

def main(args=None):

    # oram = ORAM(7, debug_mode=True)

    print(sys.argv)
    if len(sys.argv)!=2:
        print("need 1 topic numbers")
        exit(-100)
    # rclpy.init(args=args)

    topic_num = int(sys.argv[1])

    oram_list = []

    for num in range(topic_num):
        print(f"{num = }")
        p = Process(target=start_oram,args=(num,))
        oram_list.append(p)

    for p in oram_list:
        p.start()
    

if __name__ == "__main__":
    main()
