import math
import random
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from ipl import IPL
from typing import List, Dict

class IPLDashboard:
    """IPL Insights Dashboard to analyze IPL data."""
    
    def __init__(self):
        # Use Streamlit session state to initialize IPL object once and reuse it across reruns
        if 'ipl' not in st.session_state:
            ipl_matches = "data/IPL_Matches_2008_2022.csv"
            ipl_balls = "data/IPL_Ball_by_Ball_2008_2022.csv"
            st.session_state['ipl'] = IPL(ipl_matches, ipl_balls)

        # Access the IPL object from the session state
        self.ipl = st.session_state['ipl']
                
        # Set up the Streamlit sidebar and main layout
        st.set_page_config(page_title="IPL Insights Explorer", initial_sidebar_state="collapsed", layout="wide")
        self.setup_sidebar()
        self.main_content()

    def new_line(self):
        """Insert a line break in the Streamlit app."""
        st.write("")
        # st.markdown('<br>', unsafe_allow_html=True)

    def setup_sidebar(self):
        """Configure the sidebar with options for user input."""
        st.sidebar.title('IPL Insights Explorer')
        self.area_option = st.sidebar.selectbox(
            'Select Area:', ['Home', 'Team', 'Batting', 'Bowling', 'Player vs Player']
        )
        self.selected_season = st.sidebar.multiselect('Select Season:', self.ipl.allSeasons_API()['seasons'], default=['All'])

        # Setup input options based on area selected
        if self.area_option == 'Team':
            self.selected_team = st.sidebar.selectbox('Select Team:', self.ipl.allTeams_API()['teams'])
        elif self.area_option in ['Batting', 'Bowling']:
            self.selected_player = st.sidebar.selectbox('Select Player:', self.ipl.allPlayers_API()['players'])
        elif self.area_option == 'Player vs Player':
            self.selected_player1 = st.sidebar.selectbox('Select Player 1:', self.ipl.allPlayers_API()['players'])
            self.selected_player2 = st.sidebar.selectbox('Select Player 2:', self.ipl.allPlayers_API()['players'])
        else:
            pass # No additional options needed for the Home section
        
    def main_content(self):
        """Render the main content based on user selection."""
        # Call appropriate render functions based on area selected
        render_functions = {
            'Home': self.render_home,
            'Team': self.render_team_insights,
            'Batting': self.render_batting_insights,
            'Bowling': self.render_bowling_insights,
            'Player vs Player': self.render_player_vs_player_insights
        }
        render_function = render_functions.get(self.area_option)
        if render_function:
            render_function()
        else:
            st.error('Invalid selection. Please select a valid option from the sidebar.')              


    def render_home(self):
        """Render the home section of the IPL Insights Dashboard with explanations, headings, and styling."""
        st.title('🏏 IPL Insights Dashboard')
        st.markdown("""
        Welcome to the IPL Insights Dashboard! This interactive platform provides valuable insights into the Indian Premier League (IPL) cricket matches from 2008 to 2022.

        Here, you can explore team performances, batting and bowling statistics, player comparisons, and more! Utilize the options in the sidebar to navigate through different sections and discover a wealth of information about your favorite IPL teams and players.
        """)
        
        self.new_line()
        self.new_line()

        st.subheader("Explore IPL Data:")
        self.new_line()
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image("https://cdn.iconscout.com/icon/free/png-32/free-home-1754117-1493230.png?f=webp&w=32")
            st.markdown("### Home")
            st.write("Get started with the IPL Dashboard!")
            self.new_line()

            st.image("https://cdn.iconscout.com/icon/premium/png-32-thumb/cricket-bat-6941511-5693291.png?f=webp&w=32")
            st.markdown("### Batting Insights")
            st.write("Explore batting statistics and trends for different IPL players.")

        with col2:
            st.image("https://cdn.iconscout.com/icon/premium/png-32-thumb/team-flag-2121193-1785152.png?f=webp&w=32")
            st.markdown("### Team Insights")
            st.write("Analyze trends and performance statistics for your favorite teams.")
            self.new_line()

            st.image("https://cdn.iconscout.com/icon/premium/png-32-thumb/cricket-ball-1861204-1578626.png?f=webp&w=32")
            st.markdown("### Bowling Insights")
            st.write("Dive into bowling statistics and trends for various IPL players.")

        st.markdown("")
        st.markdown("")

        st.subheader("Additional Information:")
        st.markdown("#### Resources and Help")
        st.markdown("""
        For more information, visit the [IPL website](https://www.iplt20.com/) or contact us for assistance.
        """)
        st.write("We hope you enjoy exploring IPL insights! Feel free to reach out with any feedback or questions.")

    def render_team_insights(self):
        """Render team insights section."""        
        st.title('IPL Team Insights')
        st.write("Analyze trends in team performances across different IPL seasons.")
        self.new_line()
        st.write(f"Team: {self.selected_team}")

        # Ensure user has selected a season
        if not self.selected_season:
            st.warning('Please select season')
            return

        # Get team data
        data = self.ipl.teamRecord_API(self.selected_team, self.selected_season)
        if not data:
            st.info('No data available.')
            return

        self.display_overall_stats(data) 
        self.display_performance_visualizations(data, 'team')

    def render_batting_insights(self):
        """Render batting insights section."""
        st.title('IPL Batting Insights')
        st.write("Analyze trends in batting performances across different IPL players.")
        self.new_line()
        st.write(f"Player: {self.selected_player}")

        # Get player batting data
        data = self.ipl.batsmanRecord_API(self.selected_player, self.selected_season)
        if not data:
            st.info('No data available.')
            return

        self.display_overall_stats(data)
        self.display_performance_visualizations(data, 'batting')

    def render_bowling_insights(self):
        """Render bowling insights section."""
        st.title('IPL Bowling Insights')
        st.write("Analyze trends in bowling performances across different IPL players.")
        self.new_line()
        st.write(f"Player: {self.selected_player}")
        
        # Get player bowling data
        data = self.ipl.bowlerRecord_API(self.selected_player, self.selected_season)
        if not data:
            st.info('No data available.')
            return

        self.display_overall_stats(data) # self.new_line()
        self.display_performance_visualizations(data, 'bowling')

    def render_player_vs_player_insights(self):
        """Render player vs player insights section."""
        st.title('IPL Player vs Player Insights')
        st.write("Compare performances of two different players in IPL.")
        st.write(f"Player 1: {self.selected_player1}")
        st.write(f"Player 2: {self.selected_player2}")

        st.info('This feature is under development. Please check back later for updates.')
        st.info('Last updated: 2024-04-24')

        # Get data for players' comparison
        # data = self.ipl.player_vs_player_API(self.selected_player1, self.selected_player2, self.selected_season)
        # if not data:
        #     st.info('No data available.')
        #     return
        
        # self.display_performance_visualizations(data, 'player_vs_player')


    def display_overall_stats(self, data: Dict):
        """Display general team stats."""
        if not data.get('overall'):
            st.info("No data available for overall stats.")
            return

        cell = 4
        items = list(data['overall'].items())
        groups = [dict(items[i:i + cell]) for i in range(0, len(items), cell)]

        for group in groups:
            columns = st.columns(cell)
            i = 0
            for _metric, value in group.items():
                columns[i].metric(_metric.capitalize(), value, data.get('delta', {}).get(_metric, 'nan'), delta_color='normal', help=data.get('help', {}).get(_metric, ''))
                i += 1
            self.new_line()
        self.new_line()


    def display_performance_visualizations(self, data: Dict, section_type: str):
        """Display performance visualizations based on data and section type."""
        st.header("Performance Visualizations")

        if not data.get('against') or not data['against'].get('team') or not data['against'].get('season'):
            st.info("No data available for performance visualizations.")
            return
        
        # Convert data to DataFrame and melt for easier plotting
        team_data = pd.DataFrame.from_dict(data['against']['team'], orient='index').reset_index().rename(columns={'index': 'Team'})
        season_data = pd.DataFrame.from_dict(data['against']['season'], orient='index').reset_index().rename(columns={'index': 'Season'})

        # Drop non-plot columns
        self.drop_non_plot_columns(team_data, season_data)

        team_df_melted = pd.melt(team_data, id_vars='Team', value_vars=team_data.columns[1:], var_name='Metric', value_name='Value')
        season_df_melted = pd.melt(season_data, id_vars='Season', value_vars=season_data.columns[1:], var_name='Metric', value_name='Value')

        # Select chart type and metrics
        default_metrics = self.define_metrics(section_type)
        graph_type = st.selectbox('Select chart type:', ['Bar', 'Line', 'Scatter', 'Strip', 'Histogram', 'Pie', 'Sunburst'], index=0, help='Select the type of chart to display')
        selected_metrics = st.multiselect('Select Metrics:', team_data.columns[1:], default=default_metrics) # col names of team_data or season_data will be same for section_type
        
        # Filter data based on selected metrics
        team_df_filtered = team_df_melted[team_df_melted['Metric'].isin(selected_metrics)]
        season_df_filtered = season_df_melted[season_df_melted['Metric'].isin(selected_metrics)]
        
        # Plot metrics
        hover_mode = st.toggle('Enable hover mode', True)
        self.new_line()
        self.plot_metrics('Team', hover_mode, graph_type, selected_metrics, team_data, team_df_filtered)
        self.plot_metrics('Season', hover_mode, graph_type, selected_metrics, season_data, season_df_filtered)

    def drop_non_plot_columns(self, team_data: pd.DataFrame, season_data: pd.DataFrame):
        """Drop non-plot columns from the dataframes."""
        season_data.drop(columns=['Best Figure', 'Best Figure Fraction'], inplace=True, errors='ignore')
        team_data.drop(columns=['Best Figure', 'Best Figure Fraction'], inplace=True, errors='ignore')

    def define_metrics(self, section_type: str) -> (List[str]):
        """Define metrics and chart title based on section type."""
        if section_type == 'batting':
            metrics = ['Innings', 'Average', 'Strike Rate']
        elif section_type == 'bowling':
            metrics = ['Innings', 'Wickets', 'Economy']
        elif section_type == 'team' or section_type == 'season':
            metrics = ['Matches', 'Wins', 'Losses']
        else:
            raise ValueError("Invalid section type. Please provide a valid section type (batting or bowling).")
        return metrics

    def plot_metrics(self, index: str, hover_mode: bool, graph_type: str, metrics: List[str], original_df: pd.DataFrame, melted_df: pd.DataFrame):
        """Plot metrics based on selected chart type and metrics."""
        if not metrics:
            return

        fig = None
        if graph_type == 'Bar':
            fig = px.bar(melted_df, x=index, y='Value', color='Metric', barmode='group', labels={index: index, 'Value': 'Value'})
        elif graph_type == 'Line':
            fig = px.line(melted_df, x=index, y='Value', color='Metric')
            fig.update_traces(mode='lines+markers')
        elif graph_type == 'Scatter':
            if len(metrics) >= 2:
                if len(metrics) == 2:
                    fig = px.scatter(original_df, x=metrics[0], y=metrics[1], color=index, hover_name=index)
                else:
                    if len(metrics) > 3:
                        st.warning('Scatter plot can only display 3 metrics at a time. Selecting first 3 metrics.')
                    _size = original_df[metrics[2]].str.replace('*', '').astype(np.int32) if original_df[metrics[2]].dtype == 'object' and metrics[2] == 'HighestScore' else original_df[metrics[2]]
                    fig = px.scatter(original_df, x=metrics[0], y=metrics[1], size=_size, color=index, hover_name=index, size_max=_size.max())
            else:
                st.error('Scatter plot requires at least 2 metrics to be selected.')
        elif graph_type == 'Strip':
            fig = px.strip(melted_df, x=index, y='Value', color='Metric')
        elif graph_type == 'Histogram':
            fig = px.histogram(melted_df, x=index, y='Value', color='Metric')
        elif graph_type == 'Pie':
            if len(metrics) == 1:
                fig = px.pie(melted_df, names=index, values='Value', color=index, labels={index: index, 'Value': 'Value'})
            else:
                st.error('Please select exactly one metric for a pie chart.')
        elif graph_type == 'Sunburst':
            fig = px.sunburst(melted_df, path=[index, 'Metric'], values='Value', color=index,color_continuous_scale='RdBu', color_continuous_midpoint=np.average(melted_df['Value'], weights=melted_df['Value']), labels={index: index, 'Value': 'Value'}, hover_data={'Value': ':.2f'}, hover_name=index, branchvalues='total', maxdepth=2) # best for fours and sixes against each team
        else:
            st.warning('Invalid chart type selected.')
            return

        # Display the chart
        if fig:
            if hover_mode: fig.update_layout(hovermode='x')
            Dash = ''
            if self.area_option in ['Team','Batting','Bowling','Player']:
                Dash = 'Team\'s' if self.area_option == 'Team' else 'Player\'s' # update Dash based on area option
            else:
                raise ValueError("Invalid area option. Please provide a valid area option (Team, Batting, Bowling, Player vs Player).")
            fig.update_layout(title = Dash + ' Performance against Each ' + index, legend_title='Metric', width=750)
            st.plotly_chart(fig)

# Run the dashboard
if __name__ == '__main__':
    IPLDashboard()

