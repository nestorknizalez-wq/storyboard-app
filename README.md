
# Storyboard Generator — MVP (Streamlit)

Este MVP sí **muestra** el storyboard en pantalla y permite **descargar** JSON y CSV.
No guarda nada en servidores ni envía por email; todo se genera al vuelo.

## Cómo ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy rápido
1) Sube esta carpeta a un repo en GitHub.
2) Abre https://share.streamlit.io (Streamlit Community Cloud), conecta el repo y elige `app.py`.
3) La app quedará pública.

## Archivos
- `app.py`: interfaz Streamlit en español, muestra la shot list y los prompts.
- `generator.py`: lógica para generar los planos y prompts.
- `requirements.txt`: dependencias mínimas.
