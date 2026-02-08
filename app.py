import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("🚗 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")
st.warning("⚠️ Nota: Il Bollo Auto è sempre ESCLUSO dal calcolo.")

# --- FUNZIONE MATEMATICA RATA ---
def calcola_rata_fin(capitale, tasso_annuo, mesi):
    if tasso_annuo <= 0:
        return capitale / mesi if mesi > 0 else 0
    tasso_mensile = (tasso_annuo / 100) / 12
    rata = capitale * (tasso_mensile * (1 + tasso_mensile)**mesi) / ((1 + tasso_mensile)**mesi - 1)
    return rata

# --- SIDEBAR: CONFIGURAZIONE FISCALE ---
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

# --- LOGICHE FISCALI PRECISE ---
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

# --- FUNZIONE CALCOLO BENEFICI (ARCHITETTURA CORRETTA) ---
def calcola_benefici_pro(imp_servizi, imp_veicolo, interessi_passivi=0):
    # 1. Recupero IVA
    iva_veicolo = imp_veicolo * 0.22
    iva_servizi = imp_servizi * 0.22
    iva_recuperata = (iva_veicolo + iva_servizi) * iva_det
    iva_indetraibile = (iva_veicolo + iva_servizi) - iva_recuperata
    
    # 2. Deducibilità (TUIR)
    # Il limite si applica solo al veicolo + la sua
