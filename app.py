import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("🚗 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")
st.warning("⚠️ Nota: Il Bollo Auto è sempre ESCLUSO dal calcolo.")

# --- SIDEBAR: CONFIGURAZIONE FISCALE E DURATA ---
st.sidebar.header("⚙️ Configurazione")
categoria = st.sidebar.selectbox("Tipologia Cliente", [
    "Privato / Forfettario",
    "Ditta Individuale / Professionista Ordinario",
    "Società di Capitali (SRL, SPA)",
    "Agente di Commercio"
])

# Sotto-tipologia per aziende
uso_aziendale = "Standard"
if categoria == "Società di Capitali (SRL, SPA)":
    uso_aziendale = st.sidebar.selectbox("Tipologia di Utilizzo", [
        "Uso Promiscuo (Assegnata a dipendente)",
        "Uso non esclusivamente strumentale (Auto flotta)"
    ])

durata_mesi = st.sidebar.select_slider("Durata Contratto (Mesi)", options=[24, 36, 48, 60], value=48)
aliquota_user = st.sidebar.slider("Tua Aliquota Fiscale (%)", 0, 50, 24 if "Società" in categoria else 35)

# --- LOGICHE FISCALI (DETRAZIONE E DEDUZIONE) ---
if categoria == "Privato / Forfettario":
    ded, iva_det, limite = 0.0, 0.0, 0
elif categoria == "Agente di Commercio":
    ded, iva_det, limite = 0.80, 1.0, 25822
elif categoria == "Società di Capitali (SRL, SPA)":
    if "Promiscuo" in uso_aziendale:
        ded, iva_det, limite = 0.70, 0.40, 0 # Deducibilità senza limite di costo
    else:
        ded, iva_det, limite = 0.20, 0.40, 18075
else: # Professionista Ordinario / Ditta Individuale
    ded, iva_det, limite = 0.20, 0.40, 18075

aliq = aliquota_user / 100
anni = durata_mesi / 12

# --- FUNZIONI DI CALCOLO ---
def calcola_benefici(imponibile_servizi, imponibile_veicolo):
    iva_pagata = (imponibile_servizi + imponibile_veicolo) * 0.22
    iva_rec = iva_pagata * iva_det
    iva_indetraibile = iva_pagata - iva_rec
    # La quota indetraibile dell'IVA diventa un costo deducibile
    base_ded = imponibile_servizi + min(imponibile_veicolo, limite if limite > 0 else 9999999) + iva_indetraibile
    tasse_rec = (base_ded * ded) * aliq
    return iva_rec, tasse_rec

# --- INPUT DATI ---
col_a, col_l, col_n = st.columns(3)

with col_a:
    st.subheader("💰 Acquisto")
    prezzo_imp_a = st.number_input("Prezzo Auto (Imp. €)", value=35000, key="prezzo_a")
    anticipo_a = st.number_input("Anticipo Versato (€)", value=5000)
    st.write("**Spese Annue (Imp.):**")
    rca_a = st.number_input("RCA (€)", value=500)
    if_a = st.number_input("Incendio e Furto (€)", value=600)
    manut_a = st.number_input("Manutenzione (€)", value=400)
    interessi_a = st.number_input("Interessi Finanziamento (€)", value=1200)

with col_l:
    st.subheader("📈 Leasing")
    prezzo_imp_l = st.number_input("Prezzo Listino (Imp. €)", value=35000, key="prezzo_l")
    anticipo_l = st.number_input("Primo Canone (Imp. €)", value=6000)
    rata_l = st.number_input("Canone Mensile (Imp. €)", value=400)
    perc_riscatto = st.number_input("Riscatto Finale (%)", value=1.0, step=0.5)
    riscatto_l = prezzo_imp_l * (perc_riscatto / 100)
    st.write("**Servizi Esclusi (
