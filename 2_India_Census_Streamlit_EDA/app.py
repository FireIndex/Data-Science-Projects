import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from population import IND_POPULATION

class IndiaCensusDashboard:
    """India Census Dashboard to analyze demographic data of India"""
    def __init__(self):
        # use streamlit session state to initialize the object only once
        if 'india_population' not in st.session_state:
            st.session_state['india_population'] = IND_POPULATION()
        # Accessing the object from the session state
        self.india_population = st.session_state['india_population']

        # Set up the Streamlit sidebar and main layout
        st.set_page_config(page_title="India Census Dashboard", page_icon="🧊", layout='wide' )
        self.setup_sidebar()
        self.main_content()

    def new_line(self):
        """Insert a line break in the Streamlit app."""
        st.write("")
        # st.markdown("<hr style='border-top: 1px solid #333;'>", unsafe_allow_html=True)

    def setup_sidebar(self):
        """Configure the sidebar with options for user input."""
        st.sidebar.title("Indian Census")
        self.area_option = st.sidebar.selectbox("Select Area to explore", ["Home", "Population", "Poverty", "Literacy Rate"])
        
    def main_content(self):
        """Render the main content based on user selection."""
        render_functions = {
            "Home": self.render_home,
            "Population": self.render_population,
            "Poverty": self.render_poverty,
            "Literacy Rate": self.render_literacy_rate
        }
        render_function = render_functions[self.area_option]
        if render_function:
            render_function()
        else:
            st.error("Invalid selection. Please select a valid option from the sidebar.")

    def render_home(self):
        """Display the home page of the dashboard."""
        st.title("India Census Dashboard")
        st.markdown("Welcome to the India Census Dashboard! This dashboard provides insights into the demographic data of India, including population statistics, poverty rates, and literacy rates. Use the sidebar to navigate between different sections.")


    def render_population(self):
        """Display the population statistics in the dashboard."""
        st.title("Population Statistics")
        st.markdown("This section provides an overview of the population statistics in India. Dataset source - [A-02: Decadal variation in population 1901-2011](https://censusindia.gov.in/census.website/data/census-tables)")
        st.write('')
        self.new_line()

        # Display the population data
        st.subheader("Dataset 🌟")
        st.write("Data is already cleaned and optimized by the developer that is `FireIndex (Sundram)`.")
        population_data = self.india_population.get_population_data()
        st.write(population_data)
        self.new_line()

        # Perform EDA on the population data
        # st.subheader("Exploratory Data Analysis 📊")
        # st.write("Shape of the dataset", population_data.shape)
        # self.new_line()
        # col1, col2, col3 = st.columns([1, 1, 1])
        # with col1: st.write("Columns in the dataset", population_data.columns)
        # with col2: st.write("Data types of columns", population_data.dtypes)
        # with col3: st.write("Missing values in the dataset:", population_data.isnull().sum())
        # self.new_line()
        # st.write("Summary statistics:", population_data.describe())
        # self.new_line()


        # Display the population by state
        st.subheader("Population by State 🌏")
        state_population = population_data.groupby(['State Name', 'Census Year'])['Persons'].sum().reset_index().sort_values(by=['State Name', 'Census Year']).copy()
        # st.write(state_population)
        fig = px.bar(state_population, y='Persons', x='State Name', animation_frame="Census Year", animation_group="State Name", orientation='v', title=None, labels={'Persons': 'Population', 'State Name': 'State'})#, range_y=[0, state_population['Persons'].max()+1000000])
        st.plotly_chart(fig)

        # Male Felame Ratio state wise stacked bar chart periodicaly census year
        st.subheader("Gender Ratio by State 🚹🚺")
        new_df = population_data.copy()
        new_df = new_df.groupby(['State Name', 'Census Year'])[['Persons','Males','Females']].sum().reset_index().sort_values(by=['State Name', 'Census Year'])
        new_df['Males'] = new_df['Males']/new_df['Persons']
        new_df['Females'] = 1 - new_df['Males']
        new_df.drop(columns=['Persons'], inplace=True)
        # st.write(new_df)
        
        fig = px.bar(new_df, x='State Name', y=['Males', 'Females'], animation_frame="Census Year", animation_group="State Name", title=None,  labels={'value': 'Ratio', 'State Name': 'State'}, range_y=[0,1])
        st.plotly_chart(fig)

        

        

    def render_poverty(self):
        """Display the poverty rates in the dashboard."""
        st.title("Poverty Rates")
        st.markdown("This section provides an overview of the poverty rates in India.")
        # data not available
        st.error("Data not available for this section. 😵")
        

    def render_literacy_rate(self):
        """Display the literacy rates in the dashboard."""
        st.title("Literacy Rates")
        st.markdown("This section provides an overview of the literacy rates in India.")
        # data not available
        st.error("Data not available for this section. 😵")
        


if __name__ == '__main__':
    IndiaCensusDashboard()