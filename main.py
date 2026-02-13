import os
import discord
from discord.ext import tasks
from pronotepy import Client
from dotenv import load_dotenv

# --- Charger les variables d'environnement ---
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
USERNAME = os.getenv("PRONOTE_USERNAME")
PASSWORD = os.getenv("PRONOTE_PASSWORD")
PRONOTE_URL = os.getenv("PRONOTE_URL")

# --- Connexion PRONOTE via Client ---
pronote_client = Client(
    username=USERNAME,
    password=PASSWORD,
    server_url=PRONOTE_URL,
    school=PRONOTE_URL  # parfois requis pour ENT
)

# --- Discord bot setup ---
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# --- Fonction pour récupérer les notes ---
async def get_notes():
    new_notes = {}
    try:
        notes = pronote_client.notes()
        for note in notes:
            matiere = note.subject
            titre = note.title
            new_notes[(matiere, titre)] = {
                "note": note.value,
                "total": note.total
            }
    except Exception as e:
        print(f"Erreur lors de la récupération des notes : {e}")
    return new_notes

# --- Tâche Discord pour notifier les nouvelles notes ---
@tasks.loop(minutes=5)
async def check_new_notes():
    channel = bot.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
    if channel:
        new_notes = await get_notes()
        for (matiere, titre), note in new_notes.items():
            await channel.send(f"Nouvelle note en **{matiere}** : {note['note']} / {note['total']} ({titre})")

# --- Lancer la tâche au démarrage ---
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    check_new_notes.start()

# --- Lancer le bot ---
bot.run(TOKEN)
