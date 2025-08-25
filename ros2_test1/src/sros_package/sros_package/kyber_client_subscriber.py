import rclpy
from rclpy.node import Node
from sros_package.kyber_client import kyber_client
from sros_package.AES import AES
from std_msgs.msg import String



class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic_aes',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
    
        self.Aes = Aes('kyber_keys/bot1_client.key')

    def listener_callback(self, msg):
        try:
            # msg.data = bytes.fromhex(msg.data)
            msg.data = self.Aes.decrypt_string_gcm(msg.data)
            self.get_logger().info(f"I heard: {msg.data}")
        except Exception as e:
            self.get_logger().warning(f"DecryptionError: {e}")




def main(args=None):
    rclpy.init(args=args)
    # if len(sys.argv)<2:
    #     raise Exception("need topic name")

    # if len(sys.argv)<3:
    #     raise Exception("need key path")

    key = kyber_client('bot1','kyber_keys/bot1_client.key')
    print(f"{key = }")

    
    minimal_subscriber = ()

    rclpy.spin(minimal_subscriber)

    minimal_client.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':
    main()