import streamlit as st
import pandas as pd

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="Constructor de Comidas (BEDCA)",
    layout="wide"
)

st.title("🍽️ Constructor de Comidas - BEDCA")

# ---------------------------
# CARGAR DATOS
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("bedca_alimentos_limpio.csv", sep=",")
    return df

df = load_data()

# Detectar columnas numéricas (nutrientes)
nutrientes = [
    c for c in df.columns
    if c not in ["food_id", "alimento"] and df[c].dtype != "object"
]

# ---------------------------
# SELECCIÓN DE ALIMENTOS
# ---------------------------
st.sidebar.header("🥕 Selecciona alimentos")

selected_foods = st.sidebar.multiselect(
    "Alimentos",
    df["alimento"].unique()
)

# ---------------------------
# CONSTRUIR COMIDA
# ---------------------------
if selected_foods:

    st.subheader("📋 Cantidades por alimento")

    meal_data = []

    for food in selected_foods:
        grams = st.number_input(
            f"{food} (g)",
            min_value=0.0,
            value=100.0,
            step=10.0
        )

        row = df[df["alimento"] == food].iloc[0]

        # Crear entrada con todos los nutrientes
        food_entry = {"alimento": food, "gramos": grams}

        for n in nutrientes:
            food_entry[n] = row[n] * grams / 100

        meal_data.append(food_entry)

    meal_df = pd.DataFrame(meal_data)

    # ---------------------------
    # RESULTADOS POR ALIMENTO
    # ---------------------------
    st.subheader("🥗 Nutrientes por alimento")
    st.dataframe(meal_df, use_container_width=True, hide_index=True)

    # ---------------------------
    # TOTALES DE LA COMIDA
    # ---------------------------
    st.subheader("📊 Totales de la comida")

    totals = meal_df[nutrientes].sum().reset_index()
    totals.columns = ["Nutriente", "Total"]

    st.dataframe(totals, use_container_width=True, hide_index=True)

else:
    st.info("Selecciona al menos un alimento.")
