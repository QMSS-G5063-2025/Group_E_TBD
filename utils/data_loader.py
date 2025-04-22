# utils/data_loader.py
import pandas as pd
import numpy as np
import streamlit as st
import colorsys

@st.cache_data
def load_data():
    data_path = r"C:\Users\Lenovo\Desktop\Group_E_TBD-main\project\datasets\rollingsales_manhattan.xlsx"
    df = pd.read_excel(data_path)
    df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
    df = df[df['sale_price'] > 0]   
    
    # 邮编到社区和坐标的映射
    zip_to_info = {
        10001: ("Chelsea", 40.7503, -73.9967),
        10002: ("Lower East Side", 40.7153, -73.9865),
        10003: ("East Village", 40.7320, -73.9874),
        10004: ("Financial District", 40.7032, -74.0132),
        10005: ("Financial District", 40.7048, -74.0092),
        10006: ("Financial District", 40.7076, -74.0113),
        10007: ("TriBeCa", 40.7143, -74.0070),
        10009: ("East Village", 40.7265, -73.9802),
        10010: ("Gramercy", 40.7383, -73.9824),
        10011: ("Chelsea", 40.7420, -73.9992),
        10012: ("SoHo/NoHo", 40.7254, -73.9984),
        10013: ("TriBeCa/SoHo", 40.7221, -74.0050),
        10014: ("West Village", 40.7339, -74.0055),
        10016: ("Murray Hill", 40.7474, -73.9787),
        10017: ("Midtown East", 40.7520, -73.9739),
        10018: ("Midtown", 40.7551, -73.9911),
        10019: ("Midtown West", 40.7656, -73.9825),
        10020: ("Midtown", 40.7588, -73.9795),
        10021: ("Upper East Side", 40.7692, -73.9612),
        10022: ("Midtown East", 40.7587, -73.9677),
        10023: ("Upper West Side", 40.7767, -73.9825),
        10024: ("Upper West Side", 40.7897, -73.9705),
        10025: ("Upper West Side", 40.7994, -73.9674),
        10026: ("Harlem", 40.8023, -73.9527),
        10027: ("Harlem", 40.8122, -73.9556),
        10028: ("Upper East Side", 40.7768, -73.9549),
        10029: ("East Harlem", 40.7928, -73.9434),
        10030: ("Harlem", 40.8187, -73.9444),
        10031: ("Hamilton Heights", 40.8247, -73.9496),
        10032: ("Washington Heights", 40.8381, -73.9464),
        10033: ("Washington Heights", 40.8501, -73.9341),
        10034: ("Inwood", 40.8669, -73.9252),
        10035: ("East Harlem", 40.8021, -73.9309),
        10036: ("Hell's Kitchen", 40.7598, -73.9897),
        10037: ("Harlem", 40.8125, -73.9394),
        10038: ("South Street Seaport", 40.7095, -74.0023),
        10039: ("Harlem", 40.8270, -73.9368),
        10040: ("Washington Heights", 40.8585, -73.9297),
        10044: ("Roosevelt Island", 40.7618, -73.9506),
        10065: ("Upper East Side", 40.7645, -73.9601),
        10069: ("Upper West Side", 40.7751, -73.9883),
        10075: ("Upper East Side", 40.7706, -73.9537),
        10128: ("Upper East Side", 40.7808, -73.9494),
        10280: ("Battery Park City", 40.7105, -74.0158),
        10282: ("Battery Park City", 40.7168, -74.0130),
    }
    
    # 创建社区列和经纬度列 - 使用小写的'neighborhood'
    df['neighborhood'] = df['ZIP CODE'].map(lambda x: zip_to_info.get(x, ("Unknown", np.nan, np.nan))[0])
    df['latitude'] = df['ZIP CODE'].map(lambda x: zip_to_info.get(x, ("Unknown", np.nan, np.nan))[1])
    df['longitude'] = df['ZIP CODE'].map(lambda x: zip_to_info.get(x, ("Unknown", np.nan, np.nan))[2])
    
    # 删除缺失坐标或社区的行
    df = df.dropna(subset=['latitude', 'longitude', 'neighborhood']) 
    
    return df