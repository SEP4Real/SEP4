import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
total_rows = 100000
current_time = datetime(2026, 4, 1, 9, 0, 0) # Start date

history_data = []
ratings_data = []

rows_generated = 0

while rows_generated < total_rows:
    # Simulate a new room / environment baseline for this session
    base_temp = random.randint(18, 26)
    base_humidity = random.randint(35, 60)
    base_co2 = random.randint(400, 800)
    base_light = random.randint(200, 800)
    base_noise = random.randint(30, 65)
    
    # Decide how long this specific session is (ensuring we don't exceed 3000 total)
    session_length = min(random.randint(10, 100), total_rows - rows_generated)
    
    # Rating can happen at ANY minute during the session
    rating_minute = random.randint(0, max(0, session_length - 1))
    
    for minute in range(session_length):
        timestamp = current_time + timedelta(minutes=minute)
        
        # Simulate conditions changing over time 
        temp = base_temp + (minute * random.uniform(-0.02, 0.05))
        humidity = base_humidity + (minute * random.uniform(-0.1, 0.2))
        co2 = base_co2 + (minute * random.uniform(2, 15)) # CO2 rises over time
        light = base_light + random.randint(-10, 10)
        noise = base_noise + random.randint(-5, 15)
        
        history_data.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temp),
            "humidity": round(humidity),
            "co2Level": round(co2),
            "lightLevel": round(light),
            "noiseLevel": round(noise)
        })
        
        # Add a rating if we hit the predetermined rating minute
        if minute == rating_minute:
            
            # Calculate a "focus penalty" based on the environment to ensure a wide spread (1 to 5)
            focus_penalty = 0
            
            # CO2 impact on focus
            if co2 > 1400: focus_penalty += 3
            elif co2 > 1000: focus_penalty += 2
            elif co2 > 750: focus_penalty += 1
            
            # Noise impact on focus
            if noise > 60: focus_penalty += 2
            elif noise > 50: focus_penalty += 1
            
            # Temperature impact on focus (ideal study temp is roughly 20-24C)
            if temp > 25 or temp < 19: focus_penalty += 1
            
            # Base rating (5 is perfect focus, subtract penalties)
            focus_level = 5 - focus_penalty
            
            # Add a bit of human unpredictability (-1, 0, or +1), then clamp between 1 and 5
            focus_level += random.randint(-1, 1)
            final_rating = max(1, min(5, focus_level))
            
            ratings_data.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "rating": final_rating
            })
            
    rows_generated += session_length
    # Jump forward a random amount of time (0 to 2 days) to simulate the next session
    current_time += timedelta(days=random.randint(0, 2), hours=random.randint(1, 12))

# Convert to DataFrames and save to CSV
df_history = pd.DataFrame(history_data)
df_ratings = pd.DataFrame(ratings_data)

df_history.to_csv("environment_history.csv", index=False)
df_ratings.to_csv("ratings.csv", index=False)

print(f"Generated {len(df_history)} history rows and {len(df_ratings)} focus ratings.")
print("\nFocus Rating distribution generated:")
print(df_ratings['rating'].value_counts().sort_index())