import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- SISTEMA DI ACCESSO ---
def login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        # Schermata di Login centrata
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("https://wixmp-fe53c9ff592a4da924211f23.wixmp.com/users/f82fe7ec-0fdc-48d7-9d58-ebe5c84f803b/design-previews/1023c1f1-d49a-485d-8bb2-21c2bb5b5155/1765130978316-transparentThumbnail.png", use_container_width=True)
            st.subheader("🔐 Accesso Riservato")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Accedi"):
                # Credenziali richieste
                if username == "abbonamentiauto" and password == "stiamolavorandopervoi26!":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Credenziali errate. Riprova.")
        return False
    return True

# --- ESECUZIONE APP ---
if login():
    # Logout nella sidebar per comodità
    if st.sidebar.button("Esci / Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    # --- INTESTAZIONE CENTRATA ---
    t_col1, t_col2, t_col3 = st.columns([1, 1, 1])
    with t_col2:
        st.image("https://wixmp-fe53c9ff592a4da924211f23.wixmp.com/users/f82fe7ec-0fdc-48d7-9d58-ebe5c84f803b/design-previews/1023c1f1-d49a-485d-8bb2-21c2bb5b5155/1765130978316-transparentThumbnail.png", use_container_width=True)
        

    st.markdown("<h1 style='text-align: center;'>🚗 Smart Cost Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Powered by <b>abbonamentiauto.it</b></p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### Logica Imponibile (IVA 22% esclusa)")
    st.warning("⚠️ Nota: Il Bollo Auto è sempre ESCLUSO dal calcolo.")


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
        iva_veicolo = imp_veicolo * 0.22
        iva_servizi = imp_servizi * 0.22
        iva_tot = iva_veicolo + iva_servizi
        iva_recuperata = iva_tot * iva_det
        base_ded_veicolo = (imp_veicolo + (iva_veicolo * (1-iva_det)))
        veicolo_deducibile = min(base_ded_veicolo, limite) if limite > 0 else base_ded_veicolo
        base_ded_servizi = (imp_servizi + (iva_servizi * (1-iva_det)))
        risparmio_tasse = (veicolo_deducibile + base_ded_servizi) * ded * aliq
        return iva_recuperata, risparmio_tasse, iva_tot

    # --- INPUT DATI ---
    col_a, col_l, col_n = st.columns(3)

    with col_a:
        st.subheader("💰 Acquisto")
        prezzo_imp_a = st.number_input("Prezzo Auto (Imp. €)", value=35000, key="p_a")
        scelta_pago = st.radio("Pagamento", ["Contanti", "Finanziamento"])
        int_a = 0.0
        if scelta_pago == "Finanziamento":
            ant_f = st.number_input("Anticipo Finanziamento (€)", value=5000)
            tan = st.number_input("TAN (%)", value=5.95)
            cap_fin = prezzo_imp_a - ant_f
            if cap_fin > 0:
                i_m = (tan/100)/12
                rata = cap_fin * (i_m * (1+i_m)**durata_mesi) / ((1+i_m)**durata_mesi - 1)
                int_a = (rata * durata_mesi) - cap_fin
                st.info(f"Rata: € {rata:.2f}")
        spese_a = st.number_input("Assic. + Manut. (€/anno)", value=1500, key="s_a")

    with col_l:
        st.subheader("📈 Leasing")
        prezzo_imp_l = st.number_input("Prezzo Listino (Imp. €)", value=35000, key="p_l")
        ant_l = st.number_input("Primo Canone (Imp. €)", value=6000)
        rata_l = st.number_input("Canone Mensile (Imp. €)", value=400)
        riscatto_l = st.number_input("Riscatto Finale (Imp. €)", value=350)
        servizi_l = st.number_input("Servizi fuori canone (€/anno)", value=1000, key="s_l")

    with col_n:
        st.subheader("🏢 Noleggio (NLT)")
        ant_n = st.number_input("Anticipo NLT (Imp. €)", value=1500)
        rata_n = st.number_input("Canone Mensile (Imp. €)", value=277)
        st.info("💡 Manutenzione ordinaria e straordinaria, Rca, IF, K, traino e assistenza stradale.")

    # --- ELABORAZIONE ---
    sval_factor = {24: 0.65, 36: 0.55, 48: 0.45, 60: 0.35}
    val_res = prezzo_imp_a * sval_factor[durata_mesi]

    # 1. ACQUISTO
    serv_tot_a = spese_a * anni
    iva_rec_a, tax_rec_a, iva_tot_a = calcola_benefici_dettagliati(serv_tot_a + int_a, prezzo_imp_a)
    esborso_a = prezzo_imp_a + iva_tot_a + serv_tot_a + int_a
    netto_a = esborso_a - iva_rec_a - tax_rec_a - val_res

    # 2. LEASING
    serv_tot_l = servizi_l * anni
    canoni_l = ant_l + (rata_l * durata_mesi) + riscatto_l
    iva_rec_l, tax_rec_l, iva_tot_l = calcola_benefici_dettagliati(serv_tot_l, canoni_l)
    esborso_l = canoni_l + iva_tot_l + serv_tot_l
    netto_l = esborso_l - iva_rec_l - tax_rec_l - val_res

    # 3. NOLEGGIO
    costo_n = ant_n + (rata_n * durata_mesi)
    iva_rec_n, tax_rec_n, iva_tot_n = calcola_benefici_dettagliati(costo_n, 0)
    esborso_n = costo_n + iva_tot_n
    netto_n = esborso_n - iva_rec_n - tax_rec_n

    # --- TABELLA DETTAGLIATA ---
    st.divider()
    st.subheader("📊 Analisi Dettagliata TCO (Total Cost of Ownership)")

    df = pd.DataFrame({
        "Voce di Spesa": [
            "Investimento Veicolo / Canoni (Imp.)",
            "Servizi / Manutenzione (Imp.)",
            "Interessi Passivi",
            "IVA Totale Versata",
            "--- ESBORSO LORDO ---",
            "Recupero IVA (-)",
            "Risparmio Tasse (-)",
            "Valore Residuo Auto (-)",
            "--- COSTO NETTO REALE ---",
            "INCIDENZA MENSILE NETTA"
        ],
        "Acquisto": [prezzo_imp_a, serv_tot_a, int_a, iva_tot_a, esborso_a, -iva_rec_a, -tax_rec_a, -val_res, netto_a, netto_a/durata_mesi],
        "Leasing": [canoni_l, serv_tot_l, 0, iva_tot_l, esborso_l, -iva_rec_l, -tax_rec_l, -val_res, netto_l, netto_l/durata_mesi],
        "Noleggio": [costo_n, 0, 0, iva_tot_n, esborso_n, -iva_rec_n, -tax_rec_n, 0, netto_n, netto_n/durata_mesi]
    })

    st.table(df.style.format({
        "Acquisto": "€ {:.2f}", "Leasing": "€ {:.2f}", "Noleggio": "€ {:.2f}"
    }))

    # --- GRAFICO ---
    fig = go.Figure(data=[
        go.Bar(name='Costo Mensile Netto', x=['Acquisto', 'Leasing', 'Noleggio'], 
               y=[netto_a/durata_mesi, netto_l/durata_mesi, netto_n/durata_mesi], 
               marker_color='#27AE60', text=[f"€ {netto_a/durata_mesi:.0f}", f"€ {netto_l/durata_mesi:.0f}", f"€ {netto_n/durata_mesi:.0f}"],
               textposition='auto')
    ])
    fig.update_layout(title="Confronto Mensile Reale (Post-Fiscale)")
    st.plotly_chart(fig, use_container_width=True)
