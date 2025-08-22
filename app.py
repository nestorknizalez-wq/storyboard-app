import streamlit as st
import json, csv, io
from generator import Answers, generate_storyboard

st.set_page_config(page_title="Storyboard Generator", page_icon="🎬", layout="centered")

st.markdown("# 🎬 Storyboard Generator")
st.caption("Crea un storyboard de video a partir de tus ideas")

with st.form("brief"):
    objetivo = st.selectbox("¿Cuál es tu objetivo?", ["ventas","leads","branding","lanzamiento","test"])
    publico = st.text_input("¿Quién es tu público?", "Fisioterapeutas y Fitness")
    estetica = st.selectbox("Estética del video", ["cinematografica","iphone","urbana","minimal","deportiva","cozy"])
    duracion = st.slider("Duración (segundos)", min_value=15, max_value=20, step=3, value=15)
    movimiento = st.selectbox("Movimiento de cámara", ["estatico","paneos","tracking","dinamico"])
    dialogo = st.selectbox("¿Gente hablando?", ["no_visual","vo","on_cam"])
    ritmo = st.selectbox("Ritmo narrativo", ["clasico","producto","emocional","ugc"])
    luz = st.selectbox("Iluminación", ["calida","natural","fria","golden","interior"])
    restricciones = st.text_input("Restricciones/Notas (opcional)", "Evitar rojos saturados")
    cta = st.text_input("CTA", "Reserva tu plaza hoy")
    idea = st.text_area("Describe la idea en 1–2 líneas", "Anuncio vertical 15s para KOULNESS mostrando alivio muscular y rutina post-entreno.")
    submitted = st.form_submit_button("Generar storyboard")

if submitted:
    a = Answers(
        objetivo=objetivo, publico=publico, estetica=estetica,
        duracion=duracion, movimiento=movimiento, dialogo=dialogo,
        ritmo=ritmo, luz=luz, restricciones=restricciones, cta=cta
    )
    data = generate_storyboard(idea, a)
    st.success(f"🎬 Generado storyboard para: {{'objetivo': '{objetivo}', 'publico': '{publico}', 'estetica': '{estetica}', 'duracion': {duracion}}}")
    st.markdown("## Resumen")
    st.write(data["resumen"])

    st.markdown("## Shot list (planos)")
    for f in data["frames"]:
        with st.expander(f'P{f["orden"]} · {f["beat"]} · {f["duracion_s"]}s'):
            st.write(f'**Cámara:** {f["camara"]["plano"]}, {f["camara"]["lente"]}, mov.: {f["camara"]["movimiento"]}')
            st.write(f'**Acción:** {f["accion"]}')
            st.write(f'**Transición:** {f["transicion"]}')
            st.code(f['prompt_mj'], language="text")
            st.code(json.dumps(f['prompt_video'], ensure_ascii=False, indent=2), language="json")

    # Botones de descarga
    st.markdown("## Descargas")
    json_bytes = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    st.download_button("⬇️ Descargar JSON", data=json_bytes, file_name="storyboard.json", mime="application/json")

    # CSV simple
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["orden","beat","duracion_s","plano","lente","mov","accion","transicion","prompt_mj","prompt_video_json"])
    for f in data["frames"]:
        writer.writerow([f["orden"], f["beat"], f["duracion_s"], f["camara"]["plano"], f["camara"]["lente"],
                         f["camara"]["movimiento"], f["accion"], f["transicion"],
                         f["prompt_mj"], json.dumps(f["prompt_video"], ensure_ascii=False)])
    st.download_button("⬇️ Descargar CSV", data=output.getvalue(), file_name="shotlist.csv", mime="text/csv")

else:
    st.info("Rellena el brief y pulsa **Generar storyboard**. Aquí verás el shot list y podrás descargar los prompts.")
