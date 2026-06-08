import numpy as np

node_num = 64
rounds = (node_num - 1) * 100  # (node_num-1) * n round,n = 10 or 100
times_each_round = 100
real_communication_ratio = 0.3
dummy_trans_ratio = 0.5

USE_ORAM = False

if USE_ORAM:
    file_name = f"sim_datas/oram_simulation_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_{dummy_trans_ratio}"
else:
    file_name = f"sim_datas/sim_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_no_oram"
print(f"{file_name = }")
datas_x = np.load(f"{file_name}_train_x.npy")
datas_y = np.load(f"{file_name}_train_y.npy")

# print(datas)
# data to list
datas_list = datas_x.tolist()
gt_list = datas_y.tolist()


for data in zip(datas_list, gt_list):

    node_rec_count = [0] * node_num
    for m in data[0]:
        for v in m:
            # print(v)
            for i in range(node_num):
                if v[i] == 1:
                    node_rec_count[i] += 1
        # print('-'*20)

    print(f"gt: {data[1]}")
    for i in range(node_num):
        print(f"node {i} received {node_rec_count[i]} times")

    print('-'*20)