import os

def extract_and_save_subgraph(nodes_path='./Data/Nodes.txt', edges_path='./Data/Edges.txt', output_dir='./TestData', limit=3000):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 读取节点信息
    nodes = {}
    with open(nodes_path, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')
            node_id = int(parts[0])
            if node_id < limit:
                nodes[node_id] = (float(parts[1]), float(parts[2]))
            else:
                break  # 假设节点是按顺序排列的

    # 保存节点信息
    with open(os.path.join(output_dir, 'Nodes.txt'), 'w') as file:
        for node_id, (x, y) in nodes.items():
            file.write(f'{node_id} {x} {y}\n')

    # 读取并保存边信息
    edges = []
    with open(edges_path, 'r') as infile, open(os.path.join(output_dir, 'Edges.txt'), 'w') as outfile:
        for line in infile:
            parts = line.strip().split(' ')
            edge_id, start_node_id, end_node_id, distance = int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3])
            if start_node_id in nodes and end_node_id in nodes:
                edges.append((edge_id, start_node_id, end_node_id, distance))
                outfile.write(f'{edge_id} {start_node_id} {end_node_id} {distance}\n')

    return f"Extracted and saved {len(nodes)} nodes and {len(edges)} edges to {output_dir}."

# 执行函数
result = extract_and_save_subgraph()
print(result)
