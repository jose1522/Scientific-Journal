from flask import Blueprint

api = Blueprint('api', '__name__')

@api.route('/')
def index():
<<<<<<< Updated upstream
    return "Hello World"
=======
    return "Hello World"

@api.route('/translate')
def translate():
    sourceText = request.args.get('sourceText')
    targetLanguage = request.args.get('targetLanguage')
    translator = Translator()
    translation = translator.translate(sourceText,dest=targetLanguage)
    translation = {"text":translation.text}
    return json.dumps(translation)
>>>>>>> Stashed changes
