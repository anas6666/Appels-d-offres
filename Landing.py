import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Portail des Appels d'Offres & Innovation",
    layout="centered"
)

# --- 2. INJECTION CSS (ANIMATIONS & DESIGN ÉPURÉ) ---
st.markdown("""
    <style>
        /* Animation d'apparition fluide */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        div.block-container {
            animation: fadeIn 0.8s ease-out;
            font-family: 'Inter', sans-serif;
        }

        /* Section Appels d'offres au milieu */
        .ao-highlight {
            background-color: #f8f9fc;
            border-left: 3px solid #e11d48; /* Couleur rouge subtile/moderne pour attirer l'attention */
            padding: 20px 25px;
            border-radius: 6px;
            margin-top: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
            transition: all 0.3s ease;
        }
        .ao-highlight:hover {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
            transform: translateY(-2px);
        }
        .ao-highlight h3 {
            color: #1e293b;
            font-size: 1.1rem;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .ao-highlight p {
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }

        /* Boutons */
        .stButton>button {
            transition: all 0.3s ease-in-out;
            border-radius: 6px;
            background-color: #0f172a;
            color: white;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            background-color: #1e293b;
            color: white;
        }
        
        /* Titres de section */
        .section-title {
            font-weight: 600;
            color: #0f172a;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 8px;
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
    s_acc_info = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(s_acc_info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

# --- 4. LISTES & FILTRES ---
AO_CATEGORIES =[
    "Constructions & Gros Œuvre", "Génie Civil & Infrastructures", 
    "Aménagement & Finition", "Électricité & Plomberie",
    "Nettoyage & Entretien", "Gardiennage & Sécurité", "Transport & Logistique",
    "Recrutement & Intérim", "Consulting & Audit", "Formation & Coaching",
    "IT Matériel & Réseau", "IT Logiciel & Digital", "Archivage & Numérisation",
    "Fournitures de Bureau & Impression", "Matériel Médical & Laboratoire",
    "Agroalimentaire & Restauration", "Événementiel & Communication",
    "Développement Social & ONG"
]

FORBIDDEN_NAMES =[
    "n/a", "na", "anonyme", "confidentiel", "secret", "aucun", "rien", 
    "test", "freelance", "particulier", "self employed", "independant", 
    "indépendant", "x", "xxx", "-"
]

# --- 5. HEADER ---
st.title("Recevez vos Appels d'Offres Filtrés")
st.markdown("""
Gagnez des heures de recherche chaque semaine. Recevez les appels d'offres de *marchespublics.gov.ma* et *Tanmia* directement dans votre boîte de réception, triés selon votre secteur d'activité.

*En contrepartie de cet accès gratuit réservé aux entreprises, nous vous demandons de répondre à un bref questionnaire.*
""")

# --- 6. FORMULAIRE ---
with st.form("lead_gen_form"):
    
    st.markdown('<div class="section-title">1. Informations de l\'Entreprise</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Nom de l'entreprise *", placeholder="Ex: TargetUp SARL")
        secteur_entreprise = st.text_input("Secteur d'activité de l'entreprise *", placeholder="Ex: BTP, Consulting, IT...")
        email = st.text_input("Email professionnel *", placeholder="contact@entreprise.ma")
        
    with col2:
        city = st.selectbox("Ville *",["Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir", "Fès", "Béni Mellal", "Oujda", "Autre"])
        phone = st.text_input("Téléphone (WhatsApp) *", placeholder="06 XX XX XX XX")
        website = st.text_input("Site web (Optionnel)", placeholder="www.entreprise.ma")
        
    # --- MIDDLE SECTION: AO SELECTION ---
    st.markdown("""
        <div class="ao-highlight">
            <h3 style='color: #e11d48;'>🎯 Ciblage de vos Appels d'Offres</h3>
            <p>Sélectionnez les secteurs précis que vous souhaitez recevoir quotidiennement par email.</p>
        </div>
    """, unsafe_allow_html=True)
    
    tags = st.multiselect(
        "Secteurs d'Appels d'Offres souhaités *", 
        options=AO_CATEGORIES,
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="section-title">2. Étude de marché : L\'IA & l\'Automatisation</div>', unsafe_allow_html=True)
    
    q1_usage = st.selectbox("1. À quelle fréquence utilisez-vous l'Intelligence Artificielle aujourd'hui ?",["Jamais", "Rarement (quelques tests isolés)", "Régulièrement (rédaction, e-mails, recherche)", "Pleinement intégrée dans nos processus"])
    q2_lowcode = st.radio("2. Connaissez-vous les outils d'automatisation 'Low-Code' (Zapier, Make.com, n8n) ?",["Non", "Oui de nom, mais sans utilisation", "Oui, nous les utilisons activement"])
    q3_problem = st.selectbox("3. Quel est votre principal goulot d'étranglement administratif/opérationnel ?",["La veille et la préparation des Appels d'Offres", "La saisie manuelle des données (Devis, Factures, ERP)", "Le suivi commercial et la relance client", "La gestion de la conformité documentaire (Archivage, ISO)", "Le recrutement et tri des CVs", "Autre"])
    q4_time_lost = st.selectbox("4. Combien d'heures par semaine estimez-vous perdre sur des tâches manuelles et répétitives ?",["Moins de 5 heures", "Entre 5 et 10 heures", "Entre 10 et 20 heures", "Plus de 20 heures par semaine"])
    q5_budget = st.selectbox("5. Quel est votre budget annuel alloué à la digitalisation et aux logiciels métiers ?",["Moins de 10 000 DH", "Entre 10 000 DH et 50 000 DH", "Entre 50 000 DH et 200 000 DH", "Plus de 200 000 DH"])
    q6_barrier = st.selectbox("6. Quel est le principal frein à l'adoption de nouvelles technologies dans votre entreprise ?",["Le coût d'acquisition", "La complexité d'utilisation et le manque de formation", "Le temps nécessaire pour la mise en place", "La résistance au changement des équipes", "Nous n'avons pas de frein majeur"])
    q7_ao_management = st.radio("7. Comment gérez-vous actuellement vos soumissions aux Appels d'Offres ?",["Processus entièrement manuel", "Une équipe/personne dédiée à 100%", "Nous sous-traitons la recherche", "Nous avons un logiciel interne"])
    q8_premium_interest = st.radio("8. Seriez-vous intéressé par une IA qui lit le CPS à votre place et extrait le Dossier Technique ?",["Pas intéressé", "Oui, si c'est gratuit", "Oui, je serais prêt à payer un abonnement pour cette fonctionnalité"])
    q9_pilot = st.radio("9. Seriez-vous ouvert à tester une automatisation sur-mesure (Proof of Concept) gratuitement ?",["Oui, absolument", "Peut-être, à voir selon la proposition", "Non, pas pour le moment"])
    q10_automate_task = st.text_area("10. Si l'IA pouvait exécuter UNE seule tâche à votre place dès demain, quelle serait-elle ? *", placeholder="Ex: Extraire les lignes des factures fournisseurs et les envoyer sur notre ERP...")
    
    # Submit
    submitted = st.form_submit_button("S'inscrire et paramétrer mes alertes", use_container_width=True)

# --- 7. VALIDATION, SOUMISSION & SAUVEGARDE ---
if submitted:
    company_clean = company_name.strip().lower()
    
    # Vérification des champs obligatoires
    if not company_name or not secteur_entreprise or not email or not phone or not tags or not q10_automate_task:
        st.error("⚠️ Veuillez remplir tous les champs obligatoires (*).")
        
    # Vérification anti-spam pour le nom de l'entreprise
    elif company_clean in FORBIDDEN_NAMES or len(company_clean) < 2:
        st.error("❌ Veuillez entrer un nom d'entreprise valide. Les mentions anonymes, particuliers ou génériques ne sont pas acceptées pour ce service B2B.")
        
    else:
        try:
            with st.spinner('Vérification de l\'entreprise et enregistrement des préférences...'):
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                secteurs_ao_str = ", ".join(tags)
                site_web = website if website else "Non renseigné"
                
                # 18 colonnes pour Google Sheets
                row_to_insert =[
                    current_time, 
                    company_name, 
                    secteur_entreprise,
                    site_web,          # <- NOUVELLE COLONNE
                    city, 
                    email, 
                    phone,             # <- MAINTENANT OBLIGATOIRE
                    secteurs_ao_str, 
                    q1_usage, 
                    q2_lowcode, 
                    q3_problem,
                    q4_time_lost,
                    q5_budget,
                    q6_barrier,
                    q7_ao_management,
                    q8_premium_interest,
                    q9_pilot,
                    q10_automate_task
                ]
                
                gc = init_google_sheets()
                sheet = gc.open(GOOGLE_SHEET_NAME).sheet1
                sheet.append_row(row_to_insert)

            st.success("✅ Inscription validée ! Votre entreprise recevra ses premiers Appels d'Offres ciblés prochainement.")
            st.balloons()
            
        except Exception as e:
            st.error(f"Une erreur est survenue lors de l'enregistrement. Veuillez réessayer. Détails techniques : {e}")
