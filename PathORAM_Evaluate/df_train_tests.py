from df_train import train


for node_num in [8, 16, 32, 64]:

    for real_communication_ratio in [0.1,0.2,0.3, 0.5, 0.7,1.0]:
        for dummy_trans_ratio in [0.0, 0.5, 1.0]:

            # node_num = 32
            rounds = (node_num - 1) * 100  # (node_num-1) * n round,n = 10 or 100
            times_each_round = 100
            # real_communication_ratio = 0.3
            # dummy_trans_ratio = 0.5
            gen_data_flag = False  # False to load existing dataset, True to generate new dataset (which will overwrite existing dataset with the same name)
            USE_ORAM = True
            epochs = 100
            lr = 0.002

            train(node_num, rounds, times_each_round, real_communication_ratio, dummy_trans_ratio, USE_ORAM, epochs, lr, gen_data_flag)