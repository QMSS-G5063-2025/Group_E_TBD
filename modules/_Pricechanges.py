import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from utils.data_loader import load_data

def show():
    st.title("Manhattan Property Price Changes (2015-2023)")
    
    # Load data from each year
    @st.cache_data
    def load_yearly_data():
        years = list(range(2015, 2024))  # 2015 to 2023
        yearly_data = {}
        neighborhood_mapping = get_neighborhood_mapping()
        
        for year in years:
            # Check for both .xls and .xlsx files
            file_path = None
            for ext in ['.xlsx', '.xls']:
                temp_path = f"datasets/{year}_manhattan{ext}"
                if os.path.exists(temp_path):
                    file_path = temp_path
                    break
            
            if not file_path:
                continue
                
            try:
                # Load the data
                df = pd.read_excel(file_path)
                
                # Basic data cleaning for sale price
                if 'sale_price' in df.columns:
                    df['sale_price'] = pd.to_numeric(df['sale_price'], errors='coerce')
                else:
                    # Try to find a column that might contain price data
                    price_candidates = [col for col in df.columns if 'price' in str(col).lower() or 'sale' in str(col).lower()]
                    if price_candidates:
                        df['sale_price'] = pd.to_numeric(df[price_candidates[0]], errors='coerce')
                    else:
                        continue
                
                # Filter out very low values
                df = df[df['sale_price'] > 10000]
                
                # Handle the consolidated neighborhoods
                # First try to use either neighborhood column 
                if 'neighborhood' in df.columns:
                    df['consolidated_neighborhood'] = df['neighborhood'].map(
                        lambda x: next((v for k, v in neighborhood_mapping.items() 
                                      if k in str(x).upper()), None)
                    )
                else:
                    # Try to use zip code - check exact column names in the dataframe
                    zip_col = None
                    
                    # Method 1: Check if 'ZIP CODE' exists with exact case
                    if 'ZIP CODE' in df.columns:
                        zip_col = 'ZIP CODE'
                    
                    # Method 2: Check common variations
                    if not zip_col:
                        zip_variations = ['ZIP', 'ZIPCODE', 'Zip Code', 'zip_code', 'zip', 'Zip']
                        for col in zip_variations:
                            if col in df.columns:
                                zip_col = col
                                break
                    
                    # Method 3: Case insensitive search
                    if not zip_col:
                        for col in df.columns:
                            if 'zip' in str(col).lower():
                                zip_col = col
                                break
                    
                    # If we found a zip column, use it
                    if zip_col:
                        # Create mapping function that handles NaN values and different types
                        zip_to_neighborhood = get_zip_to_neighborhood_mapping()
                        
                        # Use a safe mapping approach
                        def safe_map(code):
                            try:
                                # Try to convert to integer (handles strings, floats, etc.)
                                int_code = int(float(code))
                                return zip_to_neighborhood.get(int_code, None)
                            except (ValueError, TypeError):
                                return None
                        
                        # Apply the mapping
                        df['consolidated_neighborhood'] = df[zip_col].apply(safe_map)
                
                # Remove rows with None in consolidated_neighborhood
                df = df.dropna(subset=['consolidated_neighborhood'])
                
                # Group by neighborhood and calculate statistics
                neighborhood_stats = df.groupby('consolidated_neighborhood').agg({
                    'sale_price': ['median', 'mean', 'count']
                }).reset_index()
                
                # Flatten the column hierarchy
                neighborhood_stats.columns = ['neighborhood', 'median_price', 'mean_price', 'count']
                
                # Add year column
                neighborhood_stats['year'] = year
                
                # Add to yearly data
                yearly_data[year] = neighborhood_stats
                
            except Exception as e:
                pass
        
        return yearly_data
    
    def get_neighborhood_mapping():
        """Define the consolidated neighborhoods - using the same mapping as in other modules"""
        return {
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
    
    def get_zip_to_neighborhood_mapping():
        """Create ZIP code to neighborhood mapping"""
        return {
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
    
    with st.spinner("Loading data for all years (2015-2023)..."):
        yearly_data = load_yearly_data()
    
    if not yearly_data:
        st.error("No data found for any year. Please check the data files.")
        return
    
    st.markdown("""
    <p style="font-size: 20px;">
    To explore how real estate prices have evolved from 2015 to 2023, you can select specific neighborhoods to view their median and mean sale prices over time, with each neighborhood represented by a distinct color on the line chart for clear, straightforward comparison. Another feature on the page is the bar charts that allow for comparison of price changes between the selected neighborhoods in a particular year. 
    </p>
     """, unsafe_allow_html=True)
    
    # Combine all years into a single dataframe
    all_data = pd.concat([yearly_data[year] for year in yearly_data.keys()])
    
    # Get unique neighborhoods
    neighborhoods = sorted(all_data['neighborhood'].unique())
    
    # Filters
    st.subheader("Filter Options")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Neighborhood selection
        selected_neighborhoods = st.multiselect(
            "Select Neighborhoods",
            options=neighborhoods,
            default=["Upper East Side", "Upper West Side", "SoHo/TriBeCa", "Chelsea", "Greenwich Village", "Midtown"]
        )
    
    with col2:
        # Price metric selection
        price_metric = st.radio(
            "Price Metric",
            ["median_price", "mean_price"],
            index=0,
            format_func=lambda x: "Median Price" if x == "median_price" else "Mean Price"
        )
    
    # Filter data based on selections
    if selected_neighborhoods:
        filtered_data = all_data[all_data['neighborhood'].isin(selected_neighborhoods)]
    else:
        filtered_data = all_data.copy()
    
    # Create main tabs
    tab1, tab2 = st.tabs(["Price Trends", "Yearly Comparison"])
    
    with tab1:
        st.subheader("Manhattan Neighborhood Price Trends (2015-2023)")
        
        if filtered_data.empty:
            st.warning("No data available for the selected filters.")
        else:
            # Create line chart of price trends
            fig = px.line(
                filtered_data,
                x="year",
                y=price_metric,
                color="neighborhood",
                markers=True,
                title=f"{'Median' if price_metric == 'median_price' else 'Mean'} Price by Neighborhood (2015-2023)",
                labels={
                    "year": "Year",
                    price_metric: f"{'Median' if price_metric == 'median_price' else 'Mean'} Price ($)",
                    "neighborhood": "Neighborhood"
                },
                template="plotly_white"  # Using a white template for cleaner look
            )
            
            # Format y-axis as currency
            fig.update_layout(
                yaxis=dict(
                    tickprefix="$",
                    tickformat=",",
                ),
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(2015, 2024)),
                ),
                height=600,
                legend=dict(
                    title="",
                    orientation="v",
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="rgba(0, 0, 0, 0.3)",
                    borderwidth=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <p style="font-size: 20px;">
            From the median price trends, we found that most neighborhoods remained relatively stable between 2018 and 2023, with Battery Park City consistently having higher median prices compared to others. However, the gap between the prices gradually declined over the years. 
            </p>
            <p style="font-size: 20px;">
            The mean price trends display much sharper fluctuations across neighborhoods, particularly in the Financial District, Midtown, and Greenwich Village, with dramatic spikes and dips that did not appear in the median price chart. There had likely been a few exceptionally high-value sales in these areas during those years.
            </p>
            """, unsafe_allow_html=True)

            # Calculate and display growth rates
            st.subheader("Price Growth Analysis")
            
            try:
                # Pivot data for calculations
                pivot_data = filtered_data.pivot_table(
                    index='year', 
                    columns='neighborhood', 
                    values=price_metric
                ).reset_index()
                
                # Calculate year-over-year changes
                oldest_year = min(yearly_data.keys())
                latest_year = max(yearly_data.keys())
                
                # Overall growth rate
                if oldest_year in yearly_data and latest_year in yearly_data:
                    growth_data = []
                    
                    for neighborhood in selected_neighborhoods:
                        try:
                            # Get prices for first and last year
                            start_year = min(pivot_data['year'])
                            end_year = max(pivot_data['year'])
                            start_price = pivot_data[pivot_data['year'] == start_year][neighborhood].values[0]
                            end_price = pivot_data[pivot_data['year'] == end_year][neighborhood].values[0]
                            
                            # Calculate growth
                            total_growth = (end_price / start_price - 1) * 100
                            annual_growth = ((end_price / start_price) ** (1 / (end_year - start_year)) - 1) * 100
                            
                            growth_data.append({
                                'Neighborhood': neighborhood,
                                'Start Price': start_price,
                                'End Price': end_price,
                                'Total Growth (%)': total_growth,
                                'Annual Growth (%)': annual_growth
                            })
                        except:
                            # Skip if data is missing
                            continue
                    
                    if growth_data:
                        growth_df = pd.DataFrame(growth_data)
                        growth_df = growth_df.sort_values('Total Growth (%)', ascending=False)
                        
                        # Format price columns
                        growth_df['Start Price'] = growth_df['Start Price'].apply(lambda x: f"${x:,.2f}")
                        growth_df['End Price'] = growth_df['End Price'].apply(lambda x: f"${x:,.2f}")
                        growth_df['Total Growth (%)'] = growth_df['Total Growth (%)'].apply(lambda x: f"{x:.1f}%")
                        growth_df['Annual Growth (%)'] = growth_df['Annual Growth (%)'].apply(lambda x: f"{x:.1f}%")
                        
                        st.dataframe(growth_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error calculating growth rates: {str(e)}")
    
    with tab2:
        st.subheader("Year-by-Year Comparison")
        
        # Year selection
        years_available = sorted(yearly_data.keys())
        if len(years_available) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                year1 = st.selectbox("Select First Year", options=years_available, index=0)
            
            with col2:
                year2 = st.selectbox("Select Second Year", options=years_available, index=len(years_available)-1)
            
            if year1 in yearly_data and year2 in yearly_data:
                # Get data for selected years
                data_year1 = yearly_data[year1]
                data_year2 = yearly_data[year2]
                
                # Filter by selected neighborhoods
                if selected_neighborhoods:
                    data_year1 = data_year1[data_year1['neighborhood'].isin(selected_neighborhoods)]
                    data_year2 = data_year2[data_year2['neighborhood'].isin(selected_neighborhoods)]
                
                # Merge data from both years
                comparison_data = pd.merge(
                    data_year1[['neighborhood', price_metric]],
                    data_year2[['neighborhood', price_metric]],
                    on='neighborhood',
                    suffixes=(f'_{year1}', f'_{year2}')
                )
                
                # Calculate change
                comparison_data[f'change_{year1}_to_{year2}'] = (
                    comparison_data[f'{price_metric}_{year2}'] / 
                    comparison_data[f'{price_metric}_{year1}'] - 1
                ) * 100
                
                # Sort by price change
                comparison_data = comparison_data.sort_values(f'change_{year1}_to_{year2}', ascending=False)
                
                # Create bar chart showing change
                fig = px.bar(
                    comparison_data,
                    x='neighborhood',
                    y=f'change_{year1}_to_{year2}',
                    color=f'change_{year1}_to_{year2}',
                    color_continuous_scale='RdBu_r',  # Red for negative, Blue for positive
                    title=f"Price Change from {year1} to {year2} by Neighborhood",
                    labels={
                        'neighborhood': 'Neighborhood',
                        f'change_{year1}_to_{year2}': 'Price Change (%)'
                    }
                )
                
                fig.update_layout(
                    xaxis_tickangle=-45,
                    yaxis_title="Price Change (%)",
                    coloraxis_showscale=False,
                    height=500
                )
                
                # Add a reference line at 0%
                fig.add_shape(
                    type="line",
                    x0=-0.5,
                    y0=0,
                    x1=len(comparison_data) - 0.5,
                    y1=0,
                    line=dict(
                        color="black",
                        width=1,
                        dash="dash",
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                <p style="font-size: 20px;">
                When directly comparing the prices in 2018 and 2023 we can see that as the price map has previously indicated, Washington Heights experienced the most dramatic increase in real estate prices with a more than 100% increase in mean prices and 80% in median prices. This suggests that the higher value in property was not a mere result of multiple outlier deals but a broader growth, whereas the significant growth perceived in Harlem might be because of a few high-value sales. While SoHo/Tribeca went through the biggest drop in median prices, Chelsea had the biggest decrease for mean prices. There was an indication of a general declining trend in the traditionally more expensive neighborhood.
                </p>
                """, unsafe_allow_html=True)

                # Display comparison table
                st.subheader(f"Price Comparison Table ({year1} vs {year2})")
                
                # Format table for display
                display_data = comparison_data.copy()
                display_data[f'{price_metric}_{year1}'] = display_data[f'{price_metric}_{year1}'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A")
                display_data[f'{price_metric}_{year2}'] = display_data[f'{price_metric}_{year2}'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "N/A")
                display_data[f'change_{year1}_to_{year2}'] = display_data[f'change_{year1}_to_{year2}'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
                

                # Rename columns for display
                display_data.columns = [
                    'Neighborhood', 
                    f'{"Median" if price_metric == "median_price" else "Mean"} Price ({year1})', 
                    f'{"Median" if price_metric == "median_price" else "Mean"} Price ({year2})', 
                    f'Price Change ({year1}-{year2})'
                ]
                
                st.dataframe(display_data, use_container_width=True)
    
    # Data Table
    # Removed as requested

if __name__ == "__main__":
    show()