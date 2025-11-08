receiver_res = [[{} for _ in range(8)] for _ in range(100)]

for topic in range(8):
    with open(f'../multi_node_datas/topic_{topic}.txt', 'r') as f:
        for f in f.readlines():
            f = f.strip()
            # print(f)
            split_line = f.split()
            time = int(split_line[0])
            type_ = split_line[1]
            source = int(split_line[3])
            # print(f"{time = }, {type_ = }, {source = }")
            receiver_res[time][topic][source] = type_


for i in range(8):
    with open(f'../multi_node_datas/sender_{i}.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            # print(line)
            if line == '':
                continue
            split_line = line.split()
            topic = int(split_line[0].split('_')[1])
            time = int(split_line[2])
            type_ =  split_line[3]
            source = int(split_line[5])
            # print(f"{topic = }, {time = }, {type_ = }, {source = }")
            if receiver_res[time][topic].get(source) != type_:
                print(f"mismatch at time {time:2} topic {topic} source {source}: sender {type_}")
