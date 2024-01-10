class Document:
    def __init__(self, titre, auteur, date, url, texte, type=""):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = type

    def afficher_info(self):
        print(f"Titre: {self.titre}")
        print(f"Auteur: {self.auteur}")
        print(f"Date de publication: {self.date}")
        print(f"URL source: {self.url}")
        print(f"Contenu textuel:\n{self.texte}")

    def __str__(self):
        return f"Document: {self.titre}"

    
#Classe fille de la classe Document
class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, commentNb=0, voteNb=0, type="Reddit"):
        Document.__init__(
            self, titre=titre, auteur=auteur, date=date, url=url, texte=texte, type=type
        )
        self.__commentNb = commentNb
        self.__voteNb = voteNb

    def __str__(self):
        return f"le post :{self.titre}, crée par {self.auteur} , a un score égale à {self.__voteNb} et {self.__commentNb} commentaires"

    # Méthodes pour obtenir et définir le nombre de commentaires et de votes
    def getCommentNb(self):
        return self.__commentNb

    def setCommentNb(self, commentNb):
        self.__commentNb = commentNb

    def getVoteNb(self):
        return self.__voteNb

    def setVoteNb(self, voteNb):
        self.__voteNb = voteNb

    def gettype(self):
        return "Reddit"

    

#Classe fille de la classe Document    
class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, type="Arxiv"):
        Document.__init__(
            self,
            titre=titre,
            auteur=auteur,
            date=date,
            url=url,
            texte=texte,
            type=type,
        )

    def __str__(self):
        return f"le post :{self.titre}, est crée par les auteurs  : {self.auteur}"

    def gettype(self):
        return "Arxiv"

#Création dynamique des instances de RedditDocument ou ArxivDocument en fonction du type spécifié.
class Factory:
    @staticmethod
    def create_new(doc_type, *args, **kwargs):
        if doc_type == "Reddit":
            return RedditDocument(*args, **kwargs)
        elif doc_type == "Arxiv":
            return ArxivDocument(*args, **kwargs)
        else:
            raise ValueError("Type de document non pris en charge")
