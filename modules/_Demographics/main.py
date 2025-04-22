import streamlit as st
from ._Age import show_median_age_analysis
from ._Income import show_income_analysis
from ._Race import show_race_analysis

def show():
    """Display Manhattan demographic information with multiple analysis types"""
    st.title("Manhattan Demographics Analysis")
    
    # Create tabs within the Demographics page
    tabs = st.tabs(["Age", "Income", "Race"])
    
    # Median Age tab
    with tabs[0]:
        show_median_age_analysis()
    
    # Income tab
    with tabs[1]:
        show_income_analysis()
    
    # Race tab
    with tabs[2]:
        show_race_analysis()