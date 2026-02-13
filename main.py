import os
import discord
from discord.ext import tasks
from pronotepy import Pronote
from pronotepy.ent import ENTConnection
from dotenv import load_dotenv

load_dotenv()

# --- Variables d'environnement Railway ---
TOKEN = os.getenv("DISCORD_TOKEN")
USERNAME = os.getenv("PRONOTE_USERNAME")
PASSWORD = os.getenv("PRONOTE_PASSWORD")
PRONOTE_URL = os.getenv("PRONOTE_URL")

# --- Discord ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# --- Connexion PRONOTE via ENT ---
ent = ENTConnection(PRONOTE_URL, username=USERNAME, password=PASSWORD)
pronote = Pronote(ent)

# --- Stockage des notes précédentes pour détecter les nouveautés ---
previous_notes = {}

# --- Fonction pour récupérer les notes ---
def get_notes():
    global previous_notes
    notes = pronote.notes()  # dictionnaire par matière
    new_notes = {}
    
    for matiere, liste in notes.items():
        for note in liste:
            key = (matiere, note["title"])
            if key not in previous_notes:
                new_notes[key] = note
                previous_notes[key] = note
    return notes, new_notes

# --- Calcul des moyennes ---
def calculate_averages(notes):
    averages = {}
    total_sum = 0
    total_coef = 0
    for matiere, liste in notes.items():
        somme = sum([float(n["note"]) * n["coef"] for n in liste])
        coef = sum([n["coef"] for n in liste])
        if coef > 0:
            averages[matiere] = round(somme / coef, 2)
            total_sum += somme
            total_coef += coef
    total_average = round(total_sum / total_coef, 2) if total_coef > 0 else 0
    return averages, total_average

# --- Tâche automatique pour vérifier les nouvelles notes ---
@tasks.loop(minutes=10)
async def check_new_notes():
    notes, new_notes = get_notes()
    if new_notes:
        channel = discord.utils.get(client.get_all_channels(), name="general")
        if channel:
            for (matiere, titre), note in ne:
