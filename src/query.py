#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Query:
    '''
       permet de stocker les informations liées à une requête :
       - son identifiant
       - son texte
       - la liste des identifiants des documents pertinents
    '''

    def __init__(self, idQuery, text, rel_docs):
        '''
            paramètres
            ----------
            idQuery : int
                      identifiant de la requête
            text : string
                   contenu de la requête
            rel_docs : list of int
                       liste des identifiants des documents pertinents
            stocke
            ------
            self.idQuery, self.text, self.rel_docs, les paramètres sus-
            mentionnés
        '''
        self.idQuery = idQuery
        self.text = text
        self.rel_docs = rel_docs

    def get_id(self):
        '''
            récupère l'id de la requête
            renvoie
            -------
            self.idQuery : int
                           identifiant de la requête
        '''
        return self.idQuery

    def get_text(self):
        '''
            récupère le texte de la requête
            renvoie
            -------
            self.text : string
                        contenu de la requête
        '''
        return self.text

    def get_rel_docs(self):
        '''
            récupère les documents pertinents pour la requête
            renvoie
            -------
            self.rel_docs : dict of int -> int
                            dictionnaire associant aux identifiants
                            des documents pertinents pour la requête
                            leur pertinence
        '''
        return self.rel_docs

class QueryParser:
    '''
        Permet de lire les fichiers de tests de requêtes et de
        jugements de pertinence
        stocke une collection de Query
    '''
    def __init__(self):
        '''
            stocke
            ------
            self.queriesCollection : dict of int -> string
                                     dictionnaire associant à chaque
                                     identifiant de requête le contenu
                                     de cette dernière
            self.judgementsCollection : dict of int -> Query
                                        dictionnaire associant à chaque
                                        identifiant de document l'objet
                                        Query de la requête concernée
            self.source_qry : string
                              nom du fichier contenant des jeux de
                              tests de requêtes
            self.source_rel : string
                              nom du fichier contenant les jugements de
                              pertinence pour les requêtes de test
        '''
        self.queriesCollection = None
        self.judgementsCollection = None
        self.source_qry = None

    def buildQueriesCollection(self, name):
        '''
            construit la collection de requêtes à partir du fichier passé
            en paramètre

            paramètres
            ----------
            name : nom du fichier contenant les jeux de tests de requêtes
        '''
        self.queriesCollection = dict()
        self.source_qry = name

        with open(name) as fp:
            line = fp.readline()
            while line:
                if line.startswith('.I'):
                    i=int(line.split()[1])
                    t=""
                    line = fp.readline()
                    if (line.startswith(".W")):
                        line = fp.readline()
                        while (not(line.startswith("."))):
                            t+=line
                            line = fp.readline()
                    t=t.replace('\n','').replace('\t',' ').replace('\\','')
                    if len(t) > 0:
                        self.queriesCollection[i] = t[1:]
                    else:
                        self.queriesCollection[i] = ""
                if not ('.I' in line):
                    line = fp.readline()

        print("Construction de la collection de requêtes achevée : la collection {} contient {} requêtes.".format(self.source_qry, len(self.queriesCollection)))

    def buildJudgementsCollection(self, name):
        '''
            construit la collection de judgement de pertinence à partir du
            fichier passé en paramètre

            paramètres
            ----------
            name : nom du fichier contenant les jugements de pertinence pour
            les requêtes de test
        '''
        self.judgementsCollection = dict()
        self.source_rel = name
        docs = dict()
        with open(name) as fp:
            line = fp.readline()
            while line:
                t=line.split()
                idQ=int(t[0])
                if idQ not in list(self.judgementsCollection.keys()):
                    query = Query(idQ, self.queriesCollection[idQ], [])
                    self.judgementsCollection[idQ]=query
                    self.judgementsCollection[idQ].rel_docs = dict()
                self.judgementsCollection[idQ].rel_docs[int(t[1])] = 1
                line = fp.readline()

        print("Construction de la collection de jugements de pertinence achevée : la collection {} contient {} requêtes.". \
                format(self.source_rel, len(self.judgementsCollection)))

    def getQueriesCollection(self):
        '''
            récupère la collection de requêtes

            renvoie
            -------
            self.queriesCollection : dict of int -> string
                                     collection de requêtes
        '''
        return self.queriesCollection

    def getJudgementsCollection(self):
        '''
            récupère la collection de jugements de pertinence

            renvoie
            -------
            self.queriesCollection : dict of int -> Query
                                     collection de jugements de
                                     pertinence
        '''
        return self.judgementsCollection

    def displayQueriesCollection(self):
        '''
            affiche la collection de requêtes
        '''
        for (i, text) in self.queriesCollection.items():
            print("--> Requête {}".format(i))
            print("\t{}".format(text))
            print("-------------------------------------")

    def displayJudgementsCollection(self):
        '''
            affiche la collection de jugements de pertinence
        '''
        for (i, query) in self.judgementsCollection.items():
            print("--> Requête {}".format(i))
            print("\t* Texte : {}".format(query.get_text()))
            print("\t* Documents pertinents : ")
            for idDoc, rel in query.get_rel_docs().items():
                print("\t{} ({})".format(idDoc, rel))
            print("-------------------------------------")

    def getSourceQuery(self):
        '''
            récupère le nom du fichier contenant les requêtes

            renvoie
            -------
            self.source_qry : string
        '''
        return self.source_qry

    def getSourceJudgements(self):
        '''
            récupère le nom du fichier contenant les jugements
            de pertinent

            renvoie
            -------
            self.source_rel : string
        '''
        return self.source_rel

