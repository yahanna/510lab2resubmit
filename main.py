import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import csv


events = []

for x in range(1,36):
    # time.sleep(1)
    url = "https://visitseattle.org/events/page/" + str(x)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    selector = "div.search-result-preview > div > h3 > a"
    a_eles = soup.select(selector)
    events_url = [x['href'] for x in a_eles]
    events.extend(events_url)

# Create a CSV file to save the event information
csv_file = open('events.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Event Name', 'Date', 'Location', 'Type', 'Region', 'Website'])

# Loop through each event URL
for event_url in events:
    res = requests.get(event_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Extract the event information
    event_name = soup.select_one('div.medium-6.columns.event-top > h1').text.strip()
    date = soup.select_one('div.medium-6.columns.event-top > h4 > span:nth-child(1)').text.strip()
    location = soup.select_one('div.medium-6.columns.event-top > h4 > span:nth-child(2)').text.strip()
    type = soup.select_one('div.medium-6.columns.event-top > a:nth-child(3)').text.strip()
    region = soup.select_one('div.medium-6.columns.event-top > a:nth-child(4)').text.strip()
    website = event_url
    
    # Write the event information to the CSV file
    csv_writer.writerow([event_name, date, location, type, region, website])

# Close the CSV file
csv_file.close()

# Open the original CSV file to read event information
with open('events.csv', mode='r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)
    # Create a list of all rows including headers
    rows = list(csv_reader)

# Prepare the new rows list with an additional header for Latitude and Longitude
new_rows = [rows[0] + ['Latitude', 'Longitude']]

# Iterate over the event rows (excluding the header)
for row in rows[1:]:
    location = row[2]
    base_url = "https://nominatim.openstreetmap.org/search.php"
    query_params = {
        "q": location,
        "format": "jsonv2"
    }
    
    # Fetch latitude and longitude using Nominatim API
    try:
        response = requests.get(base_url, params=query_params)
        if response.status_code == 200 and len(response.json()) > 0:
            data = response.json()[0]
            latitude = data.get('lat')
            longitude = data.get('lon')
        else:
            latitude, longitude = 'N/A', 'N/A'  # Use placeholders if no data found
    except Exception as e:
        print(f"Error fetching location data for {location}: {e}")
        latitude, longitude = 'Error', 'Error'  # Use error placeholders
    
    # Append latitude and longitude to the row
    new_rows.append(row + [latitude, longitude])

# Write the new rows into a new CSV file
with open('events_extended.csv', mode='w', newline='') as new_csv_file:
    csv_writer = csv.writer(new_csv_file)
    csv_writer.writerows(new_rows)

print("CSV file has been updated with latitude and longitude.")

# Function to parse the event date and return the last date if it's a range
def parse_event_date(date_str):
    # Handle special cases like "Ongoing"
    if date_str.lower() == 'ongoing':
        # Option 1: Return today's date for ongoing events
        return datetime.today()
        # Option 2: Return a future date if you prefer to fetch forecasts further out
        # return datetime.today() + timedelta(days=30)
    elif 'through' in date_str:
        # Parse the last date from the range "Now through MM/DD/YYYY"
        last_date_str = date_str.split(' ')[-1]
    else:
        last_date_str = date_str
    
    try:
        # Convert to datetime object
        return datetime.strptime(last_date_str, "%m/%d/%Y")
    except ValueError:
        # Handle other unexpected formats
        print(f"Unrecognized date format: {date_str}")
        # Return a default date or handle as needed
        return datetime.today()  # Or any other default date


# Function to fetch the short forecast for a given date and coordinates
def get_short_forecast(latitude, longitude, event_date):
    formatted_date = event_date.strftime("%Y-%m-%d")
    weather_api_url = f'http://api.weather.gov/points/{latitude},{longitude}'
    
    try:
        # Set a timeout for the API requests
        res = requests.get(weather_api_url, timeout=1)  # Timeout in seconds
        if res.status_code == 200:
            forecast_url = res.json().get('properties', {}).get('forecast')
            if forecast_url:
                forecast_res = requests.get(forecast_url, timeout=1)
                forecasts = forecast_res.json().get('properties', {}).get('periods', [])
                
                for forecast in forecasts:
                    if formatted_date in forecast['startTime']:
                        return forecast['shortForecast']
                return 'Weather forecast not found for specific date'
            else:
                return 'Forecast URL not found'
        else:
            return f'Weather API response code: {res.status_code}'
    except requests.exceptions.RequestException as e:
        return f'Error fetching weather data: {e}'


# Reading the CSV, updating with shortForecast (this part should replace the relevant section in your script)
with open('events_extended.csv', mode='r', newline='') as csv_file, open('events_with_forecast.csv', mode='w', newline='') as output_file:
    csv_reader = csv.reader(csv_file)
    csv_writer = csv.writer(output_file)
    headers = next(csv_reader) + ['ShortForecast']
    csv_writer.writerow(headers)

    for row in csv_reader:
        location = row[2]
        event_date_str = row[1]
        latitude, longitude = row[-2], row[-1]  # Assuming lat and lon are the last two columns

        # Parse the event date
        event_date = parse_event_date(event_date_str)
        
        # Fetch the short forecast if coordinates are available
        if latitude != 'N/A' and longitude != 'N/A':
            short_forecast = get_short_forecast(latitude, longitude, event_date)
        else:
            short_forecast = 'N/A'
        
        # Write the updated row to the new CSV
        csv_writer.writerow(row + [short_forecast])

print("CSV file has been updated with short forecasts.")
