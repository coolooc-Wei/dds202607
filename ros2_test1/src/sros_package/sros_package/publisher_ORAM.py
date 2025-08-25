import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Process, pool, Queue
from sros_package.pathORAM import ORAM
from sros_package.AES_topic import AES_publisher
from sros_package.AES_tools import AES_tools

class ORAM_Node():

    def __init__(self, topic_list: list, key_path: str,target:str):
        self.topic_list = topic_list
        self.key_path = key_path
        self.target = target
        self.topic_to_queue = {}
        self.process_list = []
        self.aes = AES_tools(self.key_path)
        self.ORAM = ORAM(len(self.topic_list))
        self.topic_name_to_ORAM_node = {}
        self.ORAM_node_to_topic_name = {}
        for ORAM_node,topic_name in enumerate(self.topic_list):
            print(ORAM_node,topic_name)
            self.topic_name_to_ORAM_node[topic_name] = ORAM_node
            self.ORAM_node_to_topic_name[ORAM_node] = topic_name

        self.create_node()
        self.start_process()


    def create_topic(self,topic_name, queue):

        print(f"{topic_name = }")

        print(f"topic: {topic_name} create")
        rclpy.init(args=None)
        aes_publisher = AES_publisher(topic_name, queue)
        rclpy.spin(aes_publisher)

        aes_publisher.destroy_node()
        rclpy.shutdown()

    def create_node(self):

        for topic_name in self.topic_list:
            queue = Queue()
            process = Process(target=self.create_topic, args=(topic_name, queue))
            self.topic_to_queue[topic_name] = queue
            self.process_list.append(process)

    def start_process(self):
        for process in self.process_list:
            process.start()

    def send_data(self, data):

        print(f"sending {data}")

        path_1,path_2 = self.ORAM.random_choose_two_path(self.topic_name_to_ORAM_node[self.target])
        ORAM_nodes = self.ORAM.get_ros_node_from_path(path_1,path_2)

        encrypt_data = self.aes.encrypt_obj_gcm(data)
        for ORAM_node in ORAM_nodes:
            topic_name = self.ORAM_node_to_topic_name[ORAM_node]
            self.topic_to_queue[topic_name].put(encrypt_data)
