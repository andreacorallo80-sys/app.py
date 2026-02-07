import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Car Calculator Pro", layout="wide")

st.title("🚗 Calcolatore Convenienza Auto")

# --- SIDEBAR ---
st.sidebar.header("1. Profilo Fiscale")
categoria = st.sidebar.selectbox("Tipologia Cliente", [
    "Privato / Forfettario",
    "Ditta Individuale / SNC / SAS",
    "Società di Capitali (SRL, SPA)",
    "Agente di Commercio"
])

# Parametri fiscali semplificati
if categoria == "Privato / Forfettario":
    ded, iva_det, aliq = 0.0, 0.0, 0.0
elif categoria == "Agente di Commercio":
    ded, iva_det, aliq = 0.80, 1.0, 0.35
elif categoria == "Società di Capitali (SRL, SPA)":
    ded, iva_det, aliq = 0.70, 0.40, 0.24
else:
    ded, iva_det, aliq = 0.20, 0.40, 0.35

# --- INPUT ---
t1, t2, t3 = st.tabs(["💰 Acquisto", "📈 Leasing", "🏢 Noleggio"])

with t1:
    prezzo_a = st.number_input("Prezzo Listino Ivato (€)", value=40000)
    spese_annue = st.number_input("Assicurazione + Manutenzione annua (€)", value=1500)

with t2:
    anticipo_l = st.number_input("Anticipo Leasing (€)", value=6000)
    rata_l = st.number_input("Rata Mensile Leasing (€)", value=450)
    riscatto_l = st.number_input("Riscatto Finale (€)", value=12000)

with t3:
    anticipo_n = st.number_input("Anticipo Noleggio (€)", value=4000)
    rata_n = st.number_input("Rata Mensile Noleggio (€)", value=600)

# --- CALCOLI (Orizzonte 4 anni) ---
durata = 48

# Funzione calcolo risparmio
def calcola_risparmio(lordo):
    iva = (lordo / 1.22) * 0.22 * iva_det
    tasse = (lordo - iva) * ded * aliq
    return iva + tasse

# NLT
totale_n = anticipo_n + (rata_n * durata)
netto_n = (totale_n - calcola_risparmio(totale_n)) / durata

# Acquisto (Svalutazione stimata al 50%)
totale_a = prezzo_a + (spese_annue * 4)
residuo = prezzo_a * 0.45
netto_a = (totale_a - calcola_risparmio(totale_a) - residuo) / durata

# Leasing
totale_l = anticipo_l + (rata_l * durata) + riscatto_l + (spese_annue * 4)
netto_l = (totale_l - calcola_risparmio(totale_l) - residuo) / durata

# --- GRAFICO ---
fig = go.Figure(data=[
    go.Bar(x=['Acquisto', 'Leasing', 'Noleggio'], y=[netto_a, netto_l, netto_n],
           marker_color=['#3498db', '#e67e22', '#2ecc71'])
])
fig.update_layout(title="Costo Mensile Netto (€)")
st.plotly_chart(fig, use_container_width=True)

st.success(f"Configurazione completata per: {categoria}")
