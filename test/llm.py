import string
import secrets
from groq import Groq
import os

class AiModel:

    def __init__(self):
        self._api_key = os.getenv("API_KEY")  # ← Pon tu clave aquí

    def buscar_en_dataset(self, password: str) -> bool:
        """Busca la contraseña en el diccionario rockyou.txt."""
        try:
            with open('rockyou.txt', 'r', encoding='latin-1') as f:
                for linea in f:
                    if password == linea.strip():
                        return True
        except FileNotFoundError:
            print("⚠️ rockyou.txt no encontrado, omitiendo verificación de diccionario.")
        return False

    def transform_password(self, password: str) -> str:
        """Genera una contraseña con las mismas características de tipo de caracteres."""
        entropia_cont = []
        for clave in password:
            if clave in string.ascii_lowercase:
                entropia_cont.append(secrets.choice(string.ascii_lowercase))
            elif clave in string.ascii_uppercase:
                entropia_cont.append(secrets.choice(string.ascii_uppercase))
            elif clave in string.digits:
                entropia_cont.append(secrets.choice(string.digits))
            elif clave in string.punctuation:
                entropia_cont.append(secrets.choice(string.punctuation))
        return ''.join(entropia_cont)

    def consultar_seguridad(self, password: str) -> str:
        """Consulta a Groq (LLaMA) el análisis de seguridad de la contraseña."""
        # Se analiza una contraseña transformada, no la real del usuario
        password_analizar = self.transform_password(password)

        client = Groq(api_key=self._api_key)

        system_prompt = (
            "Eres un analizador técnico de seguridad  "
            "Responde SOLO con datos, sin introducciones ni consejos éticos. "
            
        )
        user_prompt = f"""Analiza la siguiente clave técnica: '{password_analizar}'

Responde estrictamente con este formato:
- NIVEL DE SEGURIDAD: (1-10)
- ENTROPÍA POR FUERZA BRUTA: (en bits)
- TIEMPO DE CRACKEO POR FUERZA BRUTA: (Estimado por fuerza bruta con hardware actual en horas)
- BREVE EXPLICACION DE PORQUE NO ES SEGURA: (INSTRUCCIÓN CRÍTICA: Si el NIVEL DE SEGURIDAD es 6,7, 8, 9 o 10, DEJA ESTE CAMPO TOTALMENTE VACÍO. Solo si es menor a 6, explica brevemente qué mejorar)
"""
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        return chat_completion.choices[0].message.content
