import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("🚗 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")
st.warning("⚠️ Nota: Il Bollo Auto è sempre ESCLUSO dal calcolo e rimane a carico del cliente secondo le tariffe regionali.")

# --- SIDEBAR: CONFIGURAZIONE FISCALE E DURATA ---
st.sidebar.header("⚙️ Configurazione")
categoria = st.sidebar.selectbox("Tipologia Cliente", [
    "Privato / Forfettario",
    "Ditta Individuale / SNC / SAS",
    "Società di Capitali (SRL, SPA)",
    "Agente di Commercio"
])

durata_mesi = st.sidebar.select_slider("Durata Contratto (Mesi)", options=[24, 36, 48, 60], value=48)
aliquota_user = st.sidebar.slider("Tua Aliquota Fiscale (%)", 0, 50, 24 if "Società" in categoria else 35)

# Parametri Fiscali
if categoria == "Privato / Forfettario":
    ded, iva_det, limite = 0.0, 0.0, 0
elif categoria == "Agente di Commercio":
    ded, iva_det, limite = 0.80, 1.0, 25822
elif "Società" in categoria:
    ded, iva_det, limite = 0.70, 0.40, 0
else: # Ditta Individuale / Professionista Ordinario
    ded, iva_det, limite = 0.20, 0.40, 18075

aliq = aliquota_user / 100
anni = durata_mesi / 12

# --- FUNZIONI DI CALCOLO ---
def calcola_benefici(imponibile_servizi, imponibile_veicolo):
    iva_rec = (imponibile_servizi + imponibile_veicolo) * 0.22 * iva_det
    base_ded = imponibile_servizi + min(imponibile_veicolo, limite if limite > 0 else 9999999)
    tasse_rec = (base_ded * ded) * aliq
    return iva_rec + tasse_rec

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
    anticipo_l = st.number_input("Primo Canone / Anticipo (Imp. €)", value=6000)
    rata_l = st.number_input("Canone Mensile (Imp. €)", value=400)
    perc_riscatto = st.number_input("Riscatto Finale (%)", value=1.0, step=0.5)
    riscatto_l = prezzo_imp_l * (perc_riscatto / 100)
    st.write(f"Valore Riscatto: **€ {riscatto_l:.2f}**")
    st.write("**Servizi Esclusi (Imp. annuo):**")
    servizi_l = st.number_input("Assic. + Manut. Leasing (€)", value=1500)

with col_n:
    st.subheader("🏢 Noleggio (NLT)")
    anticipo_n = st.number_input("Anticipo NLT (Imp. €)", value=3000)
    rata_n = st.number_input("Canone Mensile (Imp. €)", value=650)
    st.info("Nota: Assicurazione, IF e Manutenzione incluse. Bollo sempre escluso.")

# --- ELABORAZIONE ---
sval_factor = {24: 0.65, 36: 0.55, 48: 0.45, 60: 0.35}
valore_rivendita = prezzo_imp_a * sval_factor[durata_mesi]

# 1. ACQUISTO
spese_tot_a = (rca_a + if_a + manut_a) * anni
esborso_a = prezzo_imp_a + spese_tot_a + interessi_a
benefici_a = calcola_benefici(spese_tot_a + interessi_a, prezzo_imp_a)
netto_a = esborso_a - benefici_a - valore_rivendita

# 2. LEASING
spese_tot_l = servizi_l * anni
esborso_l = anticipo_l + (rata_l * durata_mesi) + riscatto_l + spese_tot_l
benefici_l = calcola_benefici((rata_l * durata_mesi) + spese_tot_l, anticipo_l + riscatto_l)
netto_l = esborso_l - benefici_l - valore_rivendita

# 3. NOLEGGIO
esborso_n = anticipo_n + (rata_n * durata_mesi)
benefici_n = calcola_benefici(esborso_n, 0)
netto_n = esborso_n - benefici_n

# --- VISUALIZZAZIONE ---
st.divider()
c_graf, c_met = st.columns([2, 1])

with c_graf:
    fig = go.Figure(data=[
        go.Bar(name='Esborso Totale', x=['Acquisto', 'Leasing', 'Noleggio'], y=[esborso_a, esborso_l, esborso_n], marker_color='#BDC3C7'),
        go.Bar(name='Costo Reale Netto', x=['Acquisto', 'Leasing', 'Noleggio'], y=[netto_a, netto_l, netto_n], marker_color='#27AE60')
    ])
    fig.update_layout(barmode='group', title="Confronto Finanziario vs Reale (Bollo Escluso)")
    st.plotly_chart(fig, use_container_width=True)

with c_met:
    st.metric("Mensile Netto Acquisto", f"€ {netto_a/durata_mesi:.2f}")
    st.metric("Mensile Netto Leasing", f"€ {netto_l/durata_mesi:.2f}")
    st.metric("Mensile Netto Noleggio", f"€ {netto_n/durata_mesi:.2f}")

# Tabella Cash Flow
st.subheader("📉 Analisi di Bilancio")
df = pd.DataFrame({
    "Voce": ["Esborso Lordo", "IVA Recuperata", "Risparmio Tasse", "Valore di Rivendita", "Costo Netto Finale"],
    "Acquisto": [esborso_a, esborso_a*0.22*iva_det, (esborso_a - (esborso_a*0.22*iva_det))*ded*aliq, valore_rivendita, netto_a],
    "Leasing": [esborso_l, esborso_l*0.22*iva_det, (esborso_l - (esborso_l*0.22*iva_det))*ded*aliq, valore_rivendita, netto_l],
    "Noleggio": [esborso_n, esborso_n*0.22*iva_det, (esborso_n - (esborso_n*0.22*iva_det))*ded*aliq, 0, netto_n]
})
st.table(df.style.format(subset=["Acquisto", "Leasing", "Noleggio"], formatter="€ {:.0f}"))
