import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats
import os
import glob

def load_median_income_data(min_year=2015):
    file_pattern = os.path.join('datasets', 'Combined_*.xlsx')
    excel_files = glob.glob(file_pattern)
    
    all_data = []
    
    for file_path in excel_files:
        filename = os.path.basename(file_path)
        if 'Combined_' in filename and '.xlsx' in filename:
            year = int(filename.replace('Combined_', '').replace('.xlsx', ''))
            if year < min_year:
                continue
        else:
            continue
        
        df = pd.read_excel(file_path)
        
        median_income_rows = df[df.iloc[:, 0].str.contains("Median household income", na=False, case=False)]
        
        if median_income_rows.empty:
            continue
        
        median_income_row = median_income_rows.iloc[0]
        
        # Extract neighborhoods and median income data
        for col in range(1, len(df.columns)):
            if pd.notna(median_income_row.iloc[col]):
                col_name = df.columns[col]

                if "NYC-Manhattan Community District" in col_name and "PUMA" in col_name:
                    neighborhood = col_name.split("--")[1].split(" PUMA")[0]
                
                # Further clean neighborhood name if it contains "Estimate"
                if "Estimate" in neighborhood:
                    neighborhood = neighborhood.split("Estimate")[0].strip()

                median_income_str = str(median_income_row.iloc[col]).replace(',', '')
                median_income = float(median_income_str)

                all_data.append({
                    "Year": year,
                    "Neighborhood": neighborhood,
                    "Median_Income": median_income
                })
    
    # Dataframe
    if all_data:
        result_df = pd.DataFrame(all_data)
        result_df = result_df.drop_duplicates(subset=['Year', 'Neighborhood'])
        result_df = result_df.sort_values(by=['Neighborhood', 'Year'])
        return result_df
    
    return pd.DataFrame(columns=["Year", "Neighborhood", "Median_Income"])

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

def create_median_income_plot(df, selected_neighborhoods=None):
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
            y=neighborhood_data['Median_Income'],
            mode='lines+markers',
            name=neighborhood,
            line=dict(color=line_color, width=line_width),
            opacity=opacity,
            hovertemplate=
            '<b>%{fullData.name}</b><br>' +
            'Year: %{x}<br>' +
            'Median Income: $%{y:,.0f}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title='Manhattan Neighborhoods Median Income Trends (2015-2023)',
        xaxis=dict(
            title='Year',
            tickmode='array',
            tickvals=sorted(df['Year'].unique()),
            gridcolor='rgba(230, 230, 230, 0.8)'
        ),
        yaxis=dict(
            title='Median Income ($)',
            gridcolor='rgba(230, 230, 230, 0.8)',
            tickformat='$,.0f'
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

def analyze_income_price_relationship(year, income_df, sales_df):
    year_income_df = income_df[income_df['Year'] == year]

    neighborhood_prices = sales_df.groupby('neighborhood').agg({
        'sale_price': ['mean', 'median', 'count']
    }).reset_index()
    
    neighborhood_prices.columns = ['neighborhood', 'mean_price', 'median_price', 'sale_count']
    
    neighborhood_mapping = create_neighborhood_mapping()
    
    neighborhood_prices['mapped_neighborhood'] = neighborhood_prices['neighborhood'].apply(
        lambda x: neighborhood_mapping.get(x.upper(), "Unknown")
    )
    
    merged_df = pd.merge(
        year_income_df,
        neighborhood_prices,
        left_on='Neighborhood',
        right_on='mapped_neighborhood',
        how='inner'
    )
    
    if len(merged_df) < 2:
        st.warning("Not enough data for statistical analysis.")
        return
    
    fig = px.scatter(
        merged_df,
        x='Median_Income',
        y='median_price',
        size='sale_count',
        color='neighborhood',
        hover_name='neighborhood',
        hover_data={
            'Median_Income': ':.0f',
            'median_price': ':.2f',
            'sale_count': True,
            'mapped_neighborhood': False
        },
        labels={
            'Median_Income': 'Median Income ($)',
            'median_price': 'Median Sale Price ($)',
            'sale_count': 'Number of Sales'
        },
        title=f'Median Income vs. Median Sale Price ({year})'
    )
    
    x = merged_df['Median_Income']
    y = merged_df['median_price']

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    
    x_range = np.linspace(min(x), max(x), 100)
    y_range = slope * x_range + intercept
    
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_range,
            mode='lines',
            name=f'Best Fit Line (r={r_value:.2f})',
            line=dict(color='red', dash='dash')
        )
    )
    
    fig.update_layout(
        height=600,
        yaxis=dict(tickformat='$,.0f'),
        xaxis=dict(tickformat='$,.0f')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Correlation Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Slope", f"{slope:.3f}")
    with col2:
        st.metric("Correlation", f"{r_value:.3f}")
    with col3:
        st.metric("Standard Error", f"{std_err:.3f}")
    
    direction = "positive" if slope > 0 else "negative"
    
    st.write(f"There is a {direction} correlation ({r_value:.3f}) between neighborhood median household income and property prices, with {std_err:.3f} standard error.")

    st.markdown("""
    <p style="font-size: 20px;">
    Overall, the slight positive correlation between median incomes and median real estate sales prices suggest that neighborhoods with higher median incomes tend to have somewhat higher median sale prices.
    """, unsafe_allow_html=True)

def show_income_analysis():
    st.header("Median Household Income Analysis")
    
    with st.spinner("Loading income data..."):
        income_df_all = load_median_income_data(min_year=2015)
    
    income_df_recent = income_df_all[income_df_all['Year'] >= 2021]
    
    if not income_df_all.empty:
        analysis_tabs = st.tabs(["Trends by Neighborhood", "Income vs. Property Prices"])
        
        with analysis_tabs[0]:
            st.subheader("Data Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Neighborhoods", f"{len(income_df_all['Neighborhood'].unique())}")
            with col2:
                st.metric("Years", f"{income_df_all['Year'].min()} - {income_df_all['Year'].max()}")
            with col3:
                st.metric("Average Median Income", f"${income_df_all['Median_Income'].mean():,.0f}")
            
            st.subheader("Neighborhood Selection")
            
            all_neighborhoods = sorted(income_df_all['Neighborhood'].unique())
            
            col1, col2, col3 = st.columns(3)
            
            neighborhoods_per_column = len(all_neighborhoods) // 3 + (1 if len(all_neighborhoods) % 3 > 0 else 0)
            
            selected_neighborhoods = []
            
            with col1:
                for neighborhood in all_neighborhoods[:neighborhoods_per_column]:
                    if st.checkbox(neighborhood):
                        selected_neighborhoods.append(neighborhood)
            
            with col2:
                for neighborhood in all_neighborhoods[neighborhoods_per_column:2*neighborhoods_per_column]:
                    if st.checkbox(neighborhood):
                        selected_neighborhoods.append(neighborhood)
            
            with col3:
                for neighborhood in all_neighborhoods[2*neighborhoods_per_column:]:
                    if st.checkbox(neighborhood):
                        selected_neighborhoods.append(neighborhood)
            
            # Display chart
            st.subheader("Median Income Trends")
            st.markdown("""
            <p style="font-size: 20px;">
            The median income trends across Manhattan neighborhoods showed a clear divide between higher-income and lower-income neighborhoods. Neighborhoods like Battery Park City, Greenwich Village, SoHo, the Upper East Side, and the Upper West Side consistently maintained much higher median incomes, generally staying well above $100,000.
            </p>
            """, unsafe_allow_html=True)

            fig = create_median_income_plot(income_df_all, selected_neighborhoods)

            st.markdown("""
            <p style="font-size: 20px;">
            In contrast, neighborhoods such as Central Harlem, East Harlem, Hamilton Heights, Chinatown, and Washington Heights showed much lower median incomes, often hovering around $50,000 to $70,000 over the same period. It is noteworthy that we have previously identified the real estate price growth between 2018 and 2023, and there is only a gradual upward movement in their income levels. This might be because of the difference between district boundary definitions used in the real estate and demographics data so that they did not directly correspond to each other. It could also be because rising incomes, even if still modest compared to the citywide average, may have supported greater demand for housing since areas like SoHo, Tribeca, and Midtown remained out of reach for many buyers, making areas like Washington Heights and Hamilton Heights attractive alternatives.
            </p>
            """, unsafe_allow_html=True)

            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            if selected_neighborhoods:
                st.subheader("Comparative Statistics")
                
                # Filter
                selected_df = income_df_all[income_df_all['Neighborhood'].isin(selected_neighborhoods)]
                
                # Range
                years = sorted(selected_df['Year'].unique())
                min_year = min(years)
                max_year = max(years)
                
                changes = []
                
                for neighborhood in selected_neighborhoods:
                    neighborhood_data = selected_df[selected_df['Neighborhood'] == neighborhood]

                    if min_year in neighborhood_data['Year'].values and max_year in neighborhood_data['Year'].values:
                        start_income = neighborhood_data[neighborhood_data['Year'] == min_year]['Median_Income'].values[0]
                        end_income = neighborhood_data[neighborhood_data['Year'] == max_year]['Median_Income'].values[0]
                        
                        change = end_income - start_income
                        percent_change = (change / start_income) * 100
                        
                        changes.append({
                            'Neighborhood': neighborhood,
                            'Start_Income': start_income,
                            'End_Income': end_income,
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
                    display_df['Start_Income'] = display_df['Start_Income'].map('${:,.0f}'.format)
                    display_df['End_Income'] = display_df['End_Income'].map('${:,.0f}'.format)
                    display_df['Change'] = display_df['Change'].map('${:+,.0f}'.format)
                    display_df['Percent_Change'] = display_df['Percent_Change'].map('{:+.1f}%'.format)
                    
                    # Rename columns
                    display_df.columns = [
                        'Neighborhood', 
                        f'Median Income ({min_year})', 
                        f'Median Income ({max_year})', 
                        'Change', 
                        'Change %'
                    ]
                    
                    # Display table
                    st.dataframe(display_df, use_container_width=True)
        
        with analysis_tabs[1]:
            available_years = sorted(income_df_recent['Year'].unique())
            selected_year = st.selectbox(
                "Select Year for Analysis",
                options=available_years,
                index=len(available_years)-1,
                key="income_year_selectbox"
            )

            with st.spinner(f"Loading {selected_year} sales data..."):
                sales_df = load_sales_data(selected_year)

            if sales_df is not None:
                analyze_income_price_relationship(selected_year, income_df_recent, sales_df)
            else:
                st.warning(f"No sales data found for {selected_year}")

if __name__ == "__main__":
    show_income_analysis()