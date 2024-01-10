from Document import Document
from Author import Author
from Corpus import Corpus
from Document import RedditDocument, ArxivDocument, Factory
import praw
from datetime import datetime
import urllib.request  # Requêtes HTTP
import xmltodict  # Convertir des données XML en un dictionnaire Python
import ipywidgets as widgets #création d'éléments interactifs dans les notebooks Jupyter
from IPython.display import display #affichage de widgets et de contenu HTML



def principale(mot_cle, nb_docs):
    
   # Initialisation de l'API Reddit
    reddit = praw.Reddit(
        client_id="7p-Tif-jrcIQ8awwlazFFg",
        client_secret="UjTwgH4CQOdubhvRJcH0gNInKNYYLA",
        user_agent="hind",
    )
    
    
    # Traitement des données de Reddit
    subr = reddit.subreddit(mot_cle)
    
    
    # Traitement des données d'Arxiv
    query = mot_cle
    url = (
        "http://export.arxiv.org/api/query?search_query=all:"
        + query
        + "&start=0&max_results="
        + str(nb_docs)
    )
    
    url_read = urllib.request.urlopen(url).read()
    data = url_read.decode()
    dic = xmltodict.parse(data)
    docs = dic["feed"]["entry"]
    
    # Initialisation de dictionnaires pour stocker les documents et auteurs
    id2doc = dict()
    id2aut = dict()
    posts = []

    # Itération sur les données de Reddit
    for post in subr.hot(limit=nb_docs):
        titre = post.title
        titre = titre.replace("\n", " ")
        auteur = str(post.author)
        date = datetime.utcfromtimestamp(post.created).strftime("%Y-%m-%d %H:%M:%S")
        url = post.url
        texte = post.selftext
        doc = Factory.create_new("Reddit", titre, auteur, date, url, texte)

        posts.append(doc)

        # Instantiation de l'autheur s'il n'existe pas déjà dans le dictionnaire des autheurs
        if auteur not in id2aut:
            aut = Author(auteur)
            id2aut[auteur] = aut
            id2aut[auteur].add(doc)

        else:
            id2aut[auteur].add(doc)
            
    # Itération sur les données d'Arxiv
    for d in docs:
        titre = d["title"]
        titre = titre.replace("\n", " ")
        auteur = str(d["author"])
        date = datetime.strptime(d["published"], "%Y-%m-%dT%H:%M:%SZ").strftime(
            "%Y-%m-%d"
        )
        url = d["link"][1]["@href"]
        texte = d["summary"]

        doc = Factory.create_new("Arxiv", titre, auteur, date, url, texte)
        posts.append(doc)

        # Gestion des auteurs associés aux documents d'Arxiv 
        for atr in auteur:
            #Vérifier si on a un seul ou plusieurs autheurs
            if isinstance(atr, dict):
                mon_auteur = atr["name"]
            else:
                mon_auteur = atr

            if mon_auteur not in id2aut:
                aut = Author(mon_auteur)
                id2aut[mon_auteur] = aut
                id2aut[mon_auteur].add(doc)
            else:
                id2aut[mon_auteur].add(doc)

    for index, doc in enumerate(posts):
        id2doc[index] = doc

        
    # Création d'un corpus
    corpus = Corpus(mot_cle)

    # Ajout des documents et auteurs au corpus
    for document in id2doc.values():
        corpus.add(document)
    
    # Sauvegarde du corpus
    corpus.save("mon_corpus.pkl")
    
    # Chargement du corpus
    corpus_chargé = Corpus("Nouveau_corpus")
    corpus = corpus_chargé.load("mon_corpus.pkl")
    
    return corpus