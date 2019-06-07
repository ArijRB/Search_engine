#!/usr/bin/env python
# -*- coding: utf-8 -*-
from evalMesure import *
from models import *
import numpy as np
from scipy import stats

class EvalIRModel:
    '''
        Permet l'évaluation d'un modèle de recherche sur un ensemble
        de requêtes selon une mesure d'évaluation
    '''
    def __init__(self, model, mesure):
        '''
            paramètres
            ----------
            model : IRModel object
                    modèle à évaluer
            mesure : EvalMesure
                     mesure d'évaluation à utiliser
            stocke
            ------
            self.model, self.mesure : les paramètres sus-mentionnés
        '''
        self.model = model
        self.mesure = mesure

    def eval(self, qParser, verbose=False):
        '''
            évalue le modèle sur un ensemble de requêtes

            paramètres
            ----------
            qParser : QueryParser object
                      objet QueryParser stockant la collection de
                      requêtes sur laquelle évaluer le modèle
            verbose : boolean
                      True si l'on souhaite afficher les scores,
                      False sinon
            renvoie
            -------
            np.mean(all_evals), np.std(all_evals), all_evals :
                float, float, (np.array, shape (1, n_queries))
                moyenne et écart-type des résultats pour self.model

        '''
        allQueries_dict = qParser.getJudgementsCollection()
        all_evals = []

        for (idQ, query) in allQueries_dict.items():
            model_ranking = self.model.getRanking(query.get_text())
            model_ranking = np.array(model_ranking)[:,0] # récupération des id
            score = self.mesure.evalQuery(model_ranking, query)
            if verbose:
                print("--> Requête {} ".format(idQ))
                print("\t* Texte : {}".format(query.get_text()))
                print("\t* Documents pertinents : {}".format(query.get_rel_docs()))
                print("\t* 5 premiers documents retournés par le modèle : {}".format(model_ranking[:5]))
                print("\t* Score : {}".format(score))
                print("-------------------------------------")
            all_evals.append(score)

        all_evals = np.array(all_evals)
        return np.mean(all_evals), np.std(all_evals), all_evals

    def significantly_different(self, scores1, scores2, threshold=0.05):
        '''
            teste si deux modèles sont significativement différents

            paramètres
            ----------
            scores1 : np.array, shape (1, n_queries)
                      scores du premier modèle
            scores2 : np.array, shape (1, n_queries)
                      scores du deuxième modèle
            threshold : float (0.05 par défaut)
                        seuil de confiance
            renvoie
            -------
            diff : boolean
                   True si les modèles sont significativement différents
                   au seuil threshold, False sinon
            tstat : float
                    la statistique de test
        '''
        tstat, pvalue = stats.ttest_ind(scores1,scores2)
        diff = False
        if pvalue < threshold: # significativement différents
            diff = True

        return diff, tstat


