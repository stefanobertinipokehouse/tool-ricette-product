import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Configurazione pagina
st.set_page_config(page_title="Tool ricette Team Prodotto", layout="wide")
st.title("🍣 Tool ricette Team Prodotto")
st.markdown("Lo scopo di questo tool è supportare il team nella creazione di nuove ricette e tradurle in SOP strutturate e standardizzate.")

# 2. Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Creazione delle schede
tab_inserimento, tab_database = st.tabs(["➕ Crea Nuova SOP", "🗄️ Archivio Ricette"])

# ==========================================
# SCHEDA 1: INSERIMENTO SOP
# ==========================================
with tab_inserimento:
    
    st.header("1. Identikit Prodotto")
    col1, col2, col3 = st.columns(3)
    with col1:
        nome_ricetta = st.text_input("Nome Prodotto (es. Melanzane al Miso)*")
        categoria = st.selectbox("Categoria", ["Base", "Proteina", "Green", "Crispy", "Sides", "Salad bowl", "Poke bowl", "Altro"])
    with col2:
        batch_size = st.multiselect("Formati Batch (Seleziona uno o più)*", ["250 g", "500 g", "1 kg"])
    with col3:
        c_n, c_u = st.columns([2, 1])
        shelf_life_val = c_n.number_input("Shelf-life", min_value=1, step=1, value=4)
        shelf_life_unit = c_u.selectbox("Unità", ["ore", "giorni", "mesi"])

    st.markdown("---")
    st.header("2. Modalità di cottura")
    
    attrezzatura_prep = st.selectbox("Dispositivi di cottura", ["Forno UNOX", "Piastra a induzione", "Air Fryer", "La ricetta non prevede cottura"])
    dati_cottura = {"macchinario": attrezzatura_prep}
    
    if attrezzatura_prep != "La ricetta non prevede cottura":
        col_c1, col_c2, col_c3 = st.columns(3)
        
        if attrezzatura_prep == "Forno UNOX":
            with col_c1:
                gradi = st.number_input("Gradi (°C)", value=260, min_value=0, max_value=300, step=5)
                programma_unox = st.selectbox("Programma", ["Steam", "Roast"])
            with col_c2:
                min_u = st.number_input("Minuti", key="u_m", min_value=0, value=5)
                vapore = st.selectbox("Vapore", ["0%", "20%", "40%", "60%", "80%", "100%"])
            with col_c3:
                sec_u = st.number_input("Secondi", key="u_s", min_value=0, max_value=59)
                
            dati_cottura.update({"impostazioni": f"{gradi}°C | Prog: {programma_unox} | {min_u}m e {sec_u}s, Vapore {vapore}"})
        
        elif attrezzatura_prep == "Piastra a induzione":
            with col_c1:
                potenza = st.number_input("Potenza (W)", value=1500, step=100)
            with col_c2:
                min_p = st.number_input("Minuti", key="p_m", min_value=0, value=9)
            with col_c3:
                sec_p = st.number_input("Secondi", key="p_s", min_value=0, max_value=59)
                
            dati_cottura.update({"impostazioni": f"Potenza {potenza}W, {min_p}m e {sec_p}s"})
        
        elif attrezzatura_prep == "Air Fryer":
            with col_c1:
                mod = st.selectbox("Modalità", ["max crisp 240°", "Roast 190°", "reheat 170°"])
            with col_c2:
                min_a = st.number_input("Minuti", key="a_m", min_value=0)
            with col_c3:
                sec_a = st.number_input("Secondi", key="a_s", min_value=0, max_value=59)
                
            dati_cottura.update({"impostazioni": f"{mod}, {min_a}m e {sec_a}s"})
    else:
        dati_cottura.update({"impostazioni": "Nessuna cottura"})

    st.markdown("---")
    st.header("3. Attrezzature e Stoccaggio")
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        options_cottura = []
        if attrezzatura_prep == "Forno UNOX":
            options_cottura = ["Black Tray", "Net Tray"]
        elif attrezzatura_prep == "Piastra a induzione":
            options_cottura = ["Padella", "Pentola"]
        elif attrezzatura_prep == "Air Fryer":
            options_cottura = ["Carta siliconata", "Cestello in silicone"]
            
        if attrezzatura_prep != "La ricetta non prevede cottura":
            teglie_padelle = st.multiselect("Equipments per la cottura", options_cottura)
        else:
            teglie_padelle = [] 
            
        strumenti = st.multiselect("Equipments necessari", [
            "Tagliere Verde", "Tagliere Rosso", "Tagliere bianco", "Tagliere blu", 
            "Coltello Santoku", "Coltello piccolo (manico verde)", "Coltello piccolo (manico rosso)", 
            "Bowl in acciaio", "Colino", "Termometro", "Cucchiaio/Spatola"
        ])
        
    with col_a2:
        contenitore_gn = st.selectbox("Contenitore Finale", ["GN 1/9", "GN 1/6", "GN 1/4", "GN 1/3", "GN 1/2", "GN 1/1"])
        dpi = st.multiselect("DPI Richiesti", ["Guanti Anticalore", "Guanto Anti-taglio", "Nessuno"])
        stoccaggio = st.selectbox("Stoccaggio / Destinazione", ["WARM 80 gradi", "Frigo 0-4°C", "Abbattitore"])
        equipment_linea = st.multiselect("Equipment per la linea", [
            "Pinza Insalata", "Pinza", "scoop 1/8", "scoop 1/20", "scoop 1/36", "scoop 1/50", "teaspoon"
        ])

    st.markdown("---")
    st.header("4. Ingredienti (Scalabili)")
    
    if not batch_size:
        st.warning("⚠️ Seleziona almeno un 'Formato Batch' nella Sezione 1 per far apparire la tabella degli ingredienti.")
        ing_editati = pd.DataFrame()
    else:
        st.markdown("Inserisci le quantità associate ai batch selezionati.")
        
        color_map = {
            "250 g": "🟢 250 g",
            "500 g": "🟡 500 g",
            "1 kg": "🔴 1 kg"
        }
        
        colonne_base = ["Ingrediente"]
        colonne_dinamiche = [f"Q.tà {color_map[b]}" for b in batch_size]
        colonne_finali = colonne_base + colonne_dinamiche + ["U.M."]
        
        if 'df_ing' not in st.session_state or list(st.session_state.df_ing.columns) != colonne_finali:
            st.session_state.df_ing = pd.DataFrame(columns=colonne_finali)
            
        col_config = {
            "Ingrediente": st.column_config.TextColumn("Materia Prima", required=True),
            "U.M.": st.column_config.SelectboxColumn("Unità", options=["g", "kg", "ml", "L", "pz", "busta"])
        }
        for col in colonne_dinamiche:
            col_config[col] = st.column_config.NumberColumn(col, min_value=0.0, format="%.2f")

        ing_editati = st.data_editor(
            st.session_state.df_ing, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config=col_config
        )

    st.markdown("---")
    st.header("5. Procedimento (Workflow)")
    procedimento = st.text_area("Scrivi i passaggi operativi numerati (es. 1. Riscaldare la padella... 2. Aggiungere...)", height=200)

    if st.button("💾 Salva SOP in Google Sheets", type="primary"):
        if not nome_ricetta or not batch_size:
            st.error("⚠️ Compila i campi obbligatori (Nome Ricetta e Formati Batch) prima di salvare!")
        elif ing_editati.empty:
            st.error("⚠️ Inserisci almeno un ingrediente nella tabella!")
        else:
            # Creiamo la riga da salvare
            nuova_ricetta = pd.DataFrame([{
                "ID": datetime.now().strftime("%Y%m%d%H%M%S"),
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome Prodotto": nome_ricetta,
                "Categoria": categoria,
                "Batch Supportati": ", ".join(batch_size),
                "Shelf-life": f"{shelf_life_val} {shelf_life_unit}",
                "Modalità Cottura": f"{dati_cottura['macchinario']} - {dati_cottura['impostazioni']}",
                "Equipments Prep e Cottura": ", ".join(teglie_padelle + strumenti),
                "Equipment Linea": ", ".join(equipment_linea),
                "DPI": ", ".join(dpi),
                "Stoccaggio": f"{contenitore_gn} in {stoccaggio}",
                "Ingredienti": str(ing_editati.to_dict(orient="records")), # Google Sheets richiede testo piatto
                "Procedimento": procedimento
            }])
            
            try:
                # Leggiamo i dati attuali dal foglio
                dati_esistenti = conn.read().dropna(how="all")
                
                # Se il foglio è vuoto o non ha ancora la colonna ID
                if dati_esistenti.empty or "ID" not in dati_esistenti.columns:
                    dati_aggiornati = nuova_ricetta
                else:
                    dati_aggiornati = pd.concat([dati_esistenti, nuova_ricetta], ignore_index=True)
                
                # Aggiorniamo il file su Google Sheets
                conn.update(data=dati_aggiornati)
                
                st.success(f"✅ SOP per '{nome_ricetta}' salvata con successo su Google Sheets!")
                st.balloons()
            except Exception as e:
                st.error(f"Errore di salvataggio su Google Sheets: {e}")

# ==========================================
# SCHEDA 2: DATABASE E CANCELLAZIONE
# ==========================================
with tab_database:
    st.header("🗂️ Archivio SOP in Cloud")
    
    try:
        # Leggiamo i dati da Google Sheets (togliendo le righe vuote)
        dati_salvati = conn.read().dropna(how="all")
        
        if not dati_salvati.empty and "ID" in dati_salvati.columns:
            # Mostriamo la tabella (nascondendo ID e stringhe complesse per pulizia visiva)
            colonne_da_nascondere = ["ID", "Ingredienti"] if "Ingredienti" in dati_salvati.columns else ["ID"]
            st.dataframe(dati_salvati.drop(columns=colonne_da_nascondere), use_container_width=True)
            
            st.markdown("---")
            st.subheader("🗑️ Elimina una SOP dal Cloud")
            
            # Generiamo la lista per il menu a tendina
            nomi_sop = []
            for index, row in dati_salvati.iterrows():
                nomi_sop.append(f"{row['Nome Prodotto']} (del {row['Data']}) - ID: {row['ID']}")
            
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                sop_da_eliminare = st.selectbox("Seleziona la SOP da eliminare:", nomi_sop)
                
            with col_del2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌ Conferma Eliminazione", type="primary"):
                    # Troviamo l'ID da cancellare
                    id_da_cancellare = sop_da_eliminare.split("ID: ")[-1]
                    
                    # Filtriamo il dataframe scartando l'ID selezionato
                    db_aggiornato = dati_salvati[dati_salvati["ID"].astype(str) != id_da_cancellare]
                    
                    # Aggiorniamo Google Sheets
                    conn.update(data=db_aggiornato)
                    
                    st.success("✅ SOP eliminata con successo dal cloud!")
                    st.rerun()
        else:
            st.info("L'archivio su Google Sheets è vuoto. Inserisci la prima SOP!")
            
    except Exception as e:
        st.warning("⚠️ Non riesco a connettermi al foglio. Assicurati di aver incollato il link corretto nel file secrets.toml e di aver reso il foglio accessibile.")