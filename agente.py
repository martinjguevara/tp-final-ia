import json
from openai import OpenAI
from tools import TOOLS_SCHEMA, execute_tool

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL_NAME = "qwen2.5:3b"

SYSTEM_INSTRUCTION = {
    "role": "system",
    "content": (
        "Eres un asistente virtual y agente inteligente local. Responde SIEMPRE en ESPAÑOL.\n"
        "1. Usa el contenido provisto en '[Texto en Editor]' o '[Contenido extraído del PDF]' para responder con precisión.\n"
        "2. NO crees ni guardes archivos en disco.\n"
        "3. Solo debes invocar la herramienta 'run_python' si el usuario pide expresamente cálculos matemáticos, "
        "algoritmos o procesamiento numérico en Python."
    ),
}

def run_agent_turn(messages: list) -> tuple[str, list]:
    clean_messages = [m for m in messages if m.get("role") != "system"]
    clean_messages.insert(0, SYSTEM_INSTRUCTION)

    tool_logs = []
    
    while True:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=clean_messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content, tool_logs

        clean_messages.append(msg)
        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            try:
                func_args = json.loads(tool_call.function.arguments)
            except Exception:
                func_args = {}

            tool_logs.append(f"🔧 **Herramienta invocada:** `{func_name}` | **Argumentos:** `{func_args}`")
            result = execute_tool(func_name, func_args)
            tool_logs.append(f"**Resultado obtenido:** `{result}`")

            clean_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": str(result),
            })