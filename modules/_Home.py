import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show():
    image_path = os.path.join("img", "New-York.jpg")
    
    img_base64 = get_base64_of_bin_file(image_path)
    
    page_bg_img = f'''
    <style>
    .stApp {{
        padding: 0;
    }}
    .block-container {{
        max-width: 100%;
        padding-top: 0;
        padding-right: 0;
        padding-left: 0;
        padding-bottom: 0;
    }}
    .custom-layout {{
        display: flex;
        height: calc(100vh - 2rem);
        width: 100%;
    }}
    .image-div {{
        flex: 1;
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        height: 100%;
    }}
    .text-div {{
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 2rem;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
    st.markdown('''
    <div class="custom-layout">
        <div class="image-div"></div>
        <div class="text-div">
            <h1 style="font-size: 4rem; font-weight: bold;">Manhattan Rolling Sale Analysis</h1>
            <h2 style="font-size: 2.5rem; margin-top: 2rem;">Group_E Presentation</h2>
        </div>
    </div>
    ''', unsafe_allow_html=True)