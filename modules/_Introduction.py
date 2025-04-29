import streamlit as st

def show():
    # Custom CSS for styling
    st.markdown("""
    <style>
    .title-container {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .intro-text {
        font-size: 1.5em;
        line-height: 1.6;
    }
    /* Ensure image and text are aligned */
    .stImage {
        margin-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main content layout with adjusted column sizes
    col1, col2 = st.columns([3, 1.5])

    with col1:
        # Title
        st.markdown("# The Price of Place: Manhattan Real Estate Trends and Insights")
        
        # Introduction text
        st.markdown("""
        <div class="intro-text">
        <p>Welcome to the <em>Price of Place: Manhattan Real Estate Trends and Insights</em> page! Our webpage presents a comprehensive analysis of rolling property sales in Manhattan, New York City. Motivated by the sharp fluctuations in real estate prices, we sought to better understand how property values evolve across time and space, and what underlying factors might influence these changes.</p>

        <p>By examining neighborhood-level sales data alongside demographic profiles and proximity to healthcare resources, we present patterns and correlations that potentially shape the real estate market to provide insights on how social infrastructure and community characteristics intersect with property valuation.</p>

        <p>This analysis can support decision-making for urban planners, potential homebuyers, and anyone interested in the socioeconomic fabric of New York City, for specifically, Manhattan. To make our findings accessible, we used a variety of visualization tools including geospatial maps, data tables, histograms, line charts, scatter plots, treemaps to illustrate trends in pricing, shifts over time, and neighborhood-level disparities. </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Image display
        st.image("img/New-York2.jpg")
        st.image("img/New-York3.png")
