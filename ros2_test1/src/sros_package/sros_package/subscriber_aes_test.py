from sros_package.AES_topic import AES_subscriber
import sys
import rclpy


def main(args=None):
    rclpy.init(args=args)

    if len(sys.argv)<2:
        raise Exception("need topic name")

    if len(sys.argv)<3:
        raise Exception("need key path")

    minimal_subscriber = AES_subscriber(sys.argv[1],sys.argv[2])

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()