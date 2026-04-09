import streamlit as st
import pandas as pd

# ---------------------------
# CONFIG
# ---------------------------



st.set_page_config(
    page_title="Constructor de Comidas (BEDCA)",
    layout="wide"
)

# ---------------------------
# MODO COMPACTO PARA MÓVIL
# ---------------------------
st.markdown("""
<style>

    /* Reducir padding general */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }

    /* Sidebar más estrecho */
    [data-testid="stSidebar"] {
        width: 240px !important;
    }

    /* Tablas más compactas */
    table {
        font-size: 13px !important;
    }

    /* Inputs más pequeños */
    input, select, textarea {
        font-size: 14px !important;
        padding: 4px !important;
    }

    /* Botones más compactos */
    button[kind="primary"], button[kind="secondary"] {
        padding-top: 0.3rem !important;
        padding-bottom: 0.3rem !important;
        font-size: 14px !important;
    }

    /* Métricas más pequeñas */
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
    }

    /* Evitar scroll horizontal en móvil */
    .dataframe {
        overflow-x: auto;
    }

</style>
""", unsafe_allow_html=True)

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
    sorted(df["alimento"].unique())
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
    macro_cols = ["energia_kcal", "proteina_total", "carbohidratos", "grasa_total"]
    other_cols = [c for c in meal_df.columns if c not in macro_cols + ["alimento", "gramos"]]

    meal_df = meal_df[["alimento", "gramos"] + macro_cols + other_cols]

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

    # Ordenar nutrientes clave primero
    orden_preferido = [
        "energia_kcal", "proteina_total", "carbohidratos", "grasa_total",
        "fibra_dietetica_total", "sodio", "potasio"
    ]

    totals["orden"] = totals["Nutriente"].apply(
        lambda x: orden_preferido.index(x) if x in orden_preferido else 999
    )

    totals = totals.sort_values("orden").drop(columns="orden")

    # Redondear valores
    totals["Total"] = totals["Total"].round(2)
    st.subheader("📦 Resumen rápido")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)


    col1.metric("Kcal", f"{totals.loc[totals['Nutriente']=='energia_kcal','Total'].values[0]:.0f}")
    col2.metric("Proteína (g)", f"{totals.loc[totals['Nutriente']=='proteina_total','Total'].values[0]:.1f}")
    col3.metric("Carbs (g)", f"{totals.loc[totals['Nutriente']=='carbohidratos','Total'].values[0]:.1f}")
    col4.metric("Grasas (g)", f"{totals.loc[totals['Nutriente']=='grasa_total','Total'].values[0]:.1f}")
    st.dataframe(
        totals,
        use_container_width=True,
        hide_index=True
    )
    import altair as alt

    macro_totals = totals[totals["Nutriente"].isin(["energia_kcal", "proteina_total", "carbohidratos", "grasa_total"])]

    chart = alt.Chart(macro_totals).mark_bar().encode(
        x="Nutriente",
        y="Total",
        color="Nutriente"
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.info("Selecciona al menos un alimento.")

if "saved_meals" not in st.session_state:
    st.session_state.saved_meals = []

meal_name = st.text_input("Nombre de la comida", placeholder="Ej: Desayuno 9 abril")

if st.button("Guardar comida"):
    if meal_name.strip() == "":
        st.warning("Pon un nombre a la comida antes de guardarla")
    else:
        st.session_state.saved_meals.append({
            "nombre": meal_name,
            "alimentos": meal_df,
            "totales": totals
        })
        st.success(f"Comida '{meal_name}' guardada correctamente")

st.sidebar.header("📚 Comidas guardadas")

if st.session_state.saved_meals:
    selected_saved = st.sidebar.selectbox(
        "Selecciona una comida guardada",
        [meal["nombre"] for meal in st.session_state.saved_meals]
    )
    saved = next(m for m in st.session_state.saved_meals if m["nombre"] == selected_saved)
    st.subheader(f"📌 {selected_saved} – Alimentos")
    st.dataframe(saved["alimentos"], use_container_width=True, hide_index=True)

    st.subheader(f"📌 {selected_saved} – Totales")
    st.dataframe(saved["totales"], use_container_width=True, hide_index=True)

    col_del, col_but_nn= st.columns(2)
    col_dup, col_nn = st.columns(2)

    if col_del.button("🗑️ Borrar comida seleccionada"):
        st.session_state.saved_meals = [
            m for m in st.session_state.saved_meals if m["nombre"] != selected_saved
        ]
        st.success("Comida borrada")
    new_name = col_nn.text_input("Renombrar comida", value=selected_saved)

    if col_but_nn.button("Guardar nuevo nombre"):
        saved["nombre"] = new_name
        st.success("Nombre actualizado")
    
    if col_dup.button("📄 Duplicar comida"):
        copia = {
            "nombre": saved["nombre"] + " (copia)",
            "alimentos": saved["alimentos"].copy(),
            "totales": saved["totales"].copy()
        }
        st.session_state.saved_meals.append(copia)
        st.success("Comida duplicada")

    st.sidebar.header("📅 Totales del día")

    if st.sidebar.button("Calcular totales del día"):
        if not st.session_state.saved_meals:
            st.warning("No hay comidas guardadas para sumar")
        else:
            # Sumar todos los totales de todas las comidas
            df_totales = pd.concat([meal["totales"] for meal in st.session_state.saved_meals])
            totales_dia = df_totales.groupby("Nutriente")["Total"].sum().reset_index()

            # Mostrar resultado
            st.subheader("📊 Totales del día")
            st.dataframe(totales_dia, use_container_width=True, hide_index=True)
    csv = saved["alimentos"].to_csv(index=False, sep=';').encode("utf-8")
    st.download_button("⬇️ Descargar alimentos", csv, "comida.csv")


else:
    st.sidebar.info("No hay comidas guardadas todavía.")


