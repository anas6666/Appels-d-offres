import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Portail AO",
    page_icon="🎯",
    layout="wide"
)

# --- 2. CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    :root {
        --ink: #0a0a0f;
        --ink2: #14141e;
        --surface: #13131d;
        --border: rgba(255,255,255,0.07);
        --muted: #6b7280;
        --accent: #e63153;
        --accent2: #f97316;
        --text: #e8e8f0;
        --text-soft: #9ca3af;
    }

    /* ── GLOBAL RESET ── */
    html, body, [class*="css"] {
        background-color: var(--ink) !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .main > div {
        display: flex;
        justify-content: center;
    }

    .main .block-container {
        width: 100% !important;
        max-width: 680px !important;
        min-width: 0 !important;
        padding: 2.5rem 1.5rem 6rem !important;
        animation: pageIn 0.9s cubic-bezier(0.16,1,0.3,1) both;
        box-sizing: border-box;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    @keyframes pageIn {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── HERO ── */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(230,49,83,0.12);
        border: 1px solid rgba(230,49,83,0.3);
        color: #f87196;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 5px 14px;
        border-radius: 999px;
        margin-bottom: 1.4rem;
    }

    .hero-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.01em !important;
        color: #f1f1f8 !important;
        margin-bottom: 1rem !important;
        max-width: 600px;
        text-rendering: optimizeLegibility;
    }

    .hero-title span {
        background: linear-gradient(90deg, #e63153, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
    }

    .hero-sub {
        font-size: 1.05rem;
        color: var(--text-soft);
        line-height: 1.65;
        max-width: 100%;
        margin-bottom: 2rem;
    }

    .stat-row {
        display: flex;
        gap: 2rem;
        margin: 1.8rem 0 2.5rem;
        flex-wrap: wrap;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
    }
    .stat-num {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.9rem;
        font-weight: 800;
        background: linear-gradient(90deg, #e63153, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.78rem;
        color: var(--text-soft);
        margin-top: 3px;
        letter-spacing: 0.03em;
    }

    /* ── DIVIDER ── */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 2.5rem 0 1.5rem;
    }
    .section-divider-line {
        flex: 1;
        height: 1px;
        background: var(--border);
    }
    .section-divider-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--muted);
        white-space: nowrap;
    }

    /* ── AO TARGETING BOX ── */
    div.element-container:has(.ao-targeting-marker) {
        display: none !important;
    }

    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)) {
        background: linear-gradient(135deg, #2a0d14 0%, #1a0a0f 100%) !important;
        border: 1px solid rgba(230,49,83,0.35) !important;
        border-left: 4px solid #e63153 !important;
        border-radius: 12px !important;
        padding: 22px 26px 26px 26px !important;
        margin: 1.5rem 0 2rem 0 !important;
        position: relative;
        overflow: hidden;
        transition: all 0.25s ease;
    }
    
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker))::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 20% 0%, rgba(230,49,83,0.25), transparent 60%);
        pointer-events: none;
    }
    
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker))::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(230,49,83,0.08), transparent 60%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)):hover::after {
        opacity: 1;
    }
    
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)):hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(230,49,83,0.25);
    }
    
    .ao-box-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ff4d6d;
        margin-bottom: 0.3rem;
    }
    
    .ao-box-desc {
        color: #c7c9d1;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }

    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)) .stMultiSelect {
        margin-bottom: 0;
    }
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)) .stMultiSelect[data-baseweb="select"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.92rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    /* Styling for invalid fields - Note: This needs to be applied to specific Streamlit elements,
       which is hard to do dynamically from Python without JS injection or modifying Streamlit's internals.
       For now, we will rely on st.error messages.
    */
    .is-invalid input, .is-invalid textarea, .is-invalid div[data-baseweb="select"] {
        border-color: #ff4d6d !important; /* Red border for invalid fields */
        box-shadow: 0 0 0 3px rgba(255, 77, 109, 0.2) !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(230,49,83,0.5) !important;
        box-shadow: 0 0 0 3px rgba(230,49,83,0.1) !important;
    }

    label, .stRadio > label, .stCheckbox > label {
        color: var(--text-soft) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em !important;
    }

    .stRadio > div {
        gap: 6px !important;
    }
    .stRadio > div > label {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        transition: border-color 0.2s ease, background 0.2s ease !important;
        color: var(--text) !important;
        font-size: 0.88rem !important;
        cursor: pointer;
    }
    .stRadio > div > label:hover {
        border-color: rgba(230,49,83,0.4) !important;
        background: rgba(230,49,83,0.05) !important;
    }

    /* Evite que les radios soient sélectionnées par défaut en cachant l'outline si vide */
    .stRadio > div > label[data-baseweb="radio"] input:checked + div {
        background-color: var(--accent) !important;
        border-color: var(--accent) !important;
    }

    .stFormSubmitButton > button, .stButton > button {
        background: linear-gradient(135deg, #e63153 0%, #c91d41 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(230,49,83,0.3) !important;
        width: 100% !important;
        margin-top: 1.5rem !important;
    }
    .stFormSubmitButton > button:hover, .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(230,49,83,0.45) !important;
        background: linear-gradient(135deg, #f0365a 0%, #d42246 100%) !important;
    }

    .stAlert {
        border-radius: 10px !important;
        border-left-width: 3px !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .footer-note {
        text-align: center;
        font-size: 0.78rem;
        color: var(--muted);
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border);
    }

    #MainMenu, footer, header { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS SETUP ---
GOOGLE_SHEET_NAME = "Leads_Appels_Offres_Maroc"
WORKSHEET_NAME = "Main" # Define worksheet name globally

@st.cache_resource
def init_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    service_account_info = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=scopes
    )

    client = gspread.authorize(credentials)
    spreadsheet = client.open(GOOGLE_SHEET_NAME)

    try:
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows="1000",
            cols="30"
        )
    return client, worksheet # Return both client and worksheet

# --- 4. DATA ---
AO_CATEGORIES =[
    "Constructions & Gros Œuvre", "Génie Civil & Infrastructures",
    "Aménagement & Finition", "Électricité & Plomberie",
    "Nettoyage & Entretien", "Gardiennage & Sécurité",
    "Transport & Logistique", "Recrutement & Intérim",
    "Consulting & Audit", "Formation & Coaching",
    "IT Matériel & Réseau", "IT Logiciel & Digital",
    "Archivage & Numérisation", "Fournitures de Bureau & Impression",
    "Matériel Médical & Laboratoire", "Agroalimentaire & Restauration",
    "Événementiel & Communication", "Développement Social & ONG",
    "Énergie & Environnement", "Immobilier & Promotion",
    "Santé & Pharmaceutique", "Juridique & Notarial",
    "Agriculture & Irrigation", "Télécommunications",
]

MOROCCAN_CITIES =[
    "Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir",
    "Fès", "Meknès", "Oujda", "Béni Mellal", "Nador",
    "Tétouan", "El Jadida", "Safi", "Kénitra", "Mohammadia",
    "Khouribga", "Settat", "Laâyoune", "Dakhla", "Errachidia",
    "Ifrane", "Khénifra", "Taza", "Tiznit", "Ouarzazate",
    "Al Hoceïma", "Larache", "Guelmim", "Berrechid", "Salé",
    "Temara", "Ain Sebaa", "Hay Hassani", "Autre",
]

SECTEURS_ENTREPRISE = sorted([
    "Agriculture & Agroalimentaire",
    "Automobile & Pièces détachées",
    "Banque & Assurance",
    "BTP & Construction",
    "Chimie & Pharmacie",
    "Commerce & Distribution",
    "Conseil & Études",
    "Éducation & Formation",
    "Énergie & Environnement",
    "Hôtellerie & Restauration",
    "Immobilier & Promotion",
    "Industrie Manufacturière",
    "Informatique & Télécoms",
    "Logistique & Transport",
    "Marketing & Communication",
    "Médias & Édition",
    "Médical & Santé",
    "Services aux Entreprises",
    "Textile & Habillement",
    "Tourisme & Loisirs",
])

FORBIDDEN_PHRASES =[
    "n/a", "na", "anonyme", "confidentiel", "secret", "aucun", "rien",
    "test", "freelance", "particulier", "self employed", "independant",
    "indépendant", "x", "xxx", "-", "none", "null", ""
] # Added empty string to forbidden phrases

# --- 5. HERO ---
st.markdown('<div class="hero-badge">🎯 Accès gratuit </div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-title">
    Recevez vos Appels d'Offres<br><span>filtrés & automatisés.</span>
</div>
<div class="hero-sub">
    Accédez aux marchés publics de <strong style="color:#e8e8f0">Marchespublics</strong>, <strong style="color:#e8e8f0">Tanmia</strong>, <strong style="color:#e8e8f0">CDG</strong>, 
    <strong style="color:#e8e8f0">Bank Al-Maghrib</strong>, <strong style="color:#e8e8f0">ONCF</strong>, <strong style="color:#e8e8f0">RAM</strong>, <strong style="color:#e8e8f0">United Nations</strong>, ... directement dans votre boîte mail, filtrés selon votre secteur, <strong style="color:#e8e8f0">chaque matin à 8:00h (GMT+1).</strong> 
    <br>
    Chaque appel d’offres inclus :
    <ul>
      <li><strong style="color:#e8e8f0">Le nom du projet</strong></li>
      <li><strong style="color:#e8e8f0">La date limite</strong></li>
      <li><strong style="color:#e8e8f0">La localisation</strong></li>
      <li><strong style="color:#e8e8f0">L’organisme émetteur</strong></li>
      <li><strong style="color:#e8e8f0">Le budget estimé</strong></li>
      <li><strong style="color:#e8e8f0">La caution</strong></li>
    </ul>
    En échange, aidez-nous à cartographier la maturité digitale des entreprises marocaines.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stat-row">
    <div class="stat-item"><div class="stat-num">2 400+</div><div class="stat-label">AO publiés chaque mois</div></div>
    <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Gratuit pour les entreprises</div></div>
    <div class="stat-item"><div class="stat-num">&lt; 2 min</div><div class="stat-label">Pour paramétrer vos alertes</div></div>
</div>
""", unsafe_allow_html=True)

# --- 6. FORM (Utilisation de st.container pour l'interactivité dynamique) ---
# Use session state to manage error messages for each field
if 'errors' not in st.session_state:
    st.session_state.errors = {}

def validate_field(field_value, field_name, custom_forbidden=None):
    if custom_forbidden is None:
        custom_forbidden = FORBIDDEN_PHRASES
    
    # Check for None or empty string first for general required field check
    if field_value is None or (isinstance(field_value, str) and field_value.strip() == ""):
        return f"Le champ '{field_name}' est obligatoire."
    
    # For lists (multiselect), check if it's empty
    if isinstance(field_value, list) and not field_value:
        return f"Le champ '{field_name}' est obligatoire."

    # Check for forbidden phrases (case-insensitive and strip whitespace)
    if isinstance(field_value, str) and field_value.strip().lower() in [f.lower() for f in custom_forbidden]:
        return f"Le champ '{field_name}' contient une valeur invalide ('{field_value.strip()}')."
    
    # Specific check for multiselect where an empty list is considered invalid
    if isinstance(field_value, list) and not field_value:
        return f"Veuillez sélectionner au moins une option pour '{field_name}'."
    
    return None # No error


with st.container():

    # ── BLOCK A : ENTERPRISE INFO ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">A · Identification de l'entreprise</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        company_name     = st.text_input("Raison sociale *", placeholder="")
        if st.session_state.errors.get('company_name'): st.error(st.session_state.errors['company_name'])

        secteur_entreprise = st.selectbox("Secteur d'activité principal *", SECTEURS_ENTREPRISE, index=None, placeholder="Sélectionnez...")
        if st.session_state.errors.get('secteur_entreprise'): st.error(st.session_state.errors['secteur_entreprise'])

        email            = st.text_input("Email *", placeholder="")
        if st.session_state.errors.get('email'): st.error(st.session_state.errors['email'])

        phone            = st.text_input("Téléphone / WhatsApp *", placeholder="")
        if st.session_state.errors.get('phone'): st.error(st.session_state.errors['phone'])

    with col2:
        city             = st.selectbox("Ville du siège *", MOROCCAN_CITIES, index=None, placeholder="Sélectionnez...")
        if st.session_state.errors.get('city'): st.error(st.session_state.errors['city'])

        effectif         = st.selectbox("Effectif de l'entreprise *",[
            "Auto-entrepreneur / TPE (1-5 personnes)",
            "Petite entreprise (6-20 personnes)",
            "Moyenne entreprise (21-100 personnes)",
            "Grande entreprise (100-500 personnes)",
            "Groupe / Holding (500+ personnes)",
        ], index=None, placeholder="Sélectionnez...")
        if st.session_state.errors.get('effectif'): st.error(st.session_state.errors['effectif'])

        age_entreprise   = st.selectbox("Ancienneté de l'entreprise *",[
            "Moins d'un an", "1 à 3 ans", "3 à 7 ans", "7 à 15 ans", "Plus de 15 ans"
        ], index=None, placeholder="Sélectionnez...")
        if st.session_state.errors.get('age_entreprise'): st.error(st.session_state.errors['age_entreprise'])

        website          = st.text_input("Site web (optionnel)", placeholder="www.entreprise.ma")
        # No error for optional field

    ca_range = st.selectbox("Chiffre d'affaires annuel estimé *",[
        "Moins de 500 000 DH",
        "500 000 – 2 000 000 DH",
        "2 000 000 – 10 000 000 DH",
        "10 000 000 – 50 000 000 DH",
        "Plus de 50 000 000 DH",
        "Préfère ne pas répondre",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('ca_range'): st.error(st.session_state.errors['ca_range'])

    role_respondant = st.selectbox("Votre fonction dans l'entreprise *",[
        "Dirigeant / PDG / Associé",
        "Directeur général ou adjoint",
        "Directeur commercial / Business developer",
        "Responsable administratif & financier",
        "Responsable IT / DSI",
        "Chef de projet / Manager",
        "Autre",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('role_respondant'): st.error(st.session_state.errors['role_respondant'])

    # ── BLOCK B : AO TARGETING ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">B · Appels d'offres</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<span class="ao-targeting-marker"></span>', unsafe_allow_html=True)
    
        st.markdown("""
            <div class="ao-box-title">Ciblage de vos Appels d'Offres</div>
            <div class="ao-box-desc">Sélectionnez un ou plusieurs secteurs. Vous recevrez uniquement les AO correspondants, chaque matin par email.</div>
        """, unsafe_allow_html=True)
    
        tags = st.multiselect(
            "Secteurs d'Appels d'Offres souhaités *",
            options=AO_CATEGORIES,
            label_visibility="collapsed",
            placeholder="Choisissez vos secteurs cibles…"
        )
        if st.session_state.errors.get('tags'): st.error(st.session_state.errors['tags'])

        Email_Newsletter =  st.text_input("Email de réception des appels d’offres *", placeholder="")
        if st.session_state.errors.get('Email_Newsletter'): st.error(st.session_state.errors['Email_Newsletter'])

    q_ao_freq = st.selectbox("Combien d'AO soumettez-vous en moyenne par mois ?",[
        "Nous ne participons pas encore aux AO",
        "1 à 3 AO/mois", "4 à 10 AO/mois", "Plus de 10 AO/mois",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_ao_freq'): st.error(st.session_state.errors['q_ao_freq'])

    q_ao_management = st.radio("Comment gérez-vous actuellement votre veille AO ?",[
        "Recherche manuelle et irrégulière",
        "Une personne dédiée à la veille",
        "Abonnement à un service de veille",
        "Pas de veille structurée",
    ], index=None)
    if st.session_state.errors.get('q_ao_management'): st.error(st.session_state.errors['q_ao_management'])


    q_ao_time = st.selectbox("Combien de temps passez-vous à préparer un dossier de soumission ?",[
        "Moins de 2 jours",
        "2 à 5 jours ouvrés",
        "1 à 2 semaines",
        "Plus de 2 semaines",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_ao_time'): st.error(st.session_state.errors['q_ao_time'])

    q_ao_pain = st.selectbox("Quel est votre principal défi sur les Appels d'Offres ?",[
        "Trouver les AO pertinents à temps",
        "Lire et comprendre le CPS (Cahier des Prescriptions Spéciales)",
        "Constituer le dossier administratif",
        "Estimer le prix et préparer l'offre financière",
        "Assurer la conformité documentaire",
        "Manque de ressources humaines dédiées",
        "Autre", # Added "Autre" option here
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_ao_pain'): st.error(st.session_state.errors['q_ao_pain'])


    # Conditionally show text input if "Autre" is selected for q_ao_pain
    q_ao_pain_autre = ""
    if q_ao_pain == "Autre":
        q_ao_pain_autre = st.text_input("Veuillez préciser votre principal défi sur les Appels d'Offres *", placeholder="Décrivez votre défi...")
        if st.session_state.errors.get('q_ao_pain_autre'): st.error(st.session_state.errors['q_ao_pain_autre'])


    q_ao_win_rate = st.selectbox("Quel est votre taux de succès estimé sur vos soumissions AO ?",[
        "Je ne sais pas / pas de suivi",
        "Moins de 10%", "10% à 25%", "25% à 50%", "Plus de 50%",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_ao_win_rate'): st.error(st.session_state.errors['q_ao_win_rate'])


    # ── BLOCK C : AI & DIGITAL MATURITY ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">C · Maturité IA & Digitale</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_ai_usage = st.selectbox("À quelle fréquence utilisez-vous l'Intelligence Artistificielle en entreprise ?",[
        "Jamais — nous n'avons pas encore exploré",
        "Quelques tests individuels (ChatGPT personnel…)",
        "Utilisation régulière sur certains postes (rédaction, recherche)",
        "IA intégrée dans au moins un processus métier",
        "IA centrale dans notre stratégie opérationnelle",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_ai_usage'): st.error(st.session_state.errors['q_ai_usage'])

    q_ai_tools = st.multiselect("Quels outils IA utilisez-vous actuellement ? (plusieurs choix possibles)",[
        "ChatGPT / GPT-4", "Claude (Anthropic)", "Gemini (Google)",
        "Copilot (Microsoft)", "Midjourney / DALL-E (images)",
        "Outils IA intégrés dans des logiciels métiers",
        "IA développée en interne", "Aucun outil IA pour l'instant",
    ], placeholder="Sélectionnez…")
    # This is an optional field if "Aucun outil IA pour l'instant" is selected, otherwise it requires a selection.
    # We will handle validation in the main submission block.

    q_lowcode = st.radio("Connaissez-vous les outils d'automatisation Low-Code (n8n, Make, Zapier…) ?",[
        "Non, première fois que j'en entends parler",
        "Oui de nom, mais sans utilisation concrète",
        "Oui, nous les utilisons occasionnellement",
        "Oui, ils sont intégrés dans nos processus",
    ], index=None)
    if st.session_state.errors.get('q_lowcode'): st.error(st.session_state.errors['q_lowcode'])


    q_data_infra = st.radio("Comment gérez-vous vos données clients et opérationnelles ?",[
        "Fichiers Excel / Google Sheets uniquement",
        "CRM basique (HubSpot free, Zoho…)",
        "ERP ou CRM avancé (Odoo, SAP, Dynamics…)",
        "Base de données ou infra BI dédiée",
        "Pas de gestion structurée",
    ], index=None)
    if st.session_state.errors.get('q_data_infra'): st.error(st.session_state.errors['q_data_infra'])

    q_digital_tools =  st.text_input("Quels outils digitaux sont déjà en place dans votre entreprise ? *", placeholder="")
    if st.session_state.errors.get('q_digital_tools'): st.error(st.session_state.errors['q_digital_tools'])
    
    # ── BLOCK D : PAIN POINTS ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">D · Points de friction</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_top_pain_problem = st.text_input("Quel est votre problèmes opérationnelles actuellement ? *", placeholder="Décrivez votre situation...") # Renamed to avoid clash with q_ao_pain
    if st.session_state.errors.get('q_top_pain_problem'): st.error(st.session_state.errors['q_top_pain_problem'])


    q_time_lost = st.selectbox("Combien d'heures par semaine estimez-vous perdre sur des tâches manuelles ?",[
        "Moins de 5 heures",
        "5 à 10 heures",
        "10 à 20 heures",
        "Plus de 20 heures par semaine",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_time_lost'): st.error(st.session_state.errors['q_time_lost'])

    q_priority_dept = st.selectbox("Quel département bénéficierait le plus d'une automatisation ?",[
        "Commercial & Business Development",
        "Administration & Finances",
        "Opérations & Production",
        "RH & Recrutement",
        "IT & Systèmes",
        "Direction Générale",
        "Juridique & Conformité",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_priority_dept'): st.error(st.session_state.errors['q_priority_dept'])

    q_existing_automation = st.radio("Avez-vous déjà automatisé un processus dans votre entreprise ?",[
        "Non, tout est encore manuel",
        "Oui, quelques automatisations simples (alertes, rappels…)",
        "Oui, des workflows complets sont automatisés",
        "Oui, nous avons une stratégie d'automatisation active",
    ], index=None)
    if st.session_state.errors.get('q_existing_automation'): st.error(st.session_state.errors['q_existing_automation'])

    q_dream_automation = st.text_area(
        "Si l'IA pouvait exécuter UNE seule tâche à votre place dès demain, laquelle serait-elle ? *",
        placeholder="Ex: Analyser automatiquement les CPS et me sortir un résumé en 5 points clés avec les dates limites…",
        height=90,
    )
    if st.session_state.errors.get('q_dream_automation'): st.error(st.session_state.errors['q_dream_automation'])


    # ── BLOCK E : BUDGET & STRATEGIC FIT ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">E · Budget & Décision</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_budget = st.selectbox("Budget annuel alloué à la digitalisation & logiciels métiers ?",[
        "Moins de 10 000 DH",
        "10 000 – 50 000 DH",
        "50 000 – 200 000 DH",
        "200 000 – 500 000 DH",
        "Plus de 500 000 DH",
        "Pas encore de budget alloué",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_budget'): st.error(st.session_state.errors['q_budget'])


    q_barrier = st.selectbox("Principal frein à l'adoption de nouvelles technologies dans votre entreprise ?",[
        "Coût d'acquisition perçu comme élevé",
        "Complexité d'utilisation / manque de formation",
        "Temps de mise en place et d'intégration",
        "Résistance au changement des équipes",
        "Manque de cas d'usage concrets et prouvés au Maroc",
        "Défiance envers les données et la confidentialité",
        "Pas de frein majeur identifié",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_barrier'): st.error(st.session_state.errors['q_barrier'])

    q_timeline = st.selectbox("Dans quel délai envisagez-vous un investissement en automatisation/IA ?",[
        "Immédiatement — nous cherchons une solution",
        "Dans les 3 prochains mois",
        "Dans les 6 prochains mois",
        "Dans l'année",
        "Pas de projet concret pour l'instant",
    ], index=None, placeholder="Sélectionnez...")
    if st.session_state.errors.get('q_timeline'): st.error(st.session_state.errors['q_timeline'])


    # ── BLOCK F : INTEREST & NEXT STEP ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">F · Intérêt & Prochaine étape</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_cps_ai = st.radio("Seriez-vous intéressé par une IA qui lit le CPS à votre place et extrait le Dossier Technique ?",[
        "Pas intéressé pour l'instant",
        "Oui",
    ], index=None)
    if st.session_state.errors.get('q_cps_ai'): st.error(st.session_state.errors['q_cps_ai'])

    q_pilot = st.radio("Seriez-vous ouvert à tester une automatisation sur-mesure (Proof of Concept) ?",[
        "Oui, absolument",
        "Non, pas pour le moment",
    ], index=None)
    if st.session_state.errors.get('q_pilot'): st.error(st.session_state.errors['q_pilot'])


    q_comment = st.text_area(
        "Un commentaire libre, une question, ou une idée d'automatisation que vous souhaitez explorer ? (optionnel)",
        placeholder="Toute remarque est précieuse — nous lisons chaque réponse.",
        height=80,
    )

    submitted = st.button(
        "✦  Activer mes alertes AO personnalisées",
        use_container_width=True
    )

# --- 7. VALIDATION & SUBMISSION ---
if submitted:
    st.session_state.errors = {} # Clear previous errors on new submission

    # Perform validation for each required field
    # (variable, display_name, forbidden_phrases_list)
    validation_checks = [
        (company_name, "Raison sociale"),
        (secteur_entreprise, "Secteur d'activité principal"),
        (email, "Email"),
        (phone, "Téléphone / WhatsApp"),
        (city, "Ville du siège"),
        (effectif, "Effectif de l'entreprise"),
        (age_entreprise, "Ancienneté de l'entreprise"),
        (ca_range, "Chiffre d'affaires annuel estimé"),
        (role_respondant, "Votre fonction dans l'entreprise"),
        (tags, "Secteurs d'Appels d'Offres souhaités"),
        (Email_Newsletter, "Email de réception des appels d’offres"),
        (q_ao_freq, "Combien d'AO soumettez-vous en moyenne par mois ?"),
        (q_ao_management, "Comment gérez-vous actuellement votre veille AO ?"),
        (q_ao_time, "Combien de temps passez-vous à préparer un dossier de soumission ?"),
        (q_ao_pain, "Quel est votre principal défi sur les Appels d'Offres ?"),
        (q_ao_win_rate, "Quel est votre taux de succès estimé sur vos soumissions AO ?"),
        (q_ai_usage, "À quelle fréquence utilisez-vous l'Intelligence Artistificielle en entreprise ?"),
        (q_lowcode, "Connaissez-vous les outils d'automatisation Low-Code (n8n, Make, Zapier…) ?"),
        (q_data_infra, "Comment gérez-vous vos données clients et opérationnelles ?"),
        (q_digital_tools, "Quels outils digitaux sont déjà en place dans votre entreprise ?"),
        (q_top_pain_problem, "Votre problèmes opérationnelles actuellement"), # Renamed field
        (q_time_lost, "Combien d'heures par semaine estimez-vous perdre sur des tâches manuelles ?"),
        (q_priority_dept, "Quel département bénéficierait le plus d'une automatisation ?"),
        (q_existing_automation, "Avez-vous déjà automatisé un processus dans votre entreprise ?"),
        (q_dream_automation, "Si l'IA pouvait exécuter UNE seule tâche à votre place dès demain, laquelle serait-elle ?"),
        (q_budget, "Budget annuel alloué à la digitalisation & logiciels métiers ?"),
        (q_barrier, "Principal frein à l'adoption de nouvelles technologies dans votre entreprise ?"),
        (q_timeline, "Dans quel délai envisagez-vous un investissement en automatisation/IA ?"),
        (q_cps_ai, "Seriez-vous intéressé par une IA qui lit le CPS à votre place et extrait le Dossier Technique ?"),
        (q_pilot, "Seriez-vous ouvert à tester une automatisation sur-mesure (Proof of Concept) ?"),
    ]

    # Specific check for q_ao_pain_autre if "Autre" is selected
    if q_ao_pain == "Autre":
        validation_checks.append((q_ao_pain_autre, "Précisez votre défi AO"))

    # Populate errors dictionary
    for var, name in validation_checks:
        error_message = validate_field(var, name)
        if error_message:
            # Dynamically store error based on the original variable name
            # This requires knowing the variable name string, which is not ideal.
            # A more robust way is to pass a unique key for each widget to st.session_state.errors
            # For simplicity, we'll use a direct mapping for now.
            if name == "Raison sociale": st.session_state.errors['company_name'] = error_message
            elif name == "Secteur d'activité principal": st.session_state.errors['secteur_entreprise'] = error_message
            elif name == "Email": st.session_state.errors['email'] = error_message
            elif name == "Téléphone / WhatsApp": st.session_state.errors['phone'] = error_message
            elif name == "Ville du siège": st.session_state.errors['city'] = error_message
            elif name == "Effectif de l'entreprise": st.session_state.errors['effectif'] = error_message
            elif name == "Ancienneté de l'entreprise": st.session_state.errors['age_entreprise'] = error_message
            elif name == "Chiffre d'affaires annuel estimé": st.session_state.errors['ca_range'] = error_message
            elif name == "Votre fonction dans l'entreprise": st.session_state.errors['role_respondant'] = error_message
            elif name == "Secteurs d'Appels d'Offres souhaités": st.session_state.errors['tags'] = error_message
            elif name == "Email de réception des appels d’offres": st.session_state.errors['Email_Newsletter'] = error_message
            elif name == "Combien d'AO soumettez-vous en moyenne par mois ?": st.session_state.errors['q_ao_freq'] = error_message
            elif name == "Comment gérez-vous actuellement votre veille AO ?": st.session_state.errors['q_ao_management'] = error_message
            elif name == "Combien de temps passez-vous à préparer un dossier de soumission ?": st.session_state.errors['q_ao_time'] = error_message
            elif name == "Quel est votre principal défi sur les Appels d'Offres ?": st.session_state.errors['q_ao_pain'] = error_message
            elif name == "Précisez votre défi AO": st.session_state.errors['q_ao_pain_autre'] = error_message
            elif name == "Quel est votre taux de succès estimé sur vos soumissions AO ?": st.session_state.errors['q_ao_win_rate'] = error_message
            elif name == "À quelle fréquence utilisez-vous l'Intelligence Artistificielle en entreprise ?": st.session_state.errors['q_ai_usage'] = error_message
            elif name == "Connaissez-vous les outils d'automatisation Low-Code (n8n, Make, Zapier…) ?": st.session_state.errors['q_lowcode'] = error_message
            elif name == "Comment gérez-vous vos données clients et opérationnelles ?": st.session_state.errors['q_data_infra'] = error_message
            elif name == "Quels outils digitaux sont déjà en place dans votre entreprise ?": st.session_state.errors['q_digital_tools'] = error_message
            elif name == "Votre problèmes opérationnelles actuellement": st.session_state.errors['q_top_pain_problem'] = error_message
            elif name == "Combien d'heures par semaine estimez-vous perdre sur des tâches manuelles ?": st.session_state.errors['q_time_lost'] = error_message
            elif name == "Quel département bénéficierait le plus d'une automatisation ?": st.session_state.errors['q_priority_dept'] = error_message
            elif name == "Avez-vous déjà automatisé un processus dans votre entreprise ?": st.session_state.errors['q_existing_automation'] = error_message
            elif name == "Si l'IA pouvait exécuter UNE seule tâche à votre place dès demain, laquelle serait-elle ?": st.session_state.errors['q_dream_automation'] = error_message
            elif name == "Budget annuel alloué à la digitalisation & logiciels métiers ?": st.session_state.errors['q_budget'] = error_message
            elif name == "Principal frein à l'adoption de nouvelles technologies dans votre entreprise ?": st.session_state.errors['q_barrier'] = error_message
            elif name == "Dans quel délai envisagez-vous un investissement en automatisation/IA ?": st.session_state.errors['q_timeline'] = error_message
            elif name == "Seriez-vous intéressé par une IA qui lit le CPS à votre place et extrait le Dossier Technique ?": st.session_state.errors['q_cps_ai'] = error_message
            elif name == "Seriez-vous ouvert à tester une automatisation sur-mesure (Proof of Concept) ?": st.session_state.errors['q_pilot'] = error_message
            
    # Additional specific validations
    if not st.session_state.errors.get('email') and "@" not in email or "." not in email.split("@")[-1]:
        st.session_state.errors['email'] = "L'adresse email semble invalide. Veuillez vérifier."

    if not st.session_state.errors.get('company_name') and (company_clean in [f.lower() for f in FORBIDDEN_PHRASES] or len(company_clean) < 2):
        st.session_state.errors['company_name'] = "Veuillez entrer un nom d'entreprise valide. Ce service est réservé aux structures B2B identifiées."


    if st.session_state.errors:
        st.error("⚠️ Veuillez corriger les erreurs dans le formulaire.")
        st.rerun() # Rerun to display errors next to fields
    else:
        try:
            with st.spinner("Enregistrement en cours…"):
                client_gs, worksheet_gs = init_google_sheets() # Get both client and worksheet
                current_time       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                secteurs_ao_str    = ", ".join(tags)
                ai_tools_str       = ", ".join(q_ai_tools) if q_ai_tools else "Aucun"
                
                digital_tools_str  = q_digital_tools if q_digital_tools else "Non renseigné" # Ensure it's a string
                
                # Use the determined final_ao_pain for the sheet
                final_ao_pain_for_sheet = q_ao_pain 
                if q_ao_pain == "Autre":
                    final_ao_pain_for_sheet = f"Autre: {q_ao_pain_autre.strip()}"
                
                # Renamed q_top_pain for the sheet to match the form input
                final_top_pain_problem_for_sheet = q_top_pain_problem if q_top_pain_problem else "Non renseigné"

                # Removed placeholders, now they're just empty strings if the fields are truly gone
                q_decision_maker = ""
                q_source = ""
                
                # Create the row list
                raw_row =[
                    current_time, company_name, secteur_entreprise, ca_range,
                    age_entreprise, effectif, role_respondant,
                    website, city, email, phone,
                    secteurs_ao_str,
                    # AO Process
                    q_ao_freq, q_ao_management, q_ao_time, final_ao_pain_for_sheet, q_ao_win_rate, # Use final_ao_pain_for_sheet here
                    # AI Maturity
                    q_ai_usage, ai_tools_str, q_lowcode, q_data_infra, digital_tools_str,
                    # Pain points
                    final_top_pain_problem_for_sheet, q_time_lost, q_priority_dept, q_existing_automation, q_dream_automation,
                    # Budget & decision
                    q_budget, q_decision_maker, q_barrier, q_timeline,
                    # Interest
                    q_cps_ai, q_pilot, q_source, q_comment, Email_Newsletter
                ]
                
                # Replacement sécurisé des champs laissés vides (None or explicitly forbidden strings)
                row_to_insert =[str(val) if (val is not None and str(val).strip().lower() not in [f.lower() for f in FORBIDDEN_PHRASES]) else "Non renseigné" for val in raw_row]

                # Append the row to the worksheet
                worksheet_gs.append_row(row_to_insert)

            st.success("✅ Inscription validée ! Vous recevrez vos premiers Appels d'Offres ciblés prochainement.")
            st.session_state.errors = {} # Clear errors after successful submission

        except Exception as e:
            st.error(f"Une erreur est survenue lors de l'enregistrement. Réessayez ou contactez-nous. Détails : {e}")

# --- 8. FOOTER ---
st.markdown("""
<div class="footer-note">
    Conformité RGPD : vos données sont traitées de manière confidentielle — aucune revente à des tiers.<br>
    <strong>Morocco · Maroc</strong>
</div>
""", unsafe_allow_html=True)
