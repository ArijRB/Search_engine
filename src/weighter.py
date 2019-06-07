#!/usr/bin/env python
# -*- coding: utf-8 -*-
from indexation import *
import collections
import numpy as np
import math
import copy
import porter

class Weighter:
    '''
        Classe générique de pondération
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

    def getWeightsForDoc(self, idDoc):
        '''
            retourne les poids des termes pour un document
            dont l’identifiant est idDoc

            paramètres
            ----------
            idDoc : int
                    identifiant d'un document
        '''
        raise NotImplementedError("Please Implement this method")

    def getWeightsForStem(self, stem):
        '''
            retourne les poids du terme stem pour tous les
            documents qui le contiennent

            paramètres
            ----------
            stem : string
                   terme
        '''
        raise NotImplementedError("Please Implement this method")

    def getWeightsForQuery(self, query):
        '''
            retourne les poids des termes de la requête

            paramètres
            ----------
            query : string
                    requête
        '''
        raise NotImplementedError("Please Implement this method")

class Weighter1(Weighter):
    '''
        Classe de pondération

        Pondération tf pour les documents et les termes
        Pondération 0-1 pour les termes de la requête
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
        super(Weighter1, self).__init__(indexer)

    def getWeightsForDoc(self, idDoc):
        '''
            retourne les pondérations tf des termes pour un document
            dont l’identifiant est idDoc

            paramètres
            ----------
            idDoc : int
                    identifiant d'un document
            renvoie
            -------
            self.indexer.getTfsForDoc(idDoc) : dict of string -> int
                                               dictionnaire associant à chaque
                                               terme du document son nombre
                                               d'apparition dans le document

        '''
        return self.indexer.getTfsForDoc(idDoc)

    def getWeightsForStem(self, stem):
        '''
            retourne les pondérations tf du terme pour tous les documents
            qui le contiennent

            paramètres
            ----------
            stem : string
                   terme
            renvoie
            -------
            self.indexer.getTfsForStem(stem) : dict of int -> int
                                               dictionnaire associant à chaque
                                               document dans lequel stem apparaît le nombre
                                               d'occurrences de ce dernier
        '''
        return self.indexer.getTfsForStem(stem)

    def getWeightsForQuery(self, query):
        '''
            retourne les pondérations 0-1 pour les termes de la requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            token_weights: dict of string -> int
                           dictionnaire associant à chaque terme de la requête
                           la pondération 1
        '''
        query_lower = query.lower()
        tokens = list(set(query_lower.split(" ")))
        token_weights = dict()

        for t in tokens:
            token_weights[porter.stem(t)] = 1

        return token_weights

class Weighter2(Weighter):
    '''
        Classe de pondération

        Pondération tf pour les documents, les termes, et les termes de la requête
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
        super(Weighter2, self).__init__(indexer)

    def getWeightsForDoc(self, idDoc):
        '''
            retourne les pondérations tf des termes pour un document
            dont l’identifiant est idDoc

            paramètres
            ----------
            idDoc : int
                    identifiant d'un document
            renvoie
            -------
            self.indexer.getTfsForDoc(idDoc) : dict of string -> int
                                               dictionnaire associant à chaque
                                               terme du document son nombre
                                               d'apparition dans le document

        '''
        return self.indexer.getTfsForDoc(idDoc)

    def getWeightsForStem(self, stem):
        '''
            retourne les pondérations tf du terme pour tous les documents
            qui le contiennent

            paramètres
            ----------
            stem : string
                   terme
            renvoie
            -------
            self.indexer.getTfsForStem(stem) : dict of int -> int
                                               dictionnaire associant à chaque
                                               document dans lequel stem apparaît le nombre
                                               d'occurrences de ce dernier
        '''
        return self.indexer.getTfsForStem(stem)

    def getWeightsForQuery(self, query):
        '''
            retourne les pondérations tf des termes de la requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            token_weights: dict of string -> int
                           dictionnaire associant à chaque terme de la requête
                           sa pondération tf
        '''
        tokens = query.split(" ")
        processed_query = [porter.stem(t.lower()) for t in tokens]
        c = collections.Counter(processed_query)
        tokens = np.array(list(c.keys()))
        token_counts = np.array(list(c.values()))
        token_weights = dict()

        for i in range(len(tokens)):
            token_weights[tokens[i]] = token_counts[i]
        return token_weights

class Weighter3(Weighter):
    '''
        Classe de pondération

        Pondération tf pour les documents et les termes des documents
        Pondération idf pour les termes de la requête
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
        super(Weighter3,self).__init__(indexer)

    def getWeightsForDoc(self, idDoc):
        '''
            retourne les pondérations tf des termes pour un document
            dont l’identifiant est idDoc

            paramètres
            ----------
            idDoc : int
                    identifiant d'un document
            renvoie
            -------
            self.indexer.getTfsForDoc(idDoc) : dict of string -> int
                                               dictionnaire associant à chaque
                                               terme du document son nombre
                                               d'apparition dans le document

        '''
        return self.indexer.getTfsForDoc(idDoc)

    def getWeightsForStem(self, stem):
        '''
            retourne les pondérations tf du terme pour tous les documents
            qui le contiennent

            paramètres
            ----------
            stem : string
                   terme
            renvoie
            -------
            self.indexer.getTfsForStem(stem) : dict of int -> int
                                               dictionnaire associant à chaque
                                               document dans lequel stem apparaît le nombre
                                               d'occurrences de ce dernier
        '''
        return self.indexer.getTfsForStem(stem)

    def getWeightsForQuery(self, query):
        '''
            retourne les pondérations idf des termes de la requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            token_weights: dict of string -> float
                           dictionnaire associant à chaque terme de la requête
                           sa pondération idf
        '''
        df_dict = self.indexer.get_df()
        N = self.indexer.N
        tokens = query.split(" ")
        processed_query = [porter.stem(t.lower()) for t in tokens]
        q = list(set(processed_query))
        token_weights = dict()
        for t in processed_query:
            if t in df_dict:
                token_weights[t] = math.log((1+N)/(1+df_dict[t]))
            else:
                token_weights[t] = 0
        return token_weights

class Weighter4(Weighter):
    '''
        Classe de pondération

        Pondération 1+log(tf) pour les documents et les termes des documents
        Pondération idf pour les termes de la requête
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
        super(Weighter4, self).__init__(indexer)

    def getWeightsForDoc(self, idDoc):
        '''
            retourne les pondérations 1+log(tf) des termes pour un document
            dont l’identifiant est idDoc

            paramètres
            ----------
            idDoc : int
                    identifiant d'un document
            renvoie
            -------
            doc_weights : dict of string -> float
                          dictionnaire associant à chaque terme du document
                          sa pondération 1+log(tf)

        '''
        doc_weights = copy.deepcopy(self.indexer.getTfsForDoc(idDoc))

        for t,tf in doc_weights.items():
            doc_weights[t] = 1 + math.log(tf)
        return doc_weights

    def getWeightsForStem(self, stem):
        '''
            retourne les pondérations 1+log(tf) du terme pour tous les documents
            qui le contiennent

            paramètres
            ----------
            stem : string
                   terme
            renvoie
            -------
            stem_weights : dict of int -> float
                           dictionnaire associant à chaque document dans lequel
                           stem apparaît sa pondération 1+log(tf)
        '''
        stem_weights = copy.deepcopy(self.indexer.getTfsForStem(stem))

        for k,tf in stem_weights.items():
            stem_weights[k] = 1 + math.log(tf)
        return stem_weights

    def getWeightsForQuery(self, query):
        '''
            retourne les pondérations idf des termes de la requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            token_weights: dict of string -> float
                           dictionnaire associant à chaque terme de la requête
                           sa pondération idf
        '''
        df_dict = self.indexer.get_df()
        N = self.indexer.N
        tokens = query.split(" ")
        processed_query = [porter.stem(t.lower()) for t in tokens]
        q = list(set(processed_query))
        token_weights = dict()

        for t in processed_query:
            if t in df_dict:
                token_weights[t] = math.log((1+N)/(1+df_dict[t]))
            else:
                token_weights[t] = 0
        return token_weights

class Weighter5(Weighter):
    '''
        Classe de pondération

        Pondération (1+log(tf))*idf pour les documents et les termes des documents
        Pondération (1+log(tf))*idf pour les termes de la requête
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
        super(Weighter5, self).__init__(indexer)

    def getWeightsForDoc(self, idDoc):
        '''
            retourne les pondérations (1+log(tf))*idf des termes pour un document
            dont l’identifiant est idDoc

            paramètres
            ----------
            idDoc : int
                    identifiant d'un document
            renvoie
            -------
            doc_weights : dict of string -> float
                          dictionnaire associant à chaque terme du document
                          sa pondération (1+log(tf))*idf

        '''
        doc_weights = dict()
        tf_dict = copy.deepcopy(self.indexer.getTfsForDoc(idDoc))
        df_dict = self.indexer.get_df()
        N = self.indexer.N

        for t,tf in tf_dict.items():
            doc_weights[t] = (1 + math.log(tf)) * (math.log((1+N)/(1+df_dict[t])))

        return doc_weights

    def getWeightsForStem(self, stem):
        '''
            retourne les pondérations (1+log(tf))*idf du terme pour tous les documents
            qui le contiennent

            paramètres
            ----------
            stem : string
                   terme
            renvoie
            -------
            stem_weights : dict of int -> float
                           dictionnaire associant à chaque document dans lequel
                           stem apparaît sa pondération (1+log(tf))*idf
        '''
        stem_weights = dict()
        tf_dict = copy.deepcopy(self.indexer.getTfsForStem(stem))
        df_dict = self.indexer.get_df()
        N = self.indexer.N
        for t,tf in tf_dict.items():
            stem_weights[t] = (1 + math.log(tf)) * (math.log((1+N)/(1+df_dict[stem])))
        return stem_weights

    def getWeightsForQuery(self, query):
        '''
            retourne les pondérations (1+log(tf))*idf des termes de la requête

            paramètres
            ----------
            query : string
                    requête
            renvoie
            -------
            token_weights: dict of string -> float
                           dictionnaire associant à chaque terme de la requête
                           sa pondération (1+log(tf))*idf
        '''
        df_dict = self.indexer.get_df()
        N = self.indexer.N

        tokens = query.split(" ")
        processed_query = [porter.stem(t.lower()) for t in tokens]
        c = collections.Counter(processed_query)
        tokens = np.array(list(c.keys()))
        token_counts = np.array(list(c.values()))
        token_weights = dict()

        for i in range(len(tokens)):
            if tokens[i] in df_dict:
                token_weights[tokens[i]] = (1+math.log(token_counts[i])) * \
                        (math.log((1+N)/(1+df_dict[tokens[i]])))
            else:
                token_weights[tokens[i]] = 0

        return token_weights


