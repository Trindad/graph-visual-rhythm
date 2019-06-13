from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random

import sqlite3
from sqlite3 import Error
import csv

import matplotlib.pyplot as plt
import networkx as nx
from networkx import *

import math

import numpy as np

from itertools import izip


def create_database(c, conn):

    try:
        c.execute('''CREATE TABLE IF NOT EXISTS graphs
                    (time integer, degree text, betweeness text, 
                    closeness text, pagerank text, harmonic_centrality, local_efficiency text,
                    global_efficiency text, maximal_matching text, nVehicles integer DEFAULT 0 )''')
        c.execute("CREATE INDEX graph_index on graph (time)")
    except Error as e:
        print(e)
        return None

    return c, conn


def drawGraph(G):
    nx.draw(G, node_size=50, nodecolor='r', edge_color='b')
    plt.show()


def connecting_nodes(nodes):
    transmissionRange = 200.0  # condition in meters to create an edge between u and v
    G = nx.Graph()

    for u in nodes:
        G.add_node(u)
        for v in nodes:
            if u == v:
                continue
            G.add_node(v)
            distance = distanceBetweenVehicles(
                nodes[u][0], nodes[u][1], nodes[v][0], nodes[v][1])
            if distance <= transmissionRange:
                # print(u," ",v, " : ",distance)
                
                G.add_edge(u, v, weight=distance)
    return G


def distanceBetweenVehicles(x1, y1, x2, y2):
    return math.sqrt(math.pow(x2-x1, 2.0) + math.pow(y2-y1, 2.0))

def network_measures(G, line, c, conn):

    bc = str(betweenness_centrality(G))
    dg = str(degree_centrality(G))
    cc = str(closeness_centrality(G))
    hc = str(harmonic_centrality(G))
    pr = str(pagerank(G))
    # vr = str(voteRank(G))
    clusters = str(clustering(G))
    # eigen = str(eigenvector_centrality(G))
    # ecc = str(eccentricity(G))

    le = str(local_efficiency(G))
    ge = str(global_efficiency(G))
    mm = str(maximal_matching(G))

    t = line.split(" ")

    c.execute("INSERT INTO graphs VALUES ('" +
              t[1]+"','" + dg+"','"+bc+"','"+cc+"','"+pr+"','"+hc+"','"+clusters+"','"+le+"','"+ge+"','"+mm+"' )")
    conn.commit()

    # drawGraph(G)
    #densidade relativa de 0-1
    # density_plot(mydata)
    
def update_number_of_vehicles(time, nveh, c):

    c.execute("UPDATE graphs SET nVehicles = " +int(nveh)+" WHERE time ="+time)
    
def measure_graphs():

    #creating and inserting data
    conn = sqlite3.connect('database.db')
    conn.text_factory = str
    c = conn.cursor()
    
    create_database(c, conn)

    graphs = open("graphs.txt", "w")
    count = 0
    lim = 200
    with open("24hours/graphs.txt", "r") as f:
        nodes = {}
        for line in f:
            if count <= lim:
                if "END" not in line:
                    s1 = line.split(":")
                    nodes[int(s1[0])] = [float(s1[1]), float(s1[2])]
                else:
                    print(line)
                    G = connecting_nodes(nodes)
                    network_measures(G, line, c, conn)
                    nodes.clear()
                    graphs.write(line)
                    count = count + 1
            else:
                break
    # with open("vehicles.txt", "r") as f:
    #     for line in f:
    #         s1 = line.split(" ")
    #         update_number_of_vehicles(s1[0], s1[1], c)
    #         conn.commit()
    graphs.close()
    
    sys.stdout.flush()

def show_graph(G):

    G = nx.random_geometric_graph(50, 0.125)
    pos = nx.get_node_attributes(G, 'pos')
    # find node near center (0.5,0.5)
    dmin = 1
    ncenter = 0
    pos = nx.random_layout(G)
    # pos = nx.spring_layout(G)

    for n in pos:
        x, y = pos[n]
        d = (x-0.5)**2+(y-0.5)**2
        if d < dmin:
            ncenter = n
            dmin = d

    # color by path length from node near center
    
    p = dict(nx.degree_centrality(G))

    plt.figure(figsize=(10, 10))
    nx.draw_networkx_edges(G, pos, nodelist=[ncenter], alpha=0.8)
    nx.draw_networkx_nodes(G, pos, nodelist=list(p.keys()), node_size=80, node_color=p.values(), cmap=plt.cm.Reds_r)

    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.axis('off')
    # plt.savefig('random_geometric_graph.png')
    plt.show()

def figure_paper(filename):

    with open(filename, "r") as f:
        nodes = {}
        for line in f:
            if "END" not in line:
                s1 = line.split(":")
                nodes[int(s1[0])] = [float(s1[1]), float(s1[2])]
            else:
                show_graph(connecting_nodes(nodes))
                nodes.clear()
if __name__ == "__main__":

    measure_graphs()
    # figure_paper("draw.txt")
