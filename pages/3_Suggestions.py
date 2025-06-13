import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches
import difflib
from pathlib import Path


# Titre principal
st.markdown(
    "<h1 style='text-align: center;font-size: 60px'>👀<em> On mate quoi ?</h1></em>",
    unsafe_allow_html=True,
)
dir = Path.cwd()
# Chargement des données
main_df = pd.read_parquet(dir/"data"/"main_df.parquet")
people_df = pd.read_parquet(dir/"data"/"people_df.parquet")

# Préparation des images
BASE_POSTER_URL = "https://image.tmdb.org/t/p/w300"
main_df["poster_path"] = main_df["poster_path"].apply(
    lambda p: BASE_POSTER_URL + p if pd.notna(p) and not p.startswith("http") else p
)

# Préparation TF-IDF vectorisation
main_df["text_features"] = (
    main_df["primaryTitle"].fillna("") + " " +
    main_df["genres"].fillna("") + " " +
    main_df["overview"].fillna("")
)

vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(main_df["text_features"])
similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Moteur de recommandation
def suggere_films_semantique(titre_input, min_year, min_rating, top_n=10):
    if not titre_input.strip():
        return pd.DataFrame(), titre_input

    # Vectoriser l'entrée utilisateur
    input_vector = vectorizer.transform([titre_input])
    
    # Calculer la similarité entre l'entrée et tous les films
    scores = cosine_similarity(input_vector, tfidf_matrix)[0]
    
    # Récupérer les indices des meilleurs scores
    similar_indices = scores.argsort()[::-1][:top_n + 1]  # +1 au cas où le 1er est une correspondance exacte

    # Construire le DataFrame de résultats
    df_similaires = main_df.iloc[similar_indices].copy()

    # Supprimer les doublons exacts si présents
    df_similaires = df_similaires[df_similaires["primaryTitle"].str.lower() != titre_input.lower()]

    # Appliquer les filtres
    df_similaires = df_similaires[
        (df_similaires["vote_average"] >= min_rating) &
        (df_similaires["startYear"] >= min_year)
    ]

    matched_title = main_df.iloc[scores.argmax()]["primaryTitle"]

    return df_similaires.head(top_n), matched_title

# Etat session
if "favoris" not in st.session_state:
    st.session_state["favoris"] = []

# Filtres
st.header("💡 Suggestion de film")
film_input = st.text_input("Quel film avez-vous aimé ?", placeholder="Ex: Inception")
min_year = st.slider("Année minimale", 1960, 2025, 1992)
min_rating = st.slider("Note minimale", 0.0, 10.0, 5.0, 0.5)

# Suggestions de films
if film_input:
    suggestions, matched_title = suggere_films_semantique(film_input, min_year, min_rating)
    st.markdown(
        f"<h3 style='text-align: center;'>📽️ Suggestions basées sur : <em>{matched_title}</em></h3>",
        unsafe_allow_html=True,
    )

    if suggestions.empty:
        st.warning("Aucune suggestion ne correspond aux filtres.")
    else:
        st.markdown(
            "<div style='display: flex; flex-wrap: wrap; justify-content: center; gap: 40px;'>",
            unsafe_allow_html=True,
        )
        for i, row in suggestions.iterrows():
            is_fav = row["primaryTitle"] in st.session_state["favoris"]
            with st.container():
                col = st.columns([1])[0]
                with col:
                    st.markdown(f"<div style='width:220px; text-align:center;'>", unsafe_allow_html=True)
                    st.image(row["poster_path"], width=200)
                    st.markdown(
                        f"**{row['primaryTitle']}**<br>⭐ {row['vote_average']} • 📅 {row['startYear']}<br>🎞️ {row['genres']}",
                        unsafe_allow_html=True,
                    )
                    st.caption(row.get("overview", ""))
                    fav_button = st.button(
                        "❤️ Ajouter aux favoris" if not is_fav else "✅ Déjà ajouté",
                        key=f"fav_{i}",
                    )
                    if fav_button and not is_fav:
                        st.session_state["favoris"].append(row["primaryTitle"])
                    st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)

with st.sidebar:
    st.image(dir/"pictures"/"Logo Team Rocket.png", width=170)

# Favoris
with st.sidebar:
    st.subheader("❤️ Mes favoris")
    if not st.session_state["favoris"]:
        st.info("Aucun film favori encore ajouté.")
    else:
        for fav in st.session_state["favoris"]:
            st.markdown(f"- {fav}")
    
    # Ajout d'une ligne de séparation
    st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)

######################################################
