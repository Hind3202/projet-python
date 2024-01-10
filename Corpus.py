from Document import Document
from Author import Author
import pandas as pd
import dill



#Pour faire une seule instance de la classe Corpus
def singleton(cls):
    instances = { } #Pour stocker les instances de classes
    
    def get_instance(*args, **kwargs):
        #Création d'une instance de la classe si elle n'existe pas déjà
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance



@singleton
class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}  # Dictionnaire pour stocker les noms d'auteurs
        self.id2doc = {}   # Dictionnaire pour stocker les documents
        self.id2aut = {}   # Dictionnaire pour stocker les id des auteurs
        self.ndoc = 0      # Compteur de documents
        self.naut = 0      # Compteur d'auteurs

        
    def add(self, document):
        #Ajout de l'autheur si il n'existe pas déjà dans le dictionnaire
        if document.auteur not in self.id2aut:
            self.naut += 1
            self.authors[self.naut] = Author(document.auteur)
            self.id2aut[document.auteur] = self.naut
        #Ajout du document à l'auteur correspondant          
        self.authors[self.id2aut[document.auteur]].add(document.texte)
        self.ndoc += 1
        #Ajout du document au dictionnaire de documents
        self.id2doc[self.ndoc] = document

    #Affichage des détails de tous les documents triés par date ou titre
    def afficher_tout( self,tri):
        if tri == "date":
            documents = sorted(self.id2doc.values(), key=lambda x: x.date)
        elif tri == "titre":
            documents = sorted(self.id2doc.values(), key=lambda x: x.titre)
        else:
            documents = self.id2doc.values()
              
        for document in documents:
            print(
                f"Titre: {document.titre}\nAuteur: {document.auteur}\nDate: {document.date}\nURL: {document.url}\nTexte: {document.texte}\nType : {document.gettype()}\n\n"
            )


    def __repr__(self):
        return f"Corpus {self.nom}: Nombre de documents - {self.ndoc}, Nombre d'auteurs - {self.naut}"

    #Sauvegarde de l'objet Corpus dans le fichier en mode binaire via dill
    def save(self, file_name):
        with open(file_name, "wb") as f:
            dill.dump(self, f)

    #Chargement de l'objet corpus depuis le fichier via dill         
    def load(self, file_name):
        with open(file_name, "rb") as f:
            corpus = dill.load(f)
        return corpus
