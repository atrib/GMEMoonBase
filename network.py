#!/usr/bin/env python3

import pandas as pd
import pickle
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from networkx.algorithms.reciprocity import overall_reciprocity
from networkx.algorithms.shortest_paths.generic import average_shortest_path_length
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.community.centrality import girvan_newman
from networkx.algorithms.link_analysis.hits_alg import hits

def get_top_keys(dictionary, top):
    items = Counter(dictionary).most_common(top)
    return items

def main(file='post_comments'):
    data = pd.read_pickle(file)
    df = pd.DataFrame(data, 
                  columns=['post_id', 'post_user', 'comment_id', 'comment_user'])
    df_new = df.groupby(['post_user', 'comment_user']).size().reset_index()
    df_new['weight'] = df_new[0]
    df_new = df_new.drop(columns=[0])
    G = nx.from_pandas_edgelist(df_new, source='comment_user', target='post_user', 
                            edge_attr='weight', create_using=nx.DiGraph())
    
    #nodes = list(df_new.sample(1000).post_user)
    #G = G.subgraph(nodes)
    
    print('loaded data into network')
    
    
    results = {}
    results['num_nodes'] = G.number_of_nodes() 
    results['num_edges'] = G.number_of_edges()
    results['average_degree'] = float(results['num_edges']) / results['num_nodes']
    
    print('general stats', results)
    
    G_ud = G.to_undirected()
    G_mc = max(nx.connected_components(G_ud), key=len)
    G_S = G_ud.subgraph(G_mc).copy()

    print('created directed and connected versions of network')
    
    results['diameter'] = nx.diameter(G_S)
    print('diameter', results['diameter'])
    results['avg_clustering'] = nx.average_clustering(G_ud)
    print('average clustering', results['avg_clustering'])
    results['reciprocity'] = overall_reciprocity(G)
    print('reciprocity', results['reciprocity'])
    results['avg_shortest_path'] = nx.average_shortest_path_length(G_S)
    print('average shortest path length', results['avg_shortest_path'])
    
    print('finished advanced stats')
    
    bet_cen = nx.betweenness_centrality(G_S)
    results['top_bet_cen'] = get_top_keys(bet_cen,20)
    print('betweenness centrality', results['top_bet_cen'])
    
    clo_cen = nx.closeness_centrality(G_S)
    results['top_clo_cen'] = get_top_keys(clo_cen,20)
    print('closeness centrality', results['top_clo_cen'])

    eig_cen = nx.eigenvector_centrality(G_S)
    results['top_eig_cen'] = get_top_keys(eig_cen,20)
    print('eigenvector centrality', results['top_eig_cen'])
    
    print('finished centrality measures')
    
    results['communities_greedy'] = list(greedy_modularity_communities(G_ud))
    print('finished greedy community', len(results['communities_greedy']))
    
    #results['communities_girvan_newman'] = list(girvan_newman(G_ud))
    #print('finished girvan newman community', len(results['communities_girvan_newman']))
    
    h, a = nx.hits(G)
    results['authories'] = Counter(a).most_common(20)
    results['hubs'] = Counter(h).most_common(20)
    print('finished hits', results['authories'], results['hubs'])
    
    with open('results_network.pkl', 'wb') as outfile:
        pickle.dump(results, outfile)
        
if __name__ == "__main__":
    main()