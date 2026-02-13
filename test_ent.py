from pronotepy import Pronote
from pronotepy.ent import ENTConnection

url = "https://0660014g.index-education.net/pronote"
username = "ton_identifiant_ENT"
password = "ton_motdepasse_ENT"

ent = ENTConnection(url, username=username, password=password)

try:
    pronote = Pronote(ent)
    print("Connexion réussie !")
except Exception as e:
    print("Erreur :", e)
