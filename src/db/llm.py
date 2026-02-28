import string
import secrets
from groq import Groq
import os


class AiModel:

    def __init__(self):
        self._api_key = os.getenv("GROQ_API_KEY")


    def buscar_en_dataset(self):
        with open('rockyou.txt', 'r', encoding='latin-1') as f:
            for linea in f:
                if self.password == linea.strip():
                    return True
        return False

    # comentario
    def transform_password(self):
        entropia_cont = []
        for clave in self.password:
            if clave in string.ascii_lowercase:
                entropia_cont.append(secrets.choice(string.ascii_lowercase))
            elif clave in string.ascii_uppercase:
                entropia_cont.append(secrets.choice(string.ascii_uppercase))
            elif clave in string.digits :
                entropia_cont.append(secrets.choice(string.digits))  
            elif clave in string.punctuation:
                entropia_cont.append(secrets.choice(string.punctuation))
        return ''.join(entropia_cont)

    def consultar_seguridad(self, password):
        #la entropia calculada por el modelo es la entropia en fuerza bruta, puede diferir de la entropía real de dos contraseñas semejantes
        client = Groq(api_key=self._api_key)
        system_prompt = f'Eres un analizador técnico de seguridad. Responde SOLO con datos, sin introducciones ni consejos éticos.AL final da que la contraseña usada para calcular la entropia no es la propia del usuario si no una de sus mismas caracteristicas'
        user_prompt = f"""Analiza la siguiente clave técnica: '{password}'
        
        Responde estrictamente con este formato:
        - NIVEL DE SEGURIDAD: (1-10)
        - ENTROPÍA POR FUERZA BRUTA: (en bits)
        - TIEMPO DE CRACKEO POR FUERZA BRUTA: (Estimado por fuerza bruta con hardware actual en horas)
        """
        chat_completion = client.chat.completions.create(
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
         model="llama-3.3-70b-versatile", 
        temperature=0.3
        )
        return chat_completion.choices[0].message.content
