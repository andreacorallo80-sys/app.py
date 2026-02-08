import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("🚗 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")
st.warning("⚠️ Nota: Il Bollo Auto è sempre ESCLUSO dal calcolo.")

# --- SIDEBAR: CONFIGURAZIONE FISCALE ---
st.sidebar.header("⚙️ Configurazione")
categoria = st.sidebar.selectbox("Tipologia Cliente", [
    "Privato / Forfettario",
    "Ditta Individuale / Professionista Ordinario",
    "Società di Capitali (SRL, SPA)",
    "Agente di Commercio"
])

# Scelta utilizzo per Società
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
        ded, iva_det, limite = 0.70, 0.40, 0 # Nessun limite di costo per uso promiscuo
    else:
        ded, iva_det, limite = 0.20, 0.40, 18075
else: # Professionista Ordinario / Ditta Individuale
    ded, iva_det, limite = 0.20, 0.40, 18075

aliq = aliquota_user / 100
anni = durata_mesi / 12

# --- FUNZIONE CALCOLO BENEFICI ---
def calcola_benefici(imponibile_servizi, imponibile_veicolo):
    iva_pagata = (imponibile_servizi + imponibile_veicolo) * 0.22
    iva_rec = iva_pagata * iva_det
    iva_indetraibile = iva_pagata - iva_rec
    # IVA indetraibile sommata al costo per la deduzione
    base_ded = imponibile_servizi + min(imponibile_veicolo, limite if limite > 0 else 9999999) + iva_indetraibile
    tasse_rec = (base_ded * ded) * aliq
    return iva_rec, tasse_rec

# --- INPUT DATI ---
col_a, col_l, col_n = st.columns(3)

with col_a:
    st.subheader("💰 Acquisto")
    prezzo_imp_a = st.number_input("Prezzo Auto (Imp. €)", value=35000, key="prezzo_a")
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
    st.write("**Servizi Esclusi (Imp. annuo):**")
    servizi_l = st.number_input("Assic. + Manut. Leasing (€)", value=1500)

with col_n:
    st.subheader("🏢 Noleggio (NLT)")
    anticipo_n = st.number_input("Anticipo NLT (Imp. €)", value=3000)
    rata_n = st.number_input("Canone Mensile (Imp. €)", value=650)
    st.info("Nota: RCA, IF e Manutenzione incluse.")

# --- ELABORAZIONE ---
sval_factor = {24: 0.65, 36: 0.55, 48: 0.45, 60: 0.35}
valore_rivendita = prezzo_imp_a * sval_factor[durata_mesi]

# Risultati
iva_a, tax_a = calcola_benefici((rca_a + if_a + manut_a) * anni + interessi_a, prezzo_imp_a)
esborso_a = prezzo_imp_a + (rca_a + if_a + manut_a) * anni + interessi_a
netto_a = esborso_a - iva_a - tax_a - valore_rivendita

iva_l, tax_l = calcola_benefici((rata_l * durata_mesi) + (servizi_l * anni), anticipo_l + riscatto_l)
esborso_l = anticipo_l + (rata_l * durata_mesi) + riscatto_l + (servizi_l * anni)
netto_l = esborso_l - iva_l - tax_l - valore_rivendita

iva_n, tax_n = calcola_benefici(anticipo_n + (rata_n * durata_mesi), 0)
esborso_n = anticipo_n + (rata_n * durata_mesi)
netto_n = esborso_n - iva_n - tax_n

# --- VISUALIZZAZIONE ---
st.divider()
c_graf, c_met = st.columns([2, 1])

with c_graf:
    fig = go.Figure(data=[
        go.Bar(name='Esborso Lordo', x=['Acquisto', 'Leasing', 'Noleggio'], y=[esborso_a, esborso_l, esborso_n], marker_color='#BDC3C7'),
        go.Bar(name='Costo Reale Netto', x=['Acquisto', 'Leasing', 'Noleggio'], y=[netto_a, netto_l, netto_n], marker_color='#27AE60')
    ])
    fig.update_layout(barmode='group', title="Confronto Finanziario vs Costo Reale")
    st.plotly_chart(fig, use_container_width=True)
