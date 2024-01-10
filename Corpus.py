from Document import Document
from Author import Author
import pandas as pd
import numpy as np
import dill
import re
from collections import defaultdict
from scipy.sparse import csr_matrix



###########################################################################################################################################
###############################################             Création du Corpus         ####################################################
###########################################################################################################################################


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
        self.concatenated_text = None
        self.vocabulary = set()
        self.word_freq = None
        self.vocab = dict()

        
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
        self.new_vocabulary(document.texte)
      

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
    
    
###########################################################################################################################################
###############################################          Statistiques          ############################################################
###########################################################################################################################################

    # Méthode pour concaténer le texte de tous les documents
    def concatenate_text(self):
        if self.concatenated_text is None:
            self.concatenated_text = "".join([doc.texte for doc in self.id2doc.values()])

    # Méthode pour effectuer une recherche dans le texte concaténé
    def search(self, keyword, context_length=30):
        self.concatenate_text()

        matches = list(
            re.finditer(
                rf"\b{re.escape(keyword)}\b", self.concatenated_text, re.IGNORECASE
            )
        )
        print(
            f"Number of passages containing the keyword '{keyword}': {len(matches)}\n"
        )
        print("Passages containing the keyword:\n")

        for match in matches:
            start_pos = max(0, match.start() - context_length)
            end_pos = min(len(self.concatenated_text), match.end() + context_length)
            passage = self.concatenated_text[start_pos:end_pos]
            print(f"{passage}\n")

        return

    # Méthode pour construire un concordancier pour un motif donné
    def concordancier(self, motif, long=(20, 20)):
        self.concatenate_text()
        matches = re.finditer(motif, self.concatenated_text)
        mon_corcondancier = []

        for match in matches:
            start_index = max(0, match.start() - long[0])
            end_index = min(len(self.concatenated_text), match.end() + long[1])
            left_context = self.concatenated_text[start_index : match.start()]
            right_context = self.concatenated_text[match.end() : end_index]
            mon_corcondancier.append((left_context, match.group(), right_context))

        df = pd.DataFrame(
            mon_corcondancier,
            columns=["Contexte de guache", "mot", "contexte de droite"],
        )

        return df
    
    
    def nettoyer_texte(self, texte):
        texte = texte.lower()  
        texte = texte.replace("\n", " ")
        # Suppression de la ponctuation et des chiffres
        texte = re.sub(r"[^\w\s]", "", texte)
        texte = re.sub(r"\d+", "", texte)
        return texte
    
    
    
    def construire_vocabulaire(self):
        vocabulary = set()
        for doc in self.id2doc.values():
            cleaned_text = self.nettoyer_texte(doc.texte)
            words = re.split(r'\s+', cleaned_text)  
            vocabulary.update(words)
        return vocabulary    

    
    def compter_occurrences(self):
        vocabulary = self.construire_vocabulaire()
        word_freq = {}
        for word in vocabulary:
            word_freq[word] = 0

        for doc in self.id2doc.values():
            cleaned_text = self.nettoyer_texte(doc.texte)
            words = re.split(r'\s+', cleaned_text)
            for word in words:
                if word in word_freq:
                    word_freq[word] += 1
        
        return word_freq


    def stats(self, n):
        vocabulaire = set()
        term_frequency = {}
        document_frequency = defaultdict(int)

        # Construction du vocabulaire et calcul des fréquences
        for doc in self.id2doc.values():
            mots = self.nettoyer_texte(doc.texte).split()
            vocabulaire.update(mots)

            for mot in mots:
                if mot in term_frequency:
                    term_frequency[mot] += 1
                else:
                    term_frequency[mot] = 1

            for mot in set(mots):
                if mot in document_frequency:
                    document_frequency[mot] += 1
                else:
                    document_frequency[mot] = 1

        # Tri des mots par fréquence
        mots_freq = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)[:n]

        # Création du DataFrame pour l'affichage
        df = pd.DataFrame(mots_freq, columns=['Mot', 'Fréquence'])
        
        # Ajout de la colonne Document Frequency au DataFrame
        df['Document Frequency'] = [document_frequency[mot] for mot, freq in mots_freq]
        return df

   ###########################################################################################################################################
#############################################       Moteur De Recherche         ###########################################################
###########################################################################################################################################

    def new_vocabulary(self, text):

        vocabulary = self.construire_vocabulaire()
        for word in vocabulary:
            if word not in self.vocab:
                self.vocab[word] = {
                    "id": len(self.vocab) + 1,
                    "total_occurences": 0,
                    "documents_occurences": 0,
                }
            self.vocab[word]["total_occurences"] += 1
            self.vocab[word]["documents_occurences"] += 1  
            
            
            
    def frequency_matrix(self):
            rows = []
            cols = []
            values = []
            for doc_id, doc in self.id2doc.items():
                words = self.nettoyer_texte(doc.texte).split()
                word_freq = defaultdict(int)
                for word in words:
                    word_freq[word] += 1

                for word, freq in word_freq.items():
                    if word not in self.vocab:
                        continue  # Ignorer les mots non présents dans le vocabulaire
                    cols.append(self.vocab[word]["id"] - 1)  # Ajustement de l'indice pour 0-based indexing
                    rows.append(doc_id - 1)  # Ajustement de l'indice pour 0-based indexing
                    values.append(freq)

            return csr_matrix((values, (rows, cols)), shape=(len(self.id2doc), len(self.vocab)))

    def query_to_vect(self, query):
        local_vector = np.zeros(len(self.vocab))

        for word in self.nettoyer_texte(query).split():
            if word in self.vocab:
                idx = self.vocab[word]["id"] - 1
                local_vector[idx] += 1

        return local_vector

    def cosinus_similarity(self, v1, v2):
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0
        return np.dot(v1, v2) / (norm_v1 * norm_v2)

    def search_on_scoring(self, query):
        query_vector = self.query_to_vect(query)

        scores = []
        for doc_id, doc in self.id2doc.items():
            doc_vector = self.frequency_matrix()[doc_id - 1].toarray().flatten()
            similarity = self.cosinus_similarity(query_vector, doc_vector)
            scores.append((doc_id, similarity))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return scores
