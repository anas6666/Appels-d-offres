import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIG ---
# Le secret pour éviter l'étirement : utiliser "centered" au lieu de "wide"
st.set_page_config(
    page_title="Portail AO | TargetUp Intelligence",
    page_icon="🎯",
    layout="centered" 
)

# --- 2. CSS OPTIMISÉ POUR LE RENDU DE L'IMAGE ---
st.markdown("""
<style>
    /* Importation des polices : Syne (titres larges) et DM Sans (texte) */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

    :root {
        --bg-color: #0b0f19; /* Fond très sombre, aspect premium */
        --surface: #111827;
        --border: rgba(255,255,255,0.08);
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --accent-red: #f43f5e;
        --accent-orange: #f97316;
    }

    /* Reset global du fond et texte */
    .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-main) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── CORRECTION DE L'ÉTIREMENT (BLOCK CONTAINER) ── */
    .block-container {
        max-width: 850px !important; /* Largeur parfaite pour la lisibilité */
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
        animation: fadeIn 0.8s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── HERO SECTION (Identique à la capture) ── */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(244, 63, 94, 0.05); /* Fond très discret */
        border: 1px solid rgba(244, 63, 94, 0.3); /* Bordure rouge subtile */
        color: #fb7185;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 6px 16px;
        border-radius: 50px;
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-family: 'Syne', sans-serif !important;
        font-size: 3.5rem !important; /* Très grand comme sur l'image */
        font-weight: 800 !important;
        line-height: 1.1 !important;
        letter-spacing: -0.02em !important;
        color: #ffffff !important;
        margin-bottom: 1.2rem !important;
    }

    .hero-title span {
        background: linear-gradient(90deg, #f43f5e, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: block; /* Force le retour à la ligne */
    }

    .hero-sub {
        font-size: 1.1rem;
        color: var(--text-muted);
        line-height: 1.6;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* ── STATS ROW (Identique à la capture) ── */
    .stat-row {
        display: flex;
        gap: 4rem; /* Grand espace entre les stats */
        margin-bottom: 3.5rem;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
    }
    .stat-num {
        font-family: 'Syne', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #f43f5e, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        letter-spacing: -0.03em;
    }
    .stat-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-top: 8px;
        font-weight: 500;
    }

    /* ── SÉPARATEURS DE SECTION ── */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 15px;
        margin: 3rem 0 2rem;
    }
    .section-divider-line {
        flex: 1;
        height: 1px;
        background: var(--border);
    }
    .section-divider-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #ffffff;
        white-space: nowrap;
    }

    /* ── BOITE MISE EN AVANT (AO Box) ── */
    .ao-box {
        background: rgba(244, 63, 94, 0.03);
        border: 1px solid rgba(244, 63, 94, 0.15);
        border-left: 3px solid var(--accent-red);
        padding: 20px 25px;
        border-radius: 8px;
        margin: 1.5rem 0;
    }
    .ao-box h4 {
        color: #fb7185;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .ao-box p {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: 0;
    }

    /* ── DESIGN DES INPUTS STREAMLIT ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        color: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-red) !important;
        box-shadow: 0 0 0 1px var(--accent-red) !important;
    }

    /* Labels des formulaires */
    label, .stRadio > label {
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    /* Design des boutons Radio */
    .stRadio > div { gap: 8px !important; }
    .stRadio > div > label {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 12px 15px !important;
        color: white !important;
        cursor: pointer;
    }
    .stRadio > div > label:hover {
        border-color: rgba(244, 63, 94, 0.5) !important;
    }

    /* ── BOUTON DE SOUMISSION ── */
    .stFormSubmitButton > button {
        background: linear-gradient(90deg, #f43f5e 0%, #f97316 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 16px 24px !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        width: 100% !important;
        margin-top: 2rem !important;
        transition: transform 0.2s ease !important;
    }
    .stFormSubmitButton > button:hover {
        transform: scale(1.01) !important;
    }

    /* Nettoyage UI Streamlit */
    #MainMenu, footer, header { visibility: hidden !important; }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.2rem !important; }
        .stat-row { gap: 2rem; flex-direction: column; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS SETUP ---
GOOGLE_SHEET_NAME = "Leads_Appels_Offres_Maroc"

@st.cache_resource
def init_google_sheets():
    scopes =[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # S'assurer que st.secrets contient bien la clé "gcp_service_account"
    if "gcp_service_account" in st.secrets:
        s_acc_info = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(s_acc_info, scopes=scopes)
        client = gspread.authorize(credentials)
        return client
    return None

# --- 4. DONNÉES (Listes déroulantes) ---
AO_CATEGORIES =[
    "Constructions & Gros Œuvre", "Génie Civil & Infrastructures",
    "Aménagement & Finition", "Électricité & Plomberie",
    "Nettoyage & Entretien", "Gardiennage & Sécurité",
    "Transport & Logistique", "Recrutement & Intérim",
    "Consulting & Audit", "Formation & Coaching",
    "IT Matériel & Réseau", "IT Logiciel & Digital",
    "Archivage & Numérisation", "Fournitures de Bureau & Impression",
    "Matériel Médical & Laboratoire", "Agroalimentaire & Restauration",
    "Événementiel & Communication", "Développement Social & ONG"
]

MOROCCAN_CITIES =[
    "Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir",
    "Fès", "Meknès", "Oujda", "Béni Mellal", "Nador", "Tétouan", "Autre"
]

FORBIDDEN_NAMES =[
    "n/a", "na", "anonyme", "confidentiel", "secret", "aucun", "rien",
    "test", "freelance", "particulier", "self employed", "independant", "x"
]

# --- 5. EN-TÊTE (HERO SECTION EXACTEMENT COMME L'IMAGE) ---
st.markdown('<div class="hero-badge">🎯 Accès gratuit · B2B uniquement</div>', unsafe_allow_html=True)

st.markdown("""
<div class="hero-title">
    Recevez vos<br>
    Appels d'Offres<br>
    <span>filtrés & automatisés.</span>
</div>
<div class="hero-sub">
    Accédez aux marchés publics de <strong>marchespublics.gov.ma</strong> et <strong>Tanmia</strong> directement dans votre boîte mail, filtrés selon votre secteur. En échange, aidez-nous à cartographier la maturité digitale des entreprises marocaines.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stat-row">
    <div class="stat-item"><div class="stat-num">2 400+</div><div class="stat-label">AO publiés chaque mois</div></div>
    <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Gratuit pour les entreprises</div></div>
    <div class="stat-item"><div class="stat-num">&lt; 2 min</div><div class="stat-label">Pour paramétrer vos alertes</div></div>
</div>
""", unsafe_allow_html=True)

# --- 6. LE FORMULAIRE ---
with st.form("lead_gen_form", clear_on_submit=False):

    # -- A. INFO ENTREPRISE --
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">A · Identification de l'entreprise</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Raison sociale *", placeholder="Ex: TargetUp SARL")
        secteur_entreprise = st.text_input("Secteur d'activité principal *", placeholder="Ex: BTP, IT, Consulting…")
        email = st.text_input("Email professionnel *", placeholder="contact@entreprise.ma")
        phone = st.text_input("Téléphone / WhatsApp *", placeholder="06 XX XX XX XX")
    with col2:
        city = st.selectbox("Ville du siège *", MOROCCAN_CITIES)
        effectif = st.selectbox("Effectif de l'entreprise *",["TPE (1-5)", "Petite (6-20)", "Moyenne (21-100)", "Grande (100+)"])
        ca_range = st.selectbox("Chiffre d'affaires annuel estimé *",["Moins de 500K DH", "500K - 2M DH", "2M - 10M DH", "10M - 50M DH", "Plus de 50M DH"])
        website = st.text_input("Site web (optionnel)", placeholder="www.entreprise.ma")

    # -- B. CIBLAGE AO --
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">B · Ciblage des Appels d'Offres</div>
        <div class="section-divider-line"></div>
    </div>
    
    <div class="ao-box">
        <h4>🎯 Catégories cibles</h4>
        <p>Sélectionnez les secteurs. Vous recevrez uniquement les AO correspondants chaque matin.</p>
    </div>
    """, unsafe_allow_html=True)

    tags = st.multiselect(
        "Secteurs d'Appels d'Offres souhaités *",
        options=AO_CATEGORIES,
        label_visibility="collapsed",
        placeholder="Choisissez vos secteurs cibles…"
    )

    # -- C. MATURITÉ DIGITALE & IA --
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">C · Étude IA & Automatisation</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_ao_management = st.radio("1. Comment gérez-vous actuellement votre veille AO ?",[
        "Recherche manuelle sur le portail de l'Etat",
        "Abonnement payant à un service de veille existant",
        "Pas de veille structurée"
    ])
    
    q_ai_usage = st.selectbox("2. À quelle fréquence utilisez-vous l'Intelligence Artificielle en entreprise ?",[
        "Jamais", "Quelques tests isolés", "Utilisation régulière (rédaction, recherche)", "Pleinement intégrée"
    ])

    q_lowcode = st.radio("3. Connaissez-vous les outils Low-Code (n8n, Make, Zapier…) ?", [
        "Non", "Oui de nom, mais sans utilisation", "Oui, nous les utilisons"
    ])

    q_top_pain = st.selectbox("4. Quel est votre principal goulot d'étranglement opérationnel ?",[
        "Veille et lecture des CPS d'Appels d'Offres",
        "Saisie manuelle des données (Devis, factures)",
        "Suivi commercial et relance client",
        "Recrutement et tri des candidatures",
        "Autre"
    ])

    q_time_lost = st.selectbox("5. Combien d'heures par semaine estimez-vous perdre sur des tâches manuelles ?",[
        "Moins de 5 heures", "5 à 10 heures", "10 à 20 heures", "Plus de 20 heures"
    ])

    q_cps_ai = st.radio("6. Seriez-vous intéressé par une IA qui extrait automatiquement le Dossier Technique du CPS ?",[
        "Pas intéressé", "Oui, si c'est gratuit", "Oui, prêt à payer un abonnement pour cela"
    ])

    q_dream_automation = st.text_area(
        "7. Si l'IA pouvait exécuter UNE seule tâche répétitive à votre place dès demain, laquelle serait-elle ? *",
        placeholder="Ex: Analyser les CPS et me lister les pièces administratives à fournir...",
        height=100
    )

    submitted = st.form_submit_button(
        "✦ ACTIVER MES ALERTES GRATUITES",
        use_container_width=True
    )

# --- 7. VALIDATION & SOUMISSION GOOGLE SHEETS ---
if submitted:
    company_clean = company_name.strip().lower()

    if not all([company_name, secteur_entreprise, email, phone, tags, q_dream_automation]):
        st.error("⚠️ Veuillez remplir tous les champs obligatoires (*).")
    elif company_clean in FORBIDDEN_NAMES or len(company_clean) < 2:
        st.error("❌ Nom d'entreprise invalide. Ce service B2B nécessite une Raison Sociale réelle.")
    elif "@" not in email:
        st.error("❌ Adresse email invalide.")
    else:
        try:
            with st.spinner("Création de vos alertes personnalisées..."):
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                secteurs_ao_str = ", ".join(tags)
                site_web = website if website else "N/A"

                row_to_insert =[
                    current_time, company_name, secteur_entreprise, site_web, city, 
                    effectif, ca_range, email, phone, secteurs_ao_str,
                    q_ao_management, q_ai_usage, q_lowcode, q_top_pain, 
                    q_time_lost, q_cps_ai, q_dream_automation
                ]

                gc = init_google_sheets()
                if gc:
                    sheet = gc.open(GOOGLE_SHEET_NAME).sheet1
                    sheet.append_row(row_to_insert)
                    st.success("✅ Félicitations ! Votre profil est validé. Vous allez recevoir vos Appels d'Offres d'ici demain matin.")
                    st.balloons()
                else:
                    # Rendu local si les clés Google ne sont pas encore configurées
                    st.success("✅ [Mode Test] Formulaire validé ! (Assurez-vous de configurer st.secrets pour Google Sheets).")
                    
        except Exception as e:
            st.error(f"Erreur de connexion à Google Sheets. Détails techniques : {e}")
