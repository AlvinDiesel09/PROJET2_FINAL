import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

# 📈 Configuration de la page
st.set_page_config(
    page_title="Analyse Cinématographique", page_icon="🎬", layout="wide"
)


dir = Path.cwd()
with st.sidebar:
    st.image(dir/"pictures"/"Logo Team Rocket.png", width=170)
st.write(
    "<h1 style='text-align: center; font-size: 60px;'>🎬<em> Dashboard d'Analyse Cinématographique</h1></em>",
    unsafe_allow_html=True,
)
#st.title("🎬 Dashboard d'Analyse Cinématographique")
st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")
main_df = pd.read_parquet(dir/"data"/"main_df.parquet")
people_df = pd.read_parquet(dir/"data"/"people_df.parquet")

main_df["startYear"] = (main_df["startYear"]).astype(int)


with st.sidebar:
    years = st.slider(
        "Sélectionner une période",
        1925,
        2025,
        (1980, 2010),
    )

    filtered_main = main_df.query("startYear >= @years[0] & startYear <= @years[1]")


###################  indicateur 1 ###################
def most_present_genres(df):
    df["genre"] = df["genres"].str.split(",").copy()
    exploded = df.explode("genre")
    genre_counts = exploded["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

    fig = px.histogram(
        genre_counts.sort_values(by="count", ascending=False).head(10),
        y="count",
        x="genre",
        color="genre",
        hover_name="genre",
        log_x=False,
        title=f"Répartition des genres de {years[0]} à {years[1]}",
    )
    fig.update_layout(
        xaxis_title="Genres",
        yaxis_title="Nombre de films",
    )
    return fig


st.plotly_chart(most_present_genres(filtered_main))


###################  indicateur 2 ###################
df = pd.merge(filtered_main, people_df, on="tconst", how="left")

# Supprimer tous les tconst de films d'animation
animation_tconsts = df[df["genres"].str.contains("animation", case=False, na=False)][
    "tconst"
].unique()
df = df[~df["tconst"].isin(animation_tconsts)].copy()

# Explosion des cast
df["cast"] = df["cast_list"]
df = df.explode("cast").copy()

# Filtrer acteurs et actrices
df = df[df["category"].isin(["actress", "actor"])]

# Compter les occurrences
cast_counts = df["cast"].value_counts().reset_index()
cast_counts.columns = ["cast", "count"]

# Plot
fig = px.histogram(
    cast_counts.head(20),
    y="count",
    x="cast",
    color="cast",
    hover_name="cast",
    log_x=False,
    title=f"Top 20 acteurs/actrices les plus présents de {years[0]} à {years[1]}",
)
fig.update_layout(
    xaxis_title="Acteurs/Actrices",
    yaxis_title="Nombre de films",
)
st.plotly_chart(fig)


###################  indicateur 3 ###################


df["duree"] = df["runtimeMinutes"].astype(float)
df = df.groupby("release_date")["duree"].mean().reset_index()

fig = px.line(
    df,
    x="release_date",
    y="duree",
    title=f"Évolution de la durée moyenne des films de {years[0]} à {years[1]}",
)
fig.update_layout(
    xaxis_title="Année",
    yaxis_title="Durée moyenne (minutes)",
)
st.plotly_chart(fig)


###################  indicateur 4 ###################
# Étape 1 : S'assurer que 'runtimeMinutes' est bien numérique
main_df["duree"] = pd.to_numeric(main_df["runtimeMinutes"], errors="coerce")

# Étape 2 : Extraire l'année depuis 'release_date' si ce n'est pas déjà fait
main_df["year"] = main_df["release_date"].dt.year

# Étape 3 : Calculer la décennie
main_df["decade"] = (main_df["year"] // 10) * 10

# Étape 4 : Calculer la moyenne de durée par décennie
df_decade = main_df.groupby("decade")["duree"].mean().reset_index()

# Étape 5 : Création du graphique
fig = px.line(
    df_decade,
    x="decade",
    y="duree",
    title=f"Évolution de la durée moyenne des films par décennie",
    markers=True,
    labels={"decade": "Décennie", "duree": "Durée moyenne (minutes)"},
)

fig.update_layout(
    xaxis_title="Décennie",
    yaxis_title="Durée moyenne (minutes)",
    xaxis=dict(tickmode="linear", dtick=10),  # une graduation tous les 10 ans
)

# Étape 6 : Affichage dans Streamlit
st.plotly_chart(fig)

###################  indicateur 5 ###################
col1, col2 = st.columns(2)
with col1:
    # Étape 1 : S'assurer que 'runtimeMinutes' est bien numérique
    filtered_main["duree"] = pd.to_numeric(
        filtered_main["runtimeMinutes"], errors="coerce"
    )
    # Étape 2 : Extraire l'année depuis 'release_date' si ce n'est pas déjà fait
    filtered_main["year"] = filtered_main["release_date"].dt.year

    # Étape 3 : Calculer la décennie
    filtered_main["decade"] = (filtered_main["year"] // 10) * 10

    # Étape 4 : Calculer la moyenne de durée par décennie
    df_decade_movie = filtered_main.groupby("decade")["tconst"].count().reset_index()

    fig = px.bar(
        df_decade_movie,
        x="decade",
        y="tconst",
        title=f"Évolution du nombre de films par décennie",
        labels={"decade": "Décennie", "tconst": "Nombre de films"},
    )
    fig.update_traces(marker_color="#05ec24")
    # Étape 5 : Mise en forme
    fig.update_layout(
        xaxis_title="Décennie",
        yaxis_title="Nombre de films",
        xaxis=dict(tickmode="linear", dtick=10),
    )

    # Étape 6 : Affichage dans Streamlit
    st.plotly_chart(fig)

with col2:
    # Étape 1 : S'assurer que 'runtimeMinutes' est bien numérique
    filtered_main["duree"] = pd.to_numeric(
        filtered_main["runtimeMinutes"], errors="coerce"
    )
    # Étape 2 : Extraire l'année depuis 'release_date' si ce n'est pas déjà fait
    filtered_main["year"] = filtered_main["release_date"].dt.year

    # Étape 4 : Calculer la moyenne de durée par décennie
    df_year_movie = filtered_main.groupby("year")["tconst"].count().reset_index()

    fig2 = px.bar(
        df_year_movie,
        x="year",
        y="tconst",
        title=f"Évolution du nombre de films par année",
        labels={"year": "Année", "tconst": "Nombre de films"},
    )
    fig2.update_traces(marker_color="#af1fb4")
    # Étape 5 : Mise en forme
    fig2.update_layout(
        xaxis_title="Année",
        yaxis_title="Nombre de films",
        xaxis=dict(tickmode="linear", dtick=5),
    )

    # Étape 6 : Affichage dans Streamlit
    st.plotly_chart(fig2)