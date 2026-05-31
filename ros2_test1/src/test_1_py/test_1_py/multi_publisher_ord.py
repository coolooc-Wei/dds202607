import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from multiprocessing import Process,pool,Queue
import os
import json
import time
import pickle
import base64


class MinimalPublisher(Node):

    def __init__(self,topic_queue_list):
        super().__init__('minimal_publisher')
        self.publishers_ = []
        for topic_name, q in topic_queue_list:
            publisher = self.create_publisher(String, topic_name, 10000)
            self.publishers_.append((publisher, q))

        timer_period = 0.1  # seconds
        self.timers_ = []
        for publisher, q in self.publishers_:
            timer = self.create_timer(timer_period, lambda pub=publisher, queue=q: self.timer_callback(pub, queue))
            self.timers_.append(timer)

    def timer_callback(self, publisher, q):

        if q.empty():
            return
        
        msg = String()
        msg.data = q.get()
        publisher.publish(msg)

class Node():

    def __init__(self, id, end_queue):
        self.id = id
        self.end_queue = end_queue
        self.data = None
        with open(f'multi_node_datas/test_data_{self.id}.json', 'r') as f:
            self.data = json.load(f)
        print(f"{self.data}")
        self.q_list = []
        self.p_list = []
        self.id_list = self.data['id_list'].copy()
        self.ROS_node_to_ORAM_node = {}
        for ORAM_node,ROS_node in enumerate(self.id_list):
            print(ORAM_node,ROS_node)
            self.ROS_node_to_ORAM_node[ROS_node] = ORAM_node
        print(self.ROS_node_to_ORAM_node)

        self.create_node()  
        self.start_process()
        self.test_process()
        


    def create_topic(self,topic_queue_list):

        print(f"{topic_queue_list = }")
        rclpy.init(args=None)
        minimal_publisher = MinimalPublisher(topic_queue_list)
        rclpy.spin(minimal_publisher)

        minimal_publisher.destroy_node()
        rclpy.shutdown()

    def create_node(self):

        id_list = self.data['id_list']

        # print(f"{id_list}")

        topic_queue_list = []
        for id in id_list:
            q = Queue()
            print(f"{id=} {q = }")
            topic_name = f"topic_{id}"
            topic_queue_list.append((topic_name,q))
            self.q_list.append(q)

        p = Process(target=self.create_topic,args=(topic_queue_list,))    
        self.p_list.append(p)
    
    def start_process(self):
        for p in self.p_list:
            p.start()

    def test_process(self):
        for t,i in enumerate(self.data['sends']):
            if i is not None:
                ORAM_node = self.ROS_node_to_ORAM_node[i]
                msg = base64.b64encode(pickle.dumps(Odometry())).decode('utf-8')
                self.q_list[ORAM_node].put(msg)

        while True:
            if all([q.empty() for q in self.q_list]):
                print(f"all queue empty")
                break
        self.end_queue.put(f"node {self.id} end")
        

def start(num,end_queue):
    Node(num,end_queue)

def main(args=None):

    # oram = ORAM(7, debug_mode=True)

    print(sys.argv)
    if len(sys.argv)!=2:
        print("need 1 topic numbers")
        exit(-100)
    # rclpy.init(args=args)

    topic_num = int(sys.argv[1])

    oram_list = []
    end_queue = Queue()
    for num in range(topic_num):
        print(f"{num = }")
        p = Process(target=start,args=(num,end_queue,))
        oram_list.append(p)

    start_time = time.time()
    for p in oram_list:
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
