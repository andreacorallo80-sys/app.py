import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy_financial as npf # Necessaria per calcolo rata preciso

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
    tipo_acquisto = st.radio("Modalità di pagamento", ["Contanti", "Finanziamento"])
    
    interessi_finanziamento = 0.0
    rata_acquisto_visuale = 0.0
    
    if tipo_acquisto == "Finanziamento":
        anticipo_f = st.number_input("Anticipo Finanziamento (€)", value=5000)
        tan = st.number_input("Tasso Annuale (TAN %)", value=5.9) / 100
        capitale_finanziato = prezzo_imp_a - anticipo_f
        
        if capitale_finanziato > 0:
            # Calcolo Rata Mensile (Formula Francese)
            tasso_m = tan / 12
            rata_acquisto_visuale = capitale_finanziato * (tasso_m / (1 - (1 + tasso_m)**-durata_mesi))
            totale_pagato_fin = rata_acquisto_visuale * durata_mesi
            interessi_finanziamento = totale_pagato_fin - capitale_finanziato
            st.success(f"Rata stimata: € {rata_acquisto_visuale:.2f}")
            st.caption(f"Totale interessi: € {interessi_finanziamento:.2f}")

    st.write("**Spese Annue Accessorie:**")
    rca_a = st.number_input("RCA (€)", value=500)
    if_a = st.number_input("Incendio e Furto (€)", value=600)
    manut_a = st.number_input("Manutenzione (€)", value=400)

with col_l:
    st.subheader("📈 Leasing")
    prezzo_imp_l = st.number_input("Prezzo Listino (Imp. €)", value=35000, key="prezzo_l")
    anticipo_l = st.number_input("Primo Canone (Imp. €)", value=6000)
    rata_l = st.number_input("Canone Mensile (Imp. €)", value=400)
    perc_riscatto = st.number_input("Riscatto Finale (%)", value=1.0, step=0.5)
    riscatto_l = prezzo_imp_l * (perc_riscatto / 100)
    st.write(f"Riscatto: € {riscatto_l:,.2f}")
    servizi_l = st.number_input("Assic. + Manut. Fuori Canone (Annue €)", value=1500)

with col_n:
    st.subheader("🏢 Noleggio (NLT)")
    anticipo_n = st.number_input("Anticipo NLT (Imp. €)", value=3000)
    rata_n = st.number_input("Canone Mensile (Imp. €)", value=650)
    st.info("💡 RCA, IF e Manutenzione incluse.")

# --- ELABORAZIONE ---
sval_factor = {24: 0.65, 36: 0.55, 48: 0.45, 60: 0.35}
valore_rivendita = prezzo_imp_a * sval_factor[durata_mesi]

# 1. ACQUISTO
spese_gestione_a = (rca_a + if_a + manut_a) * anni
# Gli interessi sono deducibili come spese di gestione
iva_a, tax_a = calcola_benefici(spese_gestione_a + interessi_finanziamento, prezzo_imp_a)
esborso_a = prezzo_imp_a + spese_gestione_a + interessi_finanziamento
netto_a = esborso_a - iva_a - tax_a - valore_rivendita

# 2. LEASING
spese_tot_l = servizi_l * anni
iva_l, tax_l = calcola_benefici((rata_l * durata_mesi) + spese_tot_l, anticipo_l + riscatto_l)
esborso_l = anticipo_l + (rata_l * durata_mesi) + riscatto_l + spese_tot_l
netto_l = esborso_l - iva_l - tax_l - valore_rivendita

# 3. NOLEGGIO
esborso_n = anticipo_n + (rata_n * durata_mesi)
iva_n, tax_n = calcola_benefici(esborso_n, 0)
netto_n = esborso_n - iva_n - tax_n

# --- VISUALIZZAZIONE ---
st.divider()
c_graf, c_met = st.columns([2, 1])

with c_graf:
    fig = go.Figure(data=[
        go.Bar(name='Esborso Lordo', x=['Acquisto', 'Leasing', 'Noleggio'], y=[esborso_a, esborso_l, esborso_n], marker_color='#BDC3C7'),
        go.Bar(name='Costo Reale Netto', x=['Acquisto', 'Leasing', 'Noleggio'], y=[netto_a, netto_l, netto_n], marker_color='#27AE60')
    ])
    fig.update_layout(barmode='group', title=f"Analisi su {durata_mesi} mesi")
    st.plotly_chart(fig, use_container_width=True)

with c_met:
    st.metric("Mensile Netto Acquisto", f"€ {netto_a/durata_mesi:.2f}")
    st.metric("Mensile Netto Leasing", f"€ {netto_l/durata_mesi:.2f}")
    st.metric("Mensile Netto Noleggio", f"€ {netto_n/durata_mesi:.2f}")

# --- TABELLE ---
st.subheader("📉 Dettaglio Costi e Fiscalità")
df_res = pd.DataFrame({
    "Voce": ["Esborso Lordo", "Interessi Finanziari", "IVA Recuperata", "Risparmio Tasse", "Valore Residuo", "Costo Netto Finale"],
    "Acquisto": [esborso_a, interessi_finanziamento, iva_a, tax_a, valore_rivendita, netto_a],
    "Leasing": [esborso_l, 0, iva_l, tax_l, valore_rivendita, netto_l],
    "Noleggio": [esborso_n, 0, iva_n, tax_n, 0, netto_n]
})
st.table(df_res.style.format(subset=["Acquisto", "Leasing", "Noleggio"], formatter="€ {:.0f}"))
    "Leasing": [esborso_l, iva_l, tax_l, valore_rivendita, netto_l],
    "Noleggio": [esborso_n, iva_n, tax_n, 0, netto_n]
})
st.table(df_res.style.format(subset=["Acquisto", "Leasing", "Noleggio"], formatter="€ {:.0f}"))
