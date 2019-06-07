#!/usr/bin/env python
# -*- coding: utf-8 -*-
from query import *
import math
import numpy as np

class EvalMesure:
    '''
        Classe générique pour les mesures d'évaluation
    '''
    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée
        '''
        raise NotImplementedError("Please Implement this method")

class Precision(EvalMesure):
    '''
        Classe associée à la précision au rang k
    '''
    def __init__(self, k):
        '''
            paramètres
            ----------
            k : int
                rang pour la précision
            stocke
            ------
            k : le paramètre
        '''
        super(Precision, self).__init__()
        self.k = k

    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée

            renvoie
            -------
            P : float
                précision à k calculée pour docs et query
        '''
        P = 0
        R = 0
        judgement = query.get_rel_docs()
        n = min(self.k, len(docs)) # au cas où k > nombre de documents renvoyés

        for i in range(n):
            idDoc = docs[i]
            if idDoc in judgement.keys():
                P += 1

        P /= n
        return P

class Rappel(EvalMesure):
    '''
        Classe associée au rappel au rang k
    '''
    def __init__(self, k):
        '''
            paramètres
            ----------
            k : int
                rang pour la précision
            stocke
            ------
            self.k : le paramètre
        '''
        super(Rappel, self).__init__()
        self.k = k

    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée

            renvoie
            -------
            R : float
                rappel à k calculé pour docs et query
        '''
        P = 0
        R = 0
        judgement = query.get_rel_docs()
        n = min(self.k, len(docs)) # au cas où k > nombre de documents renvoyés

        for i in range(n):
            idDoc = docs[i]
            if idDoc in judgement.keys():
                R += 1

        R /= len(judgement)
        return R

class F_mesure(EvalMesure):
    '''
        Classe associée à la F-mesure
    '''
    def __init__(self, k, beta):
        '''
            paramètres
            ----------
            k : int
                rang pour la précision
            beta : float
                   pondération bêta de la F-mesure
            stocke
            ------
            self.k, self.beta : les paramètres
        '''
        super(F_mesure, self).__init__()
        self.k = k
        self.beta = beta

    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée

            renvoie
            -------
            F : float
                F-mesure à k calculée pour docs et query
        '''
        P = 0
        R = 0
        judgement = query.get_rel_docs()
        n = min(self.k, len(docs)) # au cas où k > nombre de documents renvoyés

        for i in range(n):
            idDoc = docs[i]
            if idDoc in judgement.keys():
                R += 1
                P += 1

        R /= len(judgement)
        P /= n

        if P == 0 and R == 0:
            return 0

        F = (1+self.beta**2)*(P*R)/(self.beta**2*P+R)
        return F

class AvgPrecision(EvalMesure):
    '''
        Classe associée à la précision moyenne
    '''
    def __init__(self):
        super(AvgPrecision, self).__init__()

    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée

            renvoie
            -------
            avg : float
                  précision moyenne à k calculée pour docs et query
                  (moyenne des valeurs de précision des documents
                  pertinents par rapport à la requête)
        '''
        judgement = query.get_rel_docs()
        N = len(docs)
        n_rel = 0
        total_P = 0
        P = 0

        for k in range(N):
            if docs[k] in judgement.keys():
                n_rel += 1
                for i in range(k):
                    idDoc = docs[i]
                    if idDoc in judgement.keys():
                        P += 1
                P /= k+1
                total_P += P

        if n_rel == 0:
            return 0

        avg = total_P * 1.0 / n_rel
        return avg


class NDCG(EvalMesure):
    '''
        Classe associée à NDCG
    '''
    def __init__(self, p):
        '''
            paramètres
            ----------
            p : int
                rang
            stocke
            ------
            self.p : le paramètre
        '''
        super(NDCG, self).__init__()
        self.p = p

    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée

            renvoie
            -------
            DCG / IDCG : float
                         DCG calculé pour docs et query
        '''
        rel = query.get_rel_docs()
        if docs[0] in rel:
            DCG = rel[docs[0]]
        else:
            DCG = 0
        # liste de (idDoc, pertinence) triés selon la pertinence (liste idéale de résultats)
        sorted_rel_docs = sorted(rel.items(), key=lambda kv: kv[1], reverse=True)
        IDCG = rel[sorted_rel_docs[0][0]]
        for i in range(1, min(self.p, len(rel))):
            if docs[i] in rel:
                DCG += rel[docs[i]] / math.log(i+1,2)
            IDCG += rel[sorted_rel_docs[i][0]] / math.log(i+1,2)

        return DCG / IDCG


class ReciprocalRank(EvalMesure):
    '''
        Classe associée à ReciprocalRank (moyenne des rangs inverses)
    '''
    def __init__(self):
        super(ReciprocalRank, self).__init__()

    def evalQuery(self, docs, query):
        '''
            permet de calculer la mesure pour la liste des documents
            retournés par un modèle et un objet Query

            paramètres
            ----------
            docs : list of Document
                   liste des documents retournés par un modèle
            query : Query object
                    requête concernée

            renvoie
            -------
            mean_inv_ranks : float
                             moyenne des rangs inverses sur les documents
                             pertinents
        '''
        rel = query.get_rel_docs()
        # liste de (idDoc, pertinence) triés selon la pertinence
        sorted_rel_docs = sorted(rel.items(), key=lambda kv: kv[1], reverse=True)

        mean_inv_ranks = 0
        for (idDoc, rel) in sorted_rel_docs:
            if len(np.where(docs == idDoc)[0]) > 0:
                rank = np.where(docs == idDoc)[0][0]
                mean_inv_ranks += 1.0/(rank+1)
        mean_inv_ranks /= len(sorted_rel_docs)
        return mean_inv_ranks


