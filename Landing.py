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

    /* Élargissement du conteneur pour le layout Hero (Texte / Visuel) */
    .main .block-container {
        width: 100% !important;
        max-width: 1100px !important; 
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

    /* ── HERO SPLIT LAYOUT ── */
    .hero-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 4rem;
        margin-bottom: 4rem;
        padding-top: 1rem;
    }
    
    .hero-content {
        flex: 1.1;
        max-width: 600px;
    }
    
    .hero-visual {
        flex: 0.9;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        min-height: 380px;
    }

    @media (max-width: 850px) {
        .hero-wrapper {
            flex-direction: column;
            text-align: left;
        }
        .hero-visual {
            display: none; /* Cache l'animation sur mobile pour gagner de la place */
        }
    }

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
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        line-height: 1.15 !important;
        letter-spacing: -0.01em !important;
        color: #f1f1f8 !important;
        margin-bottom: 1rem !important;
        text-rendering: optimizeLegibility;
    }

    .hero-title span {
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-sub {
        font-size: 0.95rem;
        color: var(--text-soft);
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    
    .hero-sub ul {
        list-style: none;
        padding-left: 0;
        margin-top: 15px;
    }
    .hero-sub ul li {
        position: relative;
        padding-left: 22px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    .hero-sub ul li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: var(--accent);
        font-weight: 800;
    }

    .stat-row {
        display: flex;
        gap: 2rem;
        flex-wrap: wrap;
        border-top: 1px solid var(--border);
        padding-top: 1.5rem;
        margin-top: 1.5rem;
    }
    .stat-item {
        display: flex;
        flex-direction: column;
    }
    .stat-num {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.72rem;
        color: var(--muted);
        margin-top: 5px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* ── ANIMATED AI NETWORK (Le visuel de droite) ── */
    .ai-network {
        position: relative;
        width: 320px;
        height: 320px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .orbit {
        position: absolute;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,0.05);
        animation: spin linear infinite;
    }
    .orbit::before {
        content: '';
        position: absolute;
        top: -4px;
        left: 50%;
        width: 8px;
        height: 8px;
        background: var(--accent);
        border-radius: 50%;
        box-shadow: 0 0 12px var(--accent);
    }
    .orbit-1 { width: 100%; height: 100%; animation-duration: 25s; border: 1px dashed rgba(230,49,83,0.3); }
    .orbit-2 { width: 70%; height: 70%; animation-duration: 15s; animation-direction: reverse; }
    .orbit-2::before { background: var(--accent2); box-shadow: 0 0 12px var(--accent2); top: 50%; left: -4px; }
    .orbit-3 { width: 40%; height: 40%; animation-duration: 10s; border: 1px solid rgba(249,115,22,0.2); }
    .orbit-3::before { display: none; }
    
    .core-node {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
        border-radius: 50%;
        box-shadow: 0 0 40px rgba(230,49,83,0.6);
        animation: pulse 2s ease-in-out infinite alternate;
        z-index: 2;
    }

    .network-lines {
        position: absolute;
        width: 100%;
        height: 100%;
        z-index: 1;
    }
    .network-lines line {
        stroke: rgba(230,49,83,0.3);
        stroke-width: 1.5;
        stroke-dasharray: 4;
        animation: dash 30s linear infinite;
    }

    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes pulse { 100% { transform: scale(1.15); box-shadow: 0 0 60px rgba(249,115,22,0.7); } }
    @keyframes dash { to { stroke-dashoffset: 1000; } }

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
    div.element-container:has(.ao-targeting-marker) { display: none !important; }

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
        content: ''; position: absolute; inset: 0;
        background: radial-gradient(circle at 20% 0%, rgba(230,49,83,0.25), transparent 60%); pointer-events: none;
    }
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker))::after {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(230,49,83,0.08), transparent 60%); opacity: 0; transition: opacity 0.3s ease; pointer-events: none;
    }
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)):hover::after { opacity: 1; }
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)):hover {
        transform: translateY(-3px); box-shadow: 0 12px 40px rgba(230,49,83,0.25);
    }
    
    .ao-box-title { font-size: 1.05rem; font-weight: 700; color: #ff4d6d; margin-bottom: 0.3rem; }
    .ao-box-desc { color: #c7c9d1; font-size: 0.9rem; margin-bottom: 1.2rem; }

    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)) .stMultiSelect { margin-bottom: 0; }
    div[data-testid="stVerticalBlock"]:has(.ao-targeting-marker):not(:has(div[data-testid="stVerticalBlock"] .ao-targeting-marker)) .stMultiSelect[data-baseweb="select"] {
        background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div, .stMultiSelect > div > div {
        background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
        color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.92rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: rgba(230,49,83,0.5) !important; box-shadow: 0 0 0 3px rgba(230,49,83,0.1) !important;
    }
    label, .stRadio > label, .stCheckbox > label {
        color: var(--text-soft) !important; font-size: 0.85rem !important; font-weight: 500 !important; letter-spacing: 0.01em !important;
    }

    .stRadio > div { gap: 6px !important; }
    .stRadio > div > label {
        background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
        padding: 10px 16px !important; transition: border-color 0.2s ease, background 0.2s ease !important;
        color: var(--text) !important; font-size: 0.88rem !important; cursor: pointer;
    }
    .stRadio > div > label:hover { border-color: rgba(230,49,83,0.4) !important; background: rgba(230,49,83,0.05) !important; }
    .stRadio > div > label[data-baseweb="radio"] input:checked + div { background-color: var(--accent) !important; border-color: var(--accent) !important; }

    .stButton > button {
        background: linear-gradient(135deg, #e63153 0%, #c91d41 100%) !important; color: white !important; border: none !important;
        border-radius: 10px !important; padding: 14px 28px !important; font-family: 'Syne', sans-serif !important;
        font-size: 0.95rem !important; font-weight: 700 !important; letter-spacing: 0.04em !important;
        text-transform: uppercase !important; transition: all 0.25s ease !important; box-shadow: 0 4px 20px rgba(230,49,83,0.3) !important;
        width: 100% !important; margin-top: 1.5rem !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(230,49,83,0.45) !important;
        background: linear-gradient(135deg, #f0365a 0%, #d42246 100%) !important;
    }

    .stAlert { border-radius: 10px !important; border-left-width: 3px !important; font-family: 'DM Sans', sans-serif !important; }
    .footer-note { text-align: center; font-size: 0.78rem; color: var(--muted); margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border); }
    #MainMenu, footer, header { visibility: hidden !important; } .stDeployButton { display: none !important; }
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
    s_acc_info = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(s_acc_info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

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

FORBIDDEN_NAMES =[
    "n/a", "na", "anonyme", "confidentiel", "secret", "aucun", "rien",
    "test", "freelance", "particulier", "self employed", "independant",
    "indépendant", "x", "xxx", "-", "none", "null",
]

# --- 5. HERO SECTION ---
st.markdown("""
<div class="hero-wrapper">
    <!-- Côté Gauche : Textes & Stats -->
    <div class="hero-content">
        <div class="hero-badge">🎯 Accès gratuit</div>
        <div class="hero-title">
            Recevez vos Appels d'Offres<br><span>filtrés & automatisés.</span>
        </div>
        <div class="hero-sub">
            Accédez aux marchés publics de <strong style="color:#e8e8f0">marchespublics.gov.ma</strong>, <strong style="color:#e8e8f0">Tanmia</strong>, <strong style="color:#e8e8f0">CDG</strong>, 
            <strong style="color:#e8e8f0">Bank Al-Maghrib</strong>, <strong style="color:#e8e8f0">ONCF</strong>, <strong style="color:#e8e8f0">RAM</strong>, <strong style="color:#e8e8f0">United Nations</strong>... directement dans votre boîte mail, filtrés selon votre secteur, <strong style="color:#e8e8f0">chaque matin à 8:00h.</strong> 
            <ul>
                <li><strong style="color:#e8e8f0">Le nom du projet</strong></li>
                <li><strong style="color:#e8e8f0">La date limite</strong></li>
                <li><strong style="color:#e8e8f0">La localisation</strong></li>
                <li><strong style="color:#e8e8f0">L’organisme émetteur</strong></li>
                <li><strong style="color:#e8e8f0">Le budget estimé & La caution</strong></li>
            </ul>
        </div>
        <div class="stat-row">
            <div class="stat-item"><div class="stat-num">2 400+</div><div class="stat-label">AO publiés chaque mois</div></div>
            <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Gratuit pour les entreprises</div></div>
            <div class="stat-item"><div class="stat-num">&lt; 2 min</div><div class="stat-label">Pour paramétrer vos alertes</div></div>
        </div>
    </div>

    <!-- Côté Droit : Visuel Abstrait Tech/IA 100% CSS (Pas d'image) -->
    <div class="hero-visual">
        <div class="ai-network">
            <div class="orbit orbit-1"></div>
            <div class="orbit orbit-2"></div>
            <div class="orbit orbit-3"></div>
            <div class="core-node"></div>
            
            <svg class="network-lines" viewBox="0 0 320 320" xmlns="http://www.w3.org/2000/svg">
                <!-- Lignes de connexion (Data flow) -->
                <line x1="160" y1="160" x2="40" y2="90" />
                <line x1="160" y1="160" x2="280" y2="60" />
                <line x1="160" y1="160" x2="260" y2="280" />
                <line x1="160" y1="160" x2="80" y2="260" />
                <line x1="160" y1="160" x2="10" y2="200" />
                <!-- Noeuds externes -->
                <circle cx="40" cy="90" r="4" fill="#e63153" />
                <circle cx="280" cy="60" r="5" fill="#f97316" />
                <circle cx="260" cy="280" r="4" fill="#e63153" />
                <circle cx="80" cy="260" r="3" fill="#f97316" />
                <circle cx="10" cy="200" r="4" fill="#e63153" />
            </svg>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- 6. FORM (Centré et contraint pour ne pas être trop étiré) ---
# L'utilisation de ces colonnes permet de centrer le formulaire sous le grand "Hero"
_, main_col, _ = st.columns([1, 4.5, 1])

with main_col:

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
        secteur_entreprise = st.selectbox("Secteur d'activité principal *", SECTEURS_ENTREPRISE, index=None, placeholder="Sélectionnez...")
        email            = st.text_input("Email *", placeholder="")
        phone            = st.text_input("Téléphone / WhatsApp *", placeholder="")
    with col2:
        city             = st.selectbox("Ville du siège *", MOROCCAN_CITIES, index=None, placeholder="Sélectionnez...")
        effectif         = st.selectbox("Effectif de l'entreprise *",[
            "Auto-entrepreneur / TPE (1-5 personnes)",
            "Petite entreprise (6-20 personnes)",
            "Moyenne entreprise (21-100 personnes)",
            "Grande entreprise (100-500 personnes)",
            "Groupe / Holding (500+ personnes)",
        ], index=None, placeholder="Sélectionnez...")
        age_entreprise   = st.selectbox("Ancienneté de l'entreprise *",[
            "Moins d'un an", "1 à 3 ans", "3 à 7 ans", "7 à 15 ans", "Plus de 15 ans"
        ], index=None, placeholder="Sélectionnez...")
        website          = st.text_input("Site web (optionnel)", placeholder="www.entreprise.ma")

    ca_range = st.selectbox("Chiffre d'affaires annuel estimé *",[
        "Moins de 500 000 DH",
        "500 000 – 2 000 000 DH",
        "2 000 000 – 10 000 000 DH",
        "10 000 000 – 50 000 000 DH",
        "Plus de 50 000 000 DH",
        "Préfère ne pas répondre",
    ], index=None, placeholder="Sélectionnez...")

    role_respondant = st.selectbox("Votre fonction dans l'entreprise *",[
        "Dirigeant / PDG / Associé",
        "Directeur général ou adjoint",
        "Directeur commercial / Business developer",
        "Responsable administratif & financier",
        "Responsable IT / DSI",
        "Chef de projet / Manager",
        "Autre",
    ], index=None, placeholder="Sélectionnez...")

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
        Email_Newsletter =  st.text_input("Email de réception des appels d’offres *", placeholder="")

    q_ao_freq = st.selectbox("Combien d'AO soumettez-vous en moyenne par mois ?",[
        "Nous ne participons pas encore aux AO",
        "1 à 3 AO/mois", "4 à 10 AO/mois", "Plus de 10 AO/mois",
    ], index=None, placeholder="Sélectionnez...")

    q_ao_management = st.radio("Comment gérez-vous actuellement votre veille AO ?",[
        "Recherche manuelle et irrégulière",
        "Une personne dédiée à la veille",
        "Abonnement à un service de veille",
        "Pas de veille structurée",
    ], index=None)

    q_ao_time = st.selectbox("Combien de temps passez-vous à préparer un dossier de soumission ?",[
        "Moins de 2 jours",
        "2 à 5 jours ouvrés",
        "1 à 2 semaines",
        "Plus de 2 semaines",
    ], index=None, placeholder="Sélectionnez...")

    q_ao_pain = st.selectbox("Quel est votre principal défi sur les Appels d'Offres ?",[
        "Trouver les AO pertinents à temps",
        "Lire et comprendre le CPS (Cahier des Prescriptions Spéciales)",
        "Constituer le dossier administratif",
        "Estimer le prix et préparer l'offre financière",
        "Assurer la conformité documentaire",
        "Manque de ressources humaines dédiées",
    ], index=None, placeholder="Sélectionnez...")

    q_ao_win_rate = st.selectbox("Quel est votre taux de succès estimé sur vos soumissions AO ?",[
        "Je ne sais pas / pas de suivi",
        "Moins de 10%", "10% à 25%", "25% à 50%", "Plus de 50%",
    ], index=None, placeholder="Sélectionnez...")

    # ── BLOCK C : AI & DIGITAL MATURITY ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">C · Maturité IA & Digitale</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_ai_usage = st.selectbox("À quelle fréquence utilisez-vous l'Intelligence Artificielle en entreprise ?",[
        "Jamais — nous n'avons pas encore exploré",
        "Quelques tests individuels (ChatGPT personnel…)",
        "Utilisation régulière sur certains postes (rédaction, recherche)",
        "IA intégrée dans au moins un processus métier",
        "IA centrale dans notre stratégie opérationnelle",
    ], index=None, placeholder="Sélectionnez...")

    q_ai_tools = st.multiselect("Quels outils IA utilisez-vous actuellement ? (plusieurs choix possibles)",[
        "ChatGPT / GPT-4", "Claude (Anthropic)", "Gemini (Google)",
        "Copilot (Microsoft)", "Midjourney / DALL-E (images)",
        "Outils IA intégrés dans des logiciels métiers",
        "IA développée en interne", "Aucun outil IA pour l'instant",
    ], placeholder="Sélectionnez…")

    q_lowcode = st.radio("Connaissez-vous les outils d'automatisation Low-Code (n8n, Make, Zapier…) ?",[
        "Non, première fois que j'en entends parler",
        "Oui de nom, mais sans utilisation concrète",
        "Oui, nous les utilisons occasionnellement",
        "Oui, ils sont intégrés dans nos processus",
    ], index=None)

    q_data_infra = st.radio("Comment gérez-vous vos données clients et opérationnelles ?",[
        "Fichiers Excel / Google Sheets uniquement",
        "CRM basique (HubSpot free, Zoho…)",
        "ERP ou CRM avancé (Odoo, SAP, Dynamics…)",
        "Base de données ou infra BI dédiée",
        "Pas de gestion structurée",
    ], index=None)

    q_digital_tools =  st.text_input("Quels outils digitaux sont déjà en place dans votre entreprise ? *", placeholder="")
    
    # ── BLOCK D : PAIN POINTS ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-line"></div>
        <div class="section-divider-label">D · Points de friction</div>
        <div class="section-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    q_top_pain = st.selectbox("Quel est votre principal goulot d'étranglement opérationnel en ce moment ?",[
        "Veille et préparation des Appels d'Offres",
        "Saisie manuelle des données (devis, factures, ERP)",
        "Suivi commercial et relance client",
        "Gestion documentaire et conformité (archivage, ISO)",
        "Recrutement et tri des candidatures",
        "Reporting & analyse de données",
        "Communication interne et coordination d'équipes",
        "Service client et support après-vente",
        "Autre",
    ], index=None, placeholder="Sélectionnez...")

    q_top_pain_autre = ""
    if q_top_pain == "Autre":
        q_top_pain_autre = st.text_input("Veuillez préciser votre goulot d'étranglement *", placeholder="Décrivez votre situation...")

    q_time_lost = st.selectbox("Combien d'heures par semaine estimez-vous perdre sur des tâches manuelles ?",[
        "Moins de 5 heures",
        "5 à 10 heures",
        "10 à 20 heures",
        "Plus de 20 heures par semaine",
    ], index=None, placeholder="Sélectionnez...")

    q_priority_dept = st.selectbox("Quel département bénéficierait le plus d'une automatisation ?",[
        "Commercial & Business Development",
        "Administration & Finances",
        "Opérations & Production",
        "RH & Recrutement",
        "IT & Systèmes",
        "Direction Générale",
        "Juridique & Conformité",
    ], index=None, placeholder="Sélectionnez...")

    q_existing_automation = st.radio("Avez-vous déjà automatisé un processus dans votre entreprise ?",[
        "Non, tout est encore manuel",
        "Oui, quelques automatisations simples (alertes, rappels…)",
        "Oui, des workflows complets sont automatisés",
        "Oui, nous avons une stratégie d'automatisation active",
    ], index=None)

    q_dream_automation = st.text_area(
        "Si l'IA pouvait exécuter UNE seule tâche à votre place dès demain, laquelle serait-elle ? *",
        placeholder="Ex: Analyser automatiquement les CPS et me sortir un résumé en 5 points clés avec les dates limites…",
        height=90,
    )

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

    q_barrier = st.selectbox("Principal frein à l'adoption de nouvelles technologies dans votre entreprise ?",[
        "Coût d'acquisition perçu comme élevé",
        "Complexité d'utilisation / manque de formation",
        "Temps de mise en place et d'intégration",
        "Résistance au changement des équipes",
        "Manque de cas d'usage concrets et prouvés au Maroc",
        "Défiance envers les données et la confidentialité",
        "Pas de frein majeur identifié",
    ], index=None, placeholder="Sélectionnez...")

    q_timeline = st.selectbox("Dans quel délai envisagez-vous un investissement en automatisation/IA ?",[
        "Immédiatement — nous cherchons une solution",
        "Dans les 3 prochains mois",
        "Dans les 6 prochains mois",
        "Dans l'année",
        "Pas de projet concret pour l'instant",
    ], index=None, placeholder="Sélectionnez...")

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

    q_pilot = st.radio("Seriez-vous ouvert à tester une automatisation sur-mesure (Proof of Concept) ?",[
        "Oui, absolument",
        "Non, pas pour le moment",
    ], index=None)

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
        company_clean = company_name.strip().lower()

        required_fields =[
            company_name, secteur_entreprise, email, phone, city, effectif,
            age_entreprise, ca_range, role_respondant, tags, Email_Newsletter, 
            q_digital_tools, q_dream_automation
        ]

        if not all(required_fields):
            st.error("⚠️ Veuillez remplir tous les champs obligatoires marqués d'un astérisque (*).")
            
        elif q_top_pain == "Autre" and not q_top_pain_autre.strip():
            st.error("⚠️ Vous avez sélectionné 'Autre' comme goulot d'étranglement. Veuillez préciser votre situation.")

        elif company_clean in FORBIDDEN_NAMES or len(company_clean) < 2:
            st.error("❌ Veuillez entrer un nom d'entreprise valide. Ce service est réservé aux structures B2B identifiées.")

        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("❌ L'adresse email semble invalide. Veuillez vérifier.")

        else:
            try:
                with st.spinner("Enregistrement en cours…"):
                    current_time       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    secteurs_ao_str    = ", ".join(tags)
                    ai_tools_str       = ", ".join(q_ai_tools) if q_ai_tools else "Aucun"
                    digital_tools_str  = q_digital_tools if q_digital_tools else "Aucun"
                    
                    final_top_pain = f"Autre : {q_top_pain_autre}" if q_top_pain == "Autre" else q_top_pain
                    
                    q_decision_maker = "Non demandé (supprimé du form)"
                    q_source = "Non demandé (supprimé du form)"
                    
                    raw_row =[
                        current_time, company_name, secteur_entreprise, ca_range,
                        age_entreprise, effectif, role_respondant,
                        website, city, email, phone,
                        secteurs_ao_str,
                        q_ao_freq, q_ao_management, q_ao_time, q_ao_pain, q_ao_win_rate,
                        q_ai_usage, ai_tools_str, q_lowcode, q_data_infra, digital_tools_str,
                        final_top_pain, q_time_lost, q_priority_dept, q_existing_automation, q_dream_automation,
                        q_budget, q_decision_maker, q_barrier, q_timeline,
                        q_cps_ai, q_pilot, q_source, q_comment, Email_Newsletter
                    ]
                    
                    row_to_insert =[str(val) if (val is not None and val != "") else "Non renseigné" for val in raw_row]

                    gc = init_google_sheets()
                    sheet = gc.open(GOOGLE_SHEET_NAME).sheet1
                    sheet.append_row(row_to_insert)

                st.success("✅ Inscription validée ! Vous recevrez vos premiers Appels d'Offres ciblés prochainement.")
                st.balloons()

            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'enregistrement. Réessayez ou contactez-nous. Détails : {e}")

# --- 8. FOOTER ---
st.markdown("""
<div class="footer-note">
    Données traitées de façon confidentielle — aucune revente à des tiers.<br>
    <strong>Morocco · Maroc</strong>
</div>
""", unsafe_allow_html=True)
