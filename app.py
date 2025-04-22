import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))

from modules import _Home, _Pricechanges, _Health, _PriceMap, _DataOverview, _Education
from modules._Demographics.main import show as _Demographics_show

st.set_page_config(
    page_title="Manhattan Rolling Sale Analysis",
    layout="wide",
    menu_items=None
)

def create_sidebar():
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("Home", use_container_width=True):
            st.session_state.page = "home"
        
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

        if st.button("Education", use_container_width=True):
            st.session_state.page = "Education"

if 'page' not in st.session_state:
    st.session_state.page = "home"

create_sidebar()

if st.session_state.page == "home":
    _Home.show()
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
elif st.session_state.page == "Education":
    _Education.show()