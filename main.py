import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add the pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))

from pages import startseite, teamkalender, trainingsstatistiken, esel_der_woche, gimmicks

# Page configuration
st.set_page_config(
    page_title="ViktoriaInsights",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide the automatic Streamlit navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1e3c72;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚽ ViktoriaInsights</h1>
        <p>Erste Mannschaft - Viktoria Buchholz</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation in Sidebar
    with st.sidebar:
        st.image("Bilder/VB_Logo.png", 
                caption="Viktoria Buchholz", width=150)
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Startseite", "Teamkalender", 
                    "Trainingsstatistiken", "Esel der Woche", "Gimmicks"],
            icons=["house", "calendar", "bar-chart", 
                  "person-x", "stars"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#1e3c72",
                    "border-radius": "5px"
                },
                "icon": {
                    "color": "white", 
                    "font-size": "18px"
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "1rem",
                    "color": "white",
                    "background-color": "transparent",
                    "--hover-color": "#2a5298"
                },
                "nav-link-selected": {
                    "background-color": "white",
                    "color": "#1e3c72",
                    "font-weight": "bold"
                },
            }
        )
    
    # Page routing
    if selected == "Startseite":
        startseite.show()
    elif selected == "Teamkalender":
        teamkalender.show()
    elif selected == "Trainingsstatistiken":
        trainingsstatistiken.show()
    elif selected == "Esel der Woche":
        esel_der_woche.show()
    elif selected == "Gimmicks":
        gimmicks.show()

if __name__ == "__main__":
    main() 