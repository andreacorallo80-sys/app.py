import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configurazione Pagina
st.set_page_config(page_title="Analisi TCO Auto Pro", layout="wide")

st.title("🚗 Analisi Comparativa Professionale Auto")
st.markdown("### Logica Imponibile (IVA 22% esclusa)")

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

# --- LOGICHE FISCALI ---
ded, iva_det, limite = 0.20, 0.40, 18075
if categoria == "Privato / Forfettario":
    ded, iva_det, limite = 0.0, 0.0, 0
elif categoria == "Agente di Commercio":
    ded, iva_det, limite = 0.80, 1.0, 25822
elif "Uso Strumentale" in uso_specifico:
    ded, iva_det, limite = 1.0, 1.0, 0 
elif "Uso Promiscuo" in uso_specifico:
    ded, iva_det, limite = 0.70, 0.40, 0 

aliq = aliquota_user / 100
anni = durata_mesi / 12

# --- FUNZIONE DI CALCOLO BENEFICI ---
def calcola_benefici_dettagliati(imp_servizi, imp_veicolo):
    # 1. IVA
    iva_veicolo = imp_veicolo * 0.22
    iva_servizi = imp_servizi * 0.22
    iva_tot = iva_veicolo + iva_servizi
    
    iva_recuperata = iva_tot * iva_det
    iva_indetraibile = iva_tot - iva_recuperata
    
    # 2. DEDUZIONE TASSE (IRPEF/IRES/IRAP)
    # Il limite si applica al veicolo + la sua parte di IVA indetraibile
    iva_indet_veicolo = iva_veicolo * (1 - iva_det)
    base_ammortamento = imp_veicolo + iva_indet_veicolo
    veicolo_deducibile = min(base_ammortamento, limite) if limite > 0 else base_ammortamento
    
    iva_indet_servizi = iva_servizi * (1 - iva_det)
    servizi_deducibili = imp_servizi + iva_indet_servizi
    
    risparmio_tasse = (veicolo_deducibile + servizi_deducibili) * ded * aliq
    
    return iva_recuperata, risparmio_tasse, iva_tot

# --- INPUT DATI ---
col_a, col_l, col_n = st.columns(3)

with col_a:
    st.subheader("💰 Acquisto / Finanziamento")
    prezzo_imp_a = st.number_input("Prezzo Auto (Imp. €)", value=35000, key="prezzo_a")
    scelta_pagamento = st.radio("Pagamento", ["Contanti", "Finanziamento"])
    int_a = 0.0
    if scelta_pagamento == "Finanziamento":
        ant_f = st.number_input("Anticipo (€)", value=5000)
        tan = st.number_input("TAN (%)", value=5.95)
        cap_fin = prezzo_imp_a - ant_f
        if cap_fin > 0:
            i_m = (tan / 100) / 12
            rata = cap_fin * (i_m * (1 + i_m)**durata_mesi) / ((1 + i_m)**durata_mesi - 1)
            int_a = (rata * durata_mesi) - cap_fin
            st.info(f"Rata: € {rata:.2f}")
    
    spese_manut_a = st.number_input("Manutenzione + Assic. (€/anno)", value=1500)

with col_l:
    st.subheader("📈 Leasing")
    prezzo_imp_l = st.number_input("Prezzo Listino (Imp. €)", value=35000, key="prezzo_l")
    anticipo_l = st.number_input("Primo Canone (Imp. €)", value=6000)
    rata_l = st.number_input("Canone Mensile (Imp. €)", value=400)
    riscatto_l = st.number_input("Riscatto Finale (Imp. €)", value=350)
    servizi_l = st.number_input("Servizi fuori canone (€/anno)", value=1000)

with col_n:
    st.subheader("🏢 Noleggio (NLT)")
    anticipo_n = st.number_input("Anticipo NLT (Imp. €)", value=1500)
    rata_n = st.number_input("Canone Mensile (Imp. €)", value=277)
    st.info("💡 Manutenzione e Assicurazione incluse.")

# --- ELABORAZIONE ---
sval_factor = {24: 0.65, 36: 0.55, 48: 0.45, 60: 0.35}
val_res = prezzo_imp_a * sval_factor[durata_mesi]

# 1. ACQUISTO
servizi_tot_a = spese_manut_a * anni
iva_rec_a, tax_rec_a, iva_tot_a = calcola_benefici_dettagliati(servizi_tot_a + int_a, prezzo_imp_a)
esborso_lordo_a = prezzo_imp_a + iva_tot_a + servizi_tot_a + int_a
netto_a = esborso_lordo_a - iva_rec_a - tax_rec_a - val_res

# 2. LEASING
servizi_tot_l = servizi_l * anni
canoni_tot_l = anticipo_l + (rata_l * durata_mesi) + riscatto_l
iva_rec_l, tax_rec_l, iva_tot_l = calcola_benefici_dettagliati(servizi_tot_l, canoni_tot_l)
esborso_lordo_l = canoni_tot_l + iva_tot_l + servizi_tot_l
netto_l = esborso_lordo_l - iva_rec_l - tax_rec_l - val_res

# 3. NOLEGGIO
costo_servizio_n = anticipo_n + (rata_n * durata_mesi)
iva_rec_n, tax_rec_n, iva_tot_n = calcola_benefici_dettagliati(costo_servizio_n, 0)
esborso_lordo_n = costo_servizio_n + iva_tot_n
netto_n = esborso_lordo_n - iva_rec_n - tax_rec_n

# --- TABELLA DETTAGLIATA ---
st.divider()
st.subheader("📊 Analisi Dettagliata dei Costi (TCO)")

data = {
    "Voce di Costo": [
        "Prezzo Veicolo / Canoni (Imponibile)",
        "Servizi Accessori / Manutenzione",
        "Interessi Finanziamento",
        "IVA Totale Pagata (22%)",
        "---",
        "ESBORSO TOTALE (Lordo Cash)",
        "---",
        "Recupero IVA (Detrazione)",
        "Risparmio Tasse (Deduzione)",
        "Valore Residuo Stimato (Asset)",
        "---",
        "COSTO NETTO REALE (Periodo)",
        "COSTO NETTO MENSILE"
    ],
    "Acquisto": [
        prezzo_imp_a, servizi_tot_a, int_a, iva_tot_a, 0,
        esborso_lordo_a, 0,
        -iva_rec_a, -tax_rec_a, -val_res, 0,
        netto_a, netto_a/durata_mesi
    ],
    "Leasing": [
        canoni_tot_l, servizi_tot_l, 0, iva_tot_l, 0,
        esborso_lordo_l, 0,
        -iva_rec_l, -tax_rec_l, -val_res, 0,
        netto_l, netto_l/durata_mesi
    ],
    "Noleggio": [
        costo_servizio_n, 0, 0, iva_tot_n, 0,
        esborso_lordo_n, 0,
        -iva_rec_n, -tax_rec_n, 0, 0,
        netto_n, netto_n/durata_mesi
    ]
}

df = pd.DataFrame(data)
st.table(df.style.format({
    "Acquisto": "€ {:.2f}",
    "Leasing": "€ {:.2f}",
    "Noleggio": "€ {:.2f}"
}))

# --- GRAFICO ---
fig = go.Figure(data=[
    go.Bar(name='Costo Mensile Netto', x=['Acquisto', 'Leasing', 'Noleggio'], y=[netto_a/durata_mesi, netto_l/durata_mesi, netto_n/durata_mesi], marker_color='#27AE60')
])
fig.update_layout(title="Confronto Mensile Netto")
st.plotly_chart(fig, use_container_width=True)
