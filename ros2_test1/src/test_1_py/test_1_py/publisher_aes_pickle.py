import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import random
from nav_msgs.msg import Odometry
import numpy as np
import pickle

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'aes_pickle', 10)
        timer_period = 0.5  # seconds
        self.i = 0
        self.public_key = self.load_public_key()
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def load_public_key(self):
        with open('kyber_keys/server/shared_secret_server.key', mode='rb') as publicfile:
            public_key = publicfile.read()
        return public_key
    
    def aes_encrypt(self,plain_text, key):
        iv = get_random_bytes(16)  # 生成隨機初始化向量
        cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建加密對象
        encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))  # 加密並補位
        return base64.b64encode(iv + encrypted).decode('utf-8')  # 返回加密後的資料（含IV）

    def get_rotation_quaternion(self,v1, v2):
        v2-=v1
        z_rot = np.arctan2(v2[1],v2[0])
        y_rot = np.arctan2(v2[2],v2[0])
        x_rot = np.arctan2(v2[1],v2[2])

        # convert to quaternion
        cy = np.cos(z_rot * 0.5)
        sy = np.sin(z_rot * 0.5)
        cp = np.cos(y_rot * 0.5)
        sp = np.sin(y_rot * 0.5)
        cr = np.cos(x_rot * 0.5)
        sr = np.sin(x_rot * 0.5)

        w = cy * cp * cr + sy * sp * sr
        x = cy * cp * sr - sy * sp * cr
        y = sy * cp * sr + cy * sp * cr
        z = sy * cp * cr - cy * sp * sr

        return [w, x, y, z]

    def timer_callback(self):
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'

        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.position.z = self.z

        self.x = self.x+random.uniform(0.0, 0.2)
        self.y = self.y+random.uniform(0.0, 0.2)
        self.z = 0.0

        v1 = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z])
        v2 = np.array([self.x, self.y, self.z])
        quaternion = self.get_rotation_quaternion(v1, v2)
    

        msg.pose.pose.orientation.w = quaternion[0]
        msg.pose.pose.orientation.x = quaternion[1]
        msg.pose.pose.orientation.y = quaternion[2]
        msg.pose.pose.orientation.z = quaternion[3]

        msg_str = String()
        msg_str.data = pickle.dumps(msg)
        msg_str.data = base64.b64encode(msg_str.data).decode('utf-8')
        msg_str.data = self.aes_encrypt(msg_str.data, self.public_key)

        self.publisher_.publish(msg_str)
        # self.get_logger().info('Publishing: "%s"' % quaternion)
        self.get_logger().info('Publishing: "%s"' % msg)
        self.get_logger().info('Publishing: "%s"' % msg_str)
        self.i += 1

        with open('data/odom_server.txt', 'a') as f:
            f.write(f"{msg}\n")


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()