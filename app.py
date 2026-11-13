import streamlit as st
from procesadores import extract_text_from_pdf, analyze_image_with_moondream
from agente import run_agent_turn

st.set_page_config(page_title="Chatbot Multimodal", layout="wide")
st.title("Chatbot Multimodal")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Entradas Multimodales")
    if st.button("Reiniciar conversación"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("**Editor de texto libre:**")
    editor_text = st.text_area("Escribe o pega texto de trabajo:", height=150)
    
    st.markdown("**Carga de archivos:**")
    uploaded_file = st.file_uploader("Sube un archivo PDF o imagen JPG:", type=["pdf", "jpg", "jpeg"])

for msg in st.session_state.messages:
    if msg["role"] in ["user", "assistant"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg.get("display", msg["content"]))

user_query = st.chat_input("Escribe tu consulta o instrucción...")

if user_query:
    clean_query = user_query.strip()
    is_image = uploaded_file is not None and uploaded_file.name.lower().endswith((".jpg", ".jpeg"))
    file_bytes = uploaded_file.read() if uploaded_file is not None else None

    with st.chat_message("user"):
        st.markdown(clean_query)
        if is_image and file_bytes:
            st.image(file_bytes, caption=uploaded_file.name, width=280)

    if is_image:
        st.session_state.messages.append({"role": "user", "content": f"[Imagen '{uploaded_file.name}'] {clean_query}"})
        with st.chat_message("assistant"):
            with st.spinner("Moondream analizando imagen..."):
                answer = analyze_image_with_moondream(file_bytes, user_question=clean_query)
                st.caption("Respondido por: **Moondream (Motor Visual)**")
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    else:
        context_blocks = []
        if editor_text.strip():
            context_blocks.append(f"[Texto en Editor]:\n{editor_text.strip()}")
        
        if uploaded_file is not None and uploaded_file.name.lower().endswith(".pdf"):
            uploaded_file.seek(0)
            pdf_text = extract_text_from_pdf(uploaded_file)
            context_blocks.append(f"[Contenido extraído del PDF '{uploaded_file.name}']:\n{pdf_text[:3500]}")

        prompt_completo = ""
        if context_blocks:
            prompt_completo = "\n\n".join(context_blocks) + "\n\n"
        prompt_completo += f"[Instrucción del usuario]: {clean_query}"

        st.session_state.messages.append({
            "role": "user",
            "content": prompt_completo,
            "display": clean_query
        })

        with st.chat_message("assistant"):
            with st.spinner("Qwen 2.5 procesando..."):
                history_copy = list(st.session_state.messages)
                answer, _ = run_agent_turn(history_copy)
                st.caption("Respondido por: **Qwen 2.5 3B (Motor Agéntico)**")

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})