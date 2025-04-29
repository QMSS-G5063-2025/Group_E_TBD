import streamlit as st
import sys
import os
import plotly.express as px

sys.path.append(os.path.dirname(__file__))

# Important: st.set_page_config must be the first Streamlit command
st.set_page_config(
    page_title="Manhattan Real Estate Sales Analysis",
    layout="wide",
    menu_items=None
)

from modules import _Home, _Pricechanges, _Health, _PriceMap, _DataOverview, _Introduction
from modules._Demographics.main import show as _Demographics_show

def create_sidebar():
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("Home", use_container_width=True):
            st.session_state.page = "home"
        
        if st.button("Introduction", use_container_width=True):
            st.session_state.page = "Introduction"
        
        st.subheader("Analysis Part")
        
        if st.button("Data Overview", use_container_width=True):
            st.session_state.page = "DataOverview"
            
        if st.button("Price Map", use_container_width=True):
            st.session_state.page = "PriceMap"
            
        if st.button("Price Change", use_container_width=True):
            st.session_state.page = "Pricechanges"
            
        if st.button("Demographics", use_container_width=True):
            st.session_state.page = "Demographics"
        
        if st.button("Health", use_container_width=True):
            st.session_state.page = "Health"

if 'page' not in st.session_state:
    st.session_state.page = "home"

create_sidebar()

if st.session_state.page == "home":
    _Home.show()
elif st.session_state.page == "Introduction":
    _Introduction.show()
elif st.session_state.page == "DataOverview":
    _DataOverview.show()
elif st.session_state.page == "PriceMap":
    _PriceMap.show()
elif st.session_state.page == "Pricechanges":
    _Pricechanges.show()
elif st.session_state.page == "Demographics":
    _Demographics_show()
elif st.session_state.page == "Health":
    _Health.show()
