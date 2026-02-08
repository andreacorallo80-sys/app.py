import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("📊 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")

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

# Parametri Fiscali Italiani
if categoria == "Privato / Forfettario":
    ded, iva_det, limite = 0.0, 0.0, 0
elif categoria == "Agente di Commercio":
    ded, iva_det, limite = 0.80, 1.0, 25822
elif "Società" in categoria:
    ded, iva_det, limite = 0.70, 0.40, 0
else: # Ditta Individuale / Professionista Ordinario
    ded, iva_det, limite = 0.20, 0.40, 18075

aliq = aliquota_user / 100

# --- INPUT DATI ---
col_a, col_l, col_n = st.columns(3)

with col_a:
    st.subheader("💰 Acquisto")
    prezzo_imp = st.number_input("Prezzo Auto (Imp. €)", value=35000)
    st.write("**Spese Annue Accessorie (Imp.):**")
    rca = st.number_input("Assicurazione RCA/Kasko (€)", value=1000)
    tagliandi = st.number_input("Manutenzione/Revisioni (€)", value=400)
    gomme = st.number_input("Pneumatici (media annua €)", value=250)
    interessi_p = st.number_input("Interessi Finanziamento (€)", value=0)

with col_l:
    st.subheader("📈 Leasing")
    anticipo_l = st.number_input("Anticipo Leasing (Imp. €)", value=6000)
    rata_l = st.number_input("Canone Leasing (Imp. €)", value=450)
    riscatto_l = st.number_input("Riscatto Finale (Imp. €)", value=12000)
    spese_l = rca + tagliandi + gomme 

with col_n:
    st.subheader("🏢 Noleggio (NLT)")
    anticipo_n = st.number_input("Anticipo NLT (Imp. €)", value=3000)
    rata_n = st.number_input("Canone Mensile (Imp. €)", value=650)
    st.caption("Servizi (assicurazione, manutenzione, bollo) inclusi nel canone.")

# --- MOTORE DI CALCOLO ---
anni = durata_mesi / 12

def calcola_benefici(imponibile_servizi, imponibile_veicolo):
    iva_rec = (imponibile_servizi + imponibile_veicolo) * 0.22 * iva_det
    base_ded = imponibile_servizi + min(imponibile_veicolo, limite if limite > 0 else 9999999)
    tasse_rec = (base_ded * ded) * aliq
    return iva_rec + tasse_rec

# Svalutazione stimata
sval_factor = {24: 0.65, 36: 0.55, 48: 0.45, 60: 0.35}
valore_rivendita = prezzo_imp * sval_factor[durata_mesi]

# 1. ACQUISTO
esborso_a = prezzo_imp + (rca + tagliandi + gomme) * anni + interessi_p
benefici_a = calcola_benefici((rca + tagliandi + gomme) * anni + interessi_p, prezzo_imp)
costo_netto_a = esborso_a - benefici_a - valore_rivendita

# 2. LEASING
esborso_l = anticipo_l + (rata_l * durata_mesi) + riscatto_l + (spese_l * anni)
benefici_l = calcola_benefici((rata_l * durata_mesi) + (spese_l * anni), anticipo_l + riscatto_l)
costo_netto_l = esborso_l - benefici_l - valore_rivendita

# 3. NOLEGGIO
esborso_n = anticipo_n + (rata_n * durata_mesi)
benefici_n = calcola_benefici(esborso_n, 0)
costo_netto_n = esborso_n - benefici_n

# --- VISUALIZZAZIONE ---
st.divider()
col_graf, col_info = st.columns([2, 1])

with col_graf:
    fig = go.Figure(data=[
        go.Bar(name='Esborso Totale (Lordo)', x=['Acquisto', 'Leasing', 'Noleggio'], y=[esborso_a, esborso_l, esborso_n], marker_color='#D3D3D3'),
        go.Bar(name='Costo Reale (Netto)', x=['Acquisto', 'Leasing', 'Noleggio'], y=[costo_netto_a, costo_netto_l, costo_netto_n], marker_color='#2ecc71')
    ])
    fig.update_layout(barmode='group', title=f"Confronto su {durata_mesi} mesi (Lordo vs Netto)")
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.markdown("### 📋 Mensilità Netta")
    st.metric("Acquisto", f"€ {costo_netto_a/durata_mesi:.2f}")
    st.metric("Leasing", f"€ {costo_netto_l/durata_mesi:.2f}")
    st.metric("Noleggio", f"€ {costo_netto_n/durata_mesi:.2f}")

# --- TABELLA DETTAGLIATA ---
st.subheader("📉 Analisi Cash Flow e Dettaglio Fiscale")
tabella_dati = {
    "Voce": ["Esborso Totale (Imp.)", "IVA Pagata (22%)", "IVA Recuperata", "Risparmio Tasse", "Valore Residuo", "COSTO NETTO"],
    "Acquisto": [esborso_a, esborso_a*0.22, esborso_a*0.22*iva_det, benefici_a - (esborso_a*0.22*iva_det), valore_rivendita, costo_netto_a],
    "Noleggio": [esborso_n, esborso_n*0.22, esborso_n*0.22*iva_det, benefici_n - (esborso_n*0.22*iva_det), 0, costo_netto_n]
}
st.table(pd.DataFrame(tabella_dati).style.format(subset=["Acquisto", "Noleggio"], formatter="€ {:.0f}"))
