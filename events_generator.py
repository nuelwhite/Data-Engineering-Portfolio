import os
from faker import Faker
import random
import time
import uuid
import csv
from datetime import datetime
import logging
import json

from notebooks.workbook import events_per_file, file_counter, session_id, tmp_file, user_id


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
EVENT_TYPES = ['view', 'purchase', 'add_to_cart', 'search']

# devices metadata
DEVICES = ['Desktop', 'Mobile', 'Tablet']
OPERATING_SYSTEMS = ['Windows', 'MacOS', 'iOS', 'Android']
BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
UTM_SOURCES = ['google', 'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'other']
SHIPPING_METHODS = ['Standard', 'Express', 'Overnight']
PAYMENT_METHODS = ['Credit Card', 'Mobile Money', 'Paypal', 'Apple Pay', 'Google Pay', 'Bank Transfer', 'Cash on Delivery']

PAGE_URLS = ['homepage', 'cart_page', 'product_page', 'checkout_page', 'search_results_page']
REFERRER_URLS = ['https://www.google.com', 'https://www.facebook.com', 'https://www.twitter.com', 'https://www.instagram.com', 'https://www.linkedin.com', 'https://www.youtube.com', 'https://www.other.com']


# helper functions for script generation

def random_ip():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def get_device_and_os():
    device = random.choice(DEVICES)

    if device == 'Desktop':
        device_os  = random.choice(['Windows', 'MacOS'])
    elif device == 'Mobile':
        device_os = random.choice(['iOS', 'Android'])
    elif device == 'Tablet':
        device_os = random.choice(['iOS', 'MacOS'])

    return device, device_os

def get_page_and_utm():
    utm_source = random.choice(UTM_SOURCES)

    if utm_source == 'google':
        utm_campaign = f'{utm_source}_campaign'
    elif utm_source == 'facebook':
        utm_campaign = f'{utm_source}_campaign'
    elif utm_source == 'twitter':
        utm_campaign = f'{utm_source}_campaign'
    elif utm_source == 'instagram':
        utm_campaign = f'{utm_source}_campaign'
    elif utm_source == 'linkedin':
        utm_campaign = f'{utm_source}_campaign'
    elif utm_source == 'youtube':
        utm_campaign = f'{utm_source}_campaign'
    else:  # other
        utm_campaign = f'{utm_source}_campaign'
    
    page_url = random.choice(PAGE_URLS)
    referrer_url = random.choice(REFERRER_URLS)
    
    return utm_source, utm_campaign, page_url, referrer_url

def generate_event(user_id, session_id):
    event_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    product_id, product_category, product_price = random.choice(PRODUCTS)
    event_type = random.choices(EVENT_TYPES, weights=[0.7, 0.15, 0.1, 0.05])[0]

    quantity = 0
    order_id = ''
    cart_value = ''
    discount_applied = 'False'
    shipping_method = ''
    payment_method = ''

    if event_type == 'add_to_cart':
        quantity = random.randint(1, 5)
    elif event_type == 'purchase':
        quantity = random.randint(1, 5)
        order_id = f'order_{random.randint(1000,9999)}'
        cart_value = round(quantity * product_price, 2)
        discount_applied = random.choice([True, False])
        shipping_method = random.choice(SHIPPING_METHODS)
        payment_method = random.choice(PAYMENT_METHODS)

    
    device, operating_system = get_device_and_os()
    browser = random.choice(BROWSERS)
    ip_address = random_ip()
    latency_ms = random.randint(10, 1000)

    utm_source, utm_campaign, page_url, referrer_url = get_page_and_utm()
    age_group = random.choice(AGE_GROUPS)
    gender = random.choice(GENDERS)
    location = random.choice(LOCATIONS)
    loyalty_member = random.choice([True, False])

    
    event = {
        'event_id': event_id,
        'timestamp': timestamp,
        'event_type': event_type,
        'user_id': user_id,
        'session_id': session_id,
        'product_id': product_id,
        'product_category': product_category,
        'product_price': product_price,
        'quantity': quantity,
        'order_id': order_id,
        'cart_value': cart_value,
        'discount_applied': discount_applied,
        'shipping_method': shipping_method,
        'payment_method': payment_method,
        'location': location,
        'age_group': age_group,
        'gender': gender,
        'loyalty_member': loyalty_member,
        'device': device,
        'operating_system': operating_system,
        'browser': browser,
        'ip_address': ip_address,
        'latency_ms': latency_ms,
        'utm_source': utm_source,
        'utm_campaign': utm_campaign,
        'page_url': page_url,
        'referrer_url': referrer_url,
    }

    return event


def write_to_file(output, header):
    file_counter = 0
    
    while True:
        file_counter += 1
        tmp_file = os.path.join(output, f'event_data_{file_counter:05d}.tmp')
        final_file = tmp_file.replace('.tmp', '.csv')

        with open(tmp_file, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for _ in range(EVENTS_PER_FILE):
                user_id = random.choice(USERS)
                session_id = f'session_{random.randint(1,1000)}'
                row = generate_event(user_id, session_id)
                writer.writerow(row)


        os.rename(tmp_file, final_file)
        print(f'Generated {events_per_file} events in {final_file}')

        time.sleep(DELAY_BETWEEN_FILES)


        


