import os
import tempfile
import zipfile
import random
import datetime
import pyttsx3
import gradio as gr
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
from dotenv import load_dotenv
 

# ======= Doomify Offline – Version Template (100 % locale) =======
# Contexte : Doomify transforme n'importe quelle situation banale
# en un véritable scénario apocalyptique façon film catastrophe,
# avec texte dramatique, image spectaculaire et audio de fin du monde.

# ==== 1) Génération de texte dynamique via OpenAI ====
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ai=OpenAI(api_key=OPENAI_API_KEY)
def generate_text(action: str) -> str:
    """
    Utilise OpenAI pour générer un scénario apocalyptique dramatique
    à partir d'une action banale.
    """
    prompt = (
        "Transforme la phrase suivante en un court scénario dramatique et apocalyptique, "
        "façon blockbuster catastrophe, en français, avec 2 à 3 phrases maximum. Ne mets pas les astérix sur les phrases et meme le titre. Phrase : "
        f"« {action} »"
    )
    response = ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un narrateur de films catastrophes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()

# ==== 2) Génération d’image via Pollinations API ====

def generate_image(story: str) -> Image.Image:
    """
    Génère une image via OpenAI (DALL·E) à partir d’un résumé du scénario Doomify.
    """
    # Extraire la première phrase du scénario
    main_phrase = story.split(".")[0].replace("Doomify présente :", "").strip()
    # Prompt dédié, évite les mots interdits
    image_prompt = (
        f"Affiche de film catastrophe, dramatique, cinématographique, "
        f"scène urbaine chaotique, atmosphère de tension, "
        f"personnages en situation de crise, lumière dramatique. "
        f"un titre accrocheur, "
        f"Inspiration blockbuster. "
        f"Sujet : {main_phrase}"
    )
    response = ai.images.generate(
        model="dall-e-3",   # ou "dall-e-2" si tu veux tester
        prompt=image_prompt,
        n=1,
        size="1024x1024"
    )
    img_url = response.data[0].url
    img_resp = requests.get(img_url)
    img_resp.raise_for_status()
    img = Image.open(BytesIO(img_resp.content)).convert("RGB")
    return img



# ==== 3) Génération audio offline (pyttsx3) ====

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 140)

def generate_audio(text: str) -> str:
    """
    Crée un fichier audio local TTS pour dramatique « fin du monde ».
    """
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "audio.mp3")
    tts_engine.save_to_file(text, path)
    tts_engine.runAndWait()
    return path

# ==== 4) Fonction principale doomify ====

def doomify(prompt: str):
    """
    Orchestration : génère texte, image et audio, puis package en ZIP.
    """
    story = generate_text(prompt)
    img = generate_image(story)
    audio_path = generate_audio(story)

    tmp = tempfile.mkdtemp()
    txt_path = os.path.join(tmp, "scenario.txt")
    img_path = os.path.join(tmp, "image.png")
    zip_path = os.path.join(tmp, "doomify_result.zip")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(story)
    img.save(img_path)

    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(txt_path, arcname="scenario.txt")
        z.write(img_path, arcname="image.png")
        z.write(audio_path, arcname="audio.mp3")

    return story, img, audio_path, zip_path

# ==== 5) Interface Gradio ====

interface = gr.Interface(
    fn=doomify,
    inputs=[gr.Textbox(label="Phrase banale", placeholder="Ex: Je vais sortir les poubelles")],
    outputs=[
        gr.Textbox(label="Scénario apocalyptique"),
        gr.Image(label="Affiche " ),
        gr.Audio(label="Son dramatique"),
        gr.File(label="Télécharger le ZIP")
    ],
    title="Doomify – L’IA catastrophiste multimodale",
    description=(
        "Entrez une action banale, et Doomify transforme votre quotidien en mini-blockbuster apocalyptique : "
        "texte dramatique, affiche cinématographique, et un son de lecture."
    )
)

if __name__ == "__main__":
    interface.launch()
