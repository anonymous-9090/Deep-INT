# -*- coding: UTF-8 -*-
from statistics import pvariance
import matplotlib.pyplot as plt
import copy
import random
import networkx as nx
import numpy as np
import time

class Graph(object):
    def __init__(self, *args, **kwargs):
        self.node_neighbors = {}
        self.visited = {}
        self.A = []  # 为现存节点数组
        self.degree = []  # 为度数组

    def add_nodes(self, nodelist):
        for node in nodelist:
            self.add_node(node)

    def add_node(self, node):
        if not node in self.nodes():
            self.node_neighbors[node] = []

    def add_edge(self, edge):
        u, v = edge
        if (v not in self.node_neighbors[u]) and (u not in self.node_neighbors[v]):
            self.node_neighbors[u].append(v)
            if (u != v):
                self.node_neighbors[v].append(u)

    def nodes(self):
        return self.node_neighbors.keys()

    def not_null_node(self):
        self.A.clear()
        for node in self.nodes():
            if len(self.node_neighbors[node]) > 0:
                self.A.append(node)

    def degrees(self):
        self.degree.clear()
        Node = self.nodes()
        for node in Node:
            self.degree.append(len(self.node_neighbors[node]))

    def set_diff(self, nodes):
        others = []
        for node in self.A:
            if node not in nodes:
                others.append(node)
        return others

    def F1(self):  # 求所有联通子图
        nodes = []
        visited = []
        subgraph = {}
        i = 1
        temp = self.set_diff(nodes)
        while len(temp) > 0:
            order = self.depth_first_search(temp[0])
            subgraph[i] = order
            i += 1
            visited.extend(order)
            temp = self.set_diff(visited)
        return subgraph

    def judge(self, subgraph):
        for i in subgraph:
            t = 0
            temp = subgraph[i]
            for node in temp:
                if self.degree[node - 1] % 2 != 0:
                    t = 1  # t=1说明有奇顶点
                    break
            if t == 0:
                return i
        return 0

    def F2(self, gt):
        num = 0
        for node in gt:
            if self.degree[node - 1] % 2 != 0:
                num += 1
        return num

    def F3(self, path):
        for i in range(len(path) - 1):
            self.node_neighbors[path[i]].remove(path[i + 1])
            self.node_neighbors[path[i + 1]].remove(path[i])
        self.not_null_node()

    def depth_first_search(self, root=None):  # 在连通的前提下进行深度优先搜索
        order = []

        def dfs(node):
            self.visited[node] = True
            order.append(node)
            for n in self.node_neighbors[node]:
                if not n in self.visited:
                    dfs(n)

        if root:
            dfs(root)

        for node in self.nodes():
            if not node in self.visited:
                for v_node in self.visited:
                    if node in self.node_neighbors[v_node]:
                        dfs(node)
        self.visited.clear()
        return order

    def my_path(self, subgraph):
        odd_node = []
        path_len={}
        for node in subgraph:
            if self.degree[node - 1] % 2 != 0:
                odd_node.append(node)
        distances = {}
        g_temp = dict_copy(self.node_neighbors, subgraph)
        for i in list(g_temp.keys()):
            temp = []
            for j in g_temp[i]:
                temp.append((j, 1))
            distances[i] = temp
        for node in odd_node:
            current = node
            dis=copy.deepcopy(distances)
            d, paths = dijkstra(dis, current)
            use_dict = dict_copy(paths, odd_node)
            d = dict_copy(d, odd_node)
            n_max = max(d.items(), key=lambda x: x[1])[0]
            path_len[d[n_max]]=use_dict[n_max]
        return max(path_len.items(), key=lambda x: x[0])[1]

def dijkstra(G, s):
    d = {}  # node distances from source
    predecessor = {}  # node predecessor on the shortest path
    for v in G:
        if v == s:
            d[v] = 0
        else:
            d[v] = float("inf")
    predecessor[s] = None
    Q = list(G.keys())  # contains all nodes to find shortest paths to, intially everything.
    while (Q):  # until there is nothing left in Q
        u = min(Q, key=d.get)  # get min distance node
        Q.remove(u)
        for v in G[u]:  # relax all outgoing edges from it
            relax(u, v, d, predecessor)
    paths = {}
    for v in predecessor:
        paths[v] = [v]
        p = predecessor[v]
        while p is not None:
            paths[v].append(p)
            p = predecessor[p]
    return d, paths

def relax(u, v, d, predecessor):
    weight = v[1]
    v = v[0]
    if d[v] > d[u] + weight:
        d[v] = d[u] + weight
        predecessor[v] = u

def add_path(p1, p2):
    k=1
    for i in range(len(p2)-1):
        p1.insert(p1.index(p2[0])+k,p2[i+1])
        k+=1
    return p1

def dict_copy(dict, a):
    temp = {}
    for i in a:
        temp[i] = dict[i]
    return temp

def is_connected(G):
    start_node = list(G)[0]
    color = {v: 'white' for v in G}
    color[start_node] = 'gray'
    S = [start_node]
    while len(S) != 0:
        u = S.pop()
        for v in G[u]:
            if color[v] == 'white':
                color[v] = 'gray'
                S.append(v)
            color[u] = 'black'
    return list(color.values()).count('black') == len(G)

def odd_degree_nodes(G):
    odd_degree_nodes = []
    for u in G:
        if len(G[u]) % 2 != 0:
            odd_degree_nodes.append(u)
    return odd_degree_nodes

def from_dict(G):
    links = []
    for u in G:
        for v in G[u]:
            links.append((u, v))
    return links

def fleury(G):
    odn = odd_degree_nodes(G)
    if len(odn) > 2 or len(odn) == 1:
        return 'Not Eulerian Graph'
    else:
        g = copy.deepcopy(G)
        trail = []
        if len(odn) == 2:
            u = odn[0]
        else:
            u = list(g)[0]
        while len(from_dict(g)) > 0:
            current_vertex = u
            for u in g[current_vertex]:
                g[current_vertex].remove(u)
                g[u].remove(current_vertex)
                bridge = not is_connected(g)
                if bridge:
                    g[current_vertex].append(u)
                    g[u].append(current_vertex)
                else:
                    break
            if bridge:
                g[current_vertex].remove(u)
                g[u].remove(current_vertex)
                g.pop(current_vertex)
            if (len(trail) == 0):
                trail.append(current_vertex)
                trail.append(u)
            else:
                trail.append(u)
        return trail

def euler(G, start=None):
    path = []
    g = copy.deepcopy(G)
    def hierholzer(node):
        if (len(g[node]) == 0):
            path.append(node)
            return
        for n in g[node]:
            g[node].remove(n)
            g[n].remove(node)
            hierholzer(n)
            if (len(g[node]) == 0):
                path.append(node)
                return
    odn = odd_degree_nodes(g)
    if len(odn) > 2 or len(odn) == 1:
        return 'Not Eulerian Graph'
    else:
        if start:
            u = start
        else:
            if len(odn) == 2:
                u = odn[0]
            else:
                u = list(g)[0]
        hierholzer(u)
    path.reverse()
    return path

def path_iden(Queue, g):    #找出Queue中哪条路径应该与g相连
    for n in g:
        for path in Queue:
            if(n in path):
                Queue.remove(path)
                return path, n

def verification(Queue, testG):
    for path in Queue:
        for i in range(len(path)-1):
            testG[path[i]].remove(path[i+1])
            testG[path[i+1]].remove(path[i])
            i += 1

def find_path(G):
    num_fleury = 0
    num_path = 0
    g = Graph()
    g.add_nodes([i + 1 for i in range(len(G))])
    for i in range(len(G)):
        for j in range(len(G[i])):
            if G[i][j] != 0:
                g.add_edge((i + 1, j + 1))
    g.not_null_node()
    g.F1()
    testG = copy.deepcopy(g.node_neighbors)
    Queue = []
    while (len(g.A) > 0):
        g.degrees()
        subgraph = g.F1()
        n = len(subgraph)
        T = g.judge(subgraph)
        if (T > 0):
            if (len(Queue) > 0):
                t_path, start = path_iden(Queue, subgraph[T])
                g_temp = dict_copy(g.node_neighbors, subgraph[T])
                result = euler(g_temp, start)
                num_fleury += 1
                g.F3(result)
                result = add_path(t_path, result)
                Queue.append(result)
            else:
                g_temp = dict_copy(g.node_neighbors, subgraph[T])
                t_path = euler(g_temp)
                num_fleury += 1
                Queue.append(t_path)
                g.F3(t_path)
            continue
        for i in range(1, n + 1):
            odd_num = g.F2(subgraph[i])
            if odd_num == 2:
                g_temp = dict_copy(g.node_neighbors, subgraph[i])
                path = euler(g_temp)
                num_fleury += 1
            elif odd_num > 2:
                path = g.my_path(subgraph[i])
            else:
                break
            Queue.append(path)
            g.F3(path)
    num_path = len(Queue)
    verification(Queue, testG)
    return num_fleury, num_path, Queue

def read_graphml(file_path):
    G = nx.read_graphml(file_path)
    network_matrix = nx.to_numpy_array(G)
    return network_matrix

def handle_probe(probe):
    probe_len = [len(x) for x in probe]  #计算探针集合中每个探针的长度
    max_probe_len = max(probe_len)  #最长探针长度
    probe_num = len(probe_len)  #探针数量
    probe_var = pvariance(probe_len)

    return probe_num, max_probe_len, probe_len, sum(probe_len), probe_var

def get_euler_path(G):
    file_path = G
    network_matrix = read_graphml(file_path)
    start = time.perf_counter()
    num_fleury, num_path, q = find_path(network_matrix)
    end = time.perf_counter()
    q_minus_one = [[node - 1 for node in path] for path in q]


    print(q_minus_one)
    return q_minus_one

if __name__ == '__main__':
    file_path = 'topo/Nsfnet.graphml'
    network_matrix = read_graphml(file_path)
    start = time.perf_counter()
    num_fleury, num_path, q = find_path(network_matrix)
    end = time.perf_counter()
    q_minus_one = [[node - 1 for node in path] for path in q]

    data = handle_probe(q_minus_one)

    print(data)
    print(q_minus_one)
