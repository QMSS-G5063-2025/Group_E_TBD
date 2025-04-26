import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import shapely.wkt
import geopandas as gpd
import os
from utils.data_loader import load_data

@st.cache_data
def load_data_by_year(year):
    if year in ["2020", "2021", "2022", "2023"]:
        data_path = f"datasets/{year}_manhattan.xlsx"
            
        if os.path.exists(data_path):
            df = pd.read_excel(data_path)
            df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
            df = df[df['sale_price'] > 0]
            
            # Map neighborhoods and coordinates if they don't exist in the dataset
            if 'neighborhood' not in df.columns or 'latitude' not in df.columns or 'longitude' not in df.columns:
                # Define ZIP code to neighborhood mapping
                # This is a copy of the mapping from your data_loader.py
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
                
                # Create neighborhood and coordinates columns
                df['neighborhood'] = df['ZIP CODE'].map(lambda x: zip_to_info.get(x, ("Unknown", np.nan, np.nan))[0])
                df['latitude'] = df['ZIP CODE'].map(lambda x: zip_to_info.get(x, ("Unknown", np.nan, np.nan))[1])
                df['longitude'] = df['ZIP CODE'].map(lambda x: zip_to_info.get(x, ("Unknown", np.nan, np.nan))[2])
                
                # Remove rows with missing data
                df = df.dropna(subset=['latitude', 'longitude', 'neighborhood'])
            
            return df
        else:
            st.error(f"Dataset file not found: {data_path}")
            return load_data()  # Fall back to default data
    else:
        # Default to current data (use the existing load_data function)
        return load_data()

def show():
    """Render a map of Manhattan real estate prices by neighborhood boundaries"""
    st.title("Manhattan Real Estate Price Map")
    
    st.markdown("""
    <p style="font-size: 20px;">
    Using the same dataset from NYC Department of Finance, we presented a spatial analysis on a color-coded choropleth map of Manhattan by displaying median sales prices in each neighborhood. Instead of looking only at the data of 2023 in the overview, the user can now access annual data from 2020-2023 to observe pricing patterns and market evolution over time. They can select any year of interest to inspect the data in more detail. 
    </p>
    """, unsafe_allow_html=True)
    
    year_options = ["2023", "2022", "2021", "2020"]
    selected_year = st.selectbox("Select Year", year_options)
    
    with st.spinner(f"Loading property data for {selected_year}..."):
        df = load_data_by_year(selected_year)
        year_display = selected_year
    
    min_filter = 10000  
    max_filter = 50000000 
    df_filtered = df[(df['sale_price'] >= min_filter) & (df['sale_price'] <= max_filter)]
    
    neighborhood_stats = df_filtered.groupby('neighborhood').agg({
        'sale_price': ['median', 'mean', 'count'],
        'latitude': 'mean',
        'longitude': 'mean'
    }).reset_index()
    
    # Adjust column names
    neighborhood_stats.columns = ['neighborhood', 'median_price', 'mean_price', 'sales_count', 'latitude', 'longitude']
    
    # Try to process MODZCTA data to get neighborhood regions
    try:
        modzcta_df = pd.read_csv('datasets/Modified_Zip_Code_Tabulation_Areas__MODZCTA__20250421.csv')
        
        # Check if the dataset has geometry information
        if 'the_geom' in modzcta_df.columns:
            # Convert WKT geometry strings to GeoDataFrame
            geometries = modzcta_df['the_geom'].apply(shapely.wkt.loads)
            modzcta_gdf = gpd.GeoDataFrame(modzcta_df, geometry=geometries, crs="EPSG:4326")
            
            # Convert MODZCTA to match zipcode in our data
            modzcta_gdf['zipcode'] = modzcta_gdf['MODZCTA'].astype(int)
            
            # Filter to just Manhattan ZIP codes (10001-10282)
            manhattan_zips = [zipcode for zipcode in modzcta_gdf['zipcode']
                              if 10001 <= zipcode <= 10282]
            manhattan_gdf = modzcta_gdf[modzcta_gdf['zipcode'].isin(manhattan_zips)]
            
            # Create a zipcode to neighborhood mapping using your load_data function results
            # Here we use a more robust approach to handle duplicate neighborhoods
            zip_to_neighborhood = {}
            for index, row in df_filtered.drop_duplicates(['ZIP CODE', 'neighborhood']).iterrows():
                zip_to_neighborhood[row['ZIP CODE']] = row['neighborhood']
            
            manhattan_gdf['neighborhood'] = manhattan_gdf['zipcode'].map(zip_to_neighborhood)
            
            manhattan_gdf['neighborhood'].fillna('Other', inplace=True)
            
            # Key fix: Dissolve geometries by neighborhood to combine same-named neighborhoods
            manhattan_gdf_dissolved = manhattan_gdf.dissolve(by='neighborhood').reset_index()
            
            # Merge with neighborhood stats
            manhattan_gdf_dissolved = manhattan_gdf_dissolved.merge(
                neighborhood_stats,
                on='neighborhood',
                how='left'
            )
            
            manhattan_gdf_dissolved['median_price'].fillna(0, inplace=True)
            manhattan_gdf_dissolved['mean_price'].fillna(0, inplace=True)
            manhattan_gdf_dissolved['sales_count'].fillna(0, inplace=True)
        

            # Choropleth map
            fig = px.choropleth_mapbox(
                manhattan_gdf_dissolved,
                geojson=manhattan_gdf_dissolved.geometry.__geo_interface__,
                locations=manhattan_gdf_dissolved.index,
                color='median_price',
                color_continuous_scale='Blues',
                range_color=(neighborhood_stats['median_price'].min(), neighborhood_stats['median_price'].max()),
                hover_name='neighborhood', 
                hover_data={
                    'zipcode': False,
                    'MODZCTA': False,
                    'neighborhood': True,
                    'median_price': True,
                    'mean_price': True,
                    'sales_count': True
                },
                zoom=11,
                center={"lat": 40.78, "lon": -73.97},
                opacity=0.8,
                labels={
                    'median_price': 'Median Price ($)',
                    'mean_price': 'Mean Price ($)',
                    'sales_count': 'Number of Sales'
                },
                title=f"Manhattan Real Estate Prices ({year_display})"
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
            # If no geometry column, fall back to bubble map
            create_bubble_map(neighborhood_stats, year_display)
            
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        create_bubble_map(neighborhood_stats, year_display)
    
    show_neighborhood_rankings(neighborhood_stats, year_display)


def create_bubble_map(neighborhood_stats, year_display):
    """Create a bubble map of neighborhoods"""
    # Bubble map
    fig = px.scatter_mapbox(
        neighborhood_stats,
        lat='latitude',
        lon='longitude',
        size='median_price', 
        size_max=40,
        color='median_price',  
        color_continuous_scale='Blues',
        hover_name='neighborhood',
        hover_data={
            'neighborhood': True,
            'median_price': True,
            'mean_price': True,
            'sales_count': True,
            'latitude': False,
            'longitude': False
        },
        zoom=11,
        center={"lat": 40.78, "lon": -73.97},
        opacity=0.8,
        labels={
            'median_price': 'Median Price ($)',
            'mean_price': 'Mean Price ($)',
            'sales_count': 'Number of Sales'
        },
        title=f"Manhattan Real Estate Prices ({year_display})"
    )
    
    # Update layout
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=700
    )
    
    # Display the map
    st.plotly_chart(fig, use_container_width=True)


def show_neighborhood_rankings(neighborhood_stats, year_display):
    """Show neighborhood price rankings and visualizations"""
    # Display neighborhood price ranking
    st.subheader(f"Neighborhood Price Ranking ({year_display})")
    
    # Sort by median price
    sorted_stats = neighborhood_stats.sort_values('median_price', ascending=False)
    sorted_stats = sorted_stats.reset_index(drop=True)
    sorted_stats.index = sorted_stats.index + 1  # Rank starting from 1
    
    display_columns = ['neighborhood', 'median_price', 'mean_price', 'sales_count']
    table_data = sorted_stats[display_columns].copy()
    table_data.columns = ['Neighborhood', 'Median Price', 'Mean Price', 'Sales Count']
    
    table_data['Median Price'] = table_data['Median Price'].apply(lambda x: f"${x:,.2f}")
    table_data['Mean Price'] = table_data['Mean Price'].apply(lambda x: f"${x:,.2f}")
    
    # Display table
    st.dataframe(table_data, use_container_width=True)
    
    # Bar chart of top 15 neighborhoods by price
    st.subheader(f"Top 15 Neighborhoods by Median Price ({year_display})")
    top_neighborhoods = sorted_stats.head(15)
    
    fig = px.bar(
        top_neighborhoods,
        x='neighborhood',
        y='median_price',
        color='median_price',
        color_continuous_scale='Blues',
        labels={'neighborhood': 'Neighborhood', 'median_price': 'Median Price ($)'},
        title=f"Manhattan's Most Expensive Neighborhoods ({year_display})"
    )
    
    fig.update_layout(
        xaxis_title="Neighborhood",
        yaxis_title="Median Price ($)",
        xaxis={'categoryorder': 'total descending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)