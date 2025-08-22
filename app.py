import streamlit as st
from generator import Answers

st.title("🎬 Storyboard Generator")
st.write("Crea un storyboard de video a partir de tus ideas")

objetivo = st.selectbox("¿Cuál es tu objetivo?", ["ventas", "leads", "branding", "lanzamiento", "test"])
publico = st.text_input("¿Quién es tu público?")
estetica = st.selectbox("Estética del video", ["cinematografica", "iphone", "urbana", "minimal", "deportiva", "cozy"])
duracion = st.slider("Duración (segundos)", 10, 30, 15)

if st.button("Generar storyboard"):
    answer = Answers(
        objetivo=objetivo,
        publico=publico,
        estetica=estetica,
        duracion=duracion
    )
    st.success(f"🎬 Generado storyboard para: {answer.dict()}")

