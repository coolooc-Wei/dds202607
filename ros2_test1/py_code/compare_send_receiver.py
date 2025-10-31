import os

send_res = []
for i in range(8):
    with open(f'../multi_node_datas/sender_{i}.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            print(line)
            if line == '':
                continue
            split_line = line.split()
            topic = int(split_line[0].split('_')[1])
            time = int(split_line[2])
            type =  split_line[3]
