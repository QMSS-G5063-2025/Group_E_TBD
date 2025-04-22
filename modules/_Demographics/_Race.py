import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats
import os
import glob

def load_race_demographics_data(min_year=2015):
    file_pattern = os.path.join('datasets', 'Combined_*.xlsx')
    excel_files = glob.glob(file_pattern)
    
    all_data = []
    
    # Race categories to extract
    race_categories = [
        "White",
        "Black or African American",
        "Asian"
    ]
    
    # Process each file
    for file_path in excel_files:
        filename = os.path.basename(file_path)
        if 'Combined_' in filename and '.xlsx' in filename:
            year = int(filename.replace('Combined_', '').replace('.xlsx', ''))
            if year < min_year:
                continue
        else:
            continue
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Find race data rows
        for race in race_categories:
            race_rows = df[df.iloc[:, 0].str.contains(race, na=False, case=False)]
            
            if race_rows.empty:
                continue
            
            race_row = race_rows.iloc[0]
            
            # Get total population row for percentage calculation
            total_pop_rows = df[df.iloc[:, 0].str.contains("Total population", na=False, case=False)]
            if total_pop_rows.empty:
                continue
            
            total_pop_row = total_pop_rows.iloc[0]
            
            # Extract neighborhoods and race data
            for col in range(1, len(df.columns)):
                if pd.notna(race_row.iloc[col]) and pd.notna(total_pop_row.iloc[col]):
                    col_name = df.columns[col]

                    if "NYC-Manhattan Community District" in col_name and "PUMA" in col_name:
                        neighborhood = col_name.split("--")[1].split(" PUMA")[0]
                    
                    # Further clean neighborhood name if it contains "Estimate"
                    if "Estimate" in neighborhood:
                        neighborhood = neighborhood.split("Estimate")[0].strip()
                    
                    # Extract data and calculate percentage
                    race_count = float(str(race_row.iloc[col]).replace(',', ''))
                    total_pop = float(str(total_pop_row.iloc[col]).replace(',', ''))
                    
                    # Calculate percentage (avoid division by zero)
                    if total_pop > 0:
                        percentage = (race_count / total_pop) * 100
                    else:
                        percentage = 0
                    
                    all_data.append({
                        "Year": year,
                        "Neighborhood": neighborhood,
                        "Race": race,
                        "Count": race_count,
                        "Total_Population": total_pop,
                        "Percentage": percentage
                    })
    
    # Create dataframe
    if all_data:
        result_df = pd.DataFrame(all_data)
        result_df = result_df.drop_duplicates(subset=['Year', 'Neighborhood', 'Race'])
        result_df = result_df.sort_values(by=['Neighborhood', 'Year', 'Race'])
        return result_df
    
    return pd.DataFrame(columns=["Year", "Neighborhood", "Race", "Count", "Total_Population", "Percentage"])

def load_sales_data(year):
    file_path = os.path.join('datasets', f'{year}_manhattan.xlsx')
    
    if not os.path.exists(file_path):
        return None
    
    sales_df = pd.read_excel(file_path)
    
    sales_df['sale_price'] = pd.to_numeric(sales_df['sale_price'], errors='coerce')
    sales_df = sales_df[sales_df['sale_price'] > 10000]
    
    return sales_df

def create_neighborhood_mapping():
    neighborhood_mapping = {
        'UPPER EAST SIDE (59-79)': 'Upper East Side',
        'UPPER EAST SIDE (79-96)': 'Upper East Side',
        'UPPER EAST SIDE (96-110)': 'Upper East Side',
        'UPPER WEST SIDE (59-79)': 'Upper West Side & West Side',
        'UPPER WEST SIDE (79-96)': 'Upper West Side & West Side', 
        'UPPER WEST SIDE (96-116)': 'Upper West Side & West Side',
        
        'MIDTOWN EAST': 'Murray Hill, Gramercy & Stuyvesant Town',
        'MIDTOWN WEST': 'Chelsea, Clinton & Midtown Business District',
        'MIDTOWN CBD': 'Chelsea, Clinton & Midtown Business District',
        'MURRAY HILL': 'Murray Hill, Gramercy & Stuyvesant Town',
        'GRAMERCY': 'Murray Hill, Gramercy & Stuyvesant Town',
        'CLINTON': 'Chelsea, Clinton & Midtown Business District',
        'FASHION': 'Chelsea, Clinton & Midtown Business District',
        
        'GREENWICH VILLAGE-CENTRAL': 'Battery Park City, Greenwich Village & Soho',
        'GREENWICH VILLAGE-WEST': 'Battery Park City, Greenwich Village & Soho',
        'SOHO': 'Battery Park City, Greenwich Village & Soho',
        'TRIBECA': 'Battery Park City, Greenwich Village & Soho',
        'FINANCIAL': 'Battery Park City, Greenwich Village & Soho',
        'ALPHABET CITY': 'Chinatown & Lower East Side',
        'EAST VILLAGE': 'Chinatown & Lower East Side',
        'LOWER EAST SIDE': 'Chinatown & Lower East Side',
        'CHINATOWN': 'Chinatown & Lower East Side',
        
        'HARLEM-CENTRAL': 'Central Harlem',
        'HARLEM-EAST': 'East Harlem',
        'HARLEM-UPPER': 'Hamilton Heights, Manhattanville & West Harlem',
        'HARLEM-WEST': 'Hamilton Heights, Manhattanville & West Harlem',
        'WASHINGTON HEIGHTS LOWER': 'Washington Heights, Inwood & Marble Hill',
        'WASHINGTON HEIGHTS UPPER': 'Washington Heights, Inwood & Marble Hill',
        'INWOOD': 'Washington Heights, Inwood & Marble Hill',
        
        'CHELSEA': 'Chelsea, Clinton & Midtown Business District',
        'MANHATTAN VALLEY': 'Upper West Side & West Side',
        'MORNINGSIDE HEIGHTS': 'Hamilton Heights, Manhattanville & West Harlem',
        'ROOSEVELT ISLAND': 'Upper East Side',
        'FLATIRON': 'Murray Hill, Gramercy & Stuyvesant Town',
        'SOUTHBRIDGE': 'Battery Park City, Greenwich Village & Soho',
        'CIVIC CENTER': 'Battery Park City, Greenwich Village & Soho',
        'LITTLE ITALY': 'Chinatown & Lower East Side',
        'JAVITS CENTER': 'Chelsea, Clinton & Midtown Business District',
        'KIPS BAY': 'Murray Hill, Gramercy & Stuyvesant Town'
    }
    
    # Add case-insensitive mapping
    return {k.upper(): v for k, v in neighborhood_mapping.items()}

def create_race_stacked_area_plot(df, selected_neighborhood):
    """Create a stacked area plot for race distribution over time for a single neighborhood"""
    # Filter data for selected neighborhood
    neighborhood_df = df[df['Neighborhood'] == selected_neighborhood].copy()
    
    # Pivot data to create a dataframe with years as index, races as columns, and percentages as values
    pivot_df = neighborhood_df.pivot_table(
        values='Percentage', 
        index='Year', 
        columns='Race', 
        aggfunc='first'
    ).reset_index()
    
    # Create stacked area plot
    fig = go.Figure()
    
    # Add traces for each race category
    for race in df['Race'].unique():
        if race in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df['Year'], 
                y=pivot_df[race],
                mode='lines',
                stackgroup='one',  # Enable stacking
                name=race,
                hovertemplate=
                f'{race}: %{{y:.1f}}%<br>' +
                'Year: %{x}<extra></extra>'
            ))
    
    # Update layout
    fig.update_layout(
        title=f'Racial Composition in {selected_neighborhood} (2015-2023)',
        xaxis=dict(
            title='Year',
            tickmode='array',
            tickvals=sorted(df['Year'].unique()),
            gridcolor='rgba(230, 230, 230, 0.8)'
        ),
        yaxis=dict(
            title='Percentage (%)',
            gridcolor='rgba(230, 230, 230, 0.8)',
            range=[0, 100]
        ),
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        height=600
    )
    
    return fig

def create_race_comparison_plot(df, selected_year, selected_neighborhoods=None):
    if selected_neighborhoods is None or len(selected_neighborhoods) == 0:
        selected_neighborhoods = []
    
    # Filter data for selected year
    year_df = df[df['Year'] == selected_year].copy()
    
    # Filter for selected neighborhoods
    if selected_neighborhoods:
        year_df = year_df[year_df['Neighborhood'].isin(selected_neighborhoods)]
    
    # Pivot the data for easier plotting
    pivot_df = year_df.pivot_table(
        values='Percentage',
        index='Neighborhood',
        columns='Race',
        aggfunc='first'
    ).reset_index()
    
    # Sort neighborhoods by White percentage (or any other race you prefer)
    pivot_df = pivot_df.sort_values(by=['White'], ascending=False)
    
    # Create the bar chart
    fig = go.Figure()
    
    for race in df['Race'].unique():
        if race in pivot_df.columns:
            fig.add_trace(go.Bar(
                x=pivot_df['Neighborhood'],
                y=pivot_df[race],
                name=race,
                hovertemplate=
                '<b>%{x}</b><br>' +
                f'{race}: %{{y:.1f}}%<extra></extra>'
            ))
    
    # Update layout
    fig.update_layout(
        title=f'Racial Composition by Neighborhood ({selected_year})',
        xaxis=dict(
            title='Neighborhood',
            tickangle=45,
            gridcolor='rgba(230, 230, 230, 0.8)'
        ),
        yaxis=dict(
            title='Percentage (%)',
            gridcolor='rgba(230, 230, 230, 0.8)',
            range=[0, 100]
        ),
        barmode='group',
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=40, r=40, t=80, b=120),
        height=700
    )
    
    return fig

def analyze_white_percentage_price_relationship(year, race_df, sales_df):
    # Filter data for white race and the selected year
    white_df = race_df[(race_df['Race'] == 'White') & (race_df['Year'] == year)]

    # Aggregate sales data by neighborhood
    neighborhood_prices = sales_df.groupby('neighborhood').agg({
        'sale_price': ['mean', 'median', 'count']
    }).reset_index()
    
    neighborhood_prices.columns = ['neighborhood', 'mean_price', 'median_price', 'sale_count']
    
    # Get neighborhood mapping
    neighborhood_mapping = create_neighborhood_mapping()
    
    # Map sales data neighborhoods to demographic data neighborhoods
    neighborhood_prices['mapped_neighborhood'] = neighborhood_prices['neighborhood'].apply(
        lambda x: neighborhood_mapping.get(x.upper(), "Unknown")
    )
    
    # Merge datasets on neighborhood
    merged_df = pd.merge(
        white_df,
        neighborhood_prices,
        left_on='Neighborhood',
        right_on='mapped_neighborhood',
        how='inner'
    )
    
    # Check if we have enough data for analysis
    if len(merged_df) < 2:
        st.warning("Not enough data for statistical analysis.")
        return
    
    # Create scatter plot
    fig = px.scatter(
        merged_df,
        x='Percentage',
        y='median_price',
        size='sale_count',
        color='neighborhood',
        hover_name='neighborhood',
        hover_data={
            'Percentage': ':.1f',
            'median_price': ':.2f',
            'sale_count': True,
            'mapped_neighborhood': False
        },
        labels={
            'Percentage': 'White Population (%)',
            'median_price': 'Median Sale Price ($)',
            'sale_count': 'Number of Sales'
        },
        title=f'White Population Percentage vs. Median Sale Price ({year})'
    )
    
    # Linear regression
    x = merged_df['Percentage']
    y = merged_df['median_price']

    try:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    except Exception as e:
        st.error(f"Error in statistical analysis: {e}")
        return
    
    # Create regression line
    x_range = np.linspace(min(x), max(x), 100)
    y_range = slope * x_range + intercept
    
    # Add regression line to plot
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_range,
            mode='lines',
            name=f'Best Fit Line (r={r_value:.2f})',
            line=dict(color='red', dash='dash')
        )
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        yaxis=dict(tickformat='$,.0f'),
        xaxis=dict(title='White Population Percentage (%)')
    )
    
    # Display plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Show correlation statistics
    st.subheader("Correlation Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Slope", f"{slope:.3f}")
    with col2:
        st.metric("Correlation", f"{r_value:.3f}")
    with col3:
        st.metric("Standard Error", f"{std_err:.3f}")
    
    direction = "positive" if slope > 0 else "negative"
    
    st.write(f"There is a {direction} correlation ({r_value:.3f}) between neighborhood white population percentage and property prices, with {std_err:.3f} standard error.")

def show_race_demographics_analysis():
    st.header("Race Demographics Analysis")
    
    with st.spinner("Loading demographic data..."):
        race_df = load_race_demographics_data(min_year=2015)
    
    race_df_recent = race_df[race_df['Year'] >= 2021]
    
    if not race_df.empty:
        analysis_tabs = st.tabs(["Race Trends Over Time", "Neighborhood Racial Composition", "White Percentage vs. Property Prices"])
        
        with analysis_tabs[0]:
            st.subheader("Data Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Neighborhoods", f"{len(race_df['Neighborhood'].unique())}")
            with col2:
                st.metric("Years", f"{race_df['Year'].min()} - {race_df['Year'].max()}")
            with col3:
                st.metric("Race Categories", f"{len(race_df['Race'].unique())}")
            
            # Neighborhood selection for stacked area chart
            st.subheader("Select a Neighborhood for Racial Composition Trend")
            all_neighborhoods = sorted(race_df['Neighborhood'].unique())
            selected_neighborhood = st.selectbox(
                "Neighborhood",
                options=all_neighborhoods,
                index=0
            )
            
            # Display stacked area chart
            st.subheader(f"Racial Composition Trends in {selected_neighborhood}")
            fig = create_race_stacked_area_plot(race_df, selected_neighborhood)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics for the selected neighborhood
            st.subheader("Detailed Statistics")
            
            # Filter data for selected neighborhood
            neighborhood_data = race_df[race_df['Neighborhood'] == selected_neighborhood]
            
            # Get range of years
            years = sorted(neighborhood_data['Year'].unique())
            min_year = min(years)
            max_year = max(years)
            
            changes = []
            
            for race in sorted(race_df['Race'].unique()):
                race_data = neighborhood_data[neighborhood_data['Race'] == race]
                
                if min_year in race_data['Year'].values and max_year in race_data['Year'].values:
                    start_pct = race_data[race_data['Year'] == min_year]['Percentage'].values[0]
                    end_pct = race_data[race_data['Year'] == max_year]['Percentage'].values[0]
                    
                    change = end_pct - start_pct
                    # For percentage point change
                    percent_point_change = change
                    
                    changes.append({
                        'Race': race,
                        'Start_Percentage': start_pct,
                        'End_Percentage': end_pct,
                        'Change': change,
                        'Percent_Point_Change': percent_point_change
                    })
            
            if changes:
                changes_df = pd.DataFrame(changes)
                changes_df = changes_df.sort_values('End_Percentage', ascending=False)
                
                # Format data for display
                display_df = changes_df.copy()
                display_df['Start_Percentage'] = display_df['Start_Percentage'].map('{:.1f}%'.format)
                display_df['End_Percentage'] = display_df['End_Percentage'].map('{:.1f}%'.format)
                display_df['Change'] = display_df['Change'].map('{:+.1f}%'.format)
                display_df['Percent_Point_Change'] = display_df['Percent_Point_Change'].map('{:+.1f} pts'.format)
                
                # Rename columns
                display_df.columns = [
                    'Race/Ethnicity', 
                    f'Percentage ({min_year})', 
                    f'Percentage ({max_year})', 
                    'Change', 
                    'Change (% points)'
                ]
                
                # Display table
                st.dataframe(display_df, use_container_width=True)
        
        with analysis_tabs[1]:
            st.subheader("Compare Racial Composition by Neighborhood")
            
            # Year selection
            available_years = sorted(race_df['Year'].unique())
            selected_year = st.selectbox(
                "Select Year",
                options=available_years,
                index=len(available_years)-1,
                key="composition_year_selectbox"
            )
            
            st.subheader("Neighborhood Selection")
            
            all_neighborhoods = sorted(race_df['Neighborhood'].unique())
            
            col1, col2, col3 = st.columns(3)
            
            neighborhoods_per_column = len(all_neighborhoods) // 3 + (1 if len(all_neighborhoods) % 3 > 0 else 0)
            
            selected_neighborhoods = []
            
            with col1:
                for neighborhood in all_neighborhoods[:neighborhoods_per_column]:
                    if st.checkbox(neighborhood, key=f"comp_{neighborhood}"):
                        selected_neighborhoods.append(neighborhood)
            
            with col2:
                for neighborhood in all_neighborhoods[neighborhoods_per_column:2*neighborhoods_per_column]:
                    if st.checkbox(neighborhood, key=f"comp_{neighborhood}"):
                        selected_neighborhoods.append(neighborhood)
            
            with col3:
                for neighborhood in all_neighborhoods[2*neighborhoods_per_column:]:
                    if st.checkbox(neighborhood, key=f"comp_{neighborhood}"):
                        selected_neighborhoods.append(neighborhood)
            
            # Display chart
            if selected_neighborhoods:
                fig = create_race_comparison_plot(race_df, selected_year, selected_neighborhoods)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please select at least one neighborhood to display the chart")
        
        # New tab for White Percentage vs. Property Prices
        with analysis_tabs[2]:
            st.subheader("White Population Percentage vs. Property Prices")
            
            # Year selection for analysis
            available_years = sorted(race_df_recent['Year'].unique())
            selected_year = st.selectbox(
                "Select Year for Analysis",
                options=available_years,
                index=len(available_years)-1,
                key="white_price_year_selectbox"
            )
            
            # Load sales data for the selected year
            with st.spinner(f"Loading {selected_year} sales data..."):
                sales_df = load_sales_data(selected_year)
            
            # Analyze relationship between white percentage and property prices
            if sales_df is not None:
                analyze_white_percentage_price_relationship(selected_year, race_df_recent, sales_df)
            else:
                st.warning(f"No sales data found for {selected_year}")

def show_race_analysis():
    show_race_demographics_analysis()

if __name__ == "__main__":
    show_race_analysis()