import colorsys
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os

def load_network(nodes_file, edges_file):
    G = nx.Graph()
    pos = {}
    with open(nodes_file, 'r') as nf:
        for line in nf:
            node_id, x, y = line.strip().split()
            G.add_node(int(node_id))
            pos[int(node_id)] = (float(x), float(y))
    
    with open(edges_file, 'r') as ef:
        for line in ef:
            _, start_node_id, end_node_id, _ = line.strip().split()
            G.add_edge(int(start_node_id), int(end_node_id))
    
    return G, pos

def block_center_nodes(G, pos):
    center_x = np.mean([pos[node][0] for node in G])
    center_y = np.mean([pos[node][1] for node in G])

    distances = {node: np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2) for node, (x, y) in pos.items()}

    nodes_to_block_count = int(len(G) * 0.01) 
    nodes_sorted_by_distance = sorted(distances, key=distances.get)[:nodes_to_block_count]

    G.remove_nodes_from(nodes_sorted_by_distance)
    return nodes_sorted_by_distance

def generate_hsl_colors(n):
    colors = []
    step = 360 / n
    
    saturation = 80  
    lightness = 50   
    
    for i in range(n):
        hue = int(step * i)
        colors.append(f"hsl({hue}, {saturation}%, {lightness}%)")
    return colors

def hsl_to_rgb_corrected(hsl_colors):
    rgb_colors_corrected = []
    for hsl in hsl_colors:
        h, s, l = hsl[4:-1].split(', ')
        h = int(h)
        s = float(s.strip('%')) / 100
        l = float(l.strip('%')) / 100
        rgb = colorsys.hls_to_rgb(h/360, l, s)
        rgb_hex = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
        rgb_colors_corrected.append(rgb_hex)
    return rgb_colors_corrected



def visualize_network(G, pos, alpha, step, overloaded_nodes_by_step):
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
    colors = hsl_to_rgb_corrected(generate_hsl_colors(25))
    for i, nodes in enumerate(overloaded_nodes_by_step):
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_size=50, 
                               node_color=colors[i % len(colors)], label=f'Step {i+1}')
    plt.title(f"Network after cascading failures, alpha={alpha}")
    plt.legend()
    plt.axis('off')
    plt.savefig(f'./Images/network_alpha_{alpha:.2f}_step_{step}.png')
    plt.close()

def simulate_cascade(G, pos, alpha):
    initial_load = nx.betweenness_centrality(G)
    block_center_nodes(G, pos)
    capacity = {node: load * (1 + alpha) for node, load in initial_load.items()}
    overload = True
    step = 0
    sizes = []
    overloaded_nodes_by_step = []
    while overload:
        step += 1
        load = nx.betweenness_centrality(G)
        overloaded_nodes = [node for node, l in load.items() if l > capacity[node]]
        overloaded_nodes_by_step.append(overloaded_nodes)
        G.remove_nodes_from(overloaded_nodes)
        overload = len(overloaded_nodes) > 0
        sizes.append((len(max(nx.connected_components(G), key=len)) / len(pos), 
                      len(sorted(nx.connected_components(G), key=len, reverse=True)[1]) / len(pos) if len(G) > 1 else 0))
    visualize_network(G, pos, alpha, step, overloaded_nodes_by_step)
    return step, sizes

def plot_cascades_vs_alpha(alpha_values, cascade_counts):
    plt.figure(figsize=(8, 6))
    plt.plot(alpha_values, cascade_counts, '-o', color='b')
    plt.xlabel('Alpha')
    plt.ylabel('Number of Cascading Rounds')
    plt.title('Cascading Rounds vs Alpha')
    plt.grid(True)
    plt.savefig('./Images/cascades_vs_alpha.png')
    plt.close()

def plot_cc_ratios_vs_cascades(alpha_values, cc_ratios):
    plt.figure(figsize=(14, 7))
    for i, alpha in enumerate(alpha_values):
        sizes = cc_ratios[i]
        cascades = range(1, len(sizes) + 1)
        largest_cc_ratios = [size[0] for size in sizes]
        second_largest_cc_ratios = [size[1] for size in sizes]
        
        plt.subplot(1, 2, 1)
        plt.plot(cascades, largest_cc_ratios, label=f'Alpha={alpha:.1f}')
        plt.xlabel('Cascades')
        plt.ylabel('Largest CC Size Ratio')
        plt.title('Largest CC Size Ratios vs Cascades')
        
        plt.subplot(1, 2, 2)
        plt.plot(cascades, second_largest_cc_ratios, label=f'Alpha={alpha:.1f}')
        plt.xlabel('Cascades')
        plt.ylabel('Second Largest CC Size Ratio')
        plt.title('Second Largest CC Size Ratios vs Cascades')

    plt.subplot(1, 2, 1)
    plt.legend(loc='upper left')
    plt.subplot(1, 2, 2)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig('./Images/cc_ratios_vs_cascades.png')
    plt.close()

if __name__ == '__main__':
    nodes_file = './Data/Nodes.txt'
    edges_file = './Data/Edges.txt'
    G, pos = load_network(nodes_file, edges_file)
    alpha_values = np.arange(0,1.2,0.05)
    cascade_counts = []
    cc_ratios = []

    if not os.path.exists('./Images'):
        os.makedirs('./Images')

    for alpha in alpha_values:
        G_copy = G.copy()
        step_count, sizes = simulate_cascade(G_copy, pos, alpha)
        cascade_counts.append(step_count)
        cc_ratios.append(sizes)
    
    plot_cascades_vs_alpha(alpha_values, cascade_counts)
    plot_cc_ratios_vs_cascades(alpha_values, cc_ratios)

