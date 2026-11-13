import base64
from pypdf import PdfReader
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def extract_text_from_pdf(uploaded_file) -> str:
    """Extrae todo el texto legible de un archivo PDF."""
    reader = PdfReader(uploaded_file)
    extracted = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted += page_text + "\n"
    return extracted.strip()

def analyze_image_with_moondream(image_bytes, user_question: str) -> str:
    """
    Motor Visual exclusivo: Moondream responde directamente al usuario sobre la imagen cargada.
    """
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    
    prompt = (
        f"Responde en ESPAÑOL de forma clara y directa a la siguiente consulta sobre esta imagen: "
        f"'{user_question}'. Describe con precisión los elementos, textos o detalles que correspondan."
    )

    response = client.chat.completions.create(
        model="moondream",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ]
    )
    return response.choices[0].message.content