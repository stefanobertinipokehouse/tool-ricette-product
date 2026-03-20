import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import ast

# 1. Configurazione pagina
st.set_page_config(page_title="Tool ricette Team Prodotto", layout="wide")

# Banner Poke House in cima
try:
    st.image("PHLOGO_horizontal_classicshadow.png", width=350)
except:
    pass 

# Titolo
st.title("🍣 Tool ricette Team Prodotto")

# Descrizione con bersaglio
st.markdown("🎯 Lo scopo di questo tool è supportare il team nella creazione di nuove ricette, fungendo da raccoglitore strutturato (repository) per tutte le informazioni operative.")

# 2. Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lista nazioni con bandierine
lista_nazioni = [
    "🇮🇹 Italia", "🇬🇧 UK", "🇺🇸 USA", "🇷🇴 Romania", "🇦🇹 Austria", 
    "🇵🇹 Portogallo", "🇪🇸 Spagna", "🇧🇪 Belgio", "🇫🇷 Francia", "🇳🇱 Olanda"
]

# Creazione delle schede
tab_inserimento, tab_database = st.tabs(["➕ INPUT RICETTA", "🗄️ ARCHIVIO RICETTE"])

# ==========================================
# SCHEDA 1: INSERIMENTO SOP
# ==========================================
with tab_inserimento:
    
    # --- SEZIONE 1 RIORGANIZZATA ---
    st.header("1. Dettagli generali ricetta")
    
    # Riga 1: Nome prodotto, Country, Categoria
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        nome_ricetta = st.text_input("Nome Prodotto (es. Melanzane al Miso)*")
    with r1c2:
        country = st.selectbox("Country", lista_nazioni)
    with r1c3:
        categoria = st.selectbox("Categoria", ["Base", "Proteina", "Green", "Crispy", "Sides", "Salad bowl", "Poke bowl", "Altro"])
        
    # Riga 2: Formati Batch, Shelf-life (divisa in valore e unità)
    r2c1, r2c2, r2c3 = st.columns([2, 1, 1])
    with r2c1:
        batch_size = st.multiselect("Formati Batch (Seleziona uno o più)*", ["250 g", "500 g", "1 kg"])
    with r2c2:
        shelf_life_val = st.number_input("Shelf-life", min_value=1, step=1, value=4)
    with r2c3:
        shelf_life_unit = st.selectbox("Unità", ["ore", "giorni", "mesi"])

    st.markdown("---")
    
    # --- SEZIONE 2 RIORGANIZZATA ---
    st.header("2. Modalità di cottura")
    
    # Riga 1: Dispositivi di cottura
    attrezzatura_prep = st.selectbox("Dispositivi di cottura", ["Forno UNOX", "Piastra a induzione", "Air Fryer", "La ricetta non prevede cottura"])
    dati_cottura = {"macchinario": attrezzatura_prep}
    
    if attrezzatura_prep != "La ricetta non prevede cottura":
        
        if attrezzatura_prep == "Forno UNOX":
            # Riga 2: Gradi, Programma
            r_cottura2_c1, r_cottura2_c2 = st.columns(2)
            with r_cottura2_c1:
                gradi = st.number_input("Gradi (°C)", value=260, min_value=0, max_value=300, step=5)
            with r_cottura2_c2:
                programma_unox = st.selectbox("Programma", ["Steam", "Roast"])
                
            # Riga 3: Minuti, Secondi, Vapore
            r_cottura3_c1, r_cottura3_c2, r_cottura3_c3 = st.columns(3)
            with r_cottura3_c1:
                min_u = st.number_input("Minuti", key="u_m", min_value=0, value=5)
            with r_cottura3_c2:
                sec_u = st.number_input("Secondi", key="u_s", min_value=0, max_value=59)
            with r_cottura3_c3:
                vapore = st.selectbox("Vapore", ["0%", "20%", "40%", "60%", "80%", "100%"])
                
            dati_cottura.update({"impostazioni": f"{gradi}°C | Prog: {programma_unox} | {min_u}m e {sec_u}s, Vapore {vapore}"})
        
        elif attrezzatura_prep == "Piastra a induzione":
            # Riga 2: Potenza
            r_cottura2_c1, _ = st.columns(2)
            with r_cottura2_c1:
                potenza = st.number_input("Potenza (W)", value=1500, step=100)
                
            # Riga 3: Minuti, Secondi
            r_cottura3_c1, r_cottura3_c2 = st.columns(2)
            with r_cottura3_c1:
                min_p = st.number_input("Minuti", key="p_m", min_value=0, value=9)
            with r_cottura3_c2:
                sec_p = st.number_input("Secondi", key="p_s", min_value=0, max_value=59)
                
            dati_cottura.update({"impostazioni": f"Potenza {potenza}W, {min_p}m e {sec_p}s"})
        
        elif attrezzatura_prep == "Air Fryer":
            # Riga 2: Modalità
            r_cottura2_c1, _ = st.columns(2)
            with r_cottura2_c1:
                mod = st.selectbox("Modalità", ["max crisp 240°", "Roast 190°", "reheat 170°"])
                
            # Riga 3: Minuti, Secondi
            r_cottura3_c1, r_cottura3_c2 = st.columns(2)
            with r_cottura3_c1:
                min_a = st.number_input("Minuti", key="a_m", min_value=0)
            with r_cottura3_c2:
                sec_a = st.number_input("Secondi", key="a_s", min_value=0, max_value=59)
                
            dati_cottura.update({"impostazioni": f"{mod}, {min_a}m e {sec_a}s"})
    else:
        dati_cottura.update({"impostazioni": "Nessuna cottura"})

    st.markdown("---")
    
    # --- SEZIONE 3 RIORGANIZZATA ---
    st.header("3. Attrezzature e Stoccaggio")
    
    # Logica per mostrare le teglie corrette in base alla cottura
    options_cottura = []
    if attrezzatura_prep == "Forno UNOX":
        options_cottura = ["Black Tray", "Net Tray"]
    elif attrezzatura_prep == "Piastra a induzione":
        options_cottura = ["Padella", "Pentola"]
    elif attrezzatura_prep == "Air Fryer":
        options_cottura = ["Carta siliconata", "Cestello in silicone"]
    
    # Riga 1: Equipments cottura, Equipments necessari
    r_att1_c1, r_att1_c2 = st.columns(2)
    with r_att1_c1:
        if attrezzatura_prep != "La ricetta non prevede cottura":
            teglie_padelle = st.multiselect("Equipments per la cottura", options_cottura)
        else:
            teglie_padelle = [] 
    with r_att1_c2:
        strumenti = st.multiselect("Equipments necessari", [
            "Tagliere Verde", "Tagliere Rosso", "Tagliere bianco", "Tagliere blu", 
            "Coltello Santoku", "Coltello piccolo (manico verde e rosso)", 
            "Bowl in acciaio", "Colino", "Termometro", "Cucchiaio/Spatola"
        ])
    
    # Riga 2: DPI, Stoccaggio
    r_att2_c1, r_att2_c2 = st.columns(2)
    with r_att2_c1:
        dpi = st.multiselect("DPI Richiesti", ["Guanti Anticalore", "Guanto Anti-taglio", "Nessuno"])
    with r_att2_c2:
        stoccaggio = st.selectbox("Stoccaggio / Destinazione", ["WARM 80 gradi", "Frigo 0-4°C", "Abbattitore"])
        
    # Riga 3: Contenitore in Linea, Equipment linea
    r_att3_c1, r_att3_c2 = st.columns(2)
    with r_att3_c1:
        contenitore_linea = st.selectbox("Contenitore in Linea", ["GN 1/9", "GN 1/6", "GN 1/4", "GN 1/3", "GN 1/2", "GN 1/1"])
    with r_att3_c2:
        equipment_linea = st.multiselect("Equipment per la linea", [
            "Pinza Insalata", "Pinza", "scoop 1/8", "scoop 1/20", "scoop 1/36", "scoop 1/50", "teaspoon"
        ])

    st.markdown("---")
    st.header("4. Ingredienti e Grammature")
    
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
    st.header("5. Procedimento")
    procedimento = st.text_area("Scrivi i passaggi operativi numerati (es. 1. Riscaldare la padella... 2. Aggiungere...)", height=200)

    if st.button("💾 Salva SOP in Google Sheets", type="primary"):
        if not nome_ricetta or not batch_size:
            st.error("⚠️ Compila i campi obbligatori (Nome Ricetta e Formati Batch) prima di salvare!")
        elif ing_editati.empty:
            st.error("⚠️ Inserisci almeno un ingrediente nella tabella!")
        else:
            nuova_ricetta = pd.DataFrame([{
                "ID": datetime.now().strftime("%Y%m%d%H%M%S"),
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Nome Prodotto": nome_ricetta,
                "Country": country,
                "Categoria": categoria,
                "Batch Supportati": ", ".join(batch_size),
                "Shelf-life": f"{shelf_life_val} {shelf_life_unit}",
                "Modalità Cottura": f"{dati_cottura['macchinario']} - {dati_cottura['impostazioni']}",
                "Equipments Prep e Cottura": ", ".join(teglie_padelle + strumenti),
                "Equipment Linea": ", ".join(equipment_linea),
                "DPI": ", ".join(dpi),
                "Stoccaggio": f"{contenitore_linea} in {stoccaggio}",
                "Ingredienti": str(ing_editati.to_dict(orient="records")), 
                "Procedimento": procedimento
            }])
            
            try:
                dati_esistenti = conn.read(ttl=0).dropna(how="all")
                
                if dati_esistenti.empty or "ID" not in dati_esistenti.columns:
                    dati_aggiornati = nuova_ricetta
                else:
                    dati_aggiornati = pd.concat([dati_esistenti, nuova_ricetta], ignore_index=True)
                
                conn.update(data=dati_aggiornati)
                st.success(f"✅ SOP per '{nome_ricetta}' salvata con successo su Google Sheets!")
                st.balloons()
            except Exception as e:
                st.error(f"Errore di salvataggio su Google Sheets: {e}")

# ==========================================
# SCHEDA 2: DATABASE E CANCELLAZIONE
# ==========================================
with tab_database:
    st.header("🗂️ Archivio Ricette in Cloud")
    
    try:
        # Leggiamo i dati freschi
        dati_salvati = conn.read(ttl=0).dropna(how="all")
        
        if not dati_salvati.empty and "ID" in dati_salvati.columns:
            
            # --- ZONA FILTRI E RICERCA ---
            st.subheader("🔍 Ricerca e Filtra")
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                search_term = st.text_input("Cerca ricetta per nome...")
            
            with col_f2:
                paesi_disponibili = ["Tutti i paesi"] + lista_nazioni
                country_selezionato = st.selectbox("Filtra per Country:", paesi_disponibili)
            
            with col_f3:
                categorie_disponibili = ["Tutte le categorie"] + sorted(dati_salvati["Categoria"].dropna().unique().tolist())
                categoria_selezionata = st.selectbox("Filtra per Categoria:", categorie_disponibili)
            
            # Filtriamo il DataFrame
            df_filtrato = dati_salvati.copy()
            if search_term:
                df_filtrato = df_filtrato[df_filtrato["Nome Prodotto"].str.contains(search_term, case=False, na=False)]
            if country_selezionato != "Tutti i paesi":
                df_filtrato = df_filtrato[df_filtrato["Country"] == country_selezionato]
            if categoria_selezionata != "Tutte le categorie":
                df_filtrato = df_filtrato[df_filtrato["Categoria"] == categoria_selezionata]
            
            st.markdown("---")
            
            # --- TABELLA RIASSUNTIVA INTERATTIVA ---
            if df_filtrato.empty:
                st.warning("Nessuna ricetta trovata con questi filtri. Prova a cambiare i parametri di ricerca.")
            else:
                st.subheader(f"📑 Elenco Ricette Trovate ({len(df_filtrato)})")
                
                st.info("💡 Spunta la casella a sinistra della riga per visionare la scheda dettagliata della ricetta!")
                
                tabella_riassunto = df_filtrato[["Nome Prodotto", "Country", "Categoria", "Modalità Cottura", "Data"]].copy()
                
                selezione = st.dataframe(
                    tabella_riassunto, 
                    use_container_width=True, 
                    hide_index=True,
                    on_select="rerun",           
                    selection_mode="single-row"  
                )
                
                righe_selezionate = selezione.selection.rows
                
                if len(righe_selezionate) > 0:
                    indice_riga = righe_selezionate[0]
                    row_data = df_filtrato.iloc[indice_riga]
                    id_selezionato = row_data["ID"]
                    
                    # --- VISUALIZZAZIONE SCHEDA RICETTA ---
                    st.markdown("---")
                    st.subheader(f"📖 Scheda SOP: {row_data.get('Nome Prodotto', '')}")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Country", row_data.get("Country", "N/A"))
                    c2.metric("Categoria", row_data.get("Categoria", "N/A"))
                    c3.metric("Batch Supportati", row_data.get("Batch Supportati", "N/A"))
                    c4.metric("Shelf-life", row_data.get("Shelf-life", "N/A"))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"**🔥 Modalità Cottura:**<br>{row_data.get('Modalità Cottura', 'N/A')}", unsafe_allow_html=True)
                        st.markdown(f"**🔪 Equipments Prep/Cottura:**<br>{row_data.get('Equipments Prep e Cottura', 'N/A')}", unsafe_allow_html=True)
                        st.markdown(f"**🥄 Equipment Linea:**<br>{row_data.get('Equipment Linea', 'N/A')}", unsafe_allow_html=True)
                    with col_info2:
                        st.markdown(f"**🧤 DPI Richiesti:**<br>{row_data.get('DPI', 'N/A')}", unsafe_allow_html=True)
                        st.markdown(f"**📦 Stoccaggio:**<br>{row_data.get('Stoccaggio', 'N/A')}", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown("#### 🛒 Ingredienti")
                    try:
                        ing_list = ast.literal_eval(row_data.get("Ingredienti", "[]"))
                        if ing_list:
                            st.dataframe(pd.DataFrame(ing_list), use_container_width=True)
                        else:
                            st.info("Nessun ingrediente registrato.")
                    except:
                        st.write(row_data.get("Ingredienti", ""))
                    
                    st.markdown("#### 📋 Procedimento Operativo")
                    st.info(row_data.get("Procedimento", "Nessun procedimento inserito."))
                    
                    st.markdown("---")
                    
                    with st.expander("🚨 Zona Pericolo: Elimina questa SOP"):
                        st.warning("Attenzione: l'eliminazione è irreversibile e rimuoverà la ricetta da Google Sheets.")
                        conferma = st.checkbox("Confermo di voler eliminare questa ricetta")
                        
                        if conferma:
                            if st.button("🗑️ Procedi con l'eliminazione", type="primary"):
                                db_aggiornato = dati_salvati[dati_salvati["ID"].astype(str) != str(id_selezionato)]
                                conn.update(data=db_aggiornato)
                                st.success("✅ SOP eliminata con successo dal cloud!")
                                st.rerun()

        else:
            st.info("L'archivio su Google Sheets è vuoto. Vai nella prima scheda e salva la tua prima SOP!")
            
    except Exception as e:
        st.warning("⚠️ Non riesco a connettermi al foglio. Assicurati che i 'Secrets' siano configurati correttamente.")
