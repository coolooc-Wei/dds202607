import math
import random
from os.path import split


class ORAM:
    def __init__(self, num_blocks):
        self.num_blocks = num_blocks
        self.path_count = 2 ** math.floor(math.log2(self.num_blocks))
        self.tree_map = [i for i in range(self.num_blocks)]
        self.path_map = [-1 for _ in range(self.num_blocks)]
        self.path_list = [i+1 for i in range(self.path_count)]

        print(f"{self.num_blocks = }")
        print(f"{self.path_count = }")
        print(f"{self.tree_map = }")
        print(f"{self.path_map = }")

        self.update_path_map()

        print(f"{self.path_map = }")

    def update_path_map(self):
        path_count = 0
        path_count_pow = 0
        for tree_node in range(self.num_blocks):
            ros_node_num = self.tree_map[tree_node]
            print(f"{ros_node_num = }")
            print(f"{path_count = }, {path_count_pow = }")
            split_num = self.path_count//(2**path_count_pow)
            print(f"{split_num = }")
            path_split = self.path_list[path_count*split_num:path_count*split_num + split_num]
            print(f"{path_split = }")
            # path = random.sample(path_split,1)[0]
            # print(path)
            self.path_map[ros_node_num] = path_split  # update ros_node_num -> path num
            path_count+= 1
            if path_count == 2**path_count_pow:
                path_count_pow += 1
                path_count = 0


if __name__ == "__main__":
    oram = ORAM(15)
