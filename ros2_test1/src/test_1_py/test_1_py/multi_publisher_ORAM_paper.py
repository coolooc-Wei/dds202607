import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from multiprocessing import Process,pool,Queue
import os
from test_1_py.pathORAM_test import ORAM
import json
import time
from sros_package.AES_tools import AES_tools

class MinimalPublisher(Node):

    def __init__(self,topic_name,sender_name,q):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, topic_name, 10000)
        self.topic_name = topic_name
        self.sender_name = sender_name
        self.q = q
        # print(f"publisher {self.topic_name = } {self.sender_name = } created")

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):

        if self.q.empty():
            return

        msg = String()
        msg.data = self.q.get()
        self.publisher_.publish(msg)

class ORAM_Node():

    def __init__(self,id,end_queue):
        self.id = id
        self.end_queue = end_queue
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

        self.AES_tools_dict = {}
        for id in self.id_list:
            key_path = f'kyber_keys/server/shared_secret_server_{id}.key'
            self.AES_tools_dict[id] = AES_tools(key_path)

        self.create_node()  
        self.start_process()
        self.test_process()
        


    def create_topic(self,topic_name,sender_name,q):


        print(f"{topic_name = }")
        
        print(f"topic: {topic_name} create")
        rclpy.init(args=None)
        minimal_publisher = MinimalPublisher(topic_name,sender_name,q)
        rclpy.spin(minimal_publisher)

        minimal_publisher.destroy_node()
        rclpy.shutdown()

    def create_node(self):

        id_list = self.data['id_list']

        # print(f"{id_list}")

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
                msg = Odometry()
                real_datas,fake_datas = self.AES_tools_dict[i].encrypt_obj_gcm_multi(msg,fake_num=len(nodes)-1)
                c = 0
                for node in nodes:
                    if node == ORAM_node:
                        self.q_list[node].put(real_datas)
                    # else:
                    #     self.q_list[node].put(fake_datas[c])
                    #     c += 1

        while True:
            if all([q.empty() for q in self.q_list]):
                print(f"all queue empty")
                break
        self.end_queue.put(f"node {self.id} end")

def start(num,end_queue):
    ORAM_Node(num,end_queue)

def main(args=None):

    # oram = ORAM(7, debug_mode=True)

    print(sys.argv)
    if len(sys.argv)!=2:
        print("need 1 topic numbers")
        exit(-100)
    # rclpy.init(args=args)

    topic_num = int(sys.argv[1])

    node_list = []
    end_queue = Queue()
    for num in range(topic_num):
        print(f"{num = }")
        p = Process(target=start,args=(num,end_queue,))
        node_list.append(p)

    start_time = time.time()
    for p in node_list:
        p.start()

    print("start waiting for all node end")
    while True:
        # print(f"{end_queue.qsize() = }")
        if end_queue.qsize() == topic_num:
            end_time = time.time() - start_time
            # time.sleep(5)
            print(f"all node end time: {end_time}")
            while not end_queue.empty():
                msg = end_queue.get()
                print(f"{msg = }")
            print(f"all node end")
            break

if __name__ == "__main__":
    main()
