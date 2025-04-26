import streamlit as st
from ._Age import show_median_age_analysis
from ._Income import show_income_analysis
from ._Race import show_race_analysis

def show():
    """Display Manhattan demographic information with multiple analysis types"""
    st.title("Manhattan Demographics Analysis")
    
    st.markdown("""
    <p style="font-size: 20px;">
    Leveraging the data collected by the American Community Survey, we extracted age and race from the Demographics table (DP-05) and income by the Selected Economic Characteristics table (DP-03). We compiled 1-Year data from 2015-2023 (with an exception of 2020, because the survey had no data for the year) and used them to produce line charts and scatter plots to show the change in population profiles over the years. For the interactive line charts, the user can select a specific neighborhood to inspect its demographic makeup for the chosen characteristic. The scatter plots combine the demographic information, the median sales price, and the sales count for 1 selected year for a correlation analysis. 
    </p>
    """, unsafe_allow_html=True)
    
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