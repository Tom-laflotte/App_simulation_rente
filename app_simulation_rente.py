import streamlit as st
from datetime import date
from calcul_rentes import (
    simulateur_rente,
    dico_grille_dynamique,
    dico_grille_equilibre,
    dico_grille_prudent,
)

# Création d'un mot de passe pour le site 
def check_password():
    if "password_ok" not in st.session_state:
        st.session_state.password_ok = False

    if not st.session_state.password_ok:
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            if pwd == st.secrets["password"]:
                st.session_state.password_ok = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
        st.stop()

check_password()

st.set_page_config(page_title="Simulateur de Rente", layout="wide")
st.title("Simulateur de Rente PER")

# ─────────────────────────────────────────────
# 1. CAPITAUX PAR COMPARTIMENT
# ─────────────────────────────────────────────
st.header("1. Capitaux actuels")
col1, col2, col3 = st.columns(3)
with col1:
    K1 = st.number_input("Capital compartiment 1 (€)", min_value=0.0, value=0.0, step=100.0)
with col2:
    K2 = st.number_input("Capital compartiment 2 (€)", min_value=0.0, value=0.0, step=100.0)
with col3:
    K3 = st.number_input("Capital compartiment 3 (€)", min_value=0.0, value=0.0, step=100.0)

# ─────────────────────────────────────────────
# 2. DATES
# ─────────────────────────────────────────────
st.header("2. Dates")
date_simul = date.today()
st.info(f"📅 Date de simulation (aujourd'hui) : **{date_simul.strftime('%d/%m/%Y')}**")
date_sortie = st.date_input("Date de sortie en rente prévue", min_value=date_simul, max_value = date(2080, 1, 1))
st.write(f"date_simul : {date_simul}, date_sortie : {date_sortie}")
# ─────────────────────────────────────────────
# 3. PROFIL D'INVESTISSEMENT
# ─────────────────────────────────────────────
st.header("3. Profil d'investissement")
profil = st.radio(
    "Profil de gestion",
    options=["Dynamique", "Équilibré", "Prudent"],
    horizontal=True,
)
grille_map = {
    "Dynamique": dico_grille_dynamique,
    "Équilibré": dico_grille_equilibre,
    "Prudent": dico_grille_prudent,
}
grille = grille_map[profil]

# ─────────────────────────────────────────────
# 4. VERSEMENTS ET ABONDEMENT
# ─────────────────────────────────────────────
st.header("4. Versements et abondement")
col1, col2 = st.columns(2)
with col1:
    VV_mens = st.number_input("Versements volontaires mensuels (€)", min_value=0.0, value=0.0, step=50.0)
    tau = st.number_input("Taux d'abondement (%)", min_value=0.0, max_value=300.0, value=0.0, step=1.0) / 100
    P = st.number_input("Plafond d'abondement annuel (€)", min_value=0.0, value=0.0, step=100.0)
with col2:
    A0_deja_verse = st.number_input("Abondement déjà reçu cette année (€)", min_value=0.0, value=0.0, step=100.0)
    taux_vers = st.number_input("Frais d'entrée (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1) / 100
    cotis_moins1 = st.number_input("Cotisations obligatoires reçues l'an dernier (€)", min_value=0.0, value=0.0, step=100.0)

# ─────────────────────────────────────────────
# 5. PROFIL ASSURÉ
# ─────────────────────────────────────────────
st.header("5. Profil assuré")
col1, col2 = st.columns(2)
with col1:
    date_naissance = st.date_input(
        "Date de naissance",
        min_value=date(1900, 1, 1),
        max_value=date_simul,
        value=date(1970, 1, 1),
    )
with col2:
    statut_label = st.selectbox("Statut", options=["Salarié (TS)", "Travailleur non salarié (TNS)"])
    statut = "TS" if statut_label.startswith("Salarié") else "TNS"

# ─────────────────────────────────────────────
# 6. Fiscalité en sortie
# ─────────────────────────────────────────────

st.header("6. Fiscalité en sortie")
col7, col8 = st.columns(2)
with col7:
    taux_arrerage = st.number_input(
        "Frais d'arrérages(%)",
        min_value=0.0,
        max_value=100.0,
        value=1.0,
        step=0.1,
        format="%.2f"
    ) /100 # On pense à diviser par 100 pour revenir à une proportion 

with col8:
    taux_PAS = st.number_input(
        "Taux de prélèvements à la source(%)",
        min_value=0.0,
        max_value=100.0,
        value=14.0,
        step=0.1,
        format="%.2f"
    ) /100 # idem

# ─────────────────────────────────────────────
# 7. PARAMÈTRES DE LA RENTE
# ─────────────────────────────────────────────
st.header("7. Paramètres de la rente")
col1, col2, col3 = st.columns(3)
with col1:
    type_rente = st.selectbox(
        "Type de rente",
        options=["classique", "reversion", "annuites", "reversion_annuites", "palier"],
        format_func=lambda x: {
            "classique": "Classique",
            "reversion": "Réversion",
            "annuites": "Annuités garanties",
            "reversion_annuites": "Réversion + Annuités",
            "palier": "Palier",
        }[x],
    )
with col2:
    taux = st.number_input("Taux technique (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.05) / 100
with col3:
    TE = st.selectbox("Terme de la rente", options=["Échu", "À échoir"])

frequence_label = st.selectbox(
    "Fréquence de versement",
    options=[
        "Annuelle (1/an)",
        "Semestrielle (2/an)",
        "Trimestrielle (4/an)",
        "Tous les 2 mois (6/an)",
        "Mensuelle (12/an)",
    ],
)
frequence_map = {
    "Annuelle (1/an)": 1,
    "Semestrielle (2/an)": 2,
    "Trimestrielle (4/an)": 4,
    "Tous les 2 mois (6/an)": 6,
    "Mensuelle (12/an)": 12,
}
m = frequence_map[frequence_label]



# ─────────────────────────────────────────────
# 8. PARAMÈTRES SPÉCIFIQUES AU TYPE DE RENTE
# ─────────────────────────────────────────────
kwargs = {"taux": taux, "TE": TE, "m": m}

if type_rente == "reversion":
    st.subheader("Paramètres de réversion")
    date_naissance_conjoint = st.date_input(
        "Date de naissance du conjoint",
        min_value=date(1900, 1, 1),
        max_value=date_simul,
        value=date(1970, 1, 1),
        key="conjoint",
    )
    kwargs["date_naissance_conjoint"] = date_naissance_conjoint

elif type_rente == "annuites":
    st.subheader("Paramètres annuités garanties")
    col1, col2 = st.columns(2)
    with col1:
        n = st.selectbox("Nombre d'annuités garanties (ans)", options=[5, 10, 15])
    with col2:
        alpha = st.number_input("Pourcentage garanti (%)", min_value=0.0, max_value=100.0, value=100.0, step=1.0) / 100
    kwargs["n"] = n
    kwargs["alpha"] = alpha

elif type_rente == "reversion_annuites":
    st.subheader("Paramètres réversion + annuités")
    col1, col2 = st.columns(2)
    with col1:
        date_naissance_conjoint = st.date_input(
            "Date de naissance du conjoint",
            min_value=date(1900, 1, 1),
            max_value=date_simul,
            value=date(1970, 1, 1),
            key="conjoint2",
        )
        alpha = st.number_input("Pourcentage de réversion (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0) / 100
    with col2:
        n = st.selectbox("Nombre d'annuités garanties (ans)", options=[5, 10, 15])
        beta = st.number_input("Pourcentage garanti (%)", min_value=0.0, max_value=100.0, value=100.0, step=1.0) / 100
    kwargs["date_naissance_conjoint"] = date_naissance_conjoint
    kwargs["alpha"] = alpha
    kwargs["n"] = n
    kwargs["beta"] = beta

# ─────────────────────────────────────────────
# 9. LANCEMENT DE LA SIMULATION
# ─────────────────────────────────────────────
st.divider()
if st.button("🔍 Lancer la simulation", type="primary", use_container_width=True):
    try:
        rente_brute, rente_nette = simulateur_rente(
            K1=K1,
            K2=K2,
            K3=K3,
            date_simul=date_simul,
            date_sortie=date_sortie,
            grille=grille,
            VV_mens=VV_mens,
            tau=tau,
            P=P,
            A0_deja_verse=A0_deja_verse,
            statut=statut,
            taux_vers=taux_vers,
            cotis_moins1=cotis_moins1,
            date_naissance=date_naissance,
            type_rente=type_rente,
            taux_arrerage=taux_arrerage,
            taux_PAS=taux_PAS,
            **kwargs,
        )
        st.success("Simulation effectuée avec succès !")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="🎯 Rente annuelle estimée brute", value=f"{rente_brute:,.2f} €")
        with col_res2:
            st.metric(label="🎯 Rente annuelle estimée nette", value=f"{rente_nette:,.2f} €")

    except Exception as e:
        import traceback
        st.error(f"Erreur : {e}")
        st.code(traceback.format_exc())  # ← affiche la stack trace complète
        # st.error(f"Erreur lors de la simulation : {e}")
