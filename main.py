import numpy as np
from file_loading import file_loader
import math
from pprint import pprint


class Cluster:

    def __init__(self,data,similariteMatrix,tradeOff,numberClusters,convergence,realName):
        self.loader = file_loader()
        self.data = self.loader.load_file(data,True)
        self.similarite = self.loader.load_file(similariteMatrix,True)
        self.names = self.loader.load_file(realName)
        self.T = tradeOff
        self.Nc = numberClusters
        self.c = convergence
        self.N = len(self.data)
        self.pi = 1.0/float(self.N)
        self.initialization()
        self.learn()
        print("Fin du clustering !")
        '''for i in range(self.N):
            print(sum(self.Pci[i]))'''
        self.generateClusters()


    def generateClusters(self):
        self.association = {}
        for i in range(self.Nc):
            self.association[i] = []
        tab = range(self.Nc)
        for i in range(self.N):
            classe  = np.random.choice(tab,p=self.Pci[i])
            self.association[classe].append(self.names[i])
        print("Association :")
        pprint(self.association)

    def initialization(self):
        self.Pci = []
        for i in range(self.N):
            self.Pci= self.Pci + list(np.random.dirichlet(np.ones(self.Nc),size=1))
        self.m =0
        print("Taille de la matrice PCmi ",len(self.Pci))
        print("Longueur : ",len(self.Pci[0]))
        self.PciNew = list(np.zeros((self.N,self.Nc)))
        print("Taille de la matrice PciNew ",len(self.PciNew))
        print("Longueur : ",len(self.PciNew[0]))

    #return P(m)(C)
    def get_pc(self,C):
        result = 0.0
        for i in range(self.N):
            result+=self.Pci[i][C] * self.pi
        return result

    def getSimC(self,C):
        return 0

    #wrong value  : self.similarite[element][C]
    def calculateNewPci(self,element):
        for C in range(self.Nc):
            subCalcul = self.T*(2.0*float(self.similarite[element][C])-self.getSimC(C))
            self.PciNew[element][C]= self.get_pc(C)*math.exp(subCalcul)
             

    def majPci(self,element):
        oldvalue = float(sum(self.PciNew[element]))
        for C in range(self.Nc):
            self.PciNew[element][C] = self.PciNew[element][C]/oldvalue
   
    def should_stop(self):
        stop = True
        for i in range(self.N):
            for C in range(self.Nc):
                if(self.PciNew[i][C] - self.Pci[i][C] > self.c):
                    stop = False
        return stop

    def learn(self):
        while(True):
            for i in range(self.N):
                self.calculateNewPci(i)
                self.majPci(i)
                self.m +=1
            if(self.should_stop()):
                print("L'algorithme a converge en ",self.m)
                self.Pci = self.PciNew[:]
                return
            self.Pci = self.PciNew[:]
        print("L'algo n'a pas converge ")


cluster = Cluster("data/sp500_data.d","mi_sp500.d",20,35,1,"data/sp500_names.d")
