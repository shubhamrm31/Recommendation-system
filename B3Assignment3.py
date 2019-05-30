# -*- coding: utf-8 -*-
"""
@author: hina
"""
print ()

import networkx
from operator import itemgetter
import matplotlib.pyplot

# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('./amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Read the data from amazon-books-copurchase.adjlist;
# assign it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr = open("./amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph = networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])
    
# Now let's look at the ego network associated with purchasedAsin in the
# copurchaseGraph - which is esentially comprised of all the books 
# that have been copurchased with this book in the past
# (1) YOUR CODE HERE: 
#     Get the depth-1 ego network of purchasedAsin from copurchaseGraph,
#     and assign the resulting graph to purchasedAsinEgoGraph.
purchasedAsinEgoGraph = networkx.Graph()
ego = networkx.ego_graph(copurchaseGraph, purchasedAsin, radius=1)
purchasedAsinEgoGraph = networkx.Graph(ego)

egoNeighbors = [i for i in copurchaseGraph.neighbors(purchasedAsin)] 
print ("--------------------------------------------------------------")
print ("List of Ego Neighbors:")
print ("--------------------------------------------------------------")
print (egoNeighbors)


pos = networkx.spring_layout(purchasedAsinEgoGraph)  
matplotlib.pyplot.figure(figsize=(10,10))
networkx.draw_networkx_labels(purchasedAsinEgoGraph,pos,font_size=2)
networkx.draw(purchasedAsinEgoGraph, pos=pos, node_size=150, node_color='r', edge_color='r', style='dashed')
networkx.draw(ego, pos=pos, node_size=100, node_color='b', edge_color='b', style='solid')
matplotlib.pyplot.show()


# Next, recall that the edge weights in the copurchaseGraph is a measure of
# the similarity between the books connected by the edge. So we can use the 
# island method to only retain those books that are highly simialr to the 
# purchasedAsin
# (2) YOUR CODE HERE: 
#     Use the island method on purchasedAsinEgoGraph to only retain edges with 
#     threshold >= 0.5, and assign resulting graph to purchasedAsinEgoTrimGraph
threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()
for f, t, e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight'] >= threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t,weight=e['weight'])
        
pos=networkx.spring_layout(purchasedAsinEgoTrimGraph)
matplotlib.pyplot.figure(figsize=(10,10))
networkx.draw_networkx_nodes(purchasedAsinEgoTrimGraph,pos,node_size=150)
networkx.draw_networkx_labels(purchasedAsinEgoTrimGraph,pos,font_size=2)
edgewidth = [ d['weight'] for (u,v,d) in purchasedAsinEgoTrimGraph.edges(data=True)]
networkx.draw_networkx_edges(purchasedAsinEgoTrimGraph,pos,width=edgewidth)
edgelabel = networkx.get_edge_attributes(purchasedAsinEgoTrimGraph,'weight')
networkx.draw_networkx_edge_labels(purchasedAsinEgoTrimGraph,pos,edge_labels=edgelabel,font_size=2)
matplotlib.pyplot.axis('off') 
matplotlib.pyplot.show()


# Next, recall that given the purchasedAsinEgoTrimGraph you constructed above, 
# you can get at the list of nodes connected to the purchasedAsin by a single 
# hop (called the neighbors of the purchasedAsin) 
# (3) YOUR CODE HERE: 
#     Find the list of neighbors of the purchasedAsin in the 
#     purchasedAsinEgoTrimGraph, and assign it to purchasedAsinNeighbors
purchasedAsinNeighbors = [i for i in purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)] 
print ("--------------------------------------------------------------")
print ("List of Neighbors of the purchasedAsin:")
print ("--------------------------------------------------------------")
print (purchasedAsinNeighbors)


# Next, let's pick the Top Five book recommendations from among the 
# purchasedAsinNeighbors based on one or more of the following data of the 
# neighboring nodes: SalesRank, AvgRating, TotalReviews, DegreeCentrality, 
# and ClusteringCoeff
# (4) YOUR CODE HERE: 
#     Note that, given an asin, you can get at the metadata associated with  
#     it using amazonBooks (similar to lines 49-56 above).
#     Now, come up with a composite measure to make Top Five book 
#     recommendations based on one or more of the following metrics associated 
#     with nodes in purchasedAsinNeighbors: SalesRank, AvgRating, 
#     TotalReviews, DegreeCentrality, and ClusteringCoeff. Feel free to compute
#     and include other measures. 

import pandas as pd
TrimeigenventorCentrality = networkx.eigenvector_centrality(purchasedAsinEgoTrimGraph)

lst = []
for i in purchasedAsinNeighbors:    
    lsttemp = [i,
               amazonBooks[i]['Title'],
               amazonBooks[i]['SalesRank'],
               amazonBooks[i]['TotalReviews'],
               amazonBooks[i]['AvgRating'],
               amazonBooks[i]['DegreeCentrality'],
               amazonBooks[i]['ClusteringCoeff'],
               TrimeigenventorCentrality[i]]
    lst.append(lsttemp)
    Top5Book = pd.DataFrame(data=lst, 
                            columns=['ASIN', 
                                     'Title', 
                                     'SalesRank', 
                                     'TotalReviews', 
                                     'AvgRating', 
                                     'DegreeCentrality', 
                                     'ClusteringCoeff', 
                                     'TrimeigenventorCentrality'])

TrimeigenventorCentralityBook = Top5Book.sort_values(by=['TrimeigenventorCentrality'], ascending=False)
TrimeigenventorCentralityBook.reset_index(drop=True, inplace=True)

from sklearn.preprocessing import MinMaxScaler
data = Top5Book[3:6]
scaler = MinMaxScaler()
print(scaler.fit(data))
print(scaler.data_max_)
print(scaler.transform(data))
print(scaler.transform([[2, 2]]))
    

print ("--------------------------------------------------------------")
print ("Top 5 Recommendations sorted by metrics - eigen ventor Centrality:")
print ("--------------------------------------------------------------")
print (TrimeigenventorCentralityBook[['ASIN','TrimeigenventorCentrality']].head(n=5))


# Print Top 5 recommendations (ASIN, and associated Title, Sales Rank, 
# TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff)
# (5) YOUR CODE HERE:  
print ("--------------------------------------------------------------")
print ("Top 5 Recommendations:")
for idx, sr in TrimeigenventorCentralityBook.head().iterrows():
    print ("--------------------------------------------------------------")
    print ("No.", idx+1)
    print ("--------------------------------------------------------------")
    print ("ASIN = ", sr[0],
           "\nTitle = ", sr[1], 
           "\nSalesRank = ", sr[2],
           "\nTotalReviews = ", sr[3],
           "\nAvgRating = ", sr[4],
           "\nDegreeCentrality = ", sr[5],
           "\nClusteringCoeff = ", sr[6])

