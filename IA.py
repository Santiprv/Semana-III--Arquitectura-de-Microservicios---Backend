import os
from flask import Flask, request, jsonify 
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv  

load_dotenv()


app = Flask(__name__) 


CORS(app)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


@app.route('/')
def index():
    return jsonify({"status": "API activa", "mensaje": "Bienvenido al backend de Gemini"}), 200

@app.route('/preguntar', methods=['POST']) 
def preguntar():
    pregunta = request.form.get("pregunta", "")
    archivo = request.files.get("archivo")
    
    contents = [pregunta]
    
    try:
        if archivo:
            file_data = archivo.read()
            mime_type = archivo.content_type
            contents.append(types.Part.from_bytes(data=file_data, mime_type=mime_type))

        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=contents
        )

        uso = response.usage_metadata
        return jsonify({
            "respuesta": response.text,
            "tokens": {
                "entrada": uso.prompt_token_count,
                "salida": uso.candidates_token_count,
                "total": uso.total_token_count
            }
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"respuesta": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)