import os
from faker import Faker
import random
import time
import uuid
import csv
from datetime import datetime
import logging


# Configurations 
OUTPUT_DIR = 'events_data'
EVENTS_PER_FILE = 1000
DELAY_BETWEEN_FILES = 5

fake = Faker()

# Configure meta data for different events

# user metadata
USERS = [f'user_{i}'for i in range(1,1001)]
AGE_GROUPS = ['18-24', '25-34', '35-44', '45-54', '55+']
GENDERS = ['Male', 'Female']
LOCATIONS = ['Accra', 'Kumasi', 'Takoradi', 'Tamale', 'Sunyani', 'Nairobi', 'Cape Town', 'Johannesburg', 'Abuja', 'Lagos', 'Kano', 'Abuja', 'Lagos', 'Kano', 'Abuja', 'Lagos', 'Kano']


# product metadata
CATEGORIES = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Toys', 'Sports', 'Automotive', 'Health', 'Beauty', 'Other']
PRODUCTS = [
    (f'prod_{i}', random.choice(CATEGORIES), round(random.uniform(5.00, 500.00), 2))
    for i in range(1, 1001)
]


# user behavior metadata
EVENT_TYPES = ['view', 'purchase', 'add_to_cart', 'purchase', 'search']

# devices metadata
DEVICES = ['Desktop', 'Mobile', 'Tablet']
OPERATING_SYSTEMS = ['Windows', 'MacOS', 'iOS', 'Android']
BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
UTM_SOURCES = ['google', 'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'other']
SHIPPING_METHODS = ['Standard', 'Express', 'Overnight']
PAYMENT_METHODS = ['Credit Card', 'Mobile Money', 'Paypal', 'Apple Pay', 'Google Pay', 'Bank Transfer', 'Cash on Delivery']

PAGE_URLS = ['homepage', 'cart_page', 'product_page', 'checkout_page', 'search_results_page']
REFERRER_URLS = ['https://www.google.com', 'https://www.facebook.com', 'https://www.twitter.com', 'https://www.instagram.com', 'https://www.linkedin.com', 'https://www.youtube.com', 'https://www.other.com']


