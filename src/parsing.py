#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import Counter

class Document:
    '''
        représente un document
    '''
    def __init__(self, id, text, hyper=None):
        '''
            paramètres
            ---------
            id : int
                 identifiant du document
            text : string
                   contenu du document
            hyper : int list (par défault None)
                    identifiants des documents référencés par le document

            contient
            --------
            self.id, self.texte, self.hyper, définis par les paramètres
            ci-dessus
        '''
        self.id = id
        self.text = text
        self.hyper = hyper

    def get_id(self):
        '''
            renvoie
            -------
            self.id : int
                      l'identifiant du document
        '''
        return self.id

    def get_text(self):
        '''
            renvoie
            -------
            self.text : string
                      le contenu du document
        '''
        return self.text

    def get_hyperlinks(self):
        '''
            renvoie
            -------
            self.hyper : int list
                      les hyperliens du document
        '''
        return self.hyper

class Parser:
    '''
        permet de parser la collection
        stocke la collection et le nom du fichier la contenant
    '''
    def __init__(self):
        '''
            stocke
            ------
            self.collection : dict int -> Document
                              dictionnaire associant à chaque identifiant de
                              document l'objet Document correspondant
            self.source : string
                          nom du fichier contenant la collection
        '''
        self.collection = None
        self.source = None

    def buildDocCollection(self, name):
        '''
            parse le fichier et stocke la collection sous la forme d'un
            dictionnaire de Document

            paramètres
            ----------
            name : string
                   nom du fichier contenant la collection
        '''
        self.source = name
        self.collection = dict()
        count = 0 # nombre de documents

        with open(name) as fp:
            line = fp.readline()
            while line:
                if line.startswith('.I'):
                    hyper=[]
                    count += 1
                    i=int(line.split()[1])
                    t=""
                    line = fp.readline()
                    if (line.startswith(".T")):
                        line = fp.readline()
                        while (not(line.startswith("."))):
                            t+=line
                            line = fp.readline()
                    t=t.replace('\n',' ')
                    while(not(line.startswith(".I"))and line ):
                        if line.startswith('.X'):
                            line = fp.readline()
                            while (not(line.startswith(".")) ) and line:
                                aux=(line.replace('\n','')).split("	")
                                if (len(aux)>1):
                                    hyper.append(int(aux[0]))
                                line = fp.readline()
                        else:
                            line = fp.readline()
                    if len(t) > 0:
                        d = Document(i, t,hyper)
                    else:
                        d = Document(i, "",hyper)
                    self.collection[i] = d
                if not (line.startswith('.I')):
                    line = fp.readline()

        print("Construction achevée : la collection {} contient {} documents.".\
                format(self.source, count))

    def getCollection(self):
        '''
            renvoie
            -------
            self.collection : dict int -> Document
                              la collection parsée
        '''
        return self.collection

    def displayCollection(self):
        '''
            affiche la collection
        '''
        for (i,doc) in self.collection.items():
            print("--> Document {}".format(i))
            print("\tTexte : {}".format(doc.get_text()))
            if doc.get_hyperlinks() is not None:
                print("\tHyperliens : {}".format(doc.get_hyperlinks()))
            print("-------------------------------------")

    def getSource(self):
        '''
            renvoie
            -------
            self.source : string
                          le nom du fichier contenant la collection
        '''
        return self.source

    def getHyperlinksTo(self,id_doc):
        '''
            renvoie les documents citant un document

            paramètres
            ----------
            id_doc : int
                     identifiant d'un document
            renvoie
            -------
            hyperlinks : int list
                         documents citant le document d'identifiant id_doc
        '''
        hyperlinks=[]
        for (i,doc) in self.collection.items():
            hyper = doc.get_hyperlinks()
            if (hyper is not None) and (id_doc in hyper):
                hyperlinks.append(i)
        return hyperlinks

    def getHyperlinksFrom(self,id_doc):
        '''
            renvoie les documents cités par un document

            paramètres
            ----------
            id_doc : int
                     identifiant d'un document
            renvoie
            -------
            hyperlinks : dict int -> float
                         dictionnaire dont chaque clé est l'identifiant d'un
                         document cité par celui d'identifiant id_doc, et la
                         valeur correspondante est la fréquence d'apparition
                         de l'hyperlien parmi tous les hyperliens du document
        '''
        hyperlinks = self.collection[id_doc].get_hyperlinks()
        if hyperlinks is None:
            return []
        hyperlinks = dict(Counter(hyperlinks))
        total = sum(hyperlinks.values())
        for doc in hyperlinks.keys():
            hyperlinks[doc] = hyperlinks[doc] * 1./ total
        return hyperlinks
