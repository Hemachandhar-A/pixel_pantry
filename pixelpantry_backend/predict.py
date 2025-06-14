"""
import pandas as pd
from datetime import datetime
import glob

# Load growing season months for each crop
crop_season_df = pd.read_csv('crop_grow_season.csv')  # Columns: crop,grow_months

# Load weather data
file_list = glob.glob('weather*.csv')
if not file_list:
    print("No file found starting with 'weather'")
    exit()

weather_df = pd.read_csv(file_list[0], parse_dates=['time'])
weather_df['year'] = weather_df['time'].dt.year
weather_df['month'] = weather_df['time'].dt.month

results = []
current_year = datetime.now().year
start_month = datetime.now().month

for _, row in crop_season_df.iterrows():
    crop = row['crop']
    grow_months = int(row['grow_months'])
    grow_month_range = [(start_month + i - 1) % 12 + 1 for i in range(grow_months)]

    print(f"\n=== Crop: {crop} | Growing period: {grow_months} months ===")
    print(f"Growing Months (starting from {start_month}): {grow_month_range}\n")

    historical_data = []

    for year in sorted(weather_df['year'].unique())[-5:]:  # Last 5 years
        mask = (weather_df['year'] == year) & (weather_df['month'].isin(grow_month_range))
        seasonal_df = weather_df[mask]

        avg_temp = seasonal_df['temperature_2m_mean (°C)'].mean()
        total_rainfall = seasonal_df['precipitation_sum (mm)'].sum()

        print(f"Year: {year} | Avg Temp: {round(avg_temp, 2)}°C | Total Rainfall: {round(total_rainfall, 2)} mm")

        historical_data.append({
            'year': year,
            'avg_temp': avg_temp,
            'total_rainfall': total_rainfall
        })

    avg_temp_pred = sum(d['avg_temp'] for d in historical_data) / len(historical_data)
    total_rainfall_pred = sum(d['total_rainfall'] for d in historical_data) / len(historical_data)

    print(f"\nPrediction for {crop} in {current_year}:")
    print(f"Predicted Avg Temp (mean of 5 years): {round(avg_temp_pred, 2)}°C")
    print(f"Predicted Total Rainfall (sum mean): {round(total_rainfall_pred, 2)} mm\n")

    results.append({
        'crop': crop,
        'predicted_year': current_year,
        'growing_season': grow_month_range,
        'predicted_avg_temp': round(avg_temp_pred, 2),
        'predicted_total_rainfall': round(total_rainfall_pred, 2)
    })

# Function to be used by model.py later
def get_predictions():
    return results

# Optional: Print summary if run standalone
if __name__ == "__main__":
    df = pd.DataFrame(results)
    print("\n==== Weather Predictions Summary ====")
    print(df)
"""
import pandas as pd
from datetime import datetime
import glob

# Load growing season months for each crop
crop_season_df = pd.read_csv('crop_grow_season.csv')  # Columns: crop,grow_months

# Load weather data
file_list = glob.glob('weather*.csv')
if not file_list:
    print("No file found starting with 'weather'")
    exit()

weather_df = pd.read_csv(file_list[0], parse_dates=['time'])
weather_df['year'] = weather_df['time'].dt.year
weather_df['month'] = weather_df['time'].dt.month

results = []
current_year = datetime.now().year
start_month = datetime.now().month

# SOLUTION 1: Use only complete historical years (past 4 years)
for _, row in crop_season_df.iterrows():
    crop = row['crop']
    grow_months = int(row['grow_months'])
    grow_month_range = [(start_month + i - 1) % 12 + 1 for i in range(grow_months)]
    
    print(f"\n=== Crop: {crop} | Growing period: {grow_months} months ===")
    print(f"Growing Months (starting from {start_month}): {grow_month_range}\n")
    
    historical_data = []
    
    # Get past 4 complete years (excluding current year)
    historical_years = sorted([year for year in weather_df['year'].unique() if year < current_year])[-4:]
    
    for year in historical_years:
        mask = (weather_df['year'] == year) & (weather_df['month'].isin(grow_month_range))
        seasonal_df = weather_df[mask]
        
        # Skip if no data for this period
        if not seasonal_df.empty:
            avg_temp = seasonal_df['temperature_2m_mean (°C)'].mean()
            total_rainfall = seasonal_df['precipitation_sum (mm)'].sum()
            
            print(f"Year: {year} | Avg Temp: {round(avg_temp, 2)}°C | Total Rainfall: {round(total_rainfall, 2)} mm")
            
            historical_data.append({
                'year': year,
                'avg_temp': avg_temp,
                'total_rainfall': total_rainfall
            })
    
    # Calculate predictions based on past years
    if historical_data:
        avg_temp_pred = sum(d['avg_temp'] for d in historical_data) / len(historical_data)
        total_rainfall_pred = sum(d['total_rainfall'] for d in historical_data) / len(historical_data)
        
        print(f"\nPrediction for {crop} in {current_year}:")
        print(f"Predicted Avg Temp (mean of {len(historical_data)} years): {round(avg_temp_pred, 2)}°C")
        print(f"Predicted Total Rainfall (mean of {len(historical_data)} years): {round(total_rainfall_pred, 2)} mm\n")
        
        results.append({
            'crop': crop,
            'predicted_year': current_year,
            'growing_season': grow_month_range,
            'predicted_avg_temp': round(avg_temp_pred, 2),
            'predicted_total_rainfall': round(total_rainfall_pred, 2)
        })
    else:
        print(f"\nWarning: No valid historical data for {crop} to make predictions!\n")

# Function to be used by model.py later
def get_predictions():
    return results


# Optional: Print summary if run standalone
if __name__ == "__main__":
    if results:
        df = pd.DataFrame(results)
        print("\n==== Weather Predictions Summary ====")
        print(df)
    else:
        print("\nNo valid predictions could be generated.")
