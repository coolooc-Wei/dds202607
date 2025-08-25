import math
import random
import time

random.seed(time.time()) # set seed for reproducibility

class ORAM:
    def __init__(self, num_blocks, debug_mode=False):
        self.num_blocks = num_blocks
        self.path_count = 2 ** math.floor(math.log2(self.num_blocks))
        self.tree_map = [i for i in range(self.num_blocks)]
        self.path_map = [-1 for _ in range(self.num_blocks)]
        self.path_list = [i for i in range(1, self.path_count + 1)]

        self.debug_mode = debug_mode

        if self.debug_mode:
            print("Debug mode is ON")
            print(f"{self.num_blocks = }")
            print(f"{self.path_count = }")
            print(f"{self.tree_map = }")
            print(f"{self.path_map = }")
            print(f"{self.path_list = }")

        self.update_path_map()

    def pretty_print_mask(self, mask):
        if mask == -1:
            return "None Mask"
        return f"{str(bin(mask))[2:]:0>{self.path_count}}"

    def print_tree_node_ros_node_mask_mapping(self):
        for tree_node, ros_node in enumerate(self.tree_map):
            print(f"Tree Node {tree_node:>{3}} => ROS Node {ros_node:>{3}} : {self.pretty_print_mask(self.path_map[ros_node])}")


    def debugger_data(func):
        def wrap(self, *args, **kwargs):
            if not self.debug_mode:
                return func(self, *args, **kwargs)
            print(f"\n{func.__name__}=>")
            self.print_tree_node_ros_node_mask_mapping()
            print()
            res = func(self, *args, **kwargs)
            print(f"<={func.__name__}")
            self.print_tree_node_ros_node_mask_mapping()
            print()
            return res

        return wrap

    @debugger_data
    def update_path_map(self):


        path_count = 0
        path_count_pow = 0 # power of 2 for path count
        mask_count = self.path_count # number of bits in the mask
        path_mask = 2 ** mask_count - 1 # mask for all paths

        for tree_node in range(self.num_blocks):
            if self.debug_mode:
                print(f"Tree Node {tree_node:>{3}} => Path Mask: {self.pretty_print_mask(path_mask)}")
            ros_node_num = self.tree_map[tree_node]
            self.path_map[ros_node_num] = path_mask # assign the path mask to the ROS node

            path_count += 1
            path_mask = path_mask << mask_count # shift the mask left by the number of bits in the mask
            if path_count == 2 ** path_count_pow:
                path_count_pow += 1
                path_count = 0
                mask_count //= 2 # halve the mask count
                path_mask = 2 ** mask_count - 1 # reset the path mask to cover the new mask count

    @debugger_data
    def get_ros_node_from_path(self, path_num_1, path_num_2):

        if path_num_1 <= 0 or path_num_1 > self.path_count:
            raise ValueError(f"Path number {path_num_1} out of range. Must be between 1 and {self.path_count}.")

        if path_num_2 <= 0 or path_num_2 > self.path_count:
            raise ValueError(f"Path number {path_num_2} out of range. Must be between 1 and {self.path_count}.")

        # Convert path numbers to masks
        path_1 = 1 << (path_num_1 - 1)
        path_2 = 1 << (path_num_2 - 1)

        paths = path_1 | path_2 # combine the two paths into a single mask

        if self.debug_mode:
            print(f"path 1 mask:{self.pretty_print_mask(path_1)}")
            print(f"path 2 mask:{self.pretty_print_mask(path_2)}")
            print(f"Combined paths mask: {self.pretty_print_mask(paths)}")

        ros_nodes = []
        for ros_node,path_mask in enumerate(self.path_map):
            if path_mask&paths: # find ROS nodes that are in either path
                if self.debug_mode:
                    print(f"Found {ros_node:>{3}} in mask {self.pretty_print_mask(path_mask)}")
                ros_nodes.append(ros_node)

        self.shuffle_path(ros_nodes)

        return ros_nodes

    @debugger_data
    def shuffle_path(self,shuffle_ros_node_list):

        new_ros_node_list = shuffle_ros_node_list.copy()
        random.shuffle(new_ros_node_list)

        if self.debug_mode:
            print(f"{shuffle_ros_node_list = }")
            print(f"{new_ros_node_list = }")
        
        ros_node_shuffle_map = {shuffle_ros_node_list[i]: new_ros_node_list[i] for i in range(len(shuffle_ros_node_list))}
        ori_path_map = self.path_map.copy()
        for tree_node, ros_node in enumerate(self.tree_map):
            if ros_node in ros_node_shuffle_map:
                new_ros_node = ros_node_shuffle_map[ros_node]
                if self.debug_mode:
                    print(f"Tree Node {tree_node:>{3}} -> ROS Node {ros_node:>{3}} is changed to {new_ros_node:>{3}}")
                self.tree_map[tree_node] = new_ros_node
                self.path_map[new_ros_node] = ori_path_map[ros_node] # update the path map with the new ROS node

    def get_path_from_ros_node(self, ros_node):

        if ros_node < 0 or ros_node >= self.num_blocks:
            raise ValueError("ROS node number out of range.")
        mask = 1
        path_list = []
        for i in range(1,self.path_count+1):
            if self.path_map[ros_node] & mask:
                if self.debug_mode:
                    print(f"Path {i + 1} is in ROS Node {ros_node}")
                path_list.append(i)
            mask <<= 1

        return path_list

    def  random_choose_two_path(self,ros_node):

        if ros_node < 0 or ros_node >= self.num_blocks:
            raise ValueError("ROS node number out of range.")
        required_path_list = self.get_path_from_ros_node(ros_node)
        path_1 = random.choice(required_path_list)
        path_2 = path_1
        while path_2 == path_1:
            path_2 = random.choice(self.path_list)
        return [path_1, path_2]
        

if __name__ == "__main__":
    oram = ORAM(3, debug_mode=True)

    # print(oram.get_path_from_ros_node(1))
    # path_1, path_2 = oram.random_choose_two_path(1)
    for _ in range(10):
        path_1, path_2 = oram.random_choose_two_path(1)
        print(f"Randomly chosen paths for ROS node 1: {path_1}, {path_2}")
        print(oram.get_ros_node_from_path(1, 2))
    # print(oram.get_ros_node_from_path(7, 4))
    