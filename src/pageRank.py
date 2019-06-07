#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import operator
import numpy as np
import copy
import math

class PageRank:
    '''
        Classe associée à l'algorithme PageRank
    '''
    def __init__(self, model, n, k):
        '''
            paramètres
            ----------
            model : IRModel object
                    modèle de RI permettant de récupérer les documents seeds
            n : int
                nombre de documents seeds à considérer
            k : int
                nombre de liens entrants à considérer pour chaque document seed
            stocke
            ------
            self.model, self.n, self.k : les paramètres sus-mentionnés
        '''
        self.model = model
        self.n = n
        self.k = k

    def extract_graph(self, parser, seeds):
        '''
            détermine un sous-graphe de documents candidats

            paramètres
            ----------
            parser : Parser object
                     permet de récupérer les hyperliens des documents
            seeds : list of int
                    liste des identifiants des documents seeds
            renvoie
            -------
            G : dict of int -> (dict of int -> float)
                dictionnaire associant à chaque identifiant de document
                le dictionnaire des documents qu'il référence
                les noeuds de G sont les documents candidats et ceux vers
                lesquels ils pointent
        '''
        S = seeds
        G = dict()

        for node in S:
            G[node] = parser.getHyperlinksFrom(node)
            if self.k <= len(parser.getHyperlinksTo(node)):
                k_random = np.random.choice(parser.getHyperlinksTo(node),\
                        self.k, replace=False)
            else:
                k_random = parser.getHyperlinksTo(node)
            # ajout de k documents choisis aléatoirement parmi ceux pointant vers node
            for other_node in k_random:
                if other_node not in G:
                    G[other_node] = parser.getHyperlinksFrom(other_node)
            # ajout de tous les documents pointés par node
            for other_node in G[node].keys():
                if other_node not in G:
                    G[other_node] = parser.getHyperlinksFrom(other_node)
        return G

    def compute_PR_score(self, pr, G, d, a):
        '''
            calcule les scores Page Rank des documents d'un sous-graphe

            paramètres
            ----------
            pr : dict of int -> float
                 score Page Rank des documents à l'itération précédente
            G : dict of int -> (dict of int -> float)
                sous-graphe de documents
            d, a : float
                   paramètres de pondération du Page Rank
            renvoie
            -------
            new_pr : dict of int -> float
                     dictionnaire des score Page Rank des documents mis
                     à jour
        '''
        new_pr = copy.deepcopy(pr)
        total_pr=0
        for idDoc in G.keys():
            s = 0
            #for from_node in G[idDoc]:
            for from_node in G.keys():
                if idDoc in G[from_node].keys():
                    s += pr[from_node] * G[from_node][idDoc]
            new_pr[idDoc] = d * s + (1-d) * a
            total_pr += new_pr[idDoc]

        # normalisation
        for idDoc in new_pr.keys():
            new_pr[idDoc]=new_pr[idDoc]/total_pr
        return new_pr

    def compute_pageRank(self, q, parser):
        '''
            à partir d'une requête, applique l'algorithme de Page Rank
            sur un sous-graphe de documents et ordonne les documents
            selon l'importance qui leur a été attribuée

            paramètres
            ----------
            q : string
                requête
            parser : Parser object
                     permet de récupérer les hyperliens des documents
            renvoie
            -------
            sorted_pageranks : list of (int, float)
                               liste de tuples identifiant de document -
                               score Page Rank triée dans l'ordre décroissant
        '''
        ranking = np.array(self.model.getRanking(q))
        seeds = ranking[:self.n,0]
        G = self.extract_graph(parser, seeds)
        nodes = list(G.keys())

        for node, dict_target in G.items():
            nodes.extend(list(dict_target.keys()))

        page_ranks = {node:1./len(nodes) for node in nodes}
        d = 0.85
        a = 1

        current = copy.deepcopy(page_ranks)
        loss = np.inf

        while loss > 10**-4:
            new = self.compute_PR_score(current,G,d,a)
            loss = 0
            for node in new.keys():
                loss += math.pow((new[node] - current[node]),2)
            current = copy.deepcopy(new)

        sorted_pageranks = sorted(current.items(), \
            key=operator.itemgetter(1), reverse=True)
        return sorted_pageranks[:1000]



