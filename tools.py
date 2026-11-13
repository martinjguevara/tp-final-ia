import sys
import io

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Ejecuta código en Python y retorna stdout. Útil para cálculos matemáticos, algoritmos o procesamiento de datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Código Python que se ejecutará."}
                },
                "required": ["code"],
            },
        },
    },
]

def execute_python_code(code: str) -> str:
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    try:
        exec(code, {})
        output = redirected_output.getvalue()
        return output.strip() if output else "Código ejecutado con éxito (sin salida estándar)."
    except Exception as e:
        return f"Error de ejecución: {str(e)}"
    finally:
        sys.stdout = old_stdout

def execute_tool(name: str, arguments: dict) -> str:
    if name == "run_python":
        return execute_python_code(arguments.get("code", ""))
    return "Herramienta no reconocida."