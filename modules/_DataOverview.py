import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.data_loader import load_data

def show():
    st.title("Manhattan Real Estate Sales Data Overview (2023)")

    # Custom data loading function to use the specified file path
    @st.cache_data
    def load_sales_data():
        file_path = "datasets/2023_manhattan.xlsx"
        df = pd.read_excel(file_path)
        # Basic data cleaning
        df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
        df = df[df['sale_price'] > 10000] 
        
        # Define the consolidated neighborhoods - using the same mapping as in PriceMap
        neighborhood_mapping = {
            'UPPER EAST SIDE (59-79)': 'Upper East Side',
            'UPPER EAST SIDE (79-96)': 'Upper East Side',
            'UPPER EAST SIDE (96-110)': 'Upper East Side',
            'ROOSEVELT ISLAND': 'Upper East Side',
            'YORKVILLE': 'Upper East Side',
            
            'UPPER WEST SIDE (59-79)': 'Upper West Side', 
            'UPPER WEST SIDE (79-96)': 'Upper West Side',
            'UPPER WEST SIDE (96-116)': 'Upper West Side',
            'MANHATTAN VALLEY': 'Upper West Side',
            'LINCOLN CENTER': 'Upper West Side',
            
            'MIDTOWN EAST': 'Midtown East',
            'MURRAY HILL': 'Midtown East',
            'SUTTON PLACE': 'Midtown East',
            
            'MIDTOWN WEST': 'Midtown',
            'MIDTOWN CBD': 'Midtown',
            'CLINTON': 'Midtown',
            "HELL'S KITCHEN": "Midtown",
            'FASHION': 'Midtown',
            
            'GRAMERCY': 'Gramercy',
            'KIPS BAY': 'Gramercy',
            'FLATIRON': 'Gramercy',
            
            'GREENWICH VILLAGE-CENTRAL': 'Greenwich Village', 
            'GREENWICH VILLAGE-WEST': 'Greenwich Village',
            'WEST VILLAGE': 'Greenwich Village',
            
            'CHELSEA': 'Chelsea',
            
            'SOHO': 'SoHo/TriBeCa',
            'TRIBECA': 'SoHo/TriBeCa',
            'LITTLE ITALY': 'SoHo/TriBeCa',
            
            'FINANCIAL': 'Financial District',
            'CIVIC CENTER': 'Financial District',
            'SEAPORT': 'Financial District',
            'SOUTHBRIDGE': 'Financial District',
            
            'BATTERY PARK CITY': 'Battery Park City',
            
            'EAST VILLAGE': 'East Village',
            'ALPHABET CITY': 'East Village',
            
            'LOWER EAST SIDE': 'Lower East Side',
            'CHINATOWN': 'Lower East Side',
            
            'HARLEM-CENTRAL': 'Harlem',
            'HARLEM-EAST': 'Harlem',
            'HARLEM-UPPER': 'Harlem',
            'HARLEM-WEST': 'Harlem',
            'MORNINGSIDE HEIGHTS': 'Harlem',
            
            'WASHINGTON HEIGHTS LOWER': 'Washington Heights',
            'WASHINGTON HEIGHTS UPPER': 'Washington Heights',
            'INWOOD': 'Washington Heights'
        }
        
        st.markdown("""
        <p style="font-size: 20px;">
        The main dataset, the rolling sales data, we used for the analysis was released by the New York City Department of Finance. The dataset provides detailed records of property sales across the city. For simplicity because of the project scope, we chose to dive deeply into the prices of Manhattan. We offer a streamlined summary of the original dataset to help users better understand trends in Manhattan's real estate market.
        </p>
        """, unsafe_allow_html=True)

        # Apply the mapping to create a consolidated neighborhood column
        if 'neighborhood' in df.columns:
            df['consolidated_neighborhood'] = df['neighborhood'].map(
                lambda x: next((v for k, v in neighborhood_mapping.items() if k in str(x).upper()), x)
            )
        else:
            # If neighborhood doesn't exist, create it based on ZIP CODE
            zip_to_neighborhood = {
                10001: "Chelsea",
                10002: "Lower East Side",
                10003: "East Village",
                10004: "Financial District",
                10005: "Financial District",
                10006: "Financial District",
                10007: "SoHo/TriBeCa",
                10009: "East Village",
                10010: "Gramercy",
                10011: "Chelsea",
                10012: "SoHo/TriBeCa",
                10013: "SoHo/TriBeCa",
                10014: "Greenwich Village",
                10016: "Gramercy",
                10017: "Midtown East",
                10018: "Midtown",
                10019: "Midtown",
                10020: "Midtown",
                10021: "Upper East Side",
                10022: "Midtown East",
                10023: "Upper West Side",
                10024: "Upper West Side",
                10025: "Upper West Side",
                10026: "Harlem",
                10027: "Harlem",
                10028: "Upper East Side",
                10029: "Harlem",
                10030: "Harlem",
                10031: "Harlem",
                10032: "Washington Heights",
                10033: "Washington Heights",
                10034: "Washington Heights",
                10035: "Harlem",
                10036: "Midtown",
                10037: "Harlem",
                10038: "Financial District",
                10039: "Harlem",
                10040: "Washington Heights",
                10044: "Upper East Side",
                10065: "Upper East Side",
                10069: "Upper West Side",
                10075: "Upper East Side",
                10128: "Upper East Side",
                10280: "Battery Park City",
                10282: "Battery Park City",
            }
            df['consolidated_neighborhood'] = df['ZIP CODE'].map(zip_to_neighborhood)
        
        return df

    with st.spinner("Loading 2023 sales data..."):
        df = load_sales_data()
    
    # Display basic dataset information
    st.subheader("Dataset Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("Average Price", f"${df['sale_price'].mean():,.2f}")
    
    # Filter
    st.sidebar.header("Data Filters")
    
    # Price Filter
    min_price = int(df['sale_price'].min())
    max_price = int(df['sale_price'].max())
    price_range = st.sidebar.slider(
        "Price Range",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )
    
    # Neighborhood filter - using consolidated neighborhoods
    all_neighborhoods = sorted(df['consolidated_neighborhood'].dropna().unique().tolist())
    selected_neighborhoods = st.sidebar.multiselect(
        "Select Neighborhoods",
        options=all_neighborhoods,
        default=[]
    )
    
    # Filters
    filtered_df = df.copy()
    
    # Price filter data
    filtered_df = filtered_df[(filtered_df['sale_price'] >= price_range[0]) & 
                             (filtered_df['sale_price'] <= price_range[1])]
    
    # Neighborhood filter data
    if selected_neighborhoods:
        filtered_df = filtered_df[filtered_df['consolidated_neighborhood'].isin(selected_neighborhoods)]
    
    # Display Data
    st.subheader("Filtered Data Summary")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        st.metric("Filtered Records", f"{len(filtered_df):,}")
    with fcol2:
        st.metric("Average Price", f"${filtered_df['sale_price'].mean():,.2f}")
    
    # Selection of visualization
    st.subheader("Data Visualizations")
    
    st.markdown("""
    <p style="font-size: 20px;">
    To make the data more readable, we included two interactive histograms that allow for both broad and specific analysis:
    </p>
     """, unsafe_allow_html=True)
    
    viz_type = st.radio(
        "Select Visualization",
        ["Price Distribution", "Neighborhood Comparison"]
    )
    
    if viz_type == "Price Distribution":
        # Histogram       
        fig = px.histogram(
            filtered_df,
            x='sale_price',
            nbins=50,
            title="Distribution of Sale Prices (2023)",
            labels={'sale_price': 'Sale Price ($)'},
            color_discrete_sequence=['steelblue']
        )

        fig.update_layout(
            xaxis_title="Sale Price ($)",
            yaxis_title="Count",
            xaxis=dict(
                tickmode='array',
                tickvals=[0, 100000000, 200000000, 300000000, 400000000, 500000000],
                ticktext=['0', '100M', '200M', '300M', '400M', '500M']
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <p style="font-size: 20px;">
        The Price Distribution histogram shows the overall distribution of sales prices in Manhattan. Users can filter by one or more neighborhoods to directly compare pricing trends across areas.</p>
        <p style="font-size: 20px;">
        The vast majority of sale prices in 2023 were clustered at the lower end of the price range. The distribution is extremely right-skewed, with most properties selling for relatively lower amounts while only a very small number reached extremely high sale prices. Beyond around $10 million, the number of transactions drops sharply, suggesting that ultra-high-value sales are rare outliers, while the majority of real estate activity took place at more modest price points.</p> 
        """, unsafe_allow_html=True)
    
    elif viz_type == "Neighborhood Comparison":
        # Use consolidated neighborhoods for more concise visualization
        neighborhood_avg = filtered_df.groupby('consolidated_neighborhood')['sale_price'].mean().reset_index()
        neighborhood_avg = neighborhood_avg.sort_values('sale_price', ascending=False)
            
        fig = px.bar(
                neighborhood_avg,
                x='consolidated_neighborhood',
                y='sale_price',
                title="Average Sale Price by Neighborhood (2023)",
                labels={'consolidated_neighborhood': 'Neighborhood', 'sale_price': 'Average Price ($)'},
                color='sale_price',
                color_continuous_scale='Blues'
        )
        fig.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Average Price ($)",
                xaxis_title="Neighborhood",
                height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
        <p style="font-size: 20px;">
        The Neighborhood Comparison histogram displays the average sales price in each neighborhood, also filterable for targeted comparisons.</p>
        <p style="font-size: 20px;"> 
        Midtown and the Javits Center had the highest average sale prices in 2023, both significantly exceeding $7 million. These neighborhoods stood out clearly from the rest, with Midtown reaching close to $8 million on average. SoHo and Tribeca followed, with average prices hovering above $6 million. Together with Harlem and Greenwich Village, these were the top 5 most expensive neighborhoods by average sales price in 2023. On the other end, Midtown East, Lower East Side, and Upper West Side had much lower average sale prices, all falling below $3 million, indicating that only a few neighborhoods dominated the luxury real estate market.</p>
        """, unsafe_allow_html=True)
  
    # Data Table
    st.subheader("Interactive Data Table")
    
    # Column selector
    all_columns = df.columns.tolist()
    default_columns = ['ADDRESS', 'consolidated_neighborhood', 'ZIP CODE', 'sale_price']
    selected_columns = st.multiselect(
        "Select Columns to Display",
        options=all_columns,
        default=default_columns
    )
    
    # Sorting
    sort_column = st.selectbox("Sort By", options=selected_columns if selected_columns else all_columns)
    sort_ascending = st.checkbox("Sort Ascending", value=False)
    
    if sort_column:
        filtered_df = filtered_df.sort_values(by=sort_column, ascending=sort_ascending)
    
    # Display
    if selected_columns:
        st.dataframe(filtered_df[selected_columns], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)
    
    st.markdown("""
    <p style="font-size: 20px;">
    For those interested in deeper inspection of the data, the full dataset is available in a table format that is both filterable on the webpage and downloadable for independent exploration. Users can customize what the table shows by selecting variables such as address, neighborhood, zip code, borough (which is less relevant because the analysis is limited to Manhattan), and of course, sales price.
    </p>
    <p style="font-size: 20px;">
    This page is designed to support informed exploration, whether you're a curious resident, prospective buyer, or urban researcher.
    </p>
    """, unsafe_allow_html=True)
        
    # Download option
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="manhattan_sales_2023_filtered.csv",
        mime="text/csv",
    )
