import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Portail des Appels d'Offres & Innovation",
    page_icon="🇲🇦",
    layout="centered"
)

# --- 2. GOOGLE SHEETS CONNECTION SETUP ---
# Replace with the exact name of your Google Sheet
GOOGLE_SHEET_NAME = "Leads_Appels_Offres_Maroc"

@st.cache_resource
def init_google_sheets():
    """Authenticates using the Service Account from Streamlit Secrets"""
    scopes =[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Load credentials from st.secrets
    s_acc_info = st.secrets["gcp_service_account"]
    credentials = Credentials.from_service_account_info(s_acc_info, scopes=scopes)
    client = gspread.authorize(credentials)
    return client

# --- 3. THE TAGS ---
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

# --- 4. UI HEADER ---
st.title("Recevez vos Appels d'Offres Filtrés (Gratuit)")
st.markdown("""
Gagnez des heures de recherche chaque semaine. Recevez les appels d'offres de *marchespublics.gov.ma* et *Tanmia* directement dans votre boîte mail, filtrés selon **votre secteur d'activité**.

*En échange de ce service gratuit, aidez-nous à comprendre vos défis technologiques en répondant à 4 questions rapides.*
""")
st.divider()

# --- 5. THE FORM ---
with st.form("lead_gen_form"):
    
    st.subheader("🏢 1. Informations de l'Entreprise")
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Nom de l'entreprise *", placeholder="Ex: TargetUp SARL")
        email = st.text_input("Email professionnel *", placeholder="contact@entreprise.ma")
    
    with col2:
        city = st.selectbox("Ville *",["Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir", "Fès", "Béni Mellal", "Oujda", "Autre"])
        phone = st.text_input("Téléphone (WhatsApp)", placeholder="06 XX XX XX XX")
        
    tags = st.multiselect(
        "Quels secteurs d'Appels d'Offres vous intéressent ? *", 
        options=AO_CATEGORIES,
        help="Vous pouvez choisir plusieurs secteurs."
    )
    
    st.divider()
    
    st.subheader("🤖 2. Vos Défis & L'Intelligence Artificielle")
    st.markdown("Ces informations nous aident à développer de futurs outils pour vous faire gagner du temps.")
    
    ai_usage = st.selectbox(
        "1. Utilisez-vous déjà l'Intelligence Artificielle (ex: ChatGPT) dans votre entreprise ?",["Jamais", "Rarement (testé quelques fois)", "Régulièrement (rédaction, emails)", "Intégrée dans nos processus quotidiens"]
    )
    
    lowcode_knowledge = st.radio(
        "2. Connaissez-vous les outils d'automatisation 'Low-Code' (Zapier, Make.com, n8n) ?",["Non, jamais entendu parler", "Oui de nom, mais on ne les utilise pas", "Oui, nous les utilisons activement"],
        horizontal=True
    )
    
    main_problem = st.selectbox(
        "3. Quel est le plus grand problème administratif/opérationnel qui vous fait perdre du temps ?",[
            "La veille et préparation des Appels d'Offres",
            "La saisie manuelle des données (Devis, Factures)",
            "Le suivi client et la relance commerciale",
            "La gestion documentaire (Archivage, ISO)",
            "Autre (précisez ci-dessous)"
        ]
    )
    
    automate_task = st.text_area(
        "4. Si l'IA pouvait faire UNE seule tâche répétitive à votre place, laquelle choisiriez-vous ? *",
        placeholder="Ex: Lire les factures PDF de mes fournisseurs et les entrer dans Odoo automatiquement..."
    )
    
    submitted = st.form_submit_button("S'inscrire et recevoir mes Appels d'Offres 🚀", use_container_width=True)

# --- 6. HANDLING THE SUBMISSION TO GOOGLE SHEETS ---
if submitted:
    if not company_name or not email or not tags or not automate_task:
        st.error("⚠️ Veuillez remplir tous les champs obligatoires (*).")
    else:
        try:
            with st.spinner('Enregistrement de vos préférences...'):
                # Format the data as a list (Row) to insert into Google Sheets
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                secteurs_str = ", ".join(tags)
                
                row_to_insert =[
                    current_time, 
                    company_name, 
                    city, 
                    email, 
                    phone, 
                    secteurs_str, 
                    ai_usage, 
                    lowcode_knowledge, 
                    main_problem, 
                    automate_task
                ]
                
                # Connect and append to the Sheet
                gc = init_google_sheets()
                sheet = gc.open(GOOGLE_SHEET_NAME).sheet1
                sheet.append_row(row_to_insert)

            st.success(f"🎉 Félicitations {company_name} ! Votre inscription est validée. Vous recevrez vos premiers appels d'offres sous 24h.")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Une erreur s'est produite lors de l'enregistrement. Détails: {e}")
