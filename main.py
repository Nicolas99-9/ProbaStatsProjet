import numpy as np
from file_loading import file_loader
import math
from pprint import pprint
from scipy.spatial import distance
import random


class Cluster:

    def __init__(self,data,similariteMatrix,tradeOff,numberClusters,convergence,realName,typesName,matType,verbose = True):
        self.loader = file_loader()
        self.data = self.loader.load_file(data,True)
        self.similarite = self.loader.load_file(similariteMatrix,True)
        self.matType = self.loader.load_file(matType,True)
        self.typesName = self.loader.load_file(typesName,False,dic= True)
        self.names = self.loader.load_file(realName)
        self.verbose = verbose
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

    #return the domain of the compagnie
    def associate(self,tab):
        tmp = [i for i in range(len(tab)) if int(tab[i])==1]
        sss = [self.typesName[i] for i in tmp]
        return "-".join(sss)


    def compute_similar_value(self,similarValue):
        result = {}
        for element in similarValue:
            result[element] = 0.0
            for i in range(len(similarValue[element])):
                for j in range(len(similarValue[element])):
                    #print(similarValue[element][i],similarValue[element][j])
                    result[element] += distance.correlation(np.array(similarValue[element][i]).astype(float),np.array(similarValue[element][j]).astype(float))
            result[element] = result[element]/float(len(similarValue[element]))
        return result
                    


    def affichage_random(self):
        result = 483.98083886540689 #precompute value to improve performances
        '''for i in range(len(self.matType)):
            for j in range(len(self.matType)):
                result += distance.correlation(np.array(self.matType[i]).astype(float),np.array(self.matType[j]).astype(float))
        result = result/float(len(self.matType))'''
        print("Distance moyenne des elements non regroupes par classe :  ",result)
        similarValue = {}
        for i in range(self.Nc):
            similarValue[i] = []
        for i in range(len(self.matType)):
            similarValue[random.randint(0,self.Nc-1)].append(self.matType[i])
        similarValue = self.compute_similar_value(similarValue)
        print("Distance moyenne pour ", self.Nc , " clusters choisis aleatoirement avec une proba uniforme : "  , np.mean(similarValue.values()))
            

    def generateClusters(self):
        self.association = {}
        similarValue = {}
        for i in range(self.Nc):
            self.association[i] = []
            similarValue[i] = []
        tab = range(self.Nc)
        for i in range(self.N):
            classe  = np.random.choice(tab,p=self.Pci[i])
            self.association[classe].append((self.names[i],self.associate(self.matType[i])))
            similarValue[classe].append(self.matType[i])
        print("Resultats :")
        similarValue = self.compute_similar_value(similarValue)
        if(self.verbose):
            for element in self.association:
                print("---------------------------------------")
                print("Numero du cluster : ", element , " Distance moyenne : ", similarValue[element])
                for i in range(len(self.association[element])):
                    print(self.association[element][i])
        print("Similarite moyenne :", np.mean(similarValue.values()))
        self.affichage_random()

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


cluster = Cluster("data/sp500_data.d","mi_sp500.d",20,35,0.1,"data/sp500_names.d","data/sp500_TypeNames.d","data/sp500_matType.d")

'''
Resultats : 

nicolas@nicolas:/media/nicolas/NICO USB/Probas-stats-projet$ python main.py 
('Taille de la matrice PCmi ', 501)
('Longueur : ', 35)
('Taille de la matrice PciNew ', 501)
('Longueur : ', 35)
("L'algorithme a converge en ", 1002)
Fin du clustering !
Resultats :
---------------------------------------
('Numero du cluster : ', 0, ' Distance moyenne : ', 105.07825785183938)
(u'Johnson Controls [JCI]', u'Consumer-Automobiles-Auto-Auto')
(u'General Electric [GE]', u'Industrials-Capital-Industrial-Industrial')
(u'General Mills [GIS]', u'Consumer-Food-Food-Packaged')
(u'Dell Inc. [DELL]', u'Information-Technology-Computers-Computer')
(u'Omnicom Group [OMC]', u'Consumer-Media-Media-Advertising')
(u'Safeway Inc. [SWY]', u'Consumer-Food-Food-Food')
(u'Cooper Tire & Rubber [CTB]', u'Consumer-Automobiles-Auto-Tires')
(u'General Motors [GM]', u'Consumer-Automobiles-Automobiles-Automobile')
(u'AT&T Corp. (New) [T]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Deluxe Corp. [DLX]', u'Industrials-Commercial-Commercial-Diversified')
(u'Bard (C.R.) Inc. [BCR]', u'Health-Health-Health-Health')
(u'Cummins  Inc. [CMI]', u'Industrials-Capital-Machinery-Construction')
(u'Compuware Corp. [CPWR]', u'Information-Software-Software-Application')
(u'Anthem  Inc. [ATH]', u'Health-Health-Health-Managed')
(u'Lincoln National [LNC]', u'Financials-Insurance-Insurance-Life')
(u'AES Corp. [AES]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
(u'Navistar International Corp. [NAV]', u'Industrials-Capital-Machinery-Construction')
(u'Dana Corp. [DCN]', u'Consumer-Automobiles-Auto-Auto')
(u'Equity Office Properties [EOP]', u'Financials-Real-Real-Real')
(u'Fifth Third Bancorp [FITB]', u'Financials-Banks-Commercial-Regional')
(u'Motorola Inc. [MOT]', u'Information-Technology-Communications-Communications')
(u'Gannett Co. [GCI]', u'Consumer-Media-Media-Publishing')
(u'ITT Industries  Inc. [ITT]', u'Industrials-Capital-Machinery-Industrial')
(u'Mercury Interactive [MERQ]', u'Information-Software-Software-Application')
(u'Cardinal Health  Inc. [CAH]', u'Health-Health-Health-Health')
(u'Rockwell Automation  Inc. [ROK]', u'Industrials-Capital-Electrical-Electrical')
(u'Thomas & Betts [TNB]', u'Industrials-Capital-Electrical-Electrical')
(u'Bank One Corp. [ONE]', u'Financials-Banks-Commercial-Diversified')
(u'Janus Capital Group [JNS]', u'Financials-Diversified-Capital-Asset')
(u'Tribune Co. [TRB]', u'Consumer-Media-Media-Publishing')
(u'Molex Inc. [MOLX]', u'Information-Technology-Electronic-Electronic')
(u'KeyCorp [KEY]', u'Financials-Banks-Commercial-Regional')
(u'Vulcan Materials [VMC]', u'Materials-Materials-Construction-Construction')
(u'Providian Financial Corp. [PVN]', u'Financials-Diversified-Consumer-Consumer')
(u'AmerisourceBergen Corp. [ABC]', u'Health-Health-Health-Health')
(u'Cooper Industries  Ltd. [CBE]', u'Industrials-Capital-Electrical-Electrical')
(u'MedImmune Inc. [MEDI]', u'Health-Pharmaceuticals-Biotechnology-Biotechnology')
(u'International Bus. Machines [IBM]', u'Information-Technology-Computers-Computer')
(u'T. Rowe Price Group [TROW]', u'Financials-Diversified-Capital-Asset')
(u'Ford Motor [F]', u'Consumer-Automobiles-Automobiles-Automobile')
(u'McCormick & Co. [MKC]', u'Consumer-Food-Food-Packaged')
(u'Delphi Corporation [DPH]', u'Consumer-Automobiles-Auto-Auto')
(u'Zimmer Holdings [ZMH]', u'Health-Health-Health-Health')
(u'Federated Dept. Stores [FD]', u'Consumer-Retailing-Multiline-Department')
(u'Textron Inc. [TXT]', u'Industrials-Capital-Industrial-Industrial')
(u'Campbell Soup [CPB]', u'Consumer-Food-Food-Packaged')
(u'PACCAR Inc. [PCAR]', u'Industrials-Capital-Machinery-Construction')
(u'Goldman Sachs Group [GS]', u'Financials-Diversified-Capital-Investment')
(u'American Standard [ASD]', u'Industrials-Capital-Building-Building')
(u'Eaton Corp. [ETN]', u'Industrials-Capital-Machinery-Industrial')
(u'Walt Disney Co. [DIS]', u'Consumer-Media-Media-Movies')
(u'Ashland Inc. [ASH]', u'Energy-Energy-Oil-Oil')
(u'Leggett & Platt [LEG]', u'Consumer-Consumer-Household-Home')
(u'Pall Corp. [PLL]', u'Industrials-Capital-Machinery-Industrial')
(u'Union Planters Corporation [UPC]', u'Financials-Banks-Commercial-Regional')
(u'Becton  Dickinson [BDX]', u'Health-Health-Health-Health')
(u'SouthTrust Corp. [SOTR]', u'Financials-Banks-Commercial-Regional')
(u'AmSouth Bancorporation [ASO]', u'Financials-Banks-Commercial-Regional')
(u'CenterPoint Energy [CNP]', u'Utilities-Utilities-Electric-Electric')
(u'Dover Corp. [DOV]', u'Industrials-Capital-Machinery-Industrial')
(u'Schering-Plough [SGP]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'SunTrust Banks [STI]', u'Financials-Banks-Commercial-Regional')
(u'Charter One Financial [CF]', u'Financials-Banks-Commercial-Regional')
(u'Black & Decker Corp. [BDK]', u'Consumer-Consumer-Household-Household')
(u'Nordstrom [JWN]', u'Consumer-Retailing-Multiline-Department')
(u'Wells Fargo [WFC]', u'Financials-Banks-Commercial-Diversified')
(u'Harley-Davidson [HDI]', u'Consumer-Automobiles-Automobiles-Motorcycle')
(u'Bank of America Corp. [BAC]', u'Financials-Banks-Commercial-Diversified')
(u'Electronic Data Systems [EDS]', u'Information-Software-IT-Data')
(u'Huntington Bancshares [HBAN]', u'Financials-Banks-Commercial-Regional')
(u'First Data [FDC]', u'Information-Software-IT-Data')
(u'General Dynamics [GD]', u'Industrials-Capital-Aerospace-Aerospace')
(u'Dillard Inc. [DDS]', u'Consumer-Retailing-Multiline-Department')
(u'M&T Bank Corp. [MTB]', u'Financials-Banks-Commercial-Regional')
(u'Nucor Corp. [NUE]', u'Materials-Materials-Metals-Steel')
(u'Bristol-Myers Squibb [BMY]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Cintas Corporation [CTAS]', u'Industrials-Commercial-Commercial-Diversified')
(u'Johnson & Johnson [JNJ]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Eastman Kodak [EK]', u'Consumer-Consumer-Leisure-Photographic')
(u'Mylan Laboratories [MYL]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Health Management Assoc. [HMA]', u'Health-Health-Health-Health')
(u'Lockheed Martin Corp. [LMT]', u'Industrials-Capital-Aerospace-Aerospace')
(u'Parker-Hannifin [PH]', u'Industrials-Capital-Machinery-Industrial')
(u'North Fork Bancorporation [NFB]', u'Financials-Banks-Commercial-Regional')
(u'MBNA Corp. [KRB]', u'Financials-Diversified-Consumer-Consumer')
(u'Toys R Us  Inc. [TOY]', u'Consumer-Retailing-Specialty-Specialty')
(u'Wachovia Corp. (New) [WB]', u'Financials-Banks-Commercial-Diversified')
(u'Snap-On Inc. [SNA]', u'Consumer-Consumer-Household-Household')
(u'Chiron Corp. [CHIR]', u'Health-Pharmaceuticals-Biotechnology-Biotechnology')
(u'Emerson Electric [EMR]', u'Industrials-Capital-Electrical-Electrical')
(u'Visteon Corp. [VC]', u'Consumer-Automobiles-Auto-Auto')
(u'Regions Financial Corp. [RF]', u'Financials-Banks-Commercial-Regional')
(u'May Dept. Stores [MAY]', u'Consumer-Retailing-Multiline-Department')
(u'Goodrich Corporation [GR]', u'Industrials-Capital-Aerospace-Aerospace')
(u"Wendy's International [WEN]", u'Consumer-Hotels-Hotels-Restaurants')
(u'Caremark Rx [CMX]', u'Health-Health-Health-Health')
(u'Torchmark Corp. [TMK]', u'Financials-Insurance-Insurance-Life')
(u'3M Company [MMM]', u'Industrials-Capital-Industrial-Industrial')
(u'Illinois Tool Works [ITW]', u'Industrials-Capital-Machinery-Industrial')
(u'Heinz (H.J.) [HNZ]', u'Consumer-Food-Food-Packaged')
(u'Crane Company [CR]', u'Industrials-Capital-Machinery-Industrial')
(u'Newell Rubbermaid Co. [NWL]', u'Consumer-Consumer-Household-Housewares')
(u'Convergys Corp. [CVG]', u'Information-Software-IT-Data')
(u'Comerica Inc. [CMA]', u'Financials-Banks-Commercial-Diversified')
(u'Home Depot [HD]', u'Consumer-Retailing-Specialty-Home')
(u'Big Lots  Inc. [BLI]', u'Consumer-Retailing-Multiline-General')
(u'Medtronic Inc. [MDT]', u'Health-Health-Health-Health')
(u'Goodyear Tire & Rubber [GT]', u'Consumer-Automobiles-Auto-Tires')
(u'Andrew Corp. [ANDW]', u'Information-Technology-Communications-Communications')
(u'Lucent Technologies [LU]', u'Information-Technology-Communications-Communications')
(u'TECO Energy [TE]', u'Utilities-Utilities-Electric-Electric')
(u'Office Depot [ODP]', u'Consumer-Retailing-Specialty-Specialty')
(u'Grainger (W.W.) Inc. [GWW]', u'Industrials-Capital-Trading-Trading')
---------------------------------------
('Numero du cluster : ', 1, ' Distance moyenne : ', 20.661415172955138)
(u'Burlington Northern Santa Fe C [BNI]', u'Industrials-Transportation-Road-Railroads')
(u'Kimberly-Clark [KMB]', u'Consumer-Household-Household-Household')
(u'Clorox Co. [CLX]', u'Consumer-Household-Household-Household')
(u'*** [AIH]', u'No_Label')
(u'Genuine Parts [GPC]', u'Consumer-Retailing-Distributors-Distributors')
(u'Delta Air Lines [DAL]', u'Industrials-Transportation-Airlines-Airlines')
(u'AutoNation  Inc. [AN]', u'Consumer-Retailing-Specialty-Specialty')
(u'Norfolk Southern Corp. [NSC]', u'Industrials-Transportation-Road-Railroads')
(u'Century Telephone [CTL]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Charles Schwab [SCH]', u'Financials-Diversified-Capital-Investment')
(u'ProLogis [PLD]', u'Financials-Real-Real-Real')
(u"Apartment Investment & Mgmt'A' [AIV]", u'Financials-Real-Real-Real')
(u'Chubb Corp. [CB]', u'Financials-Insurance-Insurance-Property')
(u'BellSouth [BLS]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Avery Dennison Corp. [AVY]', u'Industrials-Commercial-Commercial-Office')
(u'CSX Corp. [CSX]', u'Industrials-Transportation-Road-Railroads')
(u'Fannie Mae [FNM]', u'Financials-Banks-Thrifts-Thrifts')
(u'Sysco Corp. [SYY]', u'Consumer-Food-Food-Food')
(u'Colgate-Palmolive [CL]', u'Consumer-Household-Household-Household')
(u'Union Pacific [UNP]', u'Industrials-Transportation-Road-Railroads')
(u'Cincinnati Financial [CINF]', u'Financials-Insurance-Insurance-Property')
(u'ChevronTexaco Corp. [CVX]', u'Energy-Energy-Oil-Integrated')
(u'Merck & Co. [MRK]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
---------------------------------------
('Numero du cluster : ', 2, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Anheuser-Busch [BUD]', u'Consumer-Food-Beverages-Brewers')
---------------------------------------
('Numero du cluster : ', 3, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'*** [NX]', u'No_Label')
---------------------------------------
('Numero du cluster : ', 4, ' Distance moyenne : ', 1.0196078431372539)
(u'Sempra Energy [SRE]', u'Utilities-Utilities-Gas-Gas')
(u'Consolidated Edison [ED]', u'Utilities-Utilities-Electric-Electric')
(u'Public Serv. Enterprise Inc. [PEG]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
---------------------------------------
('Numero du cluster : ', 5, ' Distance moyenne : ', 0.50980392156862742)
(u'Marathon Oil Corp. [MRO]', u'Energy-Energy-Oil-Integrated')
(u'Valero Energy [VLO]', u'Energy-Energy-Oil-Oil')
(u'Amerada Hess [AHC]', u'Energy-Energy-Oil-Integrated')
(u'Sunoco.  Inc. [SUN]', u'Energy-Energy-Oil-Oil')
---------------------------------------
('Numero du cluster : ', 6, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Applera Corp-Applied Biosystems Group [ABI]', u'Health-Health-Health-Health')
---------------------------------------
('Numero du cluster : ', 7, ' Distance moyenne : ', 2.2204460492503131e-16)
(u'Darden Restaurants [DRI]', u'Consumer-Hotels-Hotels-Restaurants')
(u'Yum! Brands  Inc [YUM]', u'Consumer-Hotels-Hotels-Restaurants')
---------------------------------------
('Numero du cluster : ', 8, ' Distance moyenne : ', 8.0024812816560402)
(u'Keyspan Energy [KSE]', u'Utilities-Utilities-Gas-Gas')
(u'*** [TWW]', u'No_Label')
(u'Mattel  Inc. [MAT]', u'Consumer-Consumer-Leisure-Leisure')
(u'Dominion Resources [D]', u'Utilities-Utilities-Electric-Electric')
(u'PPL Corp. [PPL]', u'Utilities-Utilities-Electric-Electric')
(u'Pepsi Bottling Group [PBG]', u'Consumer-Food-Beverages-Soft')
(u'TXU Corp. [TXU]', u'Utilities-Utilities-Electric-Electric')
(u'American Electric Power [AEP]', u'Utilities-Utilities-Electric-Electric')
(u'Pinnacle West Capital [PNW]', u'Utilities-Utilities-Electric-Electric')
(u'Progress Energy  Inc. [PGN]', u'Utilities-Utilities-Electric-Electric')
(u'Southern Co. [SO]', u'Utilities-Utilities-Electric-Electric')
(u'DTE Energy Co. [DTE]', u'Utilities-Utilities-Electric-Electric')
(u'Progressive Corp. [PGR]', u'Financials-Insurance-Insurance-Property')
(u'NiSource Inc. [NI]', u'Utilities-Utilities-Gas-Gas')
(u'Ameren Corporation [AEE]', u'Utilities-Utilities-Electric-Electric')
---------------------------------------
('Numero du cluster : ', 9, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Coca-Cola Enterprises [CCE]', u'Consumer-Food-Beverages-Soft')
---------------------------------------
('Numero du cluster : ', 10, ' Distance moyenne : ', 2.2204460492503131e-16)
(u'Humana Inc. [HUM]', u'Health-Health-Health-Managed')
(u'WellPoint Health Networks [WLP]', u'Health-Health-Health-Managed')
---------------------------------------
('Numero du cluster : ', 11, ' Distance moyenne : ', 1.0196078431372548)
(u'Sun Microsystems [SUNW]', u'Information-Technology-Computers-Computer')
(u'Calpine Corp. [CPN]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
---------------------------------------
('Numero du cluster : ', 12, ' Distance moyenne : ', 1.0196078431372548)
(u'Advanced Micro Devices [AMD]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Dynegy Inc. (New) Class A [DYN]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
---------------------------------------
('Numero du cluster : ', 13, ' Distance moyenne : ', 17.747903741517508)
(u'FIserv Inc. [FISV]', u'Information-Software-IT-Data')
(u'Autodesk  Inc. [ADSK]', u'Information-Software-Software-Application')
(u'Xerox Corp. [XRX]', u'Information-Technology-Office-Office')
(u'Cisco Systems [CSCO]', u'Information-Technology-Communications-Communications')
(u'Merrill Lynch [MER]', u'Financials-Diversified-Capital-Investment')
(u'Exelon Corp. [EXC]', u'Utilities-Utilities-Electric-Electric')
(u'International Game Technology [IGT]', u'Consumer-Hotels-Hotels-Casinos')
(u'Newmont Mining Corp. (Hldg. Co.) [NEM]', u'Materials-Materials-Metals-Gold')
(u'Starbucks Corp. [SBUX]', u'Consumer-Hotels-Hotels-Restaurants')
(u'NCR Corp. [NCR]', u'Information-Technology-Computers-Computer')
(u'Adobe Systems [ADBE]', u'Information-Software-Software-Systems')
(u'Clear Channel Communications [CCU]', u'Consumer-Media-Media-Broadcasting')
(u'*** [SZ]', u'No_Label')
(u'Equifax Inc. [EFX]', u'Industrials-Commercial-Commercial-Diversified')
(u"Harrah's Entertainment [HET]", u'Consumer-Hotels-Hotels-Casinos')
(u'Interpublic Group [IPG]', u'Consumer-Media-Media-Advertising')
(u'SunGard Data Systems [SDS]', u'Information-Software-IT-Data')
(u'Nextel Communications [NXTL]', u'Telecommunication-Telecommunication-Wireless-Wireless')
(u'American Power Conversion [APCC]', u'Industrials-Capital-Electrical-Electrical')
(u'Thermo Electron [TMO]', u'Information-Technology-Electronic-Electronic')
---------------------------------------
('Numero du cluster : ', 14, ' Distance moyenne : ', 4.3697478991596626)
(u'Deere & Co. [DE]', u'Industrials-Capital-Machinery-Construction')
(u'Freeport-McMoran Cp & Gld [FCX]', u'Materials-Materials-Metals-Diversified')
(u'Danaher Corp. [DHR]', u'Industrials-Capital-Machinery-Industrial')
(u'Robert Half International [RHI]', u'Industrials-Commercial-Commercial-Employment')
(u'Stanley Works [SWK]', u'Consumer-Consumer-Household-Household')
(u'Ingersoll-Rand Co. Ltd. [IR]', u'Industrials-Capital-Machinery-Industrial')
(u'Caterpillar Inc. [CAT]', u'Industrials-Capital-Machinery-Construction')
---------------------------------------
('Numero du cluster : ', 15, ' Distance moyenne : ', 2.2941176470588225)
(u'Ryder System [R]', u'Industrials-Transportation-Air-Air')
(u'Jones Apparel Group [JNY]', u'Consumer-Consumer-Textiles-Apparel')
(u'Raytheon Co. (New) [RTN]', u'Industrials-Capital-Aerospace-Aerospace')
(u'FedEx Corporation [FDX]', u'Industrials-Transportation-Air-Air')
---------------------------------------
('Numero du cluster : ', 16, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Parametric Technology [PMTC]', u'Information-Software-Software-Application')
---------------------------------------
('Numero du cluster : ', 17, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Quest Diagnostics [DGX]', u'Health-Health-Health-Health')
---------------------------------------
('Numero du cluster : ', 18, ' Distance moyenne : ', 25.190119023541698)
(u'Bed Bath & Beyond [BBBY]', u'Consumer-Retailing-Specialty-Specialty')
(u'Costco Co. [COST]', u'Consumer-Food-Food-HyperMarkets')
(u'*** [SNS]', u'No_Label')
(u'Penney (J.C.) [JCP]', u'Consumer-Retailing-Multiline-Department')
(u'Hilton Hotels [HLT]', u'Consumer-Hotels-Hotels-Hotels')
(u'TJX Companies Inc. [TJX]', u'Consumer-Retailing-Specialty-Apparel')
(u'Hewlett-Packard [HPQ]', u'Information-Technology-Computers-Computer')
(u'Pulte Homes  Inc. [PHM]', u'Consumer-Consumer-Household-Homebuilding')
(u'Plum Creek Timber Co. [PCL]', u'Financials-Real-Real-Real')
(u'Target Corp. [TGT]', u'Consumer-Retailing-Multiline-General')
(u'Best Buy Co.  Inc. [BBY]', u'Consumer-Retailing-Specialty-Computer')
(u'V.F. Corp. [VFC]', u'Consumer-Consumer-Textiles-Apparel')
(u'Staples Inc. [SPLS]', u'Consumer-Retailing-Specialty-Specialty')
(u'Dollar General [DG]', u'Consumer-Retailing-Multiline-General')
(u'Comcast Corp. [CMCSA]', u'Consumer-Media-Media-Broadcasting')
(u'Forest Laboratories [FRX]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Boston Scientific [BSX]', u'Health-Health-Health-Health')
(u'Tiffany & Co. [TIF]', u'Consumer-Retailing-Specialty-Specialty')
(u'Starwood Hotels & Resorts [HOT]', u'Consumer-Hotels-Hotels-Hotels')
(u'NIKE Inc. [NKE]', u'Consumer-Consumer-Textiles-Footwear')
(u'Sears  Roebuck & Co. [S]', u'Consumer-Retailing-Multiline-Department')
(u'AutoZone Inc. [AZO]', u'Consumer-Retailing-Specialty-Specialty')
(u'*** [GFR]', u'No_Label')
(u'Countrywide Financial Corp. [CFC]', u'Financials-Banks-Thrifts-Thrifts')
(u"Lowe's Cos. [LOW]", u'Consumer-Retailing-Specialty-Home')
(u'Walgreen Co. [WAG]', u'Consumer-Food-Food-Drug')
(u'Wal-Mart Stores [WMT]', u'Consumer-Food-Food-HyperMarkets')
(u'Limited Brands  Inc. [LTD]', u'Consumer-Retailing-Specialty-Apparel')
(u'Gap (The) [GPS]', u'Consumer-Retailing-Specialty-Apparel')
(u'Apollo Group [APOL]', u'Industrials-Commercial-Commercial-Diversified')
(u'Paychex Inc. [PAYX]', u'Information-Software-IT-Data')
---------------------------------------
('Numero du cluster : ', 19, ' Distance moyenne : ', 56.163544358363374)
(u'Loews Corp. [LTR]', u'Financials-Insurance-Insurance-Multi-line')
(u'Verizon Communications [VZ]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Aon Corp. [AOC]', u'Financials-Insurance-Insurance-Insurance')
(u'UST Inc. [UST]', u'Consumer-Food-Tobacco-Tobacco')
(u'Prudential Financial [PRU]', u'Financials-Insurance-Insurance-Life')
(u'St Jude Medical [STJ]', u'Health-Health-Health-Health')
(u'MetLife Inc. [MET]', u'Financials-Insurance-Insurance-Life')
(u'U.S. Bancorp [USB]', u'Financials-Banks-Commercial-Diversified')
(u"Marriott Int'l. [MAR]", u'Consumer-Hotels-Hotels-Hotels')
(u'State Street Corp. [STT]', u'Financials-Diversified-Capital-Asset')
(u'AFLAC Corporation [AFL]', u'Financials-Insurance-Insurance-Life')
(u'National City Corp. [NCC]', u'Financials-Banks-Commercial-Regional')
(u'Sabre Holding Corp. [TSG]', u'Information-Software-IT-Data')
(u'Zions Bancorp [ZION]', u'Financials-Banks-Commercial-Regional')
(u'XL Capital [XL]', u'Financials-Insurance-Insurance-Property')
(u'Block H&R [HRB]', u'Industrials-Commercial-Commercial-Diversified')
(u'Rockwell Collins [COL]', u'Industrials-Capital-Aerospace-Aerospace')
(u'*** [MXM]', u'No_Label')
(u'Principal Financial Group [PFG]', u'Financials-Diversified-Diversified-Other')
(u'*** [MEE]', u'No_Label')
(u'Xcel Energy Inc [XEL]', u'Utilities-Utilities-Electric-Electric')
(u'International Flav/Frag [IFF]', u'Materials-Materials-Chemicals-Specialty')
(u'Tenet Healthcare Corp. [THC]', u'Health-Health-Health-Health')
(u'Constellation Energy Group [CEG]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
(u'Avon Products [AVP]', u'Consumer-Household-Personal-Personal')
(u'Time Warner Inc. [TWX]', u'Consumer-Media-Media-Movies')
(u'Peoples Energy [PGL]', u'Utilities-Utilities-Gas-Gas')
(u"Albertson's [ABS]", u'Consumer-Food-Food-Food')
(u'Synovus Financial [SNV]', u'Financials-Banks-Commercial-Regional')
(u'Qwest Communications Int [Q]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Hartford Financial Svc.Gp. [HIG]', u'Financials-Insurance-Insurance-Multi-line')
(u'Louisiana Pacific [LPX]', u'Materials-Materials-Paper-Forest')
(u'Exxon Mobil Corp. [XOM]', u'Energy-Energy-Oil-Integrated')
(u'Golden West Financial [GDW]', u'Financials-Banks-Thrifts-Thrifts')
(u'Boeing Company [BA]', u'Industrials-Capital-Aerospace-Aerospace')
(u'SBC Communications Inc. [SBC]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'SLM Corporation [SLM]', u'Financials-Diversified-Consumer-Consumer')
(u"American Int'l. Group [AIG]", u'Financials-Insurance-Insurance-Multi-line')
(u'Federated Investors Inc. [FII]', u'Financials-Diversified-Capital-Asset')
(u'CINergy Corp. [CIN]', u'Utilities-Utilities-Electric-Electric')
(u'Fortune Brands  Inc. [FO]', u'Consumer-Consumer-Household-Housewares')
(u'Guidant Corp. [GDT]', u'Health-Health-Health-Health')
(u'Archer-Daniels-Midland [ADM]', u'Consumer-Food-Food-Agricultural')
(u'BIOGEN IDEC Inc. [BIIB]', u'Health-Pharmaceuticals-Biotechnology-Biotechnology')
(u'Lehman Bros. [LEH]', u'Financials-Diversified-Capital-Investment')
(u'Citigroup Inc. [C]', u'Financials-Diversified-Diversified-Other')
(u'Marsh & McLennan [MMC]', u'Financials-Insurance-Insurance-Insurance')
(u'Northern Trust Corp. [NTRS]', u'Financials-Diversified-Capital-Asset')
(u'Allstate Corp. [ALL]', u'Financials-Insurance-Insurance-Property')
(u'Entergy Corp. [ETR]', u'Utilities-Utilities-Electric-Electric')
(u'ConAgra Foods  Inc. [CAG]', u'Consumer-Food-Food-Packaged')
(u'FirstEnergy Corp. [FE]', u'Utilities-Utilities-Electric-Electric')
(u'Bear Stearns Cos. [BSC]', u'Financials-Diversified-Capital-Investment')
(u'Jefferson-Pilot [JP]', u'Financials-Insurance-Insurance-Life')
(u'BB&T Corporation [BBT]', u'Financials-Banks-Commercial-Regional')
(u'PG&E Corp. [PCG]', u'Utilities-Utilities-Electric-Electric')
(u'UnumProvident Corp. [UNM]', u'Financials-Insurance-Insurance-Life')
(u'Computer Sciences Corp. [CSC]', u'Information-Software-IT-Data')
(u'Marshall & Ilsley Corp. [MI]', u'Financials-Banks-Commercial-Regional')
(u'Microsoft Corp. [MSFT]', u'Information-Software-Software-Systems')
(u'McKesson Corp. (New) [MCK]', u'Health-Health-Health-Health')
(u'Wrigley (Wm) Jr. [WWY]', u'Consumer-Food-Food-Packaged')
---------------------------------------
('Numero du cluster : ', 20, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'*** [VTR]', u'No_Label')
---------------------------------------
('Numero du cluster : ', 21, ' Distance moyenne : ', 10.627450980392137)
(u'Ambac Financial Group [ABK]', u'Financials-Insurance-Insurance-Property')
(u'MBIA Inc. [MBI]', u'Financials-Insurance-Insurance-Property')
(u'McGraw-Hill [MHP]', u'Consumer-Media-Media-Publishing')
(u'Federal Home Loan Mtg. [FRE]', u'Financials-Banks-Thrifts-Thrifts')
(u'Wyeth [WYE]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'E*Trade Financial Corp. [ET]', u'Financials-Diversified-Capital-Investment')
(u'MGIC Investment [MTG]', u'Financials-Banks-Thrifts-Thrifts')
(u'Bausch & Lomb [BOL]', u'Health-Health-Health-Health')
(u'Baxter International Inc. [BAX]', u'Health-Health-Health-Health')
(u'Winn-Dixie [WIN]', u'Consumer-Food-Food-Food')
(u'ACE Limited [ACE]', u'Financials-Insurance-Insurance-Property')
(u'Circuit City Group [CC]', u'Consumer-Retailing-Specialty-Computer')
(u'Bank of New York [BK]', u'Financials-Diversified-Capital-Asset')
---------------------------------------
('Numero du cluster : ', 22, ' Distance moyenne : ', 36.412128523225107)
(u'Great Lakes Chemical [GLK]', u'Materials-Materials-Chemicals-Specialty')
(u'King Pharmaceuticals [KG]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Knight-Ridder Inc. [KRI]', u'Consumer-Media-Media-Publishing')
(u'United States Steel Corp. [X]', u'Materials-Materials-Metals-Steel')
(u'SAFECO Corp. [SAFC]', u'Financials-Insurance-Insurance-Property')
(u'Meredith Corp. [MDP]', u'Consumer-Media-Media-Publishing')
(u'Fluor Corp. (New) [FLR]', u'Industrials-Capital-Construction-Construction')
(u'Procter & Gamble [PG]', u'Consumer-Household-Household-Household')
(u'Citizens Communications [CZN]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Univision Communications [UVN]', u'Consumer-Media-Media-Broadcasting')
(u'CVS Corp. [CVS]', u'Consumer-Food-Food-Drug')
(u'Coors (Adolph) [RKY]', u'Consumer-Food-Beverages-Brewers')
(u'Hasbro Inc. [HAS]', u'Consumer-Consumer-Leisure-Leisure')
(u'Worthington Ind. [WOR]', u'Materials-Materials-Metals-Steel')
(u'Waters Corporation [WAT]', u'Information-Technology-Electronic-Electronic')
(u'Hercules  Inc. [HPC]', u'Materials-Materials-Chemicals-Diversified')
(u'Avaya Inc. [AV]', u'Information-Technology-Communications-Communications')
(u'Gateway Inc. [GTW]', u'Information-Technology-Computers-Computer')
(u'Automatic Data Processing Inc. [ADP]', u'Information-Software-IT-Data')
(u'*** [HMT]', u'No_Label')
(u'FPL Group [FPL]', u'Utilities-Utilities-Electric-Electric')
(u'Coca Cola Co. [KO]', u'Consumer-Food-Beverages-Soft')
(u'Maytag Corp. [MYG]', u'Consumer-Consumer-Household-Household')
(u'RJ Reynolds Tobacco [RJR]', u'Consumer-Food-Tobacco-Tobacco')
(u'NICOR Inc. [GAS]', u'Utilities-Utilities-Gas-Gas')
(u'Praxair  Inc. [PX]', u'Materials-Materials-Chemicals-Industrial')
(u'Watson Pharmaceuticals [WPI]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Sigma-Aldrich [SIAL]', u'Materials-Materials-Chemicals-Specialty')
(u'Engelhard Corp. [EC]', u'Materials-Materials-Chemicals-Diversified')
(u'Morgan Stanley [MWD]', u'Financials-Diversified-Capital-Investment')
(u'HCA Inc. [HCA]', u'Health-Health-Health-Health')
(u'Aetna Inc. (New) [AET]', u'Health-Health-Health-Managed')
(u'New York Times Cl. A [NYT]', u'Consumer-Media-Media-Publishing')
(u'Franklin Resources [BEN]', u'Financials-Diversified-Capital-Asset')
(u'Phelps Dodge [PD]', u'Materials-Materials-Metals-Diversified')
(u'Hershey Foods [HSY]', u'Consumer-Food-Food-Packaged')
(u'Sherwin-Williams [SHW]', u'Consumer-Retailing-Specialty-Home')
(u'Liz Claiborne  Inc. [LIZ]', u'Consumer-Consumer-Textiles-Apparel')
(u'Abbott Labs [ABT]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
---------------------------------------
('Numero du cluster : ', 23, ' Distance moyenne : ', 18.584670231728964)
(u'Dow Chemical [DOW]', u'Materials-Materials-Chemicals-Diversified')
(u'Biomet  Inc. [BMET]', u'Health-Health-Health-Health')
(u'Eastman Chemical [EMN]', u'Materials-Materials-Chemicals-Diversified')
(u'Mellon Bank Corp. [MEL]', u'Financials-Diversified-Capital-Asset')
(u'CIGNA Corp. [CI]', u'Health-Health-Health-Managed')
(u'Pfizer  Inc. [PFE]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u"Honeywell Int'l Inc. [HON]", u'Industrials-Capital-Aerospace-Aerospace')
(u'Kinder Morgan [KMI]', u'Utilities-Utilities-Gas-Gas')
(u'Sealed Air Corp.(New) [SEE]', u'Materials-Materials-Containers-Paper')
(u'Affiliated Computer [ACS]', u'Information-Software-IT-Data')
(u'Lilly (Eli) & Co. [LLY]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Allegheny Technologies Inc [ATI]', u'Materials-Materials-Metals-Steel')
(u'Intuit  Inc. [INTU]', u'Information-Software-Software-Application')
(u'Du Pont (E.I.) [DD]', u'Materials-Materials-Chemicals-Diversified')
(u'Ecolab Inc. [ECL]', u'Materials-Materials-Chemicals-Specialty')
(u'Air Products & Chemicals [APD]', u'Materials-Materials-Chemicals-Industrial')
(u'Kellogg Co. [K]', u'Consumer-Food-Food-Packaged')
(u'Supervalu Inc. [SVU]', u'Consumer-Food-Food-Food')
(u'Rohm & Haas [ROH]', u'Materials-Materials-Chemicals-Specialty')
(u'IMS Health Inc. [RX]', u'Health-Health-Health-Health')
(u'American Express [AXP]', u'Financials-Diversified-Consumer-Consumer')
(u'PPG Industries [PPG]', u'Materials-Materials-Chemicals-Diversified')
---------------------------------------
('Numero du cluster : ', 24, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Stryker Corp. [SYK]', u'Health-Health-Health-Health')
---------------------------------------
('Numero du cluster : ', 25, ' Distance moyenne : ', 1.346310159166084)
(u'*** [NXL]', u'No_Label')
(u'Simon Property Group  Inc [SPG]', u'Financials-Real-Real-Real')
(u'Equity Residential [EQR]', u'Financials-Real-Real-Real')
---------------------------------------
('Numero du cluster : ', 26, ' Distance moyenne : ', 33.267197076540974)
(u'Texas Instruments [TXN]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Electronic Arts [ERTS]', u'Information-Software-Software-Home')
(u'Tyco International [TYC]', u'Industrials-Capital-Industrial-Industrial')
(u'Micron Technology [MU]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Intel Corp. [INTC]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Power-One Inc. [PWER]', u'Industrials-Capital-Electrical-Electrical')
(u'Centex Corp. [CTX]', u'Consumer-Consumer-Household-Homebuilding')
(u'Analog Devices [ADI]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Symbol Technologies [SBL]', u'Information-Technology-Electronic-Electronic')
(u'Sanmina-SCI Corp. [SANM]', u'Information-Technology-Electronic-Electronic')
(u'PeopleSoft Inc. [PSFT]', u'Information-Software-Software-Application')
(u'Pitney-Bowes [PBI]', u'Industrials-Commercial-Commercial-Office')
(u'Amgen [AMGN]', u'Health-Pharmaceuticals-Biotechnology-Biotechnology')
(u'AT&T Wireless Services [AWE]', u'Telecommunication-Telecommunication-Wireless-Wireless')
(u'Citrix Systems [CTXS]', u'Information-Software-Software-Application')
(u"Kohl's Corp. [KSS]", u'Consumer-Retailing-Multiline-Department')
(u'Solectron [SLR]', u'Information-Technology-Electronic-Electronic')
(u'*** [SNSTA]', u'No_Label')
(u'Novellus Systems [NVLS]', u'Information-Semiconductors-Semiconductor-Semiconductor')
(u'Broadcom Corporation [BRCM]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Washington Mutual [WM]', u'Financials-Banks-Thrifts-Thrifts')
(u'Allegheny Energy [AYE]', u'Utilities-Utilities-Electric-Electric')
(u'Xilinx  Inc [XLNX]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Monster Worldwide [MNST]', u'Industrials-Commercial-Commercial-Employment')
(u'Scientific-Atlanta [SFA]', u'Information-Technology-Communications-Communications')
(u'PMC-Sierra Inc. [PMCS]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'JDS Uniphase Corp [JDSU]', u'Information-Technology-Communications-Communications')
(u'EMC Corp. [EMC]', u'Information-Technology-Computers-Computer')
(u'Genzyme Corp. [GENZ]', u'Health-Pharmaceuticals-Biotechnology-Biotechnology')
(u'CIENA Corp. [CIEN]', u'Information-Technology-Communications-Communications')
(u'Maxim Integrated Prod [MXIM]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Oracle Corp. [ORCL]', u'Information-Software-Software-Systems')
(u'Siebel  Systems Inc [SEBL]', u'Information-Software-Software-Application')
(u'National Semiconductor [NSM]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Allied Waste Industries [AW]', u'Industrials-Commercial-Commercial-Environmental')
(u'RadioShack Corp [RSH]', u'Consumer-Retailing-Specialty-Computer')
(u'QUALCOMM Inc. [QCOM]', u'Information-Technology-Communications-Communications')
(u'Corning Inc. [GLW]', u'Information-Technology-Communications-Communications')
(u'Linear Technology Corp. [LLTC]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Allergan  Inc. [AGN]', u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')
(u'Computer Associates Intl. [CA]', u'Information-Software-Software-Systems')
---------------------------------------
('Numero du cluster : ', 27, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'*** [VVI]', u'No_Label')
---------------------------------------
('Numero du cluster : ', 28, ' Distance moyenne : ', 2.7529411764705829)
(u'BJ Services [BJS]', u'Energy-Energy-Energy-Oil')
(u'Rowan Cos. [RDC]', u'Energy-Energy-Energy-Oil')
(u'Nabors Industries Ltd. [NBR]', u'Energy-Energy-Energy-Oil')
(u'Burlington Resources [BR]', u'Energy-Energy-Oil-Oil')
(u'Transocean Inc. [RIG]', u'Energy-Energy-Energy-Oil')
(u'Anadarko Petroleum [APC]', u'Energy-Energy-Oil-Oil')
(u'Schlumberger Ltd. [SLB]', u'Energy-Energy-Energy-Oil')
(u'Baker Hughes [BHI]', u'Energy-Energy-Energy-Oil')
(u'Devon Energy Corp. [DVN]', u'Energy-Energy-Oil-Oil')
(u'Halliburton Co. [HAL]', u'Energy-Energy-Energy-Oil')
---------------------------------------
('Numero du cluster : ', 29, ' Distance moyenne : ', 15.25103131981705)
(u'Teradyne Inc. [TER]', u'Information-Semiconductors-Semiconductor-Semiconductor')
(u'QLogic Corp. [QLGC]', u'Information-Technology-Communications-Communications')
(u'Altria Group  Inc. [MO]', u'Consumer-Food-Tobacco-Tobacco')
(u'NVIDIA Corp. [NVDA]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'Altera Corp. [ALTR]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u'eBay Inc. [EBAY]', u'Consumer-Retailing-Internet-Internet')
(u'LSI Logic [LSI]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u"Lexmark Int'l Inc [LXK]", u'Information-Technology-Computers-Computer')
(u'Millipore Corp. [MIL]', u'Health-Health-Health-Health')
(u'Applied Materials [AMAT]', u'Information-Semiconductors-Semiconductor-Semiconductor')
(u'Tektronix Inc. [TEK]', u'Information-Technology-Electronic-Electronic')
(u'Express Scripts [ESRX]', u'Health-Health-Health-Health')
(u'Yahoo Inc. [YHOO]', u'Information-Software-Internet-Internet')
(u'PerkinElmer [PKI]', u'Information-Technology-Electronic-Electronic')
(u'Comverse Technology [CMVT]', u'Information-Technology-Communications-Communications')
(u'Network Appliance [NTAP]', u'Information-Technology-Computers-Computer')
(u'Jabil Circuit [JBL]', u'Information-Technology-Electronic-Electronic')
(u'Agilent Technologies [A]', u'Information-Technology-Electronic-Electronic')
(u'ADC Telecommunications [ADCT]', u'Information-Technology-Communications-Communications')
(u'*** [NT]', u'No_Label')
(u'KLA-Tencor Corp. [KLAC]', u'Information-Semiconductors-Semiconductor-Semiconductor')
---------------------------------------
('Numero du cluster : ', 30, ' Distance moyenne : ', 1.1102230246251565e-16)
(u"Moody's Corp [MCO]", u'Financials-Diversified-Diversified-Specialized')
---------------------------------------
('Numero du cluster : ', 31, ' Distance moyenne : ', 2.9313725490196072)
(u'Tellabs  Inc. [TLAB]', u'Information-Technology-Communications-Communications')
(u'Waste Management Inc. [WMI]', u'Industrials-Commercial-Commercial-Environmental')
(u'Applied Micro Circuits [AMCC]', u'Information-Semiconductors-Semiconductor-Semiconductors')
(u"Edison Int'l [EIX]", u'Utilities-Utilities-Electric-Electric')
---------------------------------------
('Numero du cluster : ', 32, ' Distance moyenne : ', 1.1102230246251565e-16)
(u'Ball Corp. [BLL]', u'Materials-Materials-Containers-Metal')
---------------------------------------
('Numero du cluster : ', 33, ' Distance moyenne : ', 0.67973856209150318)
(u'Kerr-McGee [KMG]', u'Energy-Energy-Oil-Oil')
(u'ConocoPhillips [COP]', u'Energy-Energy-Oil-Integrated')
(u'EOG Resources [EOG]', u'Energy-Energy-Oil-Oil')
(u'Unocal Corp. [UCL]', u'Energy-Energy-Oil-Oil')
(u'Occidental Petroleum [OXY]', u'Energy-Energy-Oil-Integrated')
(u'Apache Corp. [APA]', u'Energy-Energy-Oil-Oil')
---------------------------------------
('Numero du cluster : ', 34, ' Distance moyenne : ', 38.483978957436086)
(u'Boise Cascade [BCC]', u'Consumer-Retailing-Specialty-Specialty')
(u'BMC Software [BMC]', u'Information-Software-Software-Systems')
(u'Northrop Grumman Corp. [NOC]', u'Industrials-Capital-Aerospace-Aerospace')
(u'PepsiCo Inc. [PEP]', u'Consumer-Food-Beverages-Soft')
(u"McDonald's Corp. [MCD]", u'Consumer-Hotels-Hotels-Restaurants')
(u'Kroger Co. [KR]', u'Consumer-Food-Food-Food')
(u'Pactiv Corp. [PTV]', u'Materials-Materials-Containers-Metal')
(u'United Technologies [UTX]', u'Industrials-Capital-Aerospace-Aerospace')
(u'Duke Energy [DUK]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
(u'MeadWestvaco Corporation [MWV]', u'Materials-Materials-Paper-Paper')
(u'Whirlpool Corp. [WHR]', u'Consumer-Consumer-Household-Household')
(u'Manor Care Inc. [HCR]', u'Health-Health-Health-Health')
(u'Symantec Corp. [SYMC]', u'Information-Software-Software-Systems')
(u'Carnival Corp. [CCL]', u'Consumer-Hotels-Hotels-Hotels')
(u'Sara Lee Corp. [SLE]', u'Consumer-Food-Food-Packaged')
(u'ALLTEL Corp. [AT]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Family Dollar Stores [FDO]', u'Consumer-Retailing-Multiline-General')
(u'KB Home [KBH]', u'Consumer-Consumer-Household-Homebuilding')
(u'El Paso Corp. [EP]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
(u'Capital One Financial [COF]', u'Financials-Diversified-Consumer-Consumer')
(u'Apple Computer [AAPL]', u'Information-Technology-Computers-Computer')
(u'CMS Energy [CMS]', u'Utilities-Utilities-Electric-Electric')
(u'PNC Bank Corp. [PNC]', u'Financials-Banks-Commercial-Regional')
(u'Alcoa Inc [AA]', u'Materials-Materials-Metals-Aluminum')
(u'Southwest Airlines [LUV]', u'Industrials-Transportation-Airlines-Airlines')
(u'Bemis Company [BMS]', u'Materials-Materials-Containers-Paper')
(u'Unisys Corp. [UIS]', u'Information-Software-IT-IT')
(u'Cendant Corporation [CD]', u'Industrials-Commercial-Commercial-Diversified')
(u'United Parcel Service [UPS]', u'Industrials-Transportation-Air-Air')
(u'International Paper [IP]', u'Materials-Materials-Paper-Paper')
(u'Masco Corp. [MAS]', u'Industrials-Capital-Building-Building')
(u'J.P. Morgan Chase & Co. [JPM]', u'Financials-Diversified-Capital-Diversified')
(u'Brunswick Corp. [BC]', u'Consumer-Consumer-Leisure-Leisure')
(u'Williams Cos. [WMB]', u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')
(u'Georgia-Pacific Group [GP]', u'Materials-Materials-Paper-Paper')
(u'Temple-Inland [TIN]', u'Materials-Materials-Containers-Paper')
(u'Weyerhaeuser Corp. [WY]', u'Materials-Materials-Paper-Forest')
(u'Sprint Corp. FON [FON]', u'Telecommunication-Telecommunication-Diversified-Integrated')
(u'Dow Jones & Co. [DJ]', u'Consumer-Media-Media-Publishing')
(u'Gillette Co. [G]', u'Consumer-Household-Personal-Personal')
(u'Monsanto Co. [MON]', u'Materials-Materials-Chemicals-Fertilizers')
('Similarite moyenne :', 11.526086684656006)
('Distance moyenne des elements non regroupes par classe :  ', 483.9808388654069)
('Distance moyenne pour ', 35, ' clusters choisis aleatoirement avec une proba uniforme : ', 12.892166677599116)
nicolas@nicolas:/media/nicolas/NICO USB/Probas-stats-projet$ 

'''
'''result:

{0: [u'Johnson Controls [JCI]',
     u'Verizon Communications [VZ]',
     u'Knight-Ridder Inc. [KRI]',
     u'Freeport-McMoran Cp & Gld [FCX]',
     u'Omnicom Group [OMC]',
     u'Prudential Financial [PRU]',
     u'General Motors [GM]',
     u'Cummins  Inc. [CMI]',
     u'Danaher Corp. [DHR]',
     u'Zions Bancorp [ZION]',
     u'AutoNation  Inc. [AN]',
     u'Stanley Works [SWK]',
     u'ITT Industries  Inc. [ITT]',
     u'Thomas & Betts [TNB]',
     u'Janus Capital Group [JNS]',
     u'Pitney-Bowes [PBI]',
     u'KeyCorp [KEY]',
     u'AmerisourceBergen Corp. [ABC]',
     u'Ford Motor [F]',
     u'McCormick & Co. [MKC]',
     u'Textron Inc. [TXT]',
     u'Kinder Morgan [KMI]',
     u'PACCAR Inc. [PCAR]',
     u'Goldman Sachs Group [GS]',
     u'American Standard [ASD]',
     u'Eaton Corp. [ETN]',
     u'Leggett & Platt [LEG]',
     u'BellSouth [BLS]',
     u'SouthTrust Corp. [SOTR]',
     u'Dover Corp. [DOV]',
     u'SunTrust Banks [STI]',
     u'Black & Decker Corp. [BDK]',
     u'Sigma-Aldrich [SIAL]',
     u'Wells Fargo [WFC]',
     u'Caterpillar Inc. [CAT]',
     u'Boeing Company [BA]',
     u'M&T Bank Corp. [MTB]',
     u'Johnson & Johnson [JNJ]',
     u'Parker-Hannifin [PH]',
     u'Wachovia Corp. (New) [WB]',
     u'Countrywide Financial Corp. [CFC]',
     u'Snap-On Inc. [SNA]',
     u'Chiron Corp. [CHIR]',
     u'Emerson Electric [EMR]',
     u'Regions Financial Corp. [RF]',
     u'Caremark Rx [CMX]',
     u'Torchmark Corp. [TMK]',
     u'3M Company [MMM]',
     u'Illinois Tool Works [ITW]',
     u'Crane Company [CR]',
     u'BB&T Corporation [BBT]',
     u'Comerica Inc. [CMA]',
     u'Medtronic Inc. [MDT]'],
 1: [u'Burlington Northern Santa Fe C [BNI]',
     u"Marriott Int'l. [MAR]",
     u'Federal Home Loan Mtg. [FRE]',
     u'Compuware Corp. [CPWR]',
     u'ConocoPhillips [COP]',
     u'Carnival Corp. [CCL]',
     u'Pepsi Bottling Group [PBG]',
     u'Bausch & Lomb [BOL]',
     u'Norfolk Southern Corp. [NSC]',
     u'Amgen [AMGN]',
     u'RJ Reynolds Tobacco [RJR]',
     u'Tenet Healthcare Corp. [THC]',
     u'Walt Disney Co. [DIS]',
     u'Avery Dennison Corp. [AVY]',
     u'Cendant Corporation [CD]',
     u'Health Management Assoc. [HMA]',
     u'Union Pacific [UNP]',
     u'Baxter International Inc. [BAX]',
     u'MBNA Corp. [KRB]',
     u'Walgreen Co. [WAG]',
     u'Brunswick Corp. [BC]',
     u'Gap (The) [GPS]',
     u'Marsh & McLennan [MMC]',
     u'PG&E Corp. [PCG]',
     u'Dow Jones & Co. [DJ]',
     u'IMS Health Inc. [RX]',
     u'Marshall & Ilsley Corp. [MI]'],
 2: [u'Anheuser-Busch [BUD]',
     u'Kimberly-Clark [KMB]',
     u'AT&T Corp. (New) [T]',
     u'Sara Lee Corp. [SLE]',
     u'Sysco Corp. [SYY]'],
 3: [u'*** [NX]',
     u'Xerox Corp. [XRX]',
     u'*** [AIH]',
     u'Wyeth [WYE]',
     u'Delta Air Lines [DAL]'],
 4: [u'Sempra Energy [SRE]',
     u'Consolidated Edison [ED]',
     u'Newmont Mining Corp. (Hldg. Co.) [NEM]',
     u'Block H&R [HRB]',
     u'FPL Group [FPL]',
     u'Constellation Energy Group [CEG]',
     u'Peoples Energy [PGL]',
     u'Southern Co. [SO]',
     u'*** [GFR]',
     u'CINergy Corp. [CIN]',
     u'Nextel Communications [NXTL]',
     u"Edison Int'l [EIX]"],
 5: [u'Marathon Oil Corp. [MRO]',
     u'*** [SNSTA]',
     u'Sunoco.  Inc. [SUN]',
     u'ChevronTexaco Corp. [CVX]'],
 6: [u'Applera Corp-Applied Biosystems Group [ABI]',
     u'General Electric [GE]',
     u'Millipore Corp. [MIL]',
     u'MedImmune Inc. [MEDI]',
     u'Forest Laboratories [FRX]',
     u'Intuit  Inc. [INTU]',
     u'Dynegy Inc. (New) Class A [DYN]',
     u'Genzyme Corp. [GENZ]'],
 7: [u'Darden Restaurants [DRI]',
     u'Yum! Brands  Inc [YUM]',
     u'HCA Inc. [HCA]',
     u'Federated Investors Inc. [FII]'],
 8: [u'Keyspan Energy [KSE]',
     u'Exelon Corp. [EXC]',
     u'Mattel  Inc. [MAT]',
     u'PPL Corp. [PPL]',
     u'Public Serv. Enterprise Inc. [PEG]',
     u'American Electric Power [AEP]',
     u'Progress Energy  Inc. [PGN]',
     u'NIKE Inc. [NKE]',
     u'Lockheed Martin Corp. [LMT]',
     u'DTE Energy Co. [DTE]',
     u'NiSource Inc. [NI]',
     u'Guidant Corp. [GDT]',
     u'Ameren Corporation [AEE]'],
 9: [u'Coca-Cola Enterprises [CCE]',
     u'Coca Cola Co. [KO]',
     u'Allegheny Energy [AYE]',
     u'ConAgra Foods  Inc. [CAG]'],
 10: [u'Humana Inc. [HUM]', u'WellPoint Health Networks [WLP]'],
 11: [u'Sun Microsystems [SUNW]',
      u'Raytheon Co. (New) [RTN]',
      u'International Game Technology [IGT]',
      u'*** [MEE]',
      u'Pinnacle West Capital [PNW]',
      u'EMC Corp. [EMC]',
      u'Calpine Corp. [CPN]'],
 12: [u'Advanced Micro Devices [AMD]',
      u'*** [MXM]',
      u'Goodyear Tire & Rubber [GT]'],
 13: [u'FIserv Inc. [FISV]',
      u'Hilton Hotels [HLT]',
      u'Dell Inc. [DELL]',
      u'Cisco Systems [CSCO]',
      u'Merrill Lynch [MER]',
      u'Power-One Inc. [PWER]',
      u'Sanmina-SCI Corp. [SANM]',
      u'FedEx Corporation [FDX]',
      u'MGIC Investment [MTG]',
      u'Vulcan Materials [VMC]',
      u'Apple Computer [AAPL]',
      u'T. Rowe Price Group [TROW]',
      u'NICOR Inc. [GAS]',
      u'Harley-Davidson [HDI]',
      u'Huntington Bancshares [HBAN]',
      u'First Data [FDC]',
      u'General Dynamics [GD]',
      u'Cintas Corporation [CTAS]',
      u'Colgate-Palmolive [CL]',
      u'Franklin Resources [BEN]',
      u'Allegheny Technologies Inc [ATI]',
      u'Equifax Inc. [EFX]',
      u'J.P. Morgan Chase & Co. [JPM]',
      u'Visteon Corp. [VC]',
      u'SunGard Data Systems [SDS]',
      u'Paychex Inc. [PAYX]',
      u'American Power Conversion [APCC]',
      u'Convergys Corp. [CVG]',
      u'Allergan  Inc. [AGN]',
      u'Bank of New York [BK]'],
 14: [u'Deere & Co. [DE]',
      u'St Jude Medical [STJ]',
      u'Safeway Inc. [SWY]',
      u'Waters Corporation [WAT]',
      u'Ingersoll-Rand Co. Ltd. [IR]',
      u'TXU Corp. [TXU]',
      u'Maytag Corp. [MYG]',
      u'Xcel Energy Inc [XEL]',
      u'Avon Products [AVP]',
      u'Schering-Plough [SGP]',
      u'Fortune Brands  Inc. [FO]',
      u'Heinz (H.J.) [HNZ]',
      u'Gillette Co. [G]'],
 15: [u'Ryder System [R]',
      u'Meredith Corp. [MDP]',
      u'Duke Energy [DUK]',
      u'Robert Half International [RHI]',
      u'Dominion Resources [D]',
      u'Rockwell Collins [COL]',
      u'PNC Bank Corp. [PNC]',
      u"Albertson's [ABS]"],
 16: [u'Parametric Technology [PMTC]',
      u'Symbol Technologies [SBL]',
      u'Avaya Inc. [AV]',
      u'CMS Energy [CMS]'],
 17: [u'Quest Diagnostics [DGX]',
      u'Anthem  Inc. [ATH]',
      u'Zimmer Holdings [ZMH]',
      u'Bristol-Myers Squibb [BMY]'],
 18: [u'Bed Bath & Beyond [BBBY]',
      u'Costco Co. [COST]',
      u'Clorox Co. [CLX]',
      u'United States Steel Corp. [X]',
      u'Penney (J.C.) [JCP]',
      u'TJX Companies Inc. [TJX]',
      u'PepsiCo Inc. [PEP]',
      u'Centex Corp. [CTX]',
      u'AES Corp. [AES]',
      u'Symantec Corp. [SYMC]',
      u'Pulte Homes  Inc. [PHM]',
      u'Family Dollar Stores [FDO]',
      u'Tribune Co. [TRB]',
      u'Capital One Financial [COF]',
      u'Target Corp. [TGT]',
      u'Best Buy Co.  Inc. [BBY]',
      u'Staples Inc. [SPLS]',
      u'Dollar General [DG]',
      u'Comcast Corp. [CMCSA]',
      u'Watson Pharmaceuticals [WPI]',
      u'Tiffany & Co. [TIF]',
      u'Nordstrom [JWN]',
      u'Starwood Hotels & Resorts [HOT]',
      u'Golden West Financial [GDW]',
      u'New York Times Cl. A [NYT]',
      u'Sears  Roebuck & Co. [S]',
      u'Masco Corp. [MAS]',
      u"Lowe's Cos. [LOW]",
      u'May Dept. Stores [MAY]',
      u'Wal-Mart Stores [WMT]',
      u'Limited Brands  Inc. [LTD]',
      u'Apollo Group [APOL]',
      u'Kellogg Co. [K]',
      u'Home Depot [HD]',
      u'Office Depot [ODP]'],
 19: [u'Loews Corp. [LTR]',
      u'SAFECO Corp. [SAFC]',
      u'Aon Corp. [AOC]',
      u'Altria Group  Inc. [MO]',
      u'UST Inc. [UST]',
      u'Biomet  Inc. [BMET]',
      u'U.S. Bancorp [USB]',
      u'Mellon Bank Corp. [MEL]',
      u'CIGNA Corp. [CI]',
      u'Lincoln National [LNC]',
      u'National City Corp. [NCC]',
      u'Dana Corp. [DCN]',
      u'Sabre Holding Corp. [TSG]',
      u'Hasbro Inc. [HAS]',
      u'Pfizer  Inc. [PFE]',
      u'Principal Financial Group [PFG]',
      u'Plum Creek Timber Co. [PCL]',
      u'Gateway Inc. [GTW]',
      u'International Flav/Frag [IFF]',
      u'Union Planters Corporation [UPC]',
      u'AmSouth Bancorporation [ASO]',
      u'Synovus Financial [SNV]',
      u'Washington Mutual [WM]',
      u'PerkinElmer [PKI]',
      u'United Parcel Service [UPS]',
      u'Hartford Financial Svc.Gp. [HIG]',
      u'Louisiana Pacific [LPX]',
      u'Bank of America Corp. [BAC]',
      u'Exxon Mobil Corp. [XOM]',
      u'SBC Communications Inc. [SBC]',
      u"American Int'l. Group [AIG]",
      u'North Fork Bancorporation [NFB]',
      u'Lehman Bros. [LEH]',
      u'Citigroup Inc. [C]',
      u'Allstate Corp. [ALL]',
      u'Hershey Foods [HSY]',
      u'FirstEnergy Corp. [FE]',
      u'Jefferson-Pilot [JP]',
      u'American Express [AXP]',
      u'Monsanto Co. [MON]',
      u'McKesson Corp. (New) [MCK]'],
 20: [u'*** [VTR]', u'*** [HMT]'],
 21: [u'Ambac Financial Group [ABK]',
      u'MetLife Inc. [MET]',
      u'MBIA Inc. [MBI]',
      u'Bard (C.R.) Inc. [BCR]',
      u'XL Capital [XL]',
      u'Charles Schwab [SCH]',
      u'Federated Dept. Stores [FD]',
      u'Chubb Corp. [CB]',
      u'Dillard Inc. [DDS]',
      u'SLM Corporation [SLM]',
      u'*** [SZ]',
      u'Cincinnati Financial [CINF]',
      u"Harrah's Entertainment [HET]",
      u'Merck & Co. [MRK]',
      u'Goodrich Corporation [GR]',
      u'Bear Stearns Cos. [BSC]',
      u'UnumProvident Corp. [UNM]',
      u'ACE Limited [ACE]',
      u'Circuit City Group [CC]'],
 22: [u'Great Lakes Chemical [GLK]',
      u'King Pharmaceuticals [KG]',
      u'Tyco International [TYC]',
      u'Deluxe Corp. [DLX]',
      u'Procter & Gamble [PG]',
      u'Worthington Ind. [WOR]',
      u'Automatic Data Processing Inc. [ADP]',
      u'Providian Financial Corp. [PVN]',
      u'Delphi Corporation [DPH]',
      u'Praxair  Inc. [PX]',
      u'Ashland Inc. [ASH]',
      u'Charter One Financial [CF]',
      u'Qwest Communications Int [Q]',
      u'Engelhard Corp. [EC]',
      u'Morgan Stanley [MWD]',
      u'Clear Channel Communications [CCU]',
      u'Eastman Kodak [EK]',
      u'Lilly (Eli) & Co. [LLY]',
      u'AutoZone Inc. [AZO]',
      u'Phelps Dodge [PD]',
      u'Sherwin-Williams [SHW]'],
 23: [u'Dow Chemical [DOW]',
      u'General Mills [GIS]',
      u'Eastman Chemical [EMN]',
      u'AFLAC Corporation [AFL]',
      u'E*Trade Financial Corp. [ET]',
      u'Whirlpool Corp. [WHR]',
      u'Motorola Inc. [MOT]',
      u'Gannett Co. [GCI]',
      u"Honeywell Int'l Inc. [HON]",
      u'Sealed Air Corp.(New) [SEE]',
      u'Affiliated Computer [ACS]',
      u'Electronic Data Systems [EDS]',
      u'Nucor Corp. [NUE]',
      u'Mylan Laboratories [MYL]',
      u'Progressive Corp. [PGR]',
      u'Du Pont (E.I.) [DD]',
      u"Wendy's International [WEN]",
      u'Ecolab Inc. [ECL]',
      u'Archer-Daniels-Midland [ADM]',
      u'Air Products & Chemicals [APD]',
      u'Corning Inc. [GLW]',
      u'Rohm & Haas [ROH]',
      u'PPG Industries [PPG]',
      u'Abbott Labs [ABT]'],
 24: [u'Stryker Corp. [SYK]',
      u'Cardinal Health  Inc. [CAH]',
      u'Becton  Dickinson [BDX]',
      u'Boston Scientific [BSX]',
      u'Aetna Inc. (New) [AET]',
      u'Big Lots  Inc. [BLI]'],
 25: [u'*** [NXL]',
      u'Equity Office Properties [EOP]',
      u"Apartment Investment & Mgmt'A' [AIV]",
      u'Simon Property Group  Inc [SPG]',
      u'Equity Residential [EQR]'],
 26: [u'Texas Instruments [TXN]',
      u'Electronic Arts [ERTS]',
      u'Micron Technology [MU]',
      u'BMC Software [BMC]',
      u'NVIDIA Corp. [NVDA]',
      u'Intel Corp. [INTC]',
      u'Fluor Corp. (New) [FLR]',
      u'Altera Corp. [ALTR]',
      u'McGraw-Hill [MHP]',
      u'eBay Inc. [EBAY]',
      u'Analog Devices [ADI]',
      u'CVS Corp. [CVS]',
      u'Mercury Interactive [MERQ]',
      u'KB Home [KBH]',
      u'PeopleSoft Inc. [PSFT]',
      u'AT&T Wireless Services [AWE]',
      u'Starbucks Corp. [SBUX]',
      u"Kohl's Corp. [KSS]",
      u'Tektronix Inc. [TEK]',
      u'Express Scripts [ESRX]',
      u'Pall Corp. [PLL]',
      u'Solectron [SLR]',
      u'Adobe Systems [ADBE]',
      u'Monster Worldwide [MNST]',
      u'PMC-Sierra Inc. [PMCS]',
      u'CIENA Corp. [CIEN]',
      u'Maxim Integrated Prod [MXIM]',
      u'Oracle Corp. [ORCL]',
      u'National Semiconductor [NSM]',
      u'Thermo Electron [TMO]',
      u'ADC Telecommunications [ADCT]',
      u'RadioShack Corp [RSH]',
      u'QUALCOMM Inc. [QCOM]',
      u'Computer Sciences Corp. [CSC]',
      u'Linear Technology Corp. [LLTC]',
      u'Andrew Corp. [ANDW]',
      u'Computer Associates Intl. [CA]',
      u'Grainger (W.W.) Inc. [GWW]'],
 27: [u'*** [VVI]',
      u"McDonald's Corp. [MCD]",
      u'CenterPoint Energy [CNP]',
      u'Allied Waste Industries [AW]'],
 28: [u'BJ Services [BJS]',
      u'*** [TWW]',
      u'Rowan Cos. [RDC]',
      u'Valero Energy [VLO]',
      u'Nabors Industries Ltd. [NBR]',
      u'Burlington Resources [BR]',
      u'Amerada Hess [AHC]',
      u'Transocean Inc. [RIG]',
      u'Anadarko Petroleum [APC]',
      u'Schlumberger Ltd. [SLB]',
      u'Baker Hughes [BHI]',
      u'Devon Energy Corp. [DVN]'],
 29: [u'Teradyne Inc. [TER]',
      u'QLogic Corp. [QLGC]',
      u'*** [SNS]',
      u'LSI Logic [LSI]',
      u'Hewlett-Packard [HPQ]',
      u"Lexmark Int'l Inc [LXK]",
      u'Fifth Third Bancorp [FITB]',
      u'El Paso Corp. [EP]',
      u'Applied Materials [AMAT]',
      u'Citrix Systems [CTXS]',
      u'Novellus Systems [NVLS]',
      u'Broadcom Corporation [BRCM]',
      u'Xilinx  Inc [XLNX]',
      u'Comverse Technology [CMVT]',
      u'Network Appliance [NTAP]',
      u'Interpublic Group [IPG]',
      u'Jabil Circuit [JBL]',
      u'Agilent Technologies [A]',
      u'BIOGEN IDEC Inc. [BIIB]',
      u'Northern Trust Corp. [NTRS]',
      u'KLA-Tencor Corp. [KLAC]',
      u'TECO Energy [TE]'],
 30: [u"Moody's Corp [MCO]",
      u'Kroger Co. [KR]',
      u'State Street Corp. [STT]',
      u'Coors (Adolph) [RKY]',
      u'International Bus. Machines [IBM]',
      u'Campbell Soup [CPB]',
      u'Toys R Us  Inc. [TOY]'],
 31: [u'Tellabs  Inc. [TLAB]',
      u'Waste Management Inc. [WMI]',
      u'Citizens Communications [CZN]',
      u'Hercules  Inc. [HPC]',
      u'Rockwell Automation  Inc. [ROK]',
      u'Molex Inc. [MOLX]',
      u'ProLogis [PLD]',
      u'Yahoo Inc. [YHOO]',
      u'Scientific-Atlanta [SFA]',
      u'Applied Micro Circuits [AMCC]',
      u'JDS Uniphase Corp [JDSU]',
      u'Williams Cos. [WMB]',
      u'Siebel  Systems Inc [SEBL]',
      u'*** [NT]',
      u'Liz Claiborne  Inc. [LIZ]'],
 32: [u'Ball Corp. [BLL]',
      u'V.F. Corp. [VFC]',
      u'Fannie Mae [FNM]',
      u'Entergy Corp. [ETR]',
      u'Supervalu Inc. [SVU]',
      u'Wrigley (Wm) Jr. [WWY]'],
 33: [u'Kerr-McGee [KMG]',
      u'EOG Resources [EOG]',
      u'Unocal Corp. [UCL]',
      u'Century Telephone [CTL]',
      u'Occidental Petroleum [OXY]',
      u'Apache Corp. [APA]',
      u'Winn-Dixie [WIN]',
      u'Halliburton Co. [HAL]'],
 34: [u'Boise Cascade [BCC]',
      u'Autodesk  Inc. [ADSK]',
      u'Northrop Grumman Corp. [NOC]',
      u'Cooper Tire & Rubber [CTB]',
      u'Jones Apparel Group [JNY]',
      u'Pactiv Corp. [PTV]',
      u'United Technologies [UTX]',
      u'Univision Communications [UVN]',
      u'MeadWestvaco Corporation [MWV]',
      u'Navistar International Corp. [NAV]',
      u'Genuine Parts [GPC]',
      u'Manor Care Inc. [HCR]',
      u'ALLTEL Corp. [AT]',
      u'Bank One Corp. [ONE]',
      u'Cooper Industries  Ltd. [CBE]',
      u'NCR Corp. [NCR]',
      u'Alcoa Inc [AA]',
      u'Time Warner Inc. [TWX]',
      u'Southwest Airlines [LUV]',
      u'Bemis Company [BMS]',
      u'Unisys Corp. [UIS]',
      u'CSX Corp. [CSX]',
      u'International Paper [IP]',
      u'Georgia-Pacific Group [GP]',
      u'Temple-Inland [TIN]',
      u'Weyerhaeuser Corp. [WY]',
      u'Newell Rubbermaid Co. [NWL]',
      u'Sprint Corp. FON [FON]',
      u'Microsoft Corp. [MSFT]',
      u'Lucent Technologies [LU]']}

#------------------------------------------------- LABELS  -----------------------------------

Association :
{0: [(u'Johnson Controls [JCI]', u'Consumer-Automobiles-Auto-Auto'),
     (u'General Electric [GE]', u'Industrials-Capital-Industrial-Industrial'),
     (u'MetLife Inc. [MET]', u'Financials-Insurance-Insurance-Life'),
     (u'Cooper Tire & Rubber [CTB]', u'Consumer-Automobiles-Auto-Tires'),
     (u'General Motors [GM]', u'Consumer-Automobiles-Automobiles-Automobile'),
     (u'Jones Apparel Group [JNY]', u'Consumer-Consumer-Textiles-Apparel'),
     (u'United Technologies [UTX]',
      u'Industrials-Capital-Aerospace-Aerospace'),
     (u'Bard (C.R.) Inc. [BCR]', u'Health-Health-Health-Health'),
     (u'Cummins  Inc. [CMI]', u'Industrials-Capital-Machinery-Construction'),
     (u'CVS Corp. [CVS]', u'Consumer-Food-Food-Drug'),
     (u'Dana Corp. [DCN]', u'Consumer-Automobiles-Auto-Auto'),
     (u'Fifth Third Bancorp [FITB]', u'Financials-Banks-Commercial-Regional'),
     (u'ITT Industries  Inc. [ITT]',
      u'Industrials-Capital-Machinery-Industrial'),
     (u'Block H&R [HRB]', u'Industrials-Commercial-Commercial-Diversified'),
     (u'Rockwell Automation  Inc. [ROK]',
      u'Industrials-Capital-Electrical-Electrical'),
     (u'Thomas & Betts [TNB]', u'Industrials-Capital-Electrical-Electrical'),
     (u'Tribune Co. [TRB]', u'Consumer-Media-Media-Publishing'),
     (u'KeyCorp [KEY]', u'Financials-Banks-Commercial-Regional'),
     (u'Maytag Corp. [MYG]', u'Consumer-Consumer-Household-Household'),
     (u'Capital One Financial [COF]',
      u'Financials-Diversified-Consumer-Consumer'),
     (u'Best Buy Co.  Inc. [BBY]', u'Consumer-Retailing-Specialty-Computer'),
     (u'Ford Motor [F]', u'Consumer-Automobiles-Automobiles-Automobile'),
     (u'Delphi Corporation [DPH]', u'Consumer-Automobiles-Auto-Auto'),
     (u'Federated Dept. Stores [FD]',
      u'Consumer-Retailing-Multiline-Department'),
     (u'Textron Inc. [TXT]', u'Industrials-Capital-Industrial-Industrial'),
     (u'PACCAR Inc. [PCAR]', u'Industrials-Capital-Machinery-Construction'),
     (u'American Standard [ASD]', u'Industrials-Capital-Building-Building'),
     (u'Eaton Corp. [ETN]', u'Industrials-Capital-Machinery-Industrial'),
     (u'Comcast Corp. [CMCSA]', u'Consumer-Media-Media-Broadcasting'),
     (u'SouthTrust Corp. [SOTR]', u'Financials-Banks-Commercial-Regional'),
     (u'AmSouth Bancorporation [ASO]',
      u'Financials-Banks-Commercial-Regional'),
     (u'Dover Corp. [DOV]', u'Industrials-Capital-Machinery-Industrial'),
     (u'SunTrust Banks [STI]', u'Financials-Banks-Commercial-Regional'),
     (u'Black & Decker Corp. [BDK]',
      u'Consumer-Consumer-Household-Household'),
     (u'Nordstrom [JWN]', u'Consumer-Retailing-Multiline-Department'),
     (u'Wells Fargo [WFC]', u'Financials-Banks-Commercial-Diversified'),
     (u'Bank of America Corp. [BAC]',
      u'Financials-Banks-Commercial-Diversified'),
     (u'Electronic Data Systems [EDS]', u'Information-Software-IT-Data'),
     (u'Morgan Stanley [MWD]', u'Financials-Diversified-Capital-Investment'),
     (u'Huntington Bancshares [HBAN]',
      u'Financials-Banks-Commercial-Regional'),
     (u'Golden West Financial [GDW]', u'Financials-Banks-Thrifts-Thrifts'),
     (u'Boeing Company [BA]', u'Industrials-Capital-Aerospace-Aerospace'),
     (u'M&T Bank Corp. [MTB]', u'Financials-Banks-Commercial-Regional'),
     (u'Nucor Corp. [NUE]', u'Materials-Materials-Metals-Steel'),
     (u'New York Times Cl. A [NYT]', u'Consumer-Media-Media-Publishing'),
     (u'Bristol-Myers Squibb [BMY]',
      u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
     (u'Johnson & Johnson [JNJ]',
      u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
     (u'Eastman Kodak [EK]', u'Consumer-Consumer-Leisure-Photographic'),
     (u'AutoZone Inc. [AZO]', u'Consumer-Retailing-Specialty-Specialty'),
     (u'Parker-Hannifin [PH]', u'Industrials-Capital-Machinery-Industrial'),
     (u'North Fork Bancorporation [NFB]',
      u'Financials-Banks-Commercial-Regional'),
     (u'Allegheny Technologies Inc [ATI]',
      u'Materials-Materials-Metals-Steel'),
     (u'Masco Corp. [MAS]', u'Industrials-Capital-Building-Building'),
     (u'Toys R Us  Inc. [TOY]', u'Consumer-Retailing-Specialty-Specialty'),
     (u'Phelps Dodge [PD]', u'Materials-Materials-Metals-Diversified'),
     (u'Countrywide Financial Corp. [CFC]',
      u'Financials-Banks-Thrifts-Thrifts'),
     (u'Equifax Inc. [EFX]',
      u'Industrials-Commercial-Commercial-Diversified'),
     (u'J.P. Morgan Chase & Co. [JPM]',
      u'Financials-Diversified-Capital-Diversified'),
     (u'Regions Financial Corp. [RF]',
      u'Financials-Banks-Commercial-Regional'),
     (u'Brunswick Corp. [BC]', u'Consumer-Consumer-Leisure-Leisure'),
     (u"Wendy's International [WEN]", u'Consumer-Hotels-Hotels-Restaurants'),
     (u'Caremark Rx [CMX]', u'Health-Health-Health-Health'),
     (u'SunGard Data Systems [SDS]', u'Information-Software-IT-Data'),
     (u'Illinois Tool Works [ITW]',
      u'Industrials-Capital-Machinery-Industrial'),
     (u'Crane Company [CR]', u'Industrials-Capital-Machinery-Industrial'),
     (u'Thermo Electron [TMO]',
      u'Information-Technology-Electronic-Electronic'),
     (u'BB&T Corporation [BBT]', u'Financials-Banks-Commercial-Regional'),
     (u'Computer Associates Intl. [CA]',
      u'Information-Software-Software-Systems'),
     (u'Office Depot [ODP]', u'Consumer-Retailing-Specialty-Specialty'),
     (u'Grainger (W.W.) Inc. [GWW]', u'Industrials-Capital-Trading-Trading')],
 1: [(u'Burlington Northern Santa Fe C [BNI]',
      u'Industrials-Transportation-Road-Railroads'),
     (u'Clorox Co. [CLX]', u'Consumer-Household-Household-Household'),
     (u'PepsiCo Inc. [PEP]', u'Consumer-Food-Beverages-Soft'),
     (u'Federal Home Loan Mtg. [FRE]', u'Financials-Banks-Thrifts-Thrifts'),
     (u'Duke Energy [DUK]',
      u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
     (u'Carnival Corp. [CCL]', u'Consumer-Hotels-Hotels-Hotels'),
     (u'Rockwell Collins [COL]', u'Industrials-Capital-Aerospace-Aerospace'),
     (u'Bank One Corp. [ONE]', u'Financials-Banks-Commercial-Diversified'),
     (u'Janus Capital Group [JNS]', u'Financials-Diversified-Capital-Asset'),
     (u'Norfolk Southern Corp. [NSC]',
      u'Industrials-Transportation-Road-Railroads'),
     (u'RJ Reynolds Tobacco [RJR]', u'Consumer-Food-Tobacco-Tobacco'),
     (u'Avon Products [AVP]', u'Consumer-Household-Personal-Personal'),
     (u'Synovus Financial [SNV]', u'Financials-Banks-Commercial-Regional'),
     (u'Avery Dennison Corp. [AVY]',
      u'Industrials-Commercial-Commercial-Office'),
     (u'CSX Corp. [CSX]', u'Industrials-Transportation-Road-Railroads'),
     (u'Engelhard Corp. [EC]', u'Materials-Materials-Chemicals-Diversified'),
     (u'First Data [FDC]', u'Information-Software-IT-Data'),
     (u'Fannie Mae [FNM]', u'Financials-Banks-Thrifts-Thrifts'),
     (u'Union Pacific [UNP]', u'Industrials-Transportation-Road-Railroads'),
     (u'Winn-Dixie [WIN]', u'Consumer-Food-Food-Food'),
     (u'Goodrich Corporation [GR]',
      u'Industrials-Capital-Aerospace-Aerospace'),
     (u'ConAgra Foods  Inc. [CAG]', u'Consumer-Food-Food-Packaged'),
     (u'UnumProvident Corp. [UNM]', u'Financials-Insurance-Insurance-Life'),
     (u'IMS Health Inc. [RX]', u'Health-Health-Health-Health'),
     (u'Marshall & Ilsley Corp. [MI]',
      u'Financials-Banks-Commercial-Regional')],
 2: [(u'Anheuser-Busch [BUD]', u'Consumer-Food-Beverages-Brewers'),
     (u'General Mills [GIS]', u'Consumer-Food-Food-Packaged'),
     (u'Sara Lee Corp. [SLE]', u'Consumer-Food-Food-Packaged'),
     (u'Kellogg Co. [K]', u'Consumer-Food-Food-Packaged')],
 3: [(u'*** [NX]', u'No_Label')],
 4: [(u'Sempra Energy [SRE]', u'Utilities-Utilities-Gas-Gas'),
     (u'Consolidated Edison [ED]', u'Utilities-Utilities-Electric-Electric'),
     (u'FPL Group [FPL]', u'Utilities-Utilities-Electric-Electric'),
     (u'Constellation Energy Group [CEG]',
      u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
     (u'DTE Energy Co. [DTE]', u'Utilities-Utilities-Electric-Electric'),
     (u'Dynegy Inc. (New) Class A [DYN]',
      u'Utilities-Utilities-Multi-Utilities-Multi-Utilities')],
 5: [(u'Marathon Oil Corp. [MRO]', u'Energy-Energy-Oil-Integrated'),
     (u'AES Corp. [AES]',
      u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
     (u'Valero Energy [VLO]', u'Energy-Energy-Oil-Oil'),
     (u'ConocoPhillips [COP]', u'Energy-Energy-Oil-Integrated'),
     (u'Amerada Hess [AHC]', u'Energy-Energy-Oil-Integrated'),
     (u'Ashland Inc. [ASH]', u'Energy-Energy-Oil-Oil'),
     (u'Aetna Inc. (New) [AET]', u'Health-Health-Health-Managed'),
     (u'Baxter International Inc. [BAX]', u'Health-Health-Health-Health')],
 6: [(u'Applera Corp-Applied Biosystems Group [ABI]',
      u'Health-Health-Health-Health'),
     (u'Millipore Corp. [MIL]', u'Health-Health-Health-Health'),
     (u'MedImmune Inc. [MEDI]',
      u'Health-Pharmaceuticals-Biotechnology-Biotechnology'),
     (u'Forest Laboratories [FRX]',
      u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
     (u'Becton  Dickinson [BDX]', u'Health-Health-Health-Health'),
     (u'Chiron Corp. [CHIR]',
      u'Health-Pharmaceuticals-Biotechnology-Biotechnology'),
     (u'Genzyme Corp. [GENZ]',
      u'Health-Pharmaceuticals-Biotechnology-Biotechnology'),
     (u'Heinz (H.J.) [HNZ]', u'Consumer-Food-Food-Packaged'),
     (u'Allergan  Inc. [AGN]',
      u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')],
 7: [(u'Darden Restaurants [DRI]', u'Consumer-Hotels-Hotels-Restaurants'),
     (u'Yum! Brands  Inc [YUM]', u'Consumer-Hotels-Hotels-Restaurants'),
     (u'ChevronTexaco Corp. [CVX]', u'Energy-Energy-Oil-Integrated')],
 8: [(u'Keyspan Energy [KSE]', u'Utilities-Utilities-Gas-Gas'),
     (u'Exelon Corp. [EXC]', u'Utilities-Utilities-Electric-Electric'),
     (u'Dominion Resources [D]', u'Utilities-Utilities-Electric-Electric'),
     (u'PPL Corp. [PPL]', u'Utilities-Utilities-Electric-Electric'),
     (u'Public Serv. Enterprise Inc. [PEG]',
      u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
     (u'American Electric Power [AEP]',
      u'Utilities-Utilities-Electric-Electric'),
     (u'Pinnacle West Capital [PNW]',
      u'Utilities-Utilities-Electric-Electric'),
     (u'Xcel Energy Inc [XEL]', u'Utilities-Utilities-Electric-Electric'),
     (u'NICOR Inc. [GAS]', u'Utilities-Utilities-Gas-Gas'),
     (u'Progress Energy  Inc. [PGN]',
      u'Utilities-Utilities-Electric-Electric'),
     (u'Peoples Energy [PGL]', u'Utilities-Utilities-Gas-Gas'),
     (u'Southern Co. [SO]', u'Utilities-Utilities-Electric-Electric'),
     (u'Sunoco.  Inc. [SUN]', u'Energy-Energy-Oil-Oil'),
     (u'NiSource Inc. [NI]', u'Utilities-Utilities-Gas-Gas'),
     (u'Entergy Corp. [ETR]', u'Utilities-Utilities-Electric-Electric'),
     (u'Ameren Corporation [AEE]', u'Utilities-Utilities-Electric-Electric')],
 9: [(u'Coca-Cola Enterprises [CCE]', u'Consumer-Food-Beverages-Soft'),
     (u'Cardinal Health  Inc. [CAH]', u'Health-Health-Health-Health')],
 10: [(u'Humana Inc. [HUM]', u'Health-Health-Health-Managed'),
      (u'*** [AIH]', u'No_Label'),
      (u'Wyeth [WYE]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'Tenet Healthcare Corp. [THC]', u'Health-Health-Health-Health'),
      (u'*** [GFR]', u'No_Label'),
      (u'WellPoint Health Networks [WLP]', u'Health-Health-Health-Managed')],
 11: [(u'Sun Microsystems [SUNW]',
       u'Information-Technology-Computers-Computer'),
      (u'Autodesk  Inc. [ADSK]',
       u'Information-Software-Software-Application'),
      (u'Hewlett-Packard [HPQ]',
       u'Information-Technology-Computers-Computer'),
      (u'Time Warner Inc. [TWX]', u'Consumer-Media-Media-Movies'),
      (u'CINergy Corp. [CIN]', u'Utilities-Utilities-Electric-Electric'),
      (u'Visteon Corp. [VC]', u'Consumer-Automobiles-Auto-Auto'),
      (u'Calpine Corp. [CPN]',
       u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
      (u'Andrew Corp. [ANDW]',
       u'Information-Technology-Communications-Communications')],
 12: [(u'Advanced Micro Devices [AMD]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'eBay Inc. [EBAY]', u'Consumer-Retailing-Internet-Internet'),
      (u'El Paso Corp. [EP]',
       u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
      (u'Watson Pharmaceuticals [WPI]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'Goodyear Tire & Rubber [GT]', u'Consumer-Automobiles-Auto-Tires'),
      (u'Abbott Labs [ABT]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals')],
 13: [(u'FIserv Inc. [FISV]', u'Information-Software-IT-Data'),
      (u'Cisco Systems [CSCO]',
       u'Information-Technology-Communications-Communications'),
      (u'Merrill Lynch [MER]', u'Financials-Diversified-Capital-Investment'),
      (u"Marriott Int'l. [MAR]", u'Consumer-Hotels-Hotels-Hotels'),
      (u'Mellon Bank Corp. [MEL]', u'Financials-Diversified-Capital-Asset'),
      (u'Robert Half International [RHI]',
       u'Industrials-Commercial-Commercial-Employment'),
      (u'Anthem  Inc. [ATH]', u'Health-Health-Health-Managed'),
      (u'AutoNation  Inc. [AN]', u'Consumer-Retailing-Specialty-Specialty'),
      (u'Pfizer  Inc. [PFE]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'ALLTEL Corp. [AT]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Pitney-Bowes [PBI]', u'Industrials-Commercial-Commercial-Office'),
      (u'Century Telephone [CTL]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Vulcan Materials [VMC]',
       u'Materials-Materials-Construction-Construction'),
      (u'International Bus. Machines [IBM]',
       u'Information-Technology-Computers-Computer'),
      (u'NCR Corp. [NCR]', u'Information-Technology-Computers-Computer'),
      (u'Goldman Sachs Group [GS]',
       u'Financials-Diversified-Capital-Investment'),
      (u'Walt Disney Co. [DIS]', u'Consumer-Media-Media-Movies'),
      (u'CenterPoint Energy [CNP]', u'Utilities-Utilities-Electric-Electric'),
      (u'Harley-Davidson [HDI]',
       u'Consumer-Automobiles-Automobiles-Motorcycle'),
      (u'Clear Channel Communications [CCU]',
       u'Consumer-Media-Media-Broadcasting'),
      (u'Cintas Corporation [CTAS]',
       u'Industrials-Commercial-Commercial-Diversified'),
      (u'Health Management Assoc. [HMA]', u'Health-Health-Health-Health'),
      (u'Paychex Inc. [PAYX]', u'Information-Software-IT-Data'),
      (u'American Power Conversion [APCC]',
       u'Industrials-Capital-Electrical-Electrical'),
      (u'*** [NT]', u'No_Label'),
      (u'Computer Sciences Corp. [CSC]', u'Information-Software-IT-Data')],
 14: [(u'Deere & Co. [DE]', u'Industrials-Capital-Machinery-Construction'),
      (u'Kroger Co. [KR]', u'Consumer-Food-Food-Food'),
      (u'Danaher Corp. [DHR]', u'Industrials-Capital-Machinery-Industrial'),
      (u'Mattel  Inc. [MAT]', u'Consumer-Consumer-Leisure-Leisure'),
      (u'Sabre Holding Corp. [TSG]', u'Information-Software-IT-Data'),
      (u'Waters Corporation [WAT]',
       u'Information-Technology-Electronic-Electronic'),
      (u'Stanley Works [SWK]', u'Consumer-Consumer-Household-Household'),
      (u'Ingersoll-Rand Co. Ltd. [IR]',
       u'Industrials-Capital-Machinery-Industrial'),
      (u'T. Rowe Price Group [TROW]',
       u'Financials-Diversified-Capital-Asset'),
      (u'International Flav/Frag [IFF]',
       u'Materials-Materials-Chemicals-Specialty'),
      (u'Caterpillar Inc. [CAT]',
       u'Industrials-Capital-Machinery-Construction'),
      (u'Lilly (Eli) & Co. [LLY]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'Mylan Laboratories [MYL]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'Lockheed Martin Corp. [LMT]',
       u'Industrials-Capital-Aerospace-Aerospace'),
      (u'Snap-On Inc. [SNA]', u'Consumer-Consumer-Household-Household'),
      (u'Convergys Corp. [CVG]', u'Information-Software-IT-Data')],
 15: [(u'Ryder System [R]', u'Industrials-Transportation-Air-Air'),
      (u'CIGNA Corp. [CI]', u'Health-Health-Health-Managed'),
      (u'International Game Technology [IGT]',
       u'Consumer-Hotels-Hotels-Casinos'),
      (u'Hercules  Inc. [HPC]', u'Materials-Materials-Chemicals-Diversified'),
      (u'Boston Scientific [BSX]', u'Health-Health-Health-Health'),
      (u'Lehman Bros. [LEH]', u'Financials-Diversified-Capital-Investment')],
 16: [(u'Parametric Technology [PMTC]',
       u'Information-Software-Software-Application'),
      (u'Centex Corp. [CTX]', u'Consumer-Consumer-Household-Homebuilding'),
      (u'FedEx Corporation [FDX]', u'Industrials-Transportation-Air-Air'),
      (u'McCormick & Co. [MKC]', u'Consumer-Food-Food-Packaged')],
 17: [(u'Quest Diagnostics [DGX]', u'Health-Health-Health-Health'),
      (u'Verizon Communications [VZ]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Sprint Corp. FON [FON]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Lucent Technologies [LU]',
       u'Information-Technology-Communications-Communications')],
 18: [(u'Bed Bath & Beyond [BBBY]',
       u'Consumer-Retailing-Specialty-Specialty'),
      (u'Costco Co. [COST]', u'Consumer-Food-Food-HyperMarkets'),
      (u'TJX Companies Inc. [TJX]', u'Consumer-Retailing-Specialty-Apparel'),
      (u'Biomet  Inc. [BMET]', u'Health-Health-Health-Health'),
      (u'Coors (Adolph) [RKY]', u'Consumer-Food-Beverages-Brewers'),
      (u'Navistar International Corp. [NAV]',
       u'Industrials-Capital-Machinery-Construction'),
      (u'Pulte Homes  Inc. [PHM]',
       u'Consumer-Consumer-Household-Homebuilding'),
      (u'Family Dollar Stores [FDO]',
       u'Consumer-Retailing-Multiline-General'),
      (u'KB Home [KBH]', u'Consumer-Consumer-Household-Homebuilding'),
      (u'*** [HMT]', u'No_Label'),
      (u'Target Corp. [TGT]', u'Consumer-Retailing-Multiline-General'),
      (u'Starbucks Corp. [SBUX]', u'Consumer-Hotels-Hotels-Restaurants'),
      (u'Staples Inc. [SPLS]', u'Consumer-Retailing-Specialty-Specialty'),
      (u'Dollar General [DG]', u'Consumer-Retailing-Multiline-General'),
      (u'Unisys Corp. [UIS]', u'Information-Software-IT-IT'),
      (u'Tiffany & Co. [TIF]', u'Consumer-Retailing-Specialty-Specialty'),
      (u'Starwood Hotels & Resorts [HOT]', u'Consumer-Hotels-Hotels-Hotels'),
      (u'NIKE Inc. [NKE]', u'Consumer-Consumer-Textiles-Footwear'),
      (u'Dillard Inc. [DDS]', u'Consumer-Retailing-Multiline-Department'),
      (u'Sears  Roebuck & Co. [S]',
       u'Consumer-Retailing-Multiline-Department'),
      (u'MBNA Corp. [KRB]', u'Financials-Diversified-Consumer-Consumer'),
      (u"Lowe's Cos. [LOW]", u'Consumer-Retailing-Specialty-Home'),
      (u'Interpublic Group [IPG]', u'Consumer-Media-Media-Advertising'),
      (u'May Dept. Stores [MAY]', u'Consumer-Retailing-Multiline-Department'),
      (u'Wal-Mart Stores [WMT]', u'Consumer-Food-Food-HyperMarkets'),
      (u'Oracle Corp. [ORCL]', u'Information-Software-Software-Systems'),
      (u'Limited Brands  Inc. [LTD]',
       u'Consumer-Retailing-Specialty-Apparel'),
      (u'Gap (The) [GPS]', u'Consumer-Retailing-Specialty-Apparel'),
      (u'Apollo Group [APOL]',
       u'Industrials-Commercial-Commercial-Diversified'),
      (u'Home Depot [HD]', u'Consumer-Retailing-Specialty-Home'),
      (u'Circuit City Group [CC]', u'Consumer-Retailing-Specialty-Computer'),
      (u'Liz Claiborne  Inc. [LIZ]', u'Consumer-Consumer-Textiles-Apparel')],
 19: [(u'Loews Corp. [LTR]', u'Financials-Insurance-Insurance-Multi-line'),
      (u'Freeport-McMoran Cp & Gld [FCX]',
       u'Materials-Materials-Metals-Diversified'),
      (u'BMC Software [BMC]', u'Information-Software-Software-Systems'),
      (u'Aon Corp. [AOC]', u'Financials-Insurance-Insurance-Insurance'),
      (u'UST Inc. [UST]', u'Consumer-Food-Tobacco-Tobacco'),
      (u'Northrop Grumman Corp. [NOC]',
       u'Industrials-Capital-Aerospace-Aerospace'),
      (u'Prudential Financial [PRU]', u'Financials-Insurance-Insurance-Life'),
      (u'U.S. Bancorp [USB]', u'Financials-Banks-Commercial-Diversified'),
      (u'Procter & Gamble [PG]', u'Consumer-Household-Household-Household'),
      (u'State Street Corp. [STT]', u'Financials-Diversified-Capital-Asset'),
      (u'National City Corp. [NCC]', u'Financials-Banks-Commercial-Regional'),
      (u'Hasbro Inc. [HAS]', u'Consumer-Consumer-Leisure-Leisure'),
      (u'Worthington Ind. [WOR]', u'Materials-Materials-Metals-Steel'),
      (u'XL Capital [XL]', u'Financials-Insurance-Insurance-Property'),
      (u'Principal Financial Group [PFG]',
       u'Financials-Diversified-Diversified-Other'),
      (u'Apple Computer [AAPL]',
       u'Information-Technology-Computers-Computer'),
      (u"Kohl's Corp. [KSS]", u'Consumer-Retailing-Multiline-Department'),
      (u'Zimmer Holdings [ZMH]', u'Health-Health-Health-Health'),
      (u"Albertson's [ABS]", u'Consumer-Food-Food-Food'),
      (u'BellSouth [BLS]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Hartford Financial Svc.Gp. [HIG]',
       u'Financials-Insurance-Insurance-Multi-line'),
      (u'Exxon Mobil Corp. [XOM]', u'Energy-Energy-Oil-Integrated'),
      (u"American Int'l. Group [AIG]",
       u'Financials-Insurance-Insurance-Multi-line'),
      (u'Cincinnati Financial [CINF]',
       u'Financials-Insurance-Insurance-Property'),
      (u'Progressive Corp. [PGR]',
       u'Financials-Insurance-Insurance-Property'),
      (u'Archer-Daniels-Midland [ADM]', u'Consumer-Food-Food-Agricultural'),
      (u'Citigroup Inc. [C]', u'Financials-Diversified-Diversified-Other'),
      (u'Torchmark Corp. [TMK]', u'Financials-Insurance-Insurance-Life'),
      (u'Hershey Foods [HSY]', u'Consumer-Food-Food-Packaged'),
      (u'FirstEnergy Corp. [FE]', u'Utilities-Utilities-Electric-Electric'),
      (u'Comerica Inc. [CMA]', u'Financials-Banks-Commercial-Diversified'),
      (u'PG&E Corp. [PCG]', u'Utilities-Utilities-Electric-Electric'),
      (u'Gillette Co. [G]', u'Consumer-Household-Personal-Personal'),
      (u'McKesson Corp. (New) [MCK]', u'Health-Health-Health-Health'),
      (u'Wrigley (Wm) Jr. [WWY]', u'Consumer-Food-Food-Packaged')],
 20: [(u'*** [VTR]', u'No_Label'), (u'*** [MXM]', u'No_Label')],
 21: [(u'Ambac Financial Group [ABK]',
       u'Financials-Insurance-Insurance-Property'),
      (u'SAFECO Corp. [SAFC]', u'Financials-Insurance-Insurance-Property'),
      (u'MBIA Inc. [MBI]', u'Financials-Insurance-Insurance-Property'),
      (u'McGraw-Hill [MHP]', u'Consumer-Media-Media-Publishing'),
      (u'Lincoln National [LNC]', u'Financials-Insurance-Insurance-Life'),
      (u'MGIC Investment [MTG]', u'Financials-Banks-Thrifts-Thrifts'),
      (u'Charles Schwab [SCH]', u'Financials-Diversified-Capital-Investment'),
      (u'Campbell Soup [CPB]', u'Consumer-Food-Food-Packaged'),
      (u'Chubb Corp. [CB]', u'Financials-Insurance-Insurance-Property'),
      (u'HCA Inc. [HCA]', u'Health-Health-Health-Health'),
      (u'*** [SZ]', u'No_Label'),
      (u'Federated Investors Inc. [FII]',
       u'Financials-Diversified-Capital-Asset'),
      (u"Harrah's Entertainment [HET]", u'Consumer-Hotels-Hotels-Casinos'),
      (u'Merck & Co. [MRK]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'BIOGEN IDEC Inc. [BIIB]',
       u'Health-Pharmaceuticals-Biotechnology-Biotechnology'),
      (u'Allstate Corp. [ALL]', u'Financials-Insurance-Insurance-Property'),
      (u'Jefferson-Pilot [JP]', u'Financials-Insurance-Insurance-Life'),
      (u'Supervalu Inc. [SVU]', u'Consumer-Food-Food-Food'),
      (u'ACE Limited [ACE]', u'Financials-Insurance-Insurance-Property')],
 22: [(u'Great Lakes Chemical [GLK]',
       u'Materials-Materials-Chemicals-Specialty'),
      (u'King Pharmaceuticals [KG]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'Knight-Ridder Inc. [KRI]', u'Consumer-Media-Media-Publishing'),
      (u'United States Steel Corp. [X]', u'Materials-Materials-Metals-Steel'),
      (u'Meredith Corp. [MDP]', u'Consumer-Media-Media-Publishing'),
      (u'Delta Air Lines [DAL]',
       u'Industrials-Transportation-Airlines-Airlines'),
      (u'Manor Care Inc. [HCR]', u'Health-Health-Health-Health'),
      (u'Pepsi Bottling Group [PBG]', u'Consumer-Food-Beverages-Soft'),
      (u'Plum Creek Timber Co. [PCL]', u'Financials-Real-Real-Real'),
      (u'Automatic Data Processing Inc. [ADP]',
       u'Information-Software-IT-Data'),
      (u'Praxair  Inc. [PX]', u'Materials-Materials-Chemicals-Industrial'),
      (u'Leggett & Platt [LEG]', u'Consumer-Consumer-Household-Home'),
      (u'Union Planters Corporation [UPC]',
       u'Financials-Banks-Commercial-Regional'),
      (u'Charter One Financial [CF]',
       u'Financials-Banks-Commercial-Regional'),
      (u'Washington Mutual [WM]', u'Financials-Banks-Thrifts-Thrifts'),
      (u'Sigma-Aldrich [SIAL]', u'Materials-Materials-Chemicals-Specialty'),
      (u'Cendant Corporation [CD]',
       u'Industrials-Commercial-Commercial-Diversified'),
      (u'United Parcel Service [UPS]', u'Industrials-Transportation-Air-Air'),
      (u'SBC Communications Inc. [SBC]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Franklin Resources [BEN]', u'Financials-Diversified-Capital-Asset'),
      (u'Fortune Brands  Inc. [FO]',
       u'Consumer-Consumer-Household-Housewares'),
      (u'Bear Stearns Cos. [BSC]',
       u'Financials-Diversified-Capital-Investment'),
      (u'Sherwin-Williams [SHW]', u'Consumer-Retailing-Specialty-Home')],
 23: [(u'Dow Chemical [DOW]', u'Materials-Materials-Chemicals-Diversified'),
      (u'Kimberly-Clark [KMB]', u'Consumer-Household-Household-Household'),
      (u'Hilton Hotels [HLT]', u'Consumer-Hotels-Hotels-Hotels'),
      (u'Fluor Corp. (New) [FLR]',
       u'Industrials-Capital-Construction-Construction'),
      (u'Eastman Chemical [EMN]',
       u'Materials-Materials-Chemicals-Diversified'),
      (u'Pactiv Corp. [PTV]', u'Materials-Materials-Containers-Metal'),
      (u'Univision Communications [UVN]',
       u'Consumer-Media-Media-Broadcasting'),
      (u'AFLAC Corporation [AFL]', u'Financials-Insurance-Insurance-Life'),
      (u'E*Trade Financial Corp. [ET]',
       u'Financials-Diversified-Capital-Investment'),
      (u'Gannett Co. [GCI]', u'Consumer-Media-Media-Publishing'),
      (u'Bausch & Lomb [BOL]', u'Health-Health-Health-Health'),
      (u'PNC Bank Corp. [PNC]', u'Financials-Banks-Commercial-Regional'),
      (u'Kinder Morgan [KMI]', u'Utilities-Utilities-Gas-Gas'),
      (u'Sealed Air Corp.(New) [SEE]',
       u'Materials-Materials-Containers-Paper'),
      (u'Affiliated Computer [ACS]', u'Information-Software-IT-Data'),
      (u'General Dynamics [GD]', u'Industrials-Capital-Aerospace-Aerospace'),
      (u'Wachovia Corp. (New) [WB]',
       u'Financials-Banks-Commercial-Diversified'),
      (u'Intuit  Inc. [INTU]', u'Information-Software-Software-Application'),
      (u'Du Pont (E.I.) [DD]', u'Materials-Materials-Chemicals-Diversified'),
      (u'Marsh & McLennan [MMC]',
       u'Financials-Insurance-Insurance-Insurance'),
      (u'Air Products & Chemicals [APD]',
       u'Materials-Materials-Chemicals-Industrial'),
      (u'Rohm & Haas [ROH]', u'Materials-Materials-Chemicals-Specialty'),
      (u'PPG Industries [PPG]', u'Materials-Materials-Chemicals-Diversified')],
 24: [(u'Stryker Corp. [SYK]', u'Health-Health-Health-Health'),
      (u'Altria Group  Inc. [MO]', u'Consumer-Food-Tobacco-Tobacco'),
      (u'St Jude Medical [STJ]', u'Health-Health-Health-Health'),
      (u'*** [MEE]', u'No_Label'),
      (u'TXU Corp. [TXU]', u'Utilities-Utilities-Electric-Electric'),
      (u'Colgate-Palmolive [CL]', u'Consumer-Household-Household-Household'),
      (u'Big Lots  Inc. [BLI]', u'Consumer-Retailing-Multiline-General'),
      (u'Medtronic Inc. [MDT]', u'Health-Health-Health-Health')],
 25: [(u'*** [NXL]', u'No_Label'),
      (u'Equity Office Properties [EOP]', u'Financials-Real-Real-Real'),
      (u'ProLogis [PLD]', u'Financials-Real-Real-Real'),
      (u"Apartment Investment & Mgmt'A' [AIV]", u'Financials-Real-Real-Real'),
      (u'Simon Property Group  Inc [SPG]', u'Financials-Real-Real-Real'),
      (u'Equity Residential [EQR]', u'Financials-Real-Real-Real')],
 26: [(u'Texas Instruments [TXN]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Electronic Arts [ERTS]', u'Information-Software-Software-Home'),
      (u'*** [TWW]', u'No_Label'),
      (u'Micron Technology [MU]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Xerox Corp. [XRX]', u'Information-Technology-Office-Office'),
      (u'NVIDIA Corp. [NVDA]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Intel Corp. [INTC]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u"McDonald's Corp. [MCD]", u'Consumer-Hotels-Hotels-Restaurants'),
      (u'Altera Corp. [ALTR]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Analog Devices [ADI]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u"Lexmark Int'l Inc [LXK]",
       u'Information-Technology-Computers-Computer'),
      (u'Symantec Corp. [SYMC]', u'Information-Software-Software-Systems'),
      (u'Mercury Interactive [MERQ]',
       u'Information-Software-Software-Application'),
      (u'PeopleSoft Inc. [PSFT]',
       u'Information-Software-Software-Application'),
      (u'Amgen [AMGN]',
       u'Health-Pharmaceuticals-Biotechnology-Biotechnology'),
      (u'AT&T Wireless Services [AWE]',
       u'Telecommunication-Telecommunication-Wireless-Wireless'),
      (u'Tektronix Inc. [TEK]',
       u'Information-Technology-Electronic-Electronic'),
      (u'Express Scripts [ESRX]', u'Health-Health-Health-Health'),
      (u'Pall Corp. [PLL]', u'Industrials-Capital-Machinery-Industrial'),
      (u'Solectron [SLR]', u'Information-Technology-Electronic-Electronic'),
      (u'*** [SNSTA]', u'No_Label'),
      (u'Novellus Systems [NVLS]',
       u'Information-Semiconductors-Semiconductor-Semiconductor'),
      (u'Broadcom Corporation [BRCM]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Monster Worldwide [MNST]',
       u'Industrials-Commercial-Commercial-Employment'),
      (u'PMC-Sierra Inc. [PMCS]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'JDS Uniphase Corp [JDSU]',
       u'Information-Technology-Communications-Communications'),
      (u'Williams Cos. [WMB]',
       u'Utilities-Utilities-Multi-Utilities-Multi-Utilities'),
      (u'CIENA Corp. [CIEN]',
       u'Information-Technology-Communications-Communications'),
      (u'Maxim Integrated Prod [MXIM]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Siebel  Systems Inc [SEBL]',
       u'Information-Software-Software-Application'),
      (u'National Semiconductor [NSM]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'ADC Telecommunications [ADCT]',
       u'Information-Technology-Communications-Communications'),
      (u'QUALCOMM Inc. [QCOM]',
       u'Information-Technology-Communications-Communications'),
      (u'Corning Inc. [GLW]',
       u'Information-Technology-Communications-Communications'),
      (u'Linear Technology Corp. [LLTC]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Microsoft Corp. [MSFT]', u'Information-Software-Software-Systems')],
 27: [(u'*** [VVI]', u'No_Label'),
      (u'Providian Financial Corp. [PVN]',
       u'Financials-Diversified-Consumer-Consumer'),
      (u'Allied Waste Industries [AW]',
       u'Industrials-Commercial-Commercial-Environmental'),
      (u'TECO Energy [TE]', u'Utilities-Utilities-Electric-Electric')],
 28: [(u'BJ Services [BJS]', u'Energy-Energy-Energy-Oil'),
      (u'Rowan Cos. [RDC]', u'Energy-Energy-Energy-Oil'),
      (u'EOG Resources [EOG]', u'Energy-Energy-Oil-Oil'),
      (u'Nabors Industries Ltd. [NBR]', u'Energy-Energy-Energy-Oil'),
      (u'Burlington Resources [BR]', u'Energy-Energy-Oil-Oil'),
      (u'Transocean Inc. [RIG]', u'Energy-Energy-Energy-Oil'),
      (u'EMC Corp. [EMC]', u'Information-Technology-Computers-Computer'),
      (u'Schlumberger Ltd. [SLB]', u'Energy-Energy-Energy-Oil'),
      (u'Baker Hughes [BHI]', u'Energy-Energy-Energy-Oil')],
 29: [(u'Teradyne Inc. [TER]',
       u'Information-Semiconductors-Semiconductor-Semiconductor'),
      (u'QLogic Corp. [QLGC]',
       u'Information-Technology-Communications-Communications'),
      (u'Omnicom Group [OMC]', u'Consumer-Media-Media-Advertising'),
      (u'Power-One Inc. [PWER]',
       u'Industrials-Capital-Electrical-Electrical'),
      (u'LSI Logic [LSI]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Motorola Inc. [MOT]',
       u'Information-Technology-Communications-Communications'),
      (u'Sanmina-SCI Corp. [SANM]',
       u'Information-Technology-Electronic-Electronic'),
      (u'Applied Materials [AMAT]',
       u'Information-Semiconductors-Semiconductor-Semiconductor'),
      (u'Citrix Systems [CTXS]',
       u'Information-Software-Software-Application'),
      (u'Yahoo Inc. [YHOO]', u'Information-Software-Internet-Internet'),
      (u'PerkinElmer [PKI]', u'Information-Technology-Electronic-Electronic'),
      (u'Adobe Systems [ADBE]', u'Information-Software-Software-Systems'),
      (u'Xilinx  Inc [XLNX]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Sysco Corp. [SYY]', u'Consumer-Food-Food-Food'),
      (u'Scientific-Atlanta [SFA]',
       u'Information-Technology-Communications-Communications'),
      (u'Comverse Technology [CMVT]',
       u'Information-Technology-Communications-Communications'),
      (u'Applied Micro Circuits [AMCC]',
       u'Information-Semiconductors-Semiconductor-Semiconductors'),
      (u'Network Appliance [NTAP]',
       u'Information-Technology-Computers-Computer'),
      (u'Jabil Circuit [JBL]',
       u'Information-Technology-Electronic-Electronic'),
      (u'Agilent Technologies [A]',
       u'Information-Technology-Electronic-Electronic'),
      (u'Nextel Communications [NXTL]',
       u'Telecommunication-Telecommunication-Wireless-Wireless'),
      (u'KLA-Tencor Corp. [KLAC]',
       u'Information-Semiconductors-Semiconductor-Semiconductor')],
 30: [(u"Moody's Corp [MCO]",
       u'Financials-Diversified-Diversified-Specialized'),
      (u'Tyco International [TYC]',
       u'Industrials-Capital-Industrial-Industrial'),
      (u'*** [SNS]', u'No_Label'),
      (u'Penney (J.C.) [JCP]', u'Consumer-Retailing-Multiline-Department'),
      (u'Deluxe Corp. [DLX]',
       u'Industrials-Commercial-Commercial-Diversified'),
      (u'Genuine Parts [GPC]',
       u'Consumer-Retailing-Distributors-Distributors'),
      (u'Coca Cola Co. [KO]', u'Consumer-Food-Beverages-Soft')],
 31: [(u'Tellabs  Inc. [TLAB]',
       u'Information-Technology-Communications-Communications'),
      (u'Dell Inc. [DELL]', u'Information-Technology-Computers-Computer'),
      (u'Waste Management Inc. [WMI]',
       u'Industrials-Commercial-Commercial-Environmental'),
      (u'Citizens Communications [CZN]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Symbol Technologies [SBL]',
       u'Information-Technology-Electronic-Electronic'),
      (u'Avaya Inc. [AV]',
       u'Information-Technology-Communications-Communications'),
      (u'Gateway Inc. [GTW]', u'Information-Technology-Computers-Computer'),
      (u'Molex Inc. [MOLX]', u'Information-Technology-Electronic-Electronic'),
      (u'AmerisourceBergen Corp. [ABC]', u'Health-Health-Health-Health'),
      (u'Schering-Plough [SGP]',
       u'Health-Pharmaceuticals-Pharmaceuticals-Pharmaceuticals'),
      (u'Qwest Communications Int [Q]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'Guidant Corp. [GDT]', u'Health-Health-Health-Health'),
      (u"Edison Int'l [EIX]", u'Utilities-Utilities-Electric-Electric'),
      (u'Monsanto Co. [MON]', u'Materials-Materials-Chemicals-Fertilizers'),
      (u'Bank of New York [BK]', u'Financials-Diversified-Capital-Asset')],
 32: [(u'Ball Corp. [BLL]', u'Materials-Materials-Containers-Metal'),
      (u'Safeway Inc. [SWY]', u'Consumer-Food-Food-Food'),
      (u'Newmont Mining Corp. (Hldg. Co.) [NEM]',
       u'Materials-Materials-Metals-Gold')],
 33: [(u'Kerr-McGee [KMG]', u'Energy-Energy-Oil-Oil'),
      (u'Unocal Corp. [UCL]', u'Energy-Energy-Oil-Oil'),
      (u'Occidental Petroleum [OXY]', u'Energy-Energy-Oil-Integrated'),
      (u'Allegheny Energy [AYE]', u'Utilities-Utilities-Electric-Electric'),
      (u'Apache Corp. [APA]', u'Energy-Energy-Oil-Oil'),
      (u'Anadarko Petroleum [APC]', u'Energy-Energy-Oil-Oil'),
      (u'Devon Energy Corp. [DVN]', u'Energy-Energy-Oil-Oil'),
      (u'Halliburton Co. [HAL]', u'Energy-Energy-Energy-Oil')],
 34: [(u'Boise Cascade [BCC]', u'Consumer-Retailing-Specialty-Specialty'),
      (u'AT&T Corp. (New) [T]',
       u'Telecommunication-Telecommunication-Diversified-Integrated'),
      (u'MeadWestvaco Corporation [MWV]', u'Materials-Materials-Paper-Paper'),
      (u'Compuware Corp. [CPWR]',
       u'Information-Software-Software-Application'),
      (u'Raytheon Co. (New) [RTN]',
       u'Industrials-Capital-Aerospace-Aerospace'),
      (u'Whirlpool Corp. [WHR]', u'Consumer-Consumer-Household-Household'),
      (u'Zions Bancorp [ZION]', u'Financials-Banks-Commercial-Regional'),
      (u'Cooper Industries  Ltd. [CBE]',
       u'Industrials-Capital-Electrical-Electrical'),
      (u'CMS Energy [CMS]', u'Utilities-Utilities-Electric-Electric'),
      (u"Honeywell Int'l Inc. [HON]",
       u'Industrials-Capital-Aerospace-Aerospace'),
      (u'V.F. Corp. [VFC]', u'Consumer-Consumer-Textiles-Apparel'),
      (u'Alcoa Inc [AA]', u'Materials-Materials-Metals-Aluminum'),
      (u'Southwest Airlines [LUV]',
       u'Industrials-Transportation-Airlines-Airlines'),
      (u'Bemis Company [BMS]', u'Materials-Materials-Containers-Paper'),
      (u'Louisiana Pacific [LPX]', u'Materials-Materials-Paper-Forest'),
      (u'International Paper [IP]', u'Materials-Materials-Paper-Paper'),
      (u'SLM Corporation [SLM]', u'Financials-Diversified-Consumer-Consumer'),
      (u'Emerson Electric [EMR]',
       u'Industrials-Capital-Electrical-Electrical'),
      (u'Walgreen Co. [WAG]', u'Consumer-Food-Food-Drug'),
      (u'Ecolab Inc. [ECL]', u'Materials-Materials-Chemicals-Specialty'),
      (u'Georgia-Pacific Group [GP]', u'Materials-Materials-Paper-Paper'),
      (u'Temple-Inland [TIN]', u'Materials-Materials-Containers-Paper'),
      (u'Weyerhaeuser Corp. [WY]', u'Materials-Materials-Paper-Forest'),
      (u'3M Company [MMM]', u'Industrials-Capital-Industrial-Industrial'),
      (u'Northern Trust Corp. [NTRS]',
       u'Financials-Diversified-Capital-Asset'),
      (u'Newell Rubbermaid Co. [NWL]',
       u'Consumer-Consumer-Household-Housewares'),
      (u'RadioShack Corp [RSH]', u'Consumer-Retailing-Specialty-Computer'),
      (u'Dow Jones & Co. [DJ]', u'Consumer-Media-Media-Publishing'),
      (u'American Express [AXP]',
       u'Financials-Diversified-Consumer-Consumer')]}


'''
