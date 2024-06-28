import os
import ssl
import urllib.request

import certifi
import mtranslate
import pytesseract
from flask import Flask, render_template, request, url_for
from gtts import gTTS
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'static/audio'

# Specify the path to Tesseract executable if necessary
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['AUDIO_FOLDER']):
    os.makedirs(app.config['AUDIO_FOLDER'])

# Set SSL context for urllib
context = ssl.create_default_context(cafile=certifi.where())
urllib.request.install_opener(urllib.request.build_opener(urllib.request.HTTPSHandler(context=context)))

@app.route('/')
def index():
    print("Rendering index page")
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        text = request.form.get('text')
        image = request.files.get('image')
        language = request.form.get('language')

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            text = extract_text_from_image(image_path)
            print(f"Extracted text from image: {text}")

        translated_text = translate_text(text, language)
        print(f"Translated text: {translated_text}")
        audio_file = create_audio(translated_text, language)
        print(f"Generated audio file: {audio_file}")

        return render_template('result.html', translated_text=translated_text, audio_file=audio_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred: " + str(e)

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def translate_text(text, language):
    return mtranslate.translate(text, language, "auto")

def create_audio(text, language):
    tts = gTTS(text=text, lang=language)
    audio_file = os.path.join(app.config['AUDIO_FOLDER'], 'translation.mp3')
    tts.save(audio_file)
    return 'audio/translation.mp3'

if __name__ == '__main__':
    app.run(debug=True)
