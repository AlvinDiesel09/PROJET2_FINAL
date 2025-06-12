import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import base64

st.set_page_config(page_title="Projet 2", layout="wide")

with st.sidebar:
    st.image("pictures/Logo Team Rocket.png", width=170)

st.markdown(
    "<h1 style='text-align: center; font-size: 60px;'>🎞️     <em>PROJET 2 </h1></em>",
    unsafe_allow_html=True,
)
st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")


# Chemin vers la vidéo
video_path = "pictures\Design sans titre.mp4"

# Lecture et encodage en base64
with open(video_path, "rb") as f:
    video_bytes = f.read()
    encoded = base64.b64encode(video_bytes).decode()

# HTML pour lecture automatique et boucle
video_html = f"""
<video autoplay loop muted playsinline style="width: 85%; border-radius: 12px;">
    <source src="data:video/mp4;base64,{encoded}" type="video/mp4">
    Votre navigateur ne supporte pas la lecture vidéo.
</video>
"""

# Affichage dans Streamlit
st.markdown(video_html, unsafe_allow_html=True)




