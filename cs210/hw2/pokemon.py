import csv
from collections import defaultdict

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
# Problem 1: Pokemon Box Dataset
# ------------------------------------------------------------

# Load the dataset
pokemon_data = load_csv('pokemonTrain.csv')

# Task 1: Percentage of fire type Pokemons at or above level 40
fire_pokemons = [row for row in pokemon_data if row['type'] == 'fire']
above_level_40 = [row for row in fire_pokemons if not is_nan(row['level']) and float(row['level']) >= 40]
percentage = (len(above_level_40) / len(fire_pokemons)) * 100 if fire_pokemons else 0
rounded_percentage = int(round_value(percentage))
with open('pokemon1.txt', 'w') as f:
    f.write(f"Percentage of fire type Pokemons at or above level 40 = {rounded_percentage}")

# Task 2: Fill missing "type" column values
weakness_to_type = defaultdict(list)
for row in pokemon_data:
    if not is_nan(row['weakness']) and not is_nan(row['type']):
        weakness_to_type[row['weakness']].append(row['type'])
most_common_type = {weakness: get_most_common(types) for weakness, types in weakness_to_type.items()}
for row in pokemon_data:
    if is_nan(row['type']) and not is_nan(row['weakness']):
        row['type'] = most_common_type.get(row['weakness'], '')

# Task 3: Fill missing "atk", "def", and "hp" values
above_40 = [row for row in pokemon_data if not is_nan(row['level']) and float(row['level']) > 40]
below_40 = [row for row in pokemon_data if not is_nan(row['level']) and float(row['level']) <= 40]

avg_above_40 = {}
avg_below_40 = {}
for stat in ['atk', 'def', 'hp']:
    above_vals = [float(row[stat]) for row in above_40 if not is_nan(row[stat])]
    below_vals = [float(row[stat]) for row in below_40 if not is_nan(row[stat])]
    avg_above_40[stat] = round_value(sum(above_vals) / len(above_vals), 1) if above_vals else 0
    avg_below_40[stat] = round_value(sum(below_vals) / len(below_vals), 1) if below_vals else 0

for row in pokemon_data:
    if not is_nan(row['level']):
        level = float(row['level'])
        for stat in ['atk', 'def', 'hp']:
            if is_nan(row[stat]):
                row[stat] = avg_above_40[stat] if level > 40 else avg_below_40[stat]

# Save modified data
save_csv(pokemon_data, 'pokemonResult.csv', fieldnames=pokemon_data[0].keys())

# Task 4: Pokemon type to personality mapping
type_to_personality = defaultdict(set)
for row in pokemon_data:
    if not is_nan(row['type']) and not is_nan(row['personality']):
        type_to_personality[row['type']].add(row['personality'])
sorted_type_to_personality = {k: sorted(v) for k, v in sorted(type_to_personality.items())}
with open('pokemon4.txt', 'w') as f:
    f.write("Pokemon type to personality mapping:\n")
    for type_, personalities in sorted_type_to_personality.items():
        f.write(f"   {type_}: {', '.join(personalities)}\n")

# Task 5: Average HP for stage 3.0 Pokemons
stage_3_pokemons = [row for row in pokemon_data if not is_nan(row['stage']) and float(row['stage']) == 3.0]
hp_values = [float(row['hp']) for row in stage_3_pokemons if not is_nan(row['hp'])]
avg_hp = round_value(sum(hp_values) / len(hp_values)) if hp_values else 0
avg_hp = int(avg_hp)
with open('pokemon5.txt', 'w') as f:
    f.write(f"Average hit point for Pokemons of stage 3.0 = {avg_hp}")
