
for path_num in range(8):
    

    overlap_path = ["1100","0011"]

    path = f"../multi_node_datas/path_data_{path_num}.txt"
    print(f"Analyzing {path}...")
    f = open(path, "r")
    lines = f.readlines()

    overlap_path_num = 0
    non_overlap_path_num = 0
    for i in range(3,len(lines),3):
        line = lines[i].strip()
        # print(f"Line {i+1}: {line}")
        combined_mask = line.split('combined_paths_mask = ')[1]
        # print(f"{combined_mask = }")
        for test_path in overlap_path:
            if combined_mask == test_path:
                # print("find")
                overlap_path_num += 1
                break
        else:
            non_overlap_path_num += 1

    print(f"{overlap_path_num = }")
    print(f"{non_overlap_path_num = }")