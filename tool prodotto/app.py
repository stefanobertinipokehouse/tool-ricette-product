import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. Configurazione della pagina
st.set_page_config(page_title="Ricette Product team", layout="wide")

st.title("📝 Ricette Product team")

# Creiamo due schede separate (Tabs)
tab_inserimento, tab_database = st.tabs(["➕ Inserisci Nuova Ricetta", "🗄️ Visualizza Database"])

# ==========================================
# SCHEDA 1: INSERIMENTO RICETTA
# ==========================================
with tab_inserimento:
    st.markdown("Compila i campi sottostanti. I menu si adatteranno in base alle tue scelte.")

    st.header("1. Informazioni Generali")
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_ricetta = st.text_input("Nome Ricetta*")
        categoria = st.selectbox("Categoria", ["Base", "Proteina", "Green", "Crispy", "Sides", "Salad bowl", "Poke bowl"])
    with col2:
        porzionatura = st.selectbox("Seleziona porzionatura", ["1kg", "500g", "250g"])
    with col3:
        col_sl_num, col_sl_unit = st.columns([2, 1])
        with col_sl_num:
            shelf_life_val = st.number_input("Shelf-life", min_value=1, step=1)
        with col_sl_unit:
            shelf_life_unit = st.selectbox("Unità", ["giorni", "ore"])

    st.header("2. Attrezzature e Cottura")
    attrezzatura_prep = st.selectbox("Attrezzature Prep", ["Forno UNOX", "Piastra a induzione", "Air Fryer"])
    dati_cottura = {"macchinario": attrezzatura_prep}

    st.markdown(f"**Impostazioni per: {attrezzatura_prep}**")
    col_c1, col_c2, col_c3 = st.columns(3)

    if attrezzatura_prep == "Forno UNOX":
        with col_c1:
            gradi = st.number_input("Gradi (°C)", min_value=0, max_value=300, step=5, value=180)
        with col_c2:
            col_min, col_sec = st.columns(2)
            with col_min:
                minuti = st.number_input("Minuti", min_value=0, step=1, key="unox_min")
            with col_sec:
                secondi = st.number_input("Secondi", min_value=0, max_value=59, step=1, key="unox_sec")
        with col_c3:
            vapore = st.selectbox("Livello di vapore", ["0%", "10%", "20%", "40%", "60%", "80%", "100%"])
        dati_cottura.update({"gradi": gradi, "minuti": minuti, "secondi": secondi, "vapore": vapore})

    elif attrezzatura_prep == "Piastra a induzione":
        with col_c1:
            potenza = st.number_input("Potenza (W)", min_value=0, max_value=2500, step=100, value=1000)
        with col_c2:
            col_min, col_sec = st.columns(2)
            with col_min:
                minuti = st.number_input("Minuti", min_value=0, step=1, key="ind_min")
            with col_sec:
                secondi = st.number_input("Secondi", min_value=0, max_value=59, step=1, key="ind_sec")
        dati_cottura.update({"potenza_W": potenza, "minuti": minuti, "secondi": secondi})

    elif attrezzatura_prep == "Air Fryer":
        with col_c1:
            modalita_air = st.selectbox("Modalità e Temperatura", ["max crisp 240°", "Roast 190°", "reheat 170°"])
        with col_c2:
            col_min, col_sec = st.columns(2)
            with col_min:
                minuti = st.number_input("Minuti", min_value=0, step=1, key="air_min")
            with col_sec:
                secondi = st.number_input("Secondi", min_value=0, max_value=59, step=1, key="air_sec")
        dati_cottura.update({"modalita": modalita_air, "minuti": minuti, "secondi": secondi})

    st.markdown("---")
    equipment_linea = st.multiselect("Equipment in linea", 
                            ["Pinza Insalata", "Pinza", "scoop 1/8", "scoop 1/20", "scoop 1/36", "scoop 1/50", "teaspoon"])

    st.header("3. Ingredienti")
    st.markdown("Aggiungi le righe necessarie per gli ingredienti cliccando sulla tabella.")

    if 'df_ingredienti' not in st.session_state:
        st.session_state.df_ingredienti = pd.DataFrame(columns=["Ingrediente", "Quantità", "U.M.", "Lavorazione"])

    ingredienti_editati = st.data_editor(
        st.session_state.df_ingredienti,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Ingrediente": st.column_config.TextColumn("Ingrediente / Materia Prima", required=True),
            "Quantità": st.column_config.NumberColumn("Quantità", min_value=0.0, format="%.2f"),
            "U.M.": st.column_config.SelectboxColumn("U.M.", options=["g", "kg", "ml", "L", "pz"]),
            "Lavorazione": st.column_config.TextColumn("Lavorazione (es. tritato, a cubetti)")
        }
    )

    st.header("4. Procedimento / Workflow")
    procedimento = st.text_area("Descrivi i passaggi numerati della preparazione...", height=150)

    if st.button("💾 Salva Ricetta", type="primary"):
        if not nome_ricetta:
            st.error("Attenzione: Inserisci il nome della ricetta prima di salvare!")
        else:
            dati_ricetta = {
                "Data Inserimento": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Nome Ricetta": nome_ricetta,
                "Categoria": categoria,
                "Porzionatura": porzionatura,
                "Shelf-life": f"{shelf_life_val} {shelf_life_unit}",
                "Cottura": dati_cottura,
                "Equipment Linea": equipment_linea,
                "Ingredienti": ingredienti_editati.to_dict(orient="records"),
                "Procedimento": procedimento
            }

            file_path = "database_ricette.json"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    db = json.load(f)
            else:
                db = []
            
            db.append(dati_ricetta)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4, ensure_ascii=False)
                
            st.success(f"✅ Ricetta '{nome_ricetta}' salvata nel database!")
            st.balloons()

# ==========================================
# SCHEDA 2: VISUALIZZAZIONE DATABASE
# ==========================================
with tab_database:
    st.header("🗂️ Archivio Ricette Salvate")
    file_path = "database_ricette.json"
    
    if os.path.exists(file_path):
        # Leggiamo il file JSON
        with open(file_path, "r", encoding="utf-8") as f:
            dati_salvati = json.load(f)
            
        if len(dati_salvati) > 0:
            # Trasformiamo i dati in un formato tabellare (DataFrame)
            df_database = pd.DataFrame(dati_salvati)
            
            # Mostriamo la tabella interattiva
            st.dataframe(df_database, use_container_width=True)
            
            # Pulsante per scaricare in formato CSV (apribile con Excel)
            csv = df_database.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Scarica Database in Excel/CSV",
                data=csv,
                file_name='database_ricette_export.csv',
                mime='text/csv',
            )
        else:
            st.info("Il database è ancora vuoto. Inserisci la prima ricetta!")
    else:
        st.warning("Nessun database trovato. Salva una ricetta per crearlo.")