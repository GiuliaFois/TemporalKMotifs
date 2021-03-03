# Temporal K-Motifs
This repository contains the final work I carried out at University of Pisa for my Bachelor Degree.

The aim of my thesis was to detect recurring communication patterns, called "Temporal K-Motifs", in the Facebook OSN. A Temporal K-Motif is a particular instance of what in the state of the art has the name of "motif", that is a pattern that can occur in a network. One efficient method of detecting them is to see the network as a graph and search the patterns as particular sub-graphs. "K" is the parameter that indicates the length of the motif, in terms of number of edges in the graph. The adjective "temporal" is related to the dynamic nature of the graph where such motifs are detected. 
 The task of detecting such motifs raises two critical points:
- Real life networks are inherently dynamic (they evolve in time)
- Finding patterns in a graph is a NP-complete problem, thus it has to be tackled in an efficient way on an algorithmic level

In my thesis I developed a python library that I then used to analyze a dataset composed of Facebook groups in order to detect the Temporal K-Motifs. I then processed the results I obtained to elaborate some statistics. The file "TemporalKMotifs.pdf" contains the thesis, where a detailed explanation of this problem and some graphs showing the results can be found.




