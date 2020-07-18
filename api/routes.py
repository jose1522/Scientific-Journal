from flask import Blueprint, request
from googletrans import Translator
import json

api = Blueprint('api', '__name__')

@api.route('/')
def index():
    return "Hello World"

@api.route('/translate')
def translate():
    sourceText = request.args.get('sourceText')
    targetLanguage = request.args.get('targetLanguage')
    translator = Translator()
    translation = translator.translate(sourceText,dest=targetLanguage)
    print(translation.text)
    return translation.text