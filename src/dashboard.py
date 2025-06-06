import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.kpi_analysis import (
    calculate_basic_metrics,
    get_top_movies,
    get_genre_analysis,
    get_revenue_budget_correlation,
    get_rating_distribution,
    get_revenue_trend
)

class DataFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
        self.cooldown = 1  # seconds

    def on_modified(self, event):
        if event.src_path.endswith('.csv'):
            current_time = time.time()
            if current_time - self.last_modified > self.cooldown:
                self.last_modified = current_time
                st.rerun()

def load_latest_data():
    """Load the most recent processed data file."""
    data_dir = './data/processed'
    files = [f for f in os.listdir(data_dir) if f.startswith('processed_data_')]
    if not files:
        st.error("No processed data files found!")
        return None
    
    latest_file = max(files)  # Gets the most recent file based on date in filename
    file_path = os.path.join(data_dir, latest_file)
    return pd.read_csv(file_path)

def setup_file_watcher():
    """Set up file watcher for the processed data directory."""
    event_handler = DataFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='./data/processed', recursive=False)
    observer.start()
    return observer

def main():
    st.set_page_config(
        page_title="Movie Analysis Dashboard",
        page_icon="🎬",
        layout="wide"
    )
    
    # Set up file watcher
    observer = setup_file_watcher()
    
    try:
        st.title("🎬 Movie Analysis Dashboard")
        st.write("Last updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Load data
        df = load_latest_data()
        if df is None:
            return
        
        # Calculate basic metrics
        metrics = calculate_basic_metrics(df)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Movies", f"{metrics['total_movies']:,}")
        with col2:
            st.metric("Total Revenue", f"${metrics['total_revenue']:,.2f}M")
        with col3:
            st.metric("Average Budget", f"${metrics['avg_budget']:,.2f}M")
        with col4:
            st.metric("Average Rating", f"{metrics['avg_rating']:.2f}")
        
        # Top Movies Section
        st.header("Top Movies")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Revenue")
            top_revenue = get_top_movies(df, 'revenue_million_usd')
            st.dataframe(top_revenue)
        
        with col2:
            st.subheader("By Rating")
            top_rating = get_top_movies(df, 'vote_average')
            st.dataframe(top_rating)
        
        # Genre Analysis
        st.header("Genre Analysis")
        genre_analysis = get_genre_analysis(df)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                genre_analysis,
                x='genre',
                y='movie_count',
                title='Number of Movies by Genre'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                genre_analysis,
                x='genre',
                y='avg_revenue',
                title='Average Revenue by Genre'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Revenue vs Budget
        st.header("Revenue vs Budget Analysis")
        correlation, fig = get_revenue_budget_correlation(df)
        st.write(f"Correlation coefficient: {correlation:.2f}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Rating Distribution
        st.header("Rating Distribution")
        fig = get_rating_distribution(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Revenue Trend
        st.header("Revenue Trend Over Time")
        fig = get_revenue_trend(df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add refresh button
        if st.button("Refresh Data"):
            st.rerun()
            
    finally:
        # Clean up file watcher
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main() 