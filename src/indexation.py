#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import TextRepresenter
import collections
import math
import copy

class IndexerSimple:
    '''
        permet de construire les fichiers index d'une collection parsée

        stocke le nom du fichier source, la collection, l'index, l'index
        inversé, l'index normalisé, l'index inversé normalisé, le df, le
        tf_idf, et le nombre de documents de la collection
    '''
    def __init__(self, source):
        '''
            paramètres
            ----------
            source : string
                    nom du fichier contenant la collection
            stocke
            ------
            self.source : défini par le paramètre source
            self.collection : dict int -> Document
                              dictionnaire associant à chaque identifiant de
                              document l'objet Document correspondant
            self.index : dict of int -> (dict of string -> int)
                         dictionnaire associant à chaque identifiant de document
                         un dictionnaire associant à chaque token le constituant
                         son nombre d'apparition dans le document
            self.index_inverse : dict of string -> (dict of int -> int)
                                 dictionnaire associant à chaque token un dictionnaire
                                 associant à chaque identifiant de document dans
                                 lequel il apparaît son nombre d'occurrences
            self.index_norm : dict of int -> (dict of string -> float)
                              dictionnaire associant à chaque identifiant de
                              document un dictionnaire associant à chaque token
                              le constituant sa fréquenced'apparition dans le document
            self.index_inverse_norm : dict of string -> (dict of int -> float)
                                      dictionnaire associant à chaque token un
                                      dictionnaire associant à chaque identifiant
                                      de document dans lequel il apparaît sa fréquence
                                      d'occurrences
            self.df : dict of string -> int
                      dictionnaire associant à chaque token de la collection le
                      nombre de documents dans lequel il apparaît
            self.tf_idf : dict of string -> (dict of int -> float)
                          dictionnaire associant à chaque token de la collection
                          un dictionnaire faisant correspondre à chaque document
                          où il apparaît son tf-idf
            self.N : int
                     nombre de documents dans la collection
        '''
        self.source = source
        self.collection = None
        self.index = None
        self.index_inverse = None
        self.index_norm = None
        self.index_inverse_norm = None
        self.df = None
        self.tf_idf = None
        self.N = None

    def tokenize_count(self, ch):
        '''
            extrait les tokens d'un texte et construit un dictionnaire
            mappant chaque token à son nombre d'apparitions

            paramètres
            ----------
            ch : string
                 contenu d'un document
            renvoie
            -------
            tokens : dict of string -> int
                     dictionnaire associant à chaque token du texte
                     son nombre d'occurrences
        '''
        tokens = ch.lower()
        porter = TextRepresenter.PorterStemmer()
        tokens = porter.getTextRepresentation(tokens)

        return tokens

    def normalise(self, doc, index_inverse_norm, id_doc):
        '''
            normalise la valeur associée à un document dans un index,
            et les entrées d'un index inversé normalisé associées aux
            tokens du document

            paramètres
            ----------
            doc : dict of string -> int
                  dictionnaire associant à chaque token son nombre
                  d'occurrences dans le document d'identifiant id_doc
            index_inverse_norm : dict of string -> (dict of int -> float)
                                 index inversé normalisé
            id_doc : int
                     identifiant d'un document

            renvoie
            -------
            doc_normalise : dict of string -> float
                            dictionnaire doc dont les valeurs sont
                            normalisées
            index_inverse_norm : dict of string -> (dict of int -> float)
                                 index inversé normalisé dans lequel sont
                                 rajoutées les fréquences d'occurrences des
                                 tokens de doc dans le document id_doc
        '''
        doc_normalise = dict()
        n=sum(list(doc.values()))
        for token,occ in doc.items():
            doc_normalise[token]=occ/n
            index_inverse_norm[token][id_doc]=occ/n
        return doc_normalise,index_inverse_norm

    def normalise_index(self,index, index_inverse):
        '''
            normalise l'index et l'index inversé passés en paramètres

            paramètres
            ----------
            index : dict of int -> (dict of string -> int)
                    index d'une collection
            index_inverse : dict of string -> (dict of int -> int)
                            index inversé d'une collection

            renvoie
            -------
            self.index_norm : dict of int -> (dict of string -> float)
                              index normalisé
            self.index_inverse_norm : dict of string -> (dict of int -> float)
                                      index inversé normalisé
        '''
        index_norm=dict()
        index_inverse_norm = copy.deepcopy(index_inverse)
        for id_doc,dict_tokens in index.items():
            index_norm[id_doc], index_inverse_norm = self.normalise(dict_tokens,\
                    index_inverse_norm,id_doc)
        return index_norm,index_inverse_norm

    def indexation(self, collection):
        '''
            indexe la collection passée en paramètre
            sauvegarde les index créés dans des fichiers

            paramètres
            ----------
            collection : dict of int -> Document
                         dictionnaire associant à chaque identifiant d'un document
                         l'objet Document associé
        '''
        f_index = open("../index/" + self.source[:-4] + "_index.txt", "w")
        f_index_inverse = open("../index/" + self.source[:-4] + "_index_inverse.txt", "w")
        dict_index = dict()
        dict_index_inverse = dict()
        n = len(collection)
        df = dict()
        tf_idf = dict(dict())

        for (i, doc) in collection.items():
            text = doc.get_text()
            dict_index[i] = dict(self.tokenize_count(text))

            f_index.write("{'" + str(i) + "': " + str(dict_index[i]) + "}\n")
            for token in dict_index[i] :
                if token in dict_index_inverse.keys():
                    dict_index_inverse[token][i]=dict_index[i][token]
                    df[token] += 1
                else:
                    dict_index_inverse[token]={}
                    dict_index_inverse[token][i]=dict_index[i][token]
                    df[token] = 1

        for token in df.keys():
            f_index_inverse.write("{'" + token + "': " + str(dict_index_inverse[token]) + "}\n")
            tf_idf[token] = {}
            for (i, doc) in collection.items():
                if token in dict_index[i]:
                    tf_idf[token][i]=dict_index[i][token]*math.log((1+n)/(1+df[token]))

        self.index = dict_index
        self.index_inverse = dict_index_inverse
        self.index_norm,self.index_inverse_norm= self.normalise_index(dict_index,\
           self.index_inverse)
        self.tf_idf = tf_idf
        self.df = df
        self.N = n
        self.collection = collection

        f_index.close()
        f_index_inverse.close()

        print("Indexation de la collection {} achevée".format(self.source))

    def get_index(self, normalized=False):
        '''
            paramètres
            ----------
            normalized : boolean (par défault False)
                         True si l'on souhaite l'index normalisé
            renvoie
            -------
            self.index/index_norm : dict of int -> (dict of string
                                       -> int/float)
                                       l'index de la collection
        '''
        if normalized:
            return self.index_norm
        else:
            return self.index

    def get_index_inverse(self, normalized=False):
        '''
            paramètres
            ----------
            normalized : boolean (par défault False)
                         True si l'on souhaite l'index normalisé

            renvoie
            -------
            self.index_inverse/index_inverse_norm :
                dict of string -> (dict of int -> int/float)
                l'index inversé de la collection
        '''
        if normalized:
            return self.index_inverse_norm
        else:
            return self.index_inverse

    def get_df(self):
        '''
            renvoie
            -------
            self.df : dict of string -> int
                      le dictionnaire des Document Frequencies
        '''
        return self.df

    def get_tfidf(self):
        '''
            renvoie
            -------
            self.tfidf : dict of string -> (dict of int -> float)
                         dictionnaire associant à chaque terme son
                         tfidf pour chaque document dans lequel il
                         apparaît
        '''
        return self.tf_idf


    def getTfsForDoc(self, doc):
        '''
            retourne la représentation stem-tf d'un document à partir de
            l'index

            paramètres
            ----------
            doc : object Document
                  document

            renvoie
            -------
            self.index[doc.get_id()] : dict of string -> int
                                       dictionnaire associant à chaque token du
                                       document son nombre d'apparition dans le
                                       document
        '''
        return self.index[doc.get_id()]

    def getTfIDFsForDoc(self, doc):
        '''
            retourne la représentation stem-tfidf d'un document à partir de
            l'index

            paramètres
            ----------
            doc : object Document
                  document

            renvoie
            -------
            d : dict of string -> float
                dictionnaire associant à chaque token du document son tf-idf
                dans le document
        '''
        d = dict()
        i = doc.get_id()
        for token in self.index[i]:
            d[token] = self.tf_idf[token][i]
        return d

    def getTfsForStem(self, stem):
        '''
            retourne la représentation doc-tf d'un stem à partir de l'index
            inversé

            paramètres
            ----------
            stem : string
                   mot stemmé

            renvoie
            -------
            self.index_inverse[stem] : dict of int -> int
                                       dictionnaire associant à chaque document
                                       dans lequel stem apparaît le nombre
                                       d'occurrences de ce dernier
        '''
        return self.index_inverse[stem]

    def getTfIDFsForStem(self, stem):
        '''
            retourne la représentation doc-tfidf d'un stem à partir de l'index
            inversé

            paramètres
            ----------
            stem : string
                   mot stemmé

            renvoie
            -------
            self.tf_idf[stem] : dict of int -> float
                                dictionnaire associant à chaque document
                                dans lequel stem apparaît le tf-idf de ce
                                dernier
        '''
        return self.tf_idf[stem]

    def getStrDoc(self, doc):
        '''
            récupère le texte d'un document

            paramètres
            ----------
            doc : object Document
                  document

            renvoie
            -------
            doc.get_text() : string
                             texte du document
        '''
        return doc.get_text()

    def getCollection(self):
        '''
            récupère la collection

            renvoie
            -------
            self.collection : dict of int -> Document
                              dictionnaire associant à chaque identifiant
                              d'un document l'objet Document associé
        '''
        return self.collection
