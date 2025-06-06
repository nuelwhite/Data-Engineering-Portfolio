import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def calculate_basic_metrics(df: pd.DataFrame) -> Dict:
    """
    Calculate basic metrics for the dashboard.
    
    Args:
        df (pd.DataFrame): Processed movie data
        
    Returns:
        Dict: Dictionary containing basic metrics
    """
    try:
        metrics = {
            'total_movies': len(df),
            'total_revenue': df['revenue_million_usd'].sum(),
            'avg_budget': df['budget_million_usd'].mean(),
            'avg_rating': df['vote_average'].mean(),
            'total_votes': df['vote_count'].sum(),
            'avg_runtime': df['runtime'].mean()
        }
        return metrics
    except Exception as e:
        logging.error(f"Error calculating basic metrics: {e}")
        raise

def get_top_movies(df: pd.DataFrame, metric: str, n: int = 5) -> pd.DataFrame:
    """
    Get top N movies by specified metric.
    
    Args:
        df (pd.DataFrame): Processed movie data
        metric (str): Metric to sort by
        n (int): Number of movies to return
        
    Returns:
        pd.DataFrame: Top N movies
    """
    try:
        return df.nlargest(n, metric)[['title', metric]]
    except Exception as e:
        logging.error(f"Error getting top movies: {e}")
        raise

def get_genre_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze movies by genre.
    
    Args:
        df (pd.DataFrame): Processed movie data
        
    Returns:
        pd.DataFrame: Genre analysis
    """
    try:
        # Split genres and create genre rows
        genre_data = []
        for _, row in df.iterrows():
            genres = row['genres'].split('|')
            for genre in genres:
                genre_data.append({
                    'genre': genre,
                    'title': row['title'],
                    'revenue': row['revenue_million_usd'],
                    'budget': row['budget_million_usd'],
                    'rating': row['vote_average']
                })
        
        genre_df = pd.DataFrame(genre_data)
        
        # Calculate metrics by genre
        genre_analysis = genre_df.groupby('genre').agg({
            'title': 'count',
            'revenue': 'mean',
            'budget': 'mean',
            'rating': 'mean'
        }).reset_index()
        
        genre_analysis.columns = ['genre', 'movie_count', 'avg_revenue', 'avg_budget', 'avg_rating']
        return genre_analysis
    except Exception as e:
        logging.error(f"Error analyzing genres: {e}")
        raise

def get_revenue_budget_correlation(df: pd.DataFrame) -> Tuple[float, go.Figure]:
    """
    Calculate correlation between revenue and budget and create scatter plot.
    
    Args:
        df (pd.DataFrame): Processed movie data
        
    Returns:
        Tuple[float, go.Figure]: Correlation coefficient and scatter plot
    """
    try:
        correlation = df['revenue_million_usd'].corr(df['budget_million_usd'])
        
        fig = px.scatter(
            df,
            x='budget_million_usd',
            y='revenue_million_usd',
            hover_data=['title'],
            title='Revenue vs Budget',
            labels={
                'budget_million_usd': 'Budget (Millions USD)',
                'revenue_million_usd': 'Revenue (Millions USD)'
            }
        )
        
        return correlation, fig
    except Exception as e:
        logging.error(f"Error calculating revenue-budget correlation: {e}")
        raise

def get_rating_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create rating distribution plot.
    
    Args:
        df (pd.DataFrame): Processed movie data
        
    Returns:
        go.Figure: Rating distribution plot
    """
    try:
        fig = px.histogram(
            df,
            x='vote_average',
            nbins=20,
            title='Rating Distribution',
            labels={'vote_average': 'Rating', 'count': 'Number of Movies'}
        )
        return fig
    except Exception as e:
        logging.error(f"Error creating rating distribution: {e}")
        raise

def get_revenue_trend(df: pd.DataFrame) -> go.Figure:
    """
    Create revenue trend over time.
    
    Args:
        df (pd.DataFrame): Processed movie data
        
    Returns:
        go.Figure: Revenue trend plot
    """
    try:
        # Convert release_date to datetime if it's not already
        df['release_date'] = pd.to_datetime(df['release_date'])
        
        # Group by year and calculate metrics
        yearly_data = df.groupby(df['release_date'].dt.year).agg({
            'revenue_million_usd': 'sum',
            'title': 'count'
        }).reset_index()
        
        yearly_data.columns = ['year', 'total_revenue', 'movie_count']
        
        fig = px.line(
            yearly_data,
            x='year',
            y='total_revenue',
            title='Yearly Revenue Trend',
            labels={
                'year': 'Year',
                'total_revenue': 'Total Revenue (Millions USD)'
            }
        )
        
        return fig
    except Exception as e:
        logging.error(f"Error creating revenue trend: {e}")
        raise 