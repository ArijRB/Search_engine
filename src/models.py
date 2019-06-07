#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import collections
import porter
import numpy as np
import re
from weighter import *

def compute_norm(d):
    '''
        calcule la norme d'un document

        paramètres
        ----------
        d : dict of string -> int/float
            dictionnaire contenant les poids des termes pour un document
            ou une requête
        renvoie
        -------
        np.linalg.norm(vector) : float
                                 norme de d
    '''
    #return np.sqrt(np.sum(np.array(list(d.values()))**2))
    vector = np.array(list(d.values()))
    return np.linalg.norm(vector)

class IRModel:
    '''
        Classe générique d'un modèle de RI
    '''
    def __init__(self, indexer):
        '''
            paramètres
            ----------
            indexer : object IndexerSimple

            stocke
            ------
            self.indexer : object IndexerSimple
                           l'index passé en paramètre
        '''
        self.indexer = indexer

    def getScores(self, query):
        '''
            retourne les scores des documents pour une requête

            paramètres
            ----------
            query : string
                    requête
        '''
        raise NotImplementedError("Please Implement this method")

    def getRanking(self, query):
        '''
            retourne une liste de couples (document-score) ordonnée
            par score décroissant

            paramètres
            ----------
            query : string
                    requête
        '''
        raise NotImplementedError("Please Implement this method")

class Vectoriel(IRModel):
    '''
        Modèle vectoriel
    '''
    def __init__(self, indexer, weighter, normalized=False):
        '''
            paramètres
            ----------
            indexer : object IndexerSimple
            weighter : object Weighter
            normalized : boolean (par défault False)
                         permet de définir la fonction de score (produit
                         scalaire si False et score cosinus si True)

            stocke
            ------
            self.indexer : object IndexerSimple
            self.weighter : object Weighter
            self.normalized : boolean
            self.all_doc_weights : dict of int -> (dict of string -> int/float)
                                   dictionnaire contenant, pour chaque document
                                   de la collection, les poids des termes qu'il
                                   contient (calculés selon self.weighter)
            self.all_doc_norms : dict of int -> float
                                 dictionnaire contenant, pour chaque document de
                                 la collection, sa norme
        '''
        super().__init__(indexer)
        self.weighter = weighter
        self.normalized = normalized

        self.all_doc_weights = dict()
        self.all_doc_norms = dict()

        for (idDoc, doc) in self.indexer.getCollection().items():
            self.all_doc_weights[idDoc] = weighter.getWeightsForDoc(doc)

        for (doc_id, doc_weights) in self.all_doc_weights.items():
            self.all_doc_norms[doc_id] = compute_norm(doc_weights)

    def getScores(self, query):
        '''
            retourne les scores des documents pour une requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            scores : dict of int -> float
                     dictionnaire associant à chaque document son
                     score pour la requête (en ne gardant que ceux
                     dont le score n'est pas nul)
        '''
        query_weights = self.weighter.getWeightsForQuery(query)
        scores = dict()


        if not self.normalized:
            for (idDoc, weights) in self.all_doc_weights.items():
                rsv = 0
                for t in query_weights.keys():
                    if t in weights:
                        rsv += query_weights[t]*weights[t]
                if rsv != 0:
                    scores[idDoc] = rsv
        else:
            query_norm = compute_norm(query_weights)

            for (idDoc, weights) in self.all_doc_weights.items():
                inter = 0
                for t in query_weights.keys():
                    if t in weights:
                        inter += query_weights[t]*weights[t]
                if inter / (query_norm * self.all_doc_norms[idDoc]) != 0:
                    scores[idDoc] = inter / (query_norm * self.all_doc_norms[idDoc])

        return scores

    def getRanking(self, query):
        '''
            retourne une liste de couples (document-score) ordonnée
            par score décroissant

            paramètres
            ----------
            query : string
                    requête

            renvoie
            -------
            ranking : list of (int, float)
                      liste contenant les identifiants des documents les plus
                      pertinents et leur score, triée par ordre décroissant
        '''
        scores = self.getScores(query)
        ranking = [(idDoc, scores[idDoc]) for idDoc in sorted(scores, key=scores.get, reverse=True)]
        return ranking[:1000]

class ModeleLangue(IRModel):
    '''
        Modèle de langue
    '''
    def __init__(self, indexer):
        '''
            paramètres
            ----------
            indexer : object IndexerSimple

            stocke
            ------
            self.indexer : object IndexerSimple
            self.weighter : object Weighter1
            self.all_doc_weights : dict of int -> (dict of string -> int/float)
                                   dictionnaire contenant, pour chaque document
                                   de la collection, les poids des termes qu'il
                                   contient (calculés selon Weighter1)
            self.sum_all_stems : float
                                 somme des tfs de tous les termes de la collection
        '''
        super().__init__(indexer)
        self.weighter = Weighter1(indexer)

        self.all_doc_weights = dict()
        self.sum_all_stems = 0

        for (idDoc, doc) in self.indexer.getCollection().items():
            self.all_doc_weights[idDoc] = self.weighter.getWeightsForDoc(doc)

        for (t,dict_occ) in self.indexer.get_index_inverse().items():
            occ = list(dict_occ.values())
            self.sum_all_stems += sum(occ)

    def getScores(self, query):
        '''
            retourne les scores des documents pour une requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            scores : dict of int -> float
                     dictionnaire associant à chaque document son
                     score pour la requête (en ne gardant que ceux
                     dont le score n'est pas nul)
        '''
        query_weights = self.weighter.getWeightsForQuery(query)
        alpha = 0.8
        scores = dict()
        index_inverse = self.indexer.get_index_inverse()
        reg = dict()

        for stem in query_weights.keys():
            if stem in index_inverse:
                stem_weights = self.weighter.getWeightsForStem(stem)
                sum_stem = sum(list(stem_weights.values()))
                reg[stem] = sum_stem / self.sum_all_stems

        for (idDoc, weights) in self.all_doc_weights.items():
            s = 0
            sum_tf_doc = sum(list(weights.values())) # somme de tous les tf des termes du document
            for t in query_weights.keys():
                if t in weights:
                    tf = weights[t]
                    s += alpha * (- tf * math.log(tf/sum_tf_doc)) + (1-alpha) * reg[t]
            if s > 0:
                scores[idDoc] = s
        return scores

    def getRanking(self, query):
        '''
            retourne une liste de couples (document-score) ordonnée
            par score décroissant

            paramètres
            ----------
            query : string
                    requête

            renvoie
            -------
            ranking : list of (int, float)
                      liste contenant les identifiants des documents les plus
                      pertinents et leur score, triée par ordre décroissant
        '''
        scores = self.getScores(query)
        ranking = [(idDoc, scores[idDoc]) for idDoc in sorted(scores, key=scores.get, reverse=True)]
        return ranking[:1000]

class OkapiBM25(IRModel):
    '''
        Modèle OkapiBM25
    '''
    def __init__(self, indexer):
        '''
            paramètres
            ----------
            indexer : object IndexerSimple

            stocke
            ------
            self.indexer : object IndexerSimple
            self.weighter : object Weighter3
            self.all_doc_weights : dict of int -> (dict of string -> int/float)
                                   dictionnaire contenant, pour chaque document
                                   de la collection, les poids des termes qu'il
                                   contient (calculés selon self.weighter)
            self.all_doc_len : dict of int -> int
                               dictionnaire contenant, pour chaque document de
                               la collection, sa longueur
            self.avgdl : float
                         longueur moyenne des documents
        '''
        super().__init__(indexer)
        self.weighter = Weighter3(indexer)

        self.all_doc_weights = dict()
        self.all_doc_len = dict()

        regex_words = r'\b\w+\b'
        for (idDoc, doc) in self.indexer.getCollection().items():
            self.all_doc_weights[idDoc] = self.weighter.getWeightsForDoc(doc)
            terms = re.findall(regex_words,doc.get_text())
            self.all_doc_len[idDoc] =  len(terms)

        self.avgdl = np.mean(np.array(list(self.all_doc_len.values())))


    def getScores(self, query):
        '''
            retourne les scores des documents pour une requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            scores : dict of int -> float
                     dictionnaire associant à chaque document son
                     score pour la requête (en ne gardant que ceux
                     dont le score n'est pas nul)
        '''
        query_weights = self.weighter.getWeightsForQuery(query)
        k1 = 1.2
        b = 0.75
        scores = dict()

        for (idDoc, weights) in self.all_doc_weights.items():
            s = 0
            for t in query_weights.keys():
                if t in weights:
                    idf = query_weights[t]
                    tf = weights[t]
                    len_doc = self.all_doc_len[idDoc]
                    s += idf * (tf/(tf + k1 * (1-b) + b*(len_doc / self.avgdl)))
            if s > 0:
                scores[idDoc] = s
        return scores

    def getRanking(self, query):
        '''
            retourne une liste de couples (document-score) ordonnée
            par score décroissant

            paramètres
            ----------
            query : string
                    requête

            renvoie
            -------
            ranking : list of (int, float)
                      liste contenant les identifiants des documents les plus
                      pertinents et leur score, triée par ordre décroissant
        '''
        scores = self.getScores(query)
        ranking = [(idDoc, scores[idDoc]) for idDoc in sorted(scores, key=scores.get, reverse=True)]
        return ranking[:1000]

