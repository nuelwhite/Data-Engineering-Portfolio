import pandas as pd
import logging
from typing import List, Union, Dict, Any
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)

class DataTransformer:
    """Utility class for common data transformations used across pipelines"""
    
    @staticmethod
    def standardize_dates(df, date_columns):
        """
        Standardize date columns to datetime format.
        
        Args:
            df (pd.DataFrame): Input dataframe
            date_columns (List[str]): List of date column names to standardize
            
        Returns:
            pd.DataFrame: DataFrame with standardized dates
        """
        try:
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logger.debug(f"Standardized date column: {col}")
                else:
                    logger.warning(f"Date column not found: {col}")
            return df
        except Exception as e:
            logger.error(f"Error standardizing dates: {str(e)}")
            raise

    @staticmethod
    def round_numeric(df, columns, decimals=2):
        """
        Round numeric columns to specified decimal places.
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (List[str]): List of numeric column names to round
            decimals (int): Number of decimal places (default: 2)
            
        Returns:
            pd.DataFrame: DataFrame with rounded numeric values
        """
        try:
            for col in columns:
                if col in df.columns:
                    df[col] = df[col].round(decimals)
                    logger.debug(f"Rounded numeric column: {col}")
                else:
                    logger.warning(f"Numeric column not found: {col}")
            return df
        except Exception as e:
            logger.error(f"Error rounding numeric values: {str(e)}")
            raise

    @staticmethod
    def remove_duplicates(df, subset=None):
        """
        Remove duplicate records from the dataframe.
        
        Args:
            df (pd.DataFrame): Input dataframe
            subset (List[str], optional): List of columns to consider for duplicates
            
        Returns:
            pd.DataFrame: DataFrame with duplicates removed
        """
        try:
            original_len = len(df)
            df = df.drop_duplicates(subset=subset)
            removed_count = original_len - len(df)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} duplicate records")
            return df
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            raise

    @staticmethod
    def split_address(df, address_col):
        """
        Split address into components (street, city, state, zip).
        Handles both regular and military addresses.
        
        Args:
            df (pd.DataFrame): Input dataframe
            address_col (str): Name of the address column
            
        Returns:
            pd.DataFrame: DataFrame with split address components
        """
        try:
            if address_col not in df.columns:
                logger.error(f"Address column not found: {address_col}")
                return df

            # Split by comma first
            df[['street', 'city', 'state_zip']] = df[address_col].str.split(',', expand=True)
            
            # Function to handle state and zip
            def split_state_zip(state_zip):
                if pd.isna(state_zip):
                    return pd.Series([None, None])
                
                parts = state_zip.strip().split()
                # List of military address designators
                military_designators = ['DPO', 'APO', 'FPO', 'MPO', 'AA', 'AP', 'AE']
                
                # Check if any military designator is present
                if any(designator in parts for designator in military_designators):
                    designator = next(d for d in military_designators if d in parts)
                    idx = parts.index(designator)
                    return pd.Series([designator, ' '.join(parts[idx+1:])])
                else:
                    return pd.Series([parts[0], ' '.join(parts[1:])])

            # Split state and zip
            df[['state', 'zip']] = df['state_zip'].apply(split_state_zip)
            
            # Drop original address and state_zip columns
            df = df.drop(columns=[address_col, 'state_zip'])
            
            logger.info("Successfully split address into components")
            return df
            
        except Exception as e:
            logger.error(f"Error splitting address: {str(e)}")
            raise

    @staticmethod
    def standardize_phone(df, phone_col):
        """
        Standardize phone numbers to a consistent format.
        
        Args:
            df (pd.DataFrame): Input dataframe
            phone_col (str): Name of the phone number column
            
        Returns:
            pd.DataFrame: DataFrame with standardized phone numbers
        """
        try:
            if phone_col not in df.columns:
                logger.error(f"Phone column not found: {phone_col}")
                return df

            # Remove all non-numeric characters
            df[phone_col] = df[phone_col].str.replace(r'\D', '', regex=True)
            
            # Format as (XXX) XXX-XXXX
            df[phone_col] = df[phone_col].apply(
                lambda x: f"({x[:3]}) {x[3:6]}-{x[6:]}" if len(x) == 10 else x
            )
            
            logger.info("Successfully standardized phone numbers")
            return df
            
        except Exception as e:
            logger.error(f"Error standardizing phone numbers: {str(e)}")
            raise

    @staticmethod
    def handle_missing_values(df, 
                            numeric_columns=None,
                            categorical_columns=None,
                            date_columns=None):
        """
        Handle missing values in the dataframe based on column types.
        
        Args:
            df (pd.DataFrame): Input dataframe
            numeric_columns (List[str]): List of numeric columns
            categorical_columns (List[str]): List of categorical columns
            date_columns (List[str]): List of date columns
            
        Returns:
            pd.DataFrame: DataFrame with handled missing values
        """
        try:
            # Handle numeric columns
            if numeric_columns:
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = df[col].fillna(0)
            
            # Handle categorical columns
            if categorical_columns:
                for col in categorical_columns:
                    if col in df.columns:
                        df[col] = df[col].fillna('Unknown')
            
            # Handle date columns
            if date_columns:
                for col in date_columns:
                    if col in df.columns:
                        df[col] = df[col].fillna(pd.NaT)
            
            logger.info("Successfully handled missing values")
            return df
            
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            raise

    @staticmethod
    def process_chunk(chunk, transformations):
        """
        Apply a list of transformations to a chunk of data.
        
        Args:
            chunk (pd.DataFrame): Input data chunk
            transformations (List[Dict]): List of transformation configurations
            
        Returns:
            pd.DataFrame: Transformed data chunk
        """
        try:
            for transform in transformations:
                transform_type = transform.get('type')
                params = transform.get('params', {})
                
                if transform_type == 'standardize_dates':
                    chunk = DataTransformer.standardize_dates(chunk, **params)
                elif transform_type == 'round_numeric':
                    chunk = DataTransformer.round_numeric(chunk, **params)
                elif transform_type == 'remove_duplicates':
                    chunk = DataTransformer.remove_duplicates(chunk, **params)
                elif transform_type == 'split_address':
                    chunk = DataTransformer.split_address(chunk, **params)
                elif transform_type == 'standardize_phone':
                    chunk = DataTransformer.standardize_phone(chunk, **params)
                elif transform_type == 'handle_missing_values':
                    chunk = DataTransformer.handle_missing_values(chunk, **params)
                
            return chunk
            
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            raise 