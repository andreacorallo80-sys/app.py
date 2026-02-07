import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Configuratore Auto Pro", layout="wide")

st.title("🚗 Calcolatore Convenienza Auto 3.0")
st.markdown("### Confronto Reale: Acquisto vs Leasing vs Noleggio")

# --- SIDEBAR: PROFILO FISCALE ---
st.sidebar.header("1. Profilo Fiscale")
categoria = st.sidebar.selectbox("Tipologia Azienda/Professionista", [
    "Privato / Forfettario",
    "Ditta Individuale / SNC / SAS",
    "Società di Capitali (SRL, SPA, COOP)",
    "Agente di Commercio",
    "Azienda - Uso Strumentale"
])

uso = st.sidebar.radio("Uso del Veicolo", ["Promiscuo", "Esclusivamente Strumentale"])

# Logica parametri fiscali
if categoria == "Privato / Forfettario":
    ded, iva_det, aliquota, limite = 0.0, 0.0, 0.0, 0
elif categoria == "Agente di Commercio":
    ded, iva_det, aliquota, limite = 0.80, 1.0, 0.35, 25822
elif categoria == "Società di Capitali (SRL, SPA, COOP)":
    ded = 0.70 if uso == "Promiscuo" else 1.0
    iva_det = 0.40 if uso == "Promiscuo" else 1.0
    aliquota, limite = 0.24, 0
else: # Ditta individuale / Professionista ordinario
    ded, iva_det, aliquota, limite = 0.20, 0.40, 0.35, 18075

# --- INPUT DATI ---
t1, t2, t3 = st.tabs(["💰 Acquisto", "📈 Leasing", "🏢 Noleggio (NLT)"])

with t1:
    col1, col2 = st.columns(2)
    prezzo_a = col1.number_input("Prezzo Listino Ivato (€)", value=40000)
    sconto = col2.number_input("Sconto (%)", value=10)
    prezzo_scontato = prezzo_a * (1 - sconto/100)
    assic_maint = st.number_input("Costi annui (Assicurazione + Manutenzione) (€)", value=1500)

with t2:
    anticipo_l = st.number_input("Anticipo Leasing (€)", value=6000)
    canone_l = st.number_input("Canone mensile Leasing (€)", value=450)
    riscatto_l = st.number_input("Valore Riscatto Finale (€)", value=12000)

with t3:
    anticipo_n = st.number_input("Anticipo NLT (€)", value=4000)
    canone_n = st.number_input("Canone mensile NLT (€)", value=600)

# --- MOTORE DI CALCOLO (4 ANNI) ---
durata = 48
anni = 4

def calcola_netto(lordo, p_ded, p_iva, p_ali):
    iva_recuperata = (lordo / 1.22) * 0.22 * p_iva
    risparmio_tasse = (lordo - iva_recuperata) * p_ded * p_ali
    return lordo - iva_recuperata - risparmio_tasse

# NLT Netto
costo_nlt_lordo = anticipo_n + (canone_n * durata)
nlt_netto = calcola_netto(costo_nlt_lordo, ded, iva_det, aliquota)

# Acquisto Netto (Semplificato con svalutazione 50%)
valore_residuo = prezzo_scontato * 0.45
gestione_4anni = assicur_maint * anni
acquisto_lordo = prezzo_scontato + gestione_4anni
acquisto_netto = calcola_netto(acquisto_lordo, ded, iva_det, aliquota) - valore_residuo

# Leasing Netto
leasing_lordo = anticipo_l + (canone_l * durata) + riscatto_l + gestione_4anni
leasing_netto = calcola_netto(leasing_lordo, ded, iva_det, aliquota) - (valore_residuo * 0.9)

# --- GRAFICO ---
st.divider()
st.subheader("Confronto Costo Mensile REALE (Netto Tasse e Recupero IVA)")

mensile_n = nlt_netto / durata
mensile_a = acquisto_netto / durata
mensile_l = leasing_netto / durata

fig = go.Figure(data=[
    go.Bar(name='Costo Mensile Netto', x=['Acquisto', 'Leasing', 'Noleggio'], y=[mensile_a, mensile_l, mensile_n], 
           marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'])
])
st.plotly_chart(fig, use_container_width=True)

st.info("💡 Il calcolo include la svalutazione stimata dell'auto e il beneficio fiscale della tua categoria. Bollo auto escluso.")
