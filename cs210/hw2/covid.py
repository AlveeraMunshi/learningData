import csv
from collections import defaultdict
import re

# ------------------------------------------------------------
# Helper Functions (Shared across all problems)
# ------------------------------------------------------------

def is_nan(value):
    """Check if a value is NaN (missing)."""
    if value is None or value == "":
        return True
    if isinstance(value, str):  # Only call lower() if value is a string
        return value.lower() == "nan"
    return False  # Numeric values are not NaN in this context

def round_value(value, decimals=0):
    """Round a value to specified decimal places."""
    return round(float(value), decimals) if value is not None and not is_nan(value) else None

def get_most_common(values):
    """Find the most common value in a list. In case of a tie, return the first one alphabetically."""
    frequency = defaultdict(int)
    for value in values:
        if not is_nan(value):
            frequency[value] += 1
    if not frequency:
        return None
    max_freq = max(frequency.values())
    most_common = [value for value, freq in frequency.items() if freq == max_freq]
    return sorted(most_common)[0]

def load_csv(file_path):
    """Load a CSV file into a list of dictionaries."""
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def save_csv(data, file_path, fieldnames):
    """Save a list of dictionaries to a CSV file with the same format as the input."""
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            cleaned_row = {key: "" if is_nan(value) else str(value) for key, value in row.items()}
            writer.writerow(cleaned_row)

# ------------------------------------------------------------
# Problem 2: Covid Dataset
# ------------------------------------------------------------

# Load the dataset
covid_data = load_csv('covidTrain.csv')

# Task 1: Replace age range with average
for row in covid_data:
    if not is_nan(row['age']) and '-' in row['age']:
        start, end = map(int, row['age'].split('-'))
        row['age'] = str(round_value((start + end) / 2))

# Task 2: Change date format
date_fields = ['date_onset_symptoms', 'date_admission_hospital', 'date_confirmation']
for row in covid_data:
    for field in date_fields:
        if not is_nan(row[field]):
            day, month, year = row[field].split('.')
            row[field] = f"{month}.{day}.{year}"

# Task 3: Fill missing latitude and longitude
# Calculate average latitude and longitude for each province
province_to_lat_lon = defaultdict(lambda: {'lat': [], 'lon': []})
for row in covid_data:
    if not is_nan(row['province']):
        province_to_lat_lon[row['province']]['lat'].append(float(row['latitude']) if not is_nan(row['latitude']) else None)
        province_to_lat_lon[row['province']]['lon'].append(float(row['longitude']) if not is_nan(row['longitude']) else None)

# Calculate average latitude and longitude for each province
province_avg = {}
for province, data in province_to_lat_lon.items():
    # Remove None values
    lat_vals = [x for x in data['lat'] if x is not None]
    lon_vals = [x for x in data['lon'] if x is not None]
    # Calculate average
    province_avg[province] = {
        'latitude': round_value(sum(lat_vals) / len(lat_vals), 2) if lat_vals else 0,
        'longitude': round_value(sum(lon_vals) / len(lon_vals), 2) if lon_vals else 0
    }

for row in covid_data:
    if not is_nan(row['province']):
        if is_nan(row['latitude']):
            row['latitude'] = province_avg[row['province']]['latitude']
        if is_nan(row['longitude']):
            row['longitude'] = province_avg[row['province']]['longitude']

# Task 4: Fill missing city values
province_to_city = defaultdict(list)
for row in covid_data:
    if not is_nan(row['province']) and not is_nan(row['city']):
        province_to_city[row['province']].append(row['city'])
most_common_city = {province: get_most_common(cities) for province, cities in province_to_city.items()}
for row in covid_data:
    if is_nan(row['city']) and not is_nan(row['province']):
        row['city'] = most_common_city.get(row['province'], '')

# Task 5: Fill missing symptom values
province_to_symptoms = defaultdict(list)
for row in covid_data:
    if not is_nan(row['province']) and not is_nan(row['symptoms']):
        symptoms = re.split(r'; |;', row['symptoms'])  # Handle both separators
        province_to_symptoms[row['province']].extend(symptoms)
most_common_symptom = {province: get_most_common(symptoms) for province, symptoms in province_to_symptoms.items()}
for row in covid_data:
    if is_nan(row['symptoms']) and not is_nan(row['province']):
        row['symptoms'] = most_common_symptom.get(row['province'], '')

# Save modified data
save_csv(covid_data, 'covidResult.csv', fieldnames=covid_data[0].keys())

