import os
import discord
from discord.ext import tasks
from pronotepy import Pronote
from pronotepy.ent import ENTConnection
from dotenv import load_dotenv

# --- Charger les variables d'environnement depuis .env ---
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
        # Remplace "general" par le nom exact de ton channel Discord
        channel = discord.utils.get(client.get_all_channels(), name="general")
        if channel:
            for (matiere, titre), note in new_notes.items():
                await channel.send(
                    f"Nouvelle note en **{matiere}** : {note['note']} / {note['total']} ({titre})"
                )

# --- Événements Discord ---
@client.event
async def on_ready():
    print(f"Bot connecté en tant que {client.user}")
    check_new_notes.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Commande pour afficher toutes les notes
    if message.content.startswith("/notes"):
        notes, _ = get_notes()
        response = "📋 **Notes** :\n"
        for matiere, liste in notes.items():
            response += f"**{matiere}** : " + ", ".join(
                [f"{n['note']}/{n['total']} ({n['title']})" for n in liste]
            ) + "\n"
        await message.channel.send(response)
 # Commande pour afficher les moyennes
    if message.content.startswith("/moyenne"): 
        notes, _ = get_notes()
        averages, total_avg = calculate_averages(notes)
        response = "📊 **Moyennes** :\n"
        for matiere, avg in averages.items():
            response += f"**{matiere}** : {avg}\n"
        response += f"**Moyenne totale** : {total_avg}"
        await message.channel.send(response)

# --- Lancement du bot Discord ---
client.run(TOKEN)
