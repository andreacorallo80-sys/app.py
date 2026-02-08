import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("🚗 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")

# --- FUNZIONE MATEMATICA RATA ---
def calcola_rata(capitale, tasso_annuo, mesi):
    if tasso_annuo <= 0:
        return capitale / mesi if mesi > 0 else 0
    tasso_mensile = (tasso_annuo / 100) / 12
    rata = capitale * (tasso_mensile * (1 + tasso_mensile)**mesi) / ((1 + tasso_mensile)**mesi - 1)
    return rata

# --- SIDEBAR: CONFIGURAZIONE PROFILO ---
st.sidebar.header("⚙️ Configurazione Profilo")
categoria = st.sidebar.selectbox("Tipologia Cliente", [
    "Privato / Forfettario",
    "Ditta Individuale / Professionista Ordinario",
    "Società di Capitali (SRL, SPA)",
    "Agente di Commercio"
])

uso_specifico = "Standard"
if categoria in ["Società di Capitali (SRL, SPA)", "Ditta Individuale / Professionista Ordinario"]:
    opzioni_uso = ["Uso non esclusivamente strumentale (Auto flotta)", "Uso Strumentale (Scuola guida, Noleggio, ecc.)"]
    if categoria == "Società di Capitali (SRL, SPA)":
        opzioni_uso.insert(0, "Uso Promiscuo (Assegnata a dipendente)")
    uso_specifico = st.sidebar.selectbox("Tipologia di Utilizzo", opzioni_uso)

durata_mesi = st.sidebar.select_slider("Durata Contratto (Mesi)", options=[24, 36, 48, 60], value=48)
aliquota_user = st.sidebar.slider("Tua Aliquota Fiscale media (%)", 0, 50, 24 if "Società" in categoria else 35)

# --- LOGICHE FISCALI ---
ded, iva_det, limite = 0.20, 0.40, 18075.99
if categoria == "Privato / Forfettario":
    ded, iva_det, limite = 0.0, 0.0, 0
elif categoria == "Agente di Commercio":
    ded, iva_det, limite = 0.80, 1.0, 25822.84
elif "Uso Strumentale" in uso_specifico:
    ded, iva_det, limite = 1.0, 1.0, 0 
elif "Uso Promiscuo" in uso_specifico:
    ded, iva_det, limite = 0.70, 0.40, 0 

aliq = aliquota_user / 100
anni = durata_mesi / 12

def calcola_benefici(imponibile_servizi, imponibile_veicolo):
    iva_pagata = (imponibile_servizi + imponibile_veicolo) * 0.22
    iva_rec = iva_pagata * iva_det
    iva_indetraibile = iva_pagata - iva_rec
    quota_veicolo_deducibile = min(imponibile_veicolo, limite) if limite > 0 else imponibile_veicolo
    base_ded_totale = imponibile_servizi + quota_veicolo_deducibile + iva_indetraibile
    tasse_rec = (base_ded_totale * ded) * aliq
    return iva_rec, tasse_rec

# --- INPUT DATI ---
col_a, col_l, col_n = st.columns(3)

with col_a:
    st.subheader("💰 Acquisto")
    prezzo_imp_a = st.number_input("Prezzo Auto (Imp. €)", value=35000, key="prezzo_a")
    tipo_acquisto = st.radio("Modalità", ["Contanti", "Finanziamento"])
    
    interessi_finanziamento = 0.0
    if tipo_acquisto == "Finanziamento":
        anticipo_f = st.number_input("Anticipo / Maxirata Iniziale (€)", value=5000)
        tan = st.number_input("TAN (%)", value=5.9)
        capitale_finanziato = prezzo_imp_a - anticipo_f
        if capitale_finanziato > 0:
            rata_f = calcola_rata(capitale_finanziato, tan, durata_mesi)
            interessi_finanziamento = (rata_f * durata_mesi) - capitale_finanziato
            st.info(f"Rata Mensile: € {rata_f:.2f}")
        else:
            st.warning("L'anticipo copre l'intero valore.")

    st.write("**Spese Annue Gestione:**")
    rca_a = st.number_input("RCA (€)", value=500)
    if_a = st.number_input("Incendio e Furto (€)", value=600)
