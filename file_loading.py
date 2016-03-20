#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import codecs


#sp500_data.d => fluctuation du cours de chaque entreprise
#sp500_matType.d => même matrice mais avec des 0 ou des 1 uniquement (quand sim neg = >0 et 1 sinon)
#sp500_TypeNames => Nom des entreprises
#sp500_TypeNames => associe à chaque entreprise ton type reel (Energie, Insurance...)
#mi_sp_500d : matrice de similarite (valeurs entre 0 et 1)


class file_loader:

    def __init__(self):
        pass

    def load_file(self,fileName,isMatrix = False, dic = False):
        result = []
        if(not dic):
            with codecs.open(fileName,"r",encoding='utf-8') as my_file:
	        for line in my_file:
                    line= line.strip()
                    if(isMatrix):
                        result.append(line.split())
                    else:
                        result.append(line)
        else:
            result = {}
            with codecs.open(fileName,"r",encoding='utf-8') as my_file:
	        for line in my_file:
                    line= line.strip()
                    result[str(line.split()[0])]= line.split()[1]
        return result



'''
files = file_loader()
tmp = files.load_file("data/sp500_data.d",True)
'''
