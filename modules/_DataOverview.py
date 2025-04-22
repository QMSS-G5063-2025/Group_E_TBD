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
    
    # Neighborhood filter
    all_neighborhoods = sorted(df['neighborhood'].unique().tolist())
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
        filtered_df = filtered_df[filtered_df['neighborhood'].isin(selected_neighborhoods)]
    
    # Display Data
    st.subheader("Filtered Data Summary")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        st.metric("Filtered Records", f"{len(filtered_df):,}")
    with fcol2:
        st.metric("Average Price", f"${filtered_df['sale_price'].mean():,.2f}")
    
    # Selection of visualization
    st.subheader("Data Visualizations")
    
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
        
    elif viz_type == "Neighborhood Comparison":
        neighborhood_avg = filtered_df.groupby('neighborhood')['sale_price'].mean().reset_index()
        neighborhood_avg = neighborhood_avg.sort_values('sale_price', ascending=False)
            
        fig = px.bar(
                neighborhood_avg,
                x='neighborhood',
                y='sale_price',
                title="Average Sale Price by Neighborhood (2023)",
                labels={'neighborhood': 'Neighborhood', 'sale_price': 'Average Price ($)'},
                color='sale_price',
                color_continuous_scale='Blues'
        )
        fig.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Average Price ($)",
                xaxis_title="Neighborhood"
        )
        st.plotly_chart(fig, use_container_width=True)
  
    # Data Table
    st.subheader("Interactive Data Table")
    
    # Column selector
    all_columns = df.columns.tolist()
    default_columns = ['ADDRESS', 'neighborhood', 'ZIP CODE', 'sale_price']
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
    
    # Download option
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="manhattan_sales_2023_filtered.csv",
        mime="text/csv",
    )