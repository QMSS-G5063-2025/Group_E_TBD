import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats
import os
import glob

def load_median_age_data(min_year=2015):

    file_pattern = os.path.join('datasets', 'Combined_*.xlsx')
    excel_files = glob.glob(file_pattern)
    
    all_data = []
    
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
        
        median_age_rows = df[df.iloc[:, 0].str.contains("Median age", na=False, case=False)]
        
        if median_age_rows.empty:
            continue
        
        median_age_row = median_age_rows.iloc[0]
        
        # Extract neighborhoods and median age data
        for col in range(1, len(df.columns)):
            if pd.notna(median_age_row.iloc[col]):
                col_name = df.columns[col]

                if "NYC-Manhattan Community District" in col_name and "PUMA" in col_name:
                    neighborhood = col_name.split("--")[1].split(" PUMA")[0]
                
                # Further clean neighborhood name if it contains "Estimate"
                if "Estimate" in neighborhood:
                    neighborhood = neighborhood.split("Estimate")[0].strip()
                

                median_age = float(median_age_row.iloc[col])
                all_data.append({
                    "Year": year,
                    "Neighborhood": neighborhood,
                    "Median_Age": median_age
                })
    
    # Dataframe
    if all_data:
        result_df = pd.DataFrame(all_data)
        result_df = result_df.drop_duplicates(subset=['Year', 'Neighborhood'])
        result_df = result_df.sort_values(by=['Neighborhood', 'Year'])
        return result_df
    
    return pd.DataFrame(columns=["Year", "Neighborhood", "Median_Age"])

def load_sales_data(year):
    file_path = os.path.join('datasets', f'{year}_manhattan.xlsx')
    
    if not os.path.exists(file_path):
        return None
    
    sales_df = pd.read_excel(file_path)
    
    sales_df['sale_price'] = pd.to_numeric(sales_df['sale_price'], errors='coerce')
    sales_df = sales_df[sales_df['sale_price'] > 10000]
    
    return sales_df

# Match the neighborhood
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

def create_median_age_plot(df, selected_neighborhoods=None):
    all_neighborhoods = sorted(df['Neighborhood'].unique())
    
    if selected_neighborhoods is None or len(selected_neighborhoods) == 0:
        selected_neighborhoods = []
    
    # Plot trace plot
    fig = go.Figure()
    
    for neighborhood in all_neighborhoods:
        neighborhood_data = df[df['Neighborhood'] == neighborhood]
        
        if neighborhood in selected_neighborhoods:
            line_color = None  # Use plotly default color
            line_width = 3
            opacity = 1.0
        else:
            line_color = 'rgba(200, 200, 200, 0.5)'  # Gray
            line_width = 1.5
            opacity = 0.7
        
        fig.add_trace(go.Scatter(
            x=neighborhood_data['Year'],
            y=neighborhood_data['Median_Age'],
            mode='lines+markers',
            name=neighborhood,
            line=dict(color=line_color, width=line_width),
            opacity=opacity,
            hovertemplate=
            '<b>%{fullData.name}</b><br>' +
            'Year: %{x}<br>' +
            'Median Age: %{y:.1f} years<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title='Manhattan Neighborhoods Median Age Trends (2015-2023)',
        xaxis=dict(
            title='Year',
            tickmode='array',
            tickvals=sorted(df['Year'].unique()),
            gridcolor='rgba(230, 230, 230, 0.8)'
        ),
        yaxis=dict(
            title='Median Age (years)',
            gridcolor='rgba(230, 230, 230, 0.8)'
        ),
        hovermode='closest',
        legend=dict(
            orientation='v',
            yanchor='top',
            y=0.99,
            xanchor='right',
            x=0.99,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        height=600
    )
    
    return fig

def analyze_age_price_relationship(year, age_df, sales_df):
    year_age_df = age_df[age_df['Year'] == year]

    neighborhood_prices = sales_df.groupby('neighborhood').agg({
        'sale_price': ['mean', 'median', 'count']
    }).reset_index()
    
    neighborhood_prices.columns = ['neighborhood', 'mean_price', 'median_price', 'sale_count']
    
    neighborhood_mapping = create_neighborhood_mapping()
    
    neighborhood_prices['mapped_neighborhood'] = neighborhood_prices['neighborhood'].apply(
        lambda x: neighborhood_mapping.get(x.upper(), "Unknown")
    )
    
    # Merge
    merged_df = pd.merge(
        year_age_df,
        neighborhood_prices,
        left_on='Neighborhood',
        right_on='mapped_neighborhood',
        how='inner'
    )
    
    # Scatter plot
    fig = px.scatter(
        merged_df,
        x='Median_Age',
        y='median_price',
        size='sale_count',
        color='neighborhood',
        hover_name='neighborhood',
        hover_data={
            'Median_Age': True,
            'median_price': ':.2f',
            'sale_count': True,
            'mapped_neighborhood': False
        },
        labels={
            'Median_Age': 'Median Age (years)',
            'median_price': 'Median Sale Price ($)',
            'sale_count': 'Number of Sales'
        },
        title=f'Median Age vs. Median Sale Price ({year})'
    )
    
    # Regression line
    x = merged_df['Median_Age']
    y = merged_df['median_price']
    
    # Regression,R,P
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Range and line
    x_range = np.linspace(min(x), max(x), 100)
    y_range = slope * x_range + intercept
    
    # Add line to plot
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_range,
            mode='lines',
            name=f'Best Fit Line (r={r_value:.2f})',
            line=dict(color='red', dash='dash')
        )
    )
    
    # Dollars
    fig.update_layout(
        height=600,
        yaxis=dict(
            tickformat='$,.0f'
        )
    )
    
    # Display
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation statistics
    st.subheader("Correlation Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Slope", f"{slope:.3f}")
    with col2:
        st.metric("Correlation", f"{r_value:.3f}")
    with col3:
        st.metric("Standard Error", f"{std_err:.3f}")
    
    direction = "positive" if slope > 0 else "negative"
    
    st.write(f"There is a {direction} correlation ({r_value:.3f}) between neighborhood median age and property prices, with {std_err:.3f} standard error.")

def show_median_age_analysis():
    st.header("Median Age Analysis")
    
    with st.spinner("Loading demographic data..."):
        age_df_all = load_median_age_data(min_year=2015)
    
    age_df_recent = age_df_all[age_df_all['Year'] >= 2021]

    if not age_df_all.empty:
        analysis_tabs = st.tabs(["Trends by Neighborhood", "Age vs. Property Prices"])
        
        with analysis_tabs[0]:
            st.subheader("Data Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Neighborhoods", f"{len(age_df_all['Neighborhood'].unique())}")
            with col2:
                st.metric("Years", f"{age_df_all['Year'].min()} - {age_df_all['Year'].max()}")
            with col3:
                st.metric("Average Median Age", f"{age_df_all['Median_Age'].mean():.1f} years")
            
            st.subheader("Neighborhood Selection")
            
            all_neighborhoods = sorted(age_df_all['Neighborhood'].unique())
            
            col1, col2, col3 = st.columns(3)
            
            neighborhoods_per_column = len(all_neighborhoods) // 3 + (1 if len(all_neighborhoods) % 3 > 0 else 0)
            
            selected_neighborhoods = []
            
            with col1:
                for neighborhood in all_neighborhoods[:neighborhoods_per_column]:
                    if st.checkbox(neighborhood, key=f"nb_{neighborhood}"):
                        selected_neighborhoods.append(neighborhood)
            
            with col2:
                for neighborhood in all_neighborhoods[neighborhoods_per_column:2*neighborhoods_per_column]:
                    if st.checkbox(neighborhood, key=f"nb_{neighborhood}"):
                        selected_neighborhoods.append(neighborhood)
            
            with col3:
                for neighborhood in all_neighborhoods[2*neighborhoods_per_column:]:
                    if st.checkbox(neighborhood, key=f"nb_{neighborhood}"):
                        selected_neighborhoods.append(neighborhood)
            
            # Display chart
            st.subheader("Median Age Trends")
            fig = create_median_age_plot(age_df_all, selected_neighborhoods)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            if selected_neighborhoods:
                st.subheader("Comparative Statistics")
                
                # Filter
                selected_df = age_df_all[age_df_all['Neighborhood'].isin(selected_neighborhoods)]
                
                # Range
                years = sorted(selected_df['Year'].unique())
                min_year = min(years)
                max_year = max(years)
                
                changes = []
                
                for neighborhood in selected_neighborhoods:
                    neighborhood_data = selected_df[selected_df['Neighborhood'] == neighborhood]
                    
                    if min_year in neighborhood_data['Year'].values and max_year in neighborhood_data['Year'].values:
                        start_age = neighborhood_data[neighborhood_data['Year'] == min_year]['Median_Age'].values[0]
                        end_age = neighborhood_data[neighborhood_data['Year'] == max_year]['Median_Age'].values[0]
                        
                        change = end_age - start_age
                        percent_change = (change / start_age) * 100
                        
                        changes.append({
                            'Neighborhood': neighborhood,
                            'Start_Age': start_age,
                            'End_Age': end_age,
                            'Change': change,
                            'Percent_Change': percent_change
                        })
                
                if changes:
                    changes_df = pd.DataFrame(changes)
                    changes_df = changes_df.sort_values('Change', ascending=False)
                    
                    # Data table
                    st.subheader("Detailed Statistics")
                    
                    # Format data for display
                    display_df = changes_df.copy()
                    display_df['Start_Age'] = display_df['Start_Age'].map('{:.1f}'.format)
                    display_df['End_Age'] = display_df['End_Age'].map('{:.1f}'.format)
                    display_df['Change'] = display_df['Change'].map('{:+.1f}'.format)
                    display_df['Percent_Change'] = display_df['Percent_Change'].map('{:+.1f}%'.format)
                    
                    # Rename columns
                    display_df.columns = [
                        'Neighborhood', 
                        f'Median Age ({min_year})', 
                        f'Median Age ({max_year})', 
                        'Change', 
                        'Change %'
                    ]
                    
                    # Display table
                    st.dataframe(display_df, use_container_width=True)
                    
        
        with analysis_tabs[1]:
            available_years = sorted(age_df_recent['Year'].unique())
            selected_year = st.selectbox(
                "Select Year for Analysis",
                options=available_years,
                index=len(available_years)-1
            )

            with st.spinner(f"Loading {selected_year} sales data..."):
                sales_df = load_sales_data(selected_year)

            # Analyze relationship between age and price
            analyze_age_price_relationship(selected_year, age_df_recent, sales_df)

if __name__ == "__main__":
    show()