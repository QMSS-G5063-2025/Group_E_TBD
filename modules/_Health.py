import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import shapely.wkt
from shapely.geometry import Point
import geopandas as gpd
import os

@st.cache_data
def get_manhattan_zip_map():
    return {
        10001: "Chelsea",
        10002: "Lower East Side",
        10003: "East Village",
        10004: "Financial District",
        10005: "Financial District",
        10006: "Financial District",
        10007: "TriBeCa",
        10009: "East Village",
        10010: "Gramercy",
        10011: "Chelsea",
        10012: "SoHo/NoHo",
        10013: "TriBeCa/SoHo",
        10014: "West Village",
        10016: "Murray Hill",
        10017: "Midtown East",
        10018: "Midtown",
        10019: "Midtown West",
        10020: "Midtown",
        10021: "Upper East Side",
        10022: "Midtown East",
        10023: "Upper West Side",
        10024: "Upper West Side",
        10025: "Upper West Side",
        10026: "Harlem",
        10027: "Harlem",
        10028: "Upper East Side",
        10029: "East Harlem",
        10030: "Harlem",
        10031: "Hamilton Heights",
        10032: "Washington Heights",
        10033: "Washington Heights",
        10034: "Inwood",
        10035: "East Harlem",
        10036: "Hell's Kitchen",
        10037: "Harlem",
        10038: "South Street Seaport",
        10039: "Harlem",
        10040: "Washington Heights",
        10044: "Roosevelt Island",
        10065: "Upper East Side",
        10069: "Upper West Side",
        10075: "Upper East Side",
        10128: "Upper East Side",
        10280: "Battery Park City",
        10282: "Battery Park City",
    }

@st.cache_data
def get_neighborhood_coordinates():
    """Return coordinates for Manhattan neighborhoods"""
    return {
        "Chelsea": (40.7503, -73.9967),
        "Lower East Side": (40.7153, -73.9865),
        "East Village": (40.7320, -73.9874),
        "Financial District": (40.7048, -74.0092),
        "TriBeCa": (40.7143, -74.0070),
        "TriBeCa/SoHo": (40.7221, -74.0050),
        "SoHo/NoHo": (40.7254, -73.9984),
        "West Village": (40.7339, -74.0055),
        "Gramercy": (40.7383, -73.9824),
        "Murray Hill": (40.7474, -73.9787),
        "Midtown East": (40.7520, -73.9739),
        "Midtown": (40.7588, -73.9795),
        "Midtown West": (40.7656, -73.9825),
        "Upper East Side": (40.7692, -73.9612),
        "Upper West Side": (40.7767, -73.9825),
        "Harlem": (40.8122, -73.9556),
        "East Harlem": (40.7928, -73.9434),
        "Hamilton Heights": (40.8247, -73.9496),
        "Washington Heights": (40.8381, -73.9464),
        "Inwood": (40.8669, -73.9252),
        "Hell's Kitchen": (40.7598, -73.9897),
        "South Street Seaport": (40.7095, -74.0023),
        "Roosevelt Island": (40.7618, -73.9506),
        "Battery Park City": (40.7105, -74.0158),
    }

@st.cache_data
def load_health_facilities():
    file_path = "datasets/Health_Facility_General_Information.csv"       

    df = pd.read_csv(file_path)
        
    df['ZIP_CODE'] = df['Facility Zip Code']   
    df['FACILITY_NAME'] = df['Facility Name']
    df['LATITUDE'] = df['Facility Latitude']
    df['LONGITUDE'] = df['Facility Longitude']

    df['ZIP_CODE'] = pd.to_numeric(df['ZIP_CODE'], errors='coerce')
        
    manhattan_zips = list(get_manhattan_zip_map().keys())
    df_manhattan = df[df['ZIP_CODE'].isin(manhattan_zips)]
        
    zip_to_neighborhood = get_manhattan_zip_map()
    df_manhattan['NEIGHBORHOOD'] = df_manhattan['ZIP_CODE'].map(zip_to_neighborhood)
        
    df_manhattan['LATITUDE'] = pd.to_numeric(df_manhattan['LATITUDE'], errors='coerce')
    df_manhattan['LONGITUDE'] = pd.to_numeric(df_manhattan['LONGITUDE'], errors='coerce')
        
    df_manhattan = df_manhattan.dropna(subset=['LATITUDE', 'LONGITUDE', 'NEIGHBORHOOD'])
        
    return df_manhattan

@st.cache_data
def load_geospatial_data():
    file_path = 'datasets/Modified_Zip_Code_Tabulation_Areas__MODZCTA__20250421.csv'
            
    # Load data
    modzcta_df = pd.read_csv(file_path)
        
    # Check if dataset has geometry information
    if 'the_geom' in modzcta_df.columns:
        geometries = modzcta_df['the_geom'].apply(shapely.wkt.loads)
        modzcta_gdf = gpd.GeoDataFrame(modzcta_df, geometry=geometries, crs="EPSG:4326")
            
        modzcta_gdf['zipcode'] = modzcta_gdf['MODZCTA'].astype(int)
            
        manhattan_zips = list(get_manhattan_zip_map().keys())
        manhattan_gdf = modzcta_gdf[modzcta_gdf['zipcode'].isin(manhattan_zips)]
            
        zip_to_neighborhood = get_manhattan_zip_map()
        manhattan_gdf['neighborhood'] = manhattan_gdf['zipcode'].map(zip_to_neighborhood)
            
        manhattan_gdf['neighborhood'].fillna('Other', inplace=True)
            
        manhattan_gdf_dissolved = manhattan_gdf.dissolve(by='neighborhood').reset_index()
            
        return manhattan_gdf_dissolved
    
    return None

def create_facility_map(facilities_df, geo_data=None):
    
    neighborhood_counts = facilities_df.groupby('NEIGHBORHOOD').size().reset_index(name='FACILITY_COUNT')
    
    neighborhood_coords = get_neighborhood_coordinates()
    neighborhood_df = pd.DataFrame([
        {'NEIGHBORHOOD': nbhd, 'LATITUDE': lat, 'LONGITUDE': lon} 
        for nbhd, (lat, lon) in neighborhood_coords.items()
    ])
    
    # Merge with counts
    neighborhood_df = pd.merge(
        neighborhood_df,
        neighborhood_counts,
        on='NEIGHBORHOOD',
        how='left'
    ).fillna(0)
    
    neighborhood_df['FACILITY_COUNT'] = neighborhood_df['FACILITY_COUNT'].astype(int)
    
    tab1, tab2 = st.tabs(["Neighborhood Overview", "Individual Facilities"])
    
    with tab1:
        st.subheader("Health Facilities by Manhattan Neighborhood (2023)")
        
        if geo_data is not None:
            # Merge facility counts with geo data
            geo_data_with_counts = geo_data.merge(
                neighborhood_counts,
                left_on='neighborhood',
                right_on='NEIGHBORHOOD',
                how='left'
            ).fillna(0)
            
            # Choropleth map using neighborhood boundaries
            fig = px.choropleth_mapbox(
                geo_data_with_counts,
                geojson=geo_data_with_counts.geometry.__geo_interface__,
                locations=geo_data_with_counts.index,
                color='FACILITY_COUNT',
                color_continuous_scale='Viridis',
                hover_name='neighborhood',
                hover_data={'FACILITY_COUNT': True},
                zoom=11,
                center={"lat": 40.78, "lon": -73.97},
                opacity=0.7,
                labels={'FACILITY_COUNT': 'Number of Facilities'},
                title="Health Facilities in Manhattan by Neighborhood (2023)"
            )
            
            # Update layout for better visibility
            fig.update_layout(
                mapbox_style="carto-positron",
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                height=700,
            )
            
            # Display the map
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Bubble map using neighborhood centroids
            fig = px.scatter_mapbox(
                neighborhood_df,
                lat='LATITUDE',
                lon='LONGITUDE',
                size='FACILITY_COUNT',
                color='FACILITY_COUNT',
                color_continuous_scale='Viridis',
                size_max=30,
                zoom=11,
                center={"lat": 40.78, "lon": -73.97},
                opacity=0.7,
                hover_name='NEIGHBORHOOD',
                hover_data={'FACILITY_COUNT': True},
                labels={'FACILITY_COUNT': 'Number of Facilities'},
                title="Health Facilities in Manhattan by Neighborhood (2023)"
            )
            
            fig.update_layout(
                mapbox_style="carto-positron",
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                height=700,
            )
            

            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Health Facility Statistics by Neighborhood (2023)")
        
        # Summary statistics
        st.markdown("### Summary Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Facilities", f"{len(facilities_df)}")
        
        with col2:
            st.metric("Neighborhoods with Facilities", f"{len(neighborhood_counts)}")
        
        with col3:
            st.metric("Average per Neighborhood", f"{neighborhood_counts['FACILITY_COUNT'].mean():.1f}")
        
        # Bar chart showing facilities by neighborhood
        st.markdown("### Distribution by Neighborhood")
        sorted_counts = neighborhood_counts.sort_values('FACILITY_COUNT', ascending=False)
        
        fig = px.bar(
            sorted_counts,
            x='NEIGHBORHOOD',
            y='FACILITY_COUNT',
            color='FACILITY_COUNT',
            color_continuous_scale='Viridis',
            title="Number of Health Facilities by Manhattan Neighborhood (2023)",
            labels={
                'NEIGHBORHOOD': 'Neighborhood',
                'FACILITY_COUNT': 'Number of Facilities'
            }
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title="Neighborhood",
            yaxis_title="Number of Facilities"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Detailed Neighborhood Facility Counts")
        
        sorted_data = neighborhood_counts.sort_values('FACILITY_COUNT', ascending=False)
        
        sorted_data = sorted_data.reset_index(drop=True)
        sorted_data.index = sorted_data.index + 1

        st.dataframe(sorted_data, use_container_width=True)
    
    with tab2:
        st.subheader("Individual Health Facility Locations (2023)")
        
        # Filter
        selected_neighborhoods = st.multiselect(
            "Select Neighborhoods:",
            options=sorted(facilities_df['NEIGHBORHOOD'].unique()),
            default=[]
        )
        
        if selected_neighborhoods:
            filtered_facilities = facilities_df[facilities_df['NEIGHBORHOOD'].isin(selected_neighborhoods)]
        else:
            filtered_facilities = facilities_df
        
        st.write(f"Displaying {len(filtered_facilities)} facilities")
        
        fig = px.scatter_mapbox(
            filtered_facilities,
            lat='LATITUDE',
            lon='LONGITUDE',
            hover_name='FACILITY_NAME',
            hover_data={
                'NEIGHBORHOOD': True,
                'ZIP_CODE': True,
                'LATITUDE': False,
                'LONGITUDE': False
            },
            zoom=11,
            center={"lat": 40.78, "lon": -73.97},
            opacity=0.7,
            color_discrete_sequence=['green'],
            title="Health Facility Locations in Manhattan (2023)"
        )
        
        # Update layout for better visibility
        fig.update_layout(
            mapbox_style="carto-positron",
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            height=700
        )
        
        # Display the map
        st.plotly_chart(fig, use_container_width=True)
        
        # Show data table
        try:
            display_columns = ['FACILITY_NAME', 'NEIGHBORHOOD', 'ZIP_CODE', 'Short Description']
            st.dataframe(filtered_facilities[display_columns], use_container_width=True)
        except:
            display_columns = ['FACILITY_NAME', 'NEIGHBORHOOD', 'ZIP_CODE']
            st.dataframe(filtered_facilities[display_columns], use_container_width=True)

@st.cache_data
def load_property_data():
    file_path = "datasets/2023_manhattan.xlsx"
        
    if not os.path.exists(file_path):
        st.warning(f"Property price data file not found: {file_path}")
        return pd.DataFrame()
            
    df = pd.read_excel(file_path)
        
    df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
    df = df[df['sale_price'] > 10000]  
        
    zip_to_neighborhood = get_manhattan_zip_map()
    df['NEIGHBORHOOD'] = df['ZIP CODE'].map(zip_to_neighborhood)
        
    df = df.dropna(subset=['NEIGHBORHOOD'])
        
    return df

def analyze_facility_price_relationship(facilities_df, property_df):
    
    st.subheader("Health Facilities vs. Property Prices (2023)")
    
    facility_counts = facilities_df.groupby('NEIGHBORHOOD').size().reset_index(name='FACILITY_COUNT')
    
    price_stats = property_df.groupby('NEIGHBORHOOD').agg({
        'sale_price': ['median', 'mean', 'count']
    }).reset_index()
    
    price_stats.columns = ['NEIGHBORHOOD', 'MEDIAN_PRICE', 'MEAN_PRICE', 'SALES_COUNT']
    
    merged_df = pd.merge(facility_counts, price_stats, on='NEIGHBORHOOD', how='inner')
    
    sorted_df = merged_df.sort_values('FACILITY_COUNT', ascending=False)
    
    fig3 = px.treemap(
        merged_df,
        path=['NEIGHBORHOOD'],
        values='FACILITY_COUNT',
        color='MEDIAN_PRICE',
        color_continuous_scale='Blues',
        hover_data=['MEDIAN_PRICE', 'SALES_COUNT'],
        title="Neighborhood Comparison: Facility Count (size) vs. Property Price (color)",
        labels={
            'NEIGHBORHOOD': 'Neighborhood',
            'FACILITY_COUNT': 'Facility Count',
            'MEDIAN_PRICE': 'Median Price ($)'
        }
    )
    
    fig3.update_layout(height=600)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Correlation
    correlation = merged_df['FACILITY_COUNT'].corr(merged_df['MEDIAN_PRICE'])
    
    st.markdown(f"**Correlation between Facility Count and Median Property Price:** {correlation:.3f}")
    
    if correlation > 0.5:
        st.markdown("There appears to be a **positive relationship** between the number of health facilities and property prices in Manhattan neighborhoods. Areas with more health facilities tend to have higher property prices.")
    elif correlation < -0.5:
        st.markdown("There appears to be a **negative relationship** between the number of health facilities and property prices in Manhattan neighborhoods. Areas with more health facilities tend to have lower property prices.")
    else:
        st.markdown("There appears to be a **weak or moderate relationship** between the number of health facilities and property prices in Manhattan neighborhoods.")
    
    st.markdown("""
    <p style="font-size: 20px;">
    The Upper East Side, Harlem, and Washington Heights had the highest number of health facilities in 2023. Based on the treemap, we found a weak to moderate negative relationship between the number of facilities and median property prices, suggesting that neighborhoods with more health facilities tended to have slightly lower median property prices, although the relationship is not very strong. There are many potential explanations for this correlation. For example, neighborhoods with a lot of institutional buildings often have less space available for high-end residential development, which can limit property prices because there is not a lot of space reserved for building luxury real estate for sale. Another explanation could be that public health infrastructure tends to be placed based on population density and need (e.g., rates of chronic illness, older populations), rather than wealth. Neighborhoods with larger vulnerable populations may have more facilities, while as analyzed earlier, there was a small negative correlation between average age and real estate prices.
    </p>
     """, unsafe_allow_html=True)

    st.subheader("Detailed Neighborhood Comparison")

    display_df = merged_df.copy()
    display_df['MEDIAN_PRICE'] = display_df['MEDIAN_PRICE'].apply(lambda x: f"${x:,.2f}")
    display_df['MEAN_PRICE'] = display_df['MEAN_PRICE'].apply(lambda x: f"${x:,.2f}")
    
    display_df.columns = [
        'Neighborhood', 
        'Facility Count', 
        'Median Property Price', 
        'Mean Property Price', 
        'Property Sales Count'
    ]
    
    sorted_display_df = display_df.sort_values('Facility Count', ascending=False)
    
    st.dataframe(sorted_display_df, use_container_width=True)

def show():
    """Display Manhattan health facilities map and analysis"""
    st.title("Manhattan Health Facilities Interactive Map (2023)")
    
    st.markdown("""
    <p style="font-size: 20px;">
    On this page, we present the relationship between healthcare infrastructure and property values across Manhattan neighborhoods. Using data from the Health Facilities Information System (HFIS), we analyze the spatial distribution of hospitals and hospital extension clinics. The interactive visualization includes a color-coded choropleth map showing facility density by neighborhood, accompanied by a histogram illustrating the distribution pattern. For detailed reference, a comprehensive table provides precise facility counts for each neighborhood. 
    </p>
    """, unsafe_allow_html=True)

    with st.spinner("Loading health facility data..."):
        facilities_df = load_health_facilities()
    
    with st.spinner("Loading geospatial data..."):
        geo_data = load_geospatial_data()
    
    with st.spinner("Loading property price data..."):
        property_df = load_property_data()
    
    tab1, tab2 = st.tabs(["Facility Distribution", "Facility vs. Property Prices"])
    
    with tab1:
        st.write(f"Found {len(facilities_df)} health facilities in Manhattan in 2023")
            
        create_facility_map(facilities_df, geo_data)
    
    with tab2:
        if not property_df.empty and not facilities_df.empty:
            analyze_facility_price_relationship(facilities_df, property_df)
        else:
            st.error("Cannot perform analysis: Missing property price data or facility data")

if __name__ == "__main__":
    show()