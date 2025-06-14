import numpy as np
import pandas as pd
import subprocess
from datetime import datetime, timedelta
from constants import ordinal_map, crops_dict, reverse_crops_dict
import os


# Calculate dates
today = datetime.today()
end_date = today.strftime('%Y-%m-%d')  # today's date
start_date = datetime(today.year - 5, 1, 1).strftime('%Y-%m-%d')  # 1st Jan 5 years ago

# Debug print to confirm dates
print(f"Start Date: {start_date}")
print(f"End Date: {end_date}")

# Run encoder
subprocess.run(["python", "encoder.py"])

# Get location
result = subprocess.run(["python", "location.py"], capture_output=True, text=True)
if result.returncode != 0:
    print("Subprocess failed!")
else:
    output = result.stdout.strip()  # e.g., "12.34,77.56,Karnataka"
    lat, lng, state = output.split(',')
    print(f"Latitude: {lat}")
    print(f"Longitude: {lng}")
    print(f"State: {state}")

    # Run humidity and scrapper scripts with dynamic dates
    humidity_proc = subprocess.Popen(["python", "api_hum.py", lat, lng, start_date, end_date])
    humidity_proc.wait()
    
    subprocess.run(["python", "api_sc.py", lat, lng, start_date, end_date])
    subprocess.run(["python", "parser.py"])

    args = ["2024-25",state.upper()]  # Example state and district

    # Dynamically build the argument list
    command = ["python", "nutrient_scrapper.py"] + args
    subprocess.run(command)

    # main_program.py
    from nutrient_categorizer import categorize_nutrients

    # Example usage
    filename = 'nutritent_TAMIL NADU__.csv'
    
    result = categorize_nutrients(filename, state)

    if result is not None:
        print(result)
        
        # Unpack the first row (assuming one row per state)
        row = result.iloc[0]  # Get the first (and usually only) row for that state
        
        n_value = row['N']
        p_value = row['P']
        k_value = row['K']

        N = n_value
        P = p_value
        K = k_value
        
        print(f"N: {n_value}, P: {p_value}, K: {k_value}")
        
        # Optional: Save the result to CSV
        result.to_csv(f'npk_encoded_{state.replace(" ", "_")}.csv', index=False)
    else:
        print("No data found for the selected state.")

crops = pd.read_csv("encoded_crop_data.csv")

# encoding the crops

crops['crops_num'] = crops['label'].map(crops_dict)
crops.drop(['label'], axis=1, inplace=True)

pd.set_option('future.no_silent_downcasting', True)
crops[['N', 'P', 'K']] = crops[['N', 'P', 'K']].replace(ordinal_map)

X = crops.drop(["crops_num"], axis=1)
y = crops["crops_num"]

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.preprocessing import MinMaxScaler
ms = MinMaxScaler()

X_train = ms.fit_transform(X_train)
X_test = ms.transform(X_test)

rfc = RandomForestClassifier(random_state=42)
rfc.fit(X_train, y_train)
ypred = rfc.predict(X_test)
print("accuracy:",accuracy_score(y_test, ypred))

def recommendation(N, P, k, temperature, humidity, ph, rainfal):
    n_val = ordinal_map[N]
    p_val = ordinal_map[P]
    k_val = ordinal_map[k]

    # Convert to DataFrame with correct columns
    input_df = pd.DataFrame([{
        'N': n_val,
        'P': p_val,
        'K': k_val,
        'temperature': temperature,
        'humidity': humidity,
        'ph': ph,
        'rainfall': rainfal
    }])

    transformed_features = ms.transform(input_df)
    prediction = rfc.predict(transformed_features)
    print(prediction)
    return prediction[0]

print(N,P,K)
from predict import get_predictions

predictions = get_predictions()
for pred in predictions:
    # Simulating different nutrient & environmental conditions
    if pred['crop'] == 'Rice':
        ph, humidity = 6.0, 80
    elif pred['crop'] == 'Apple':
        ph, humidity = 6.8, 60
    else:
        ph, humidity = 6.5, 50

    avg_temp = pred['predicted_avg_temp']
    rainfall = pred['predicted_total_rainfall']
    recommended_crop = recommendation(N, P, K, avg_temp, humidity, ph, rainfall)
    
    print(f"Original Crop: {pred['crop']} | Recommended Crop: {reverse_crops_dict[recommended_crop]}")

import json

final_output = {
    "latitude": lat,
    "longitude": lng,
    "location": state,
    "N": N,
    "P": P,
    "K": K,
    "predictions": []
}

for pred in predictions:
    # Simulating different nutrient & environmental conditions
    if pred['crop'] == 'Rice':
        ph, humidity = 6.0, 80
    elif pred['crop'] == 'Apple':
        ph, humidity = 6.8, 60
    else:
        ph, humidity = 6.5, 50

    avg_temp = pred['predicted_avg_temp']
    rainfall = pred['predicted_total_rainfall']
    recommended_crop_num = recommendation(N, P, K, avg_temp, humidity, ph, rainfall)
    recommended_crop = reverse_crops_dict.get(recommended_crop_num, "Unknown Crop")

    prediction_entry = {
        "original_crop": pred['crop'],
        "predicted_avg_temp": avg_temp,
        "predicted_total_rainfall": rainfall,
        "ph": ph,
        "humidity": humidity,
        "recommended_crop": recommended_crop
    }

    final_output["predictions"].append(prediction_entry)



# Add to the end of model.py (after the JSON is created)
with open('model_output.json', 'w') as f:
    json.dump(final_output, f, indent=4)

# --- Start of code to delete CSV files ---
all_files = os.listdir('.')
csv_files = [f for f in all_files if f.endswith('.csv')]
files_to_keep = ['crop_data.csv', 'crop_grow_season.csv', 'encoded_crop_data.csv']

for file in csv_files:
    if file not in files_to_keep:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")
# --- End of code to delete CSV files ---






























#Below this is just doc string ok dw


"""

feature_importances = rfc.feature_importances_
feature_names = X.columns
feature_importance_dict = dict(zip(feature_names, feature_importances))

print("Feature Importances:")
for feature, importance in sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True):
    print(f"{feature}: {importance:.4f}")

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# After fitting and predicting:

# Evaluation metrics
print("Accuracy:", accuracy_score(y_test, ypred))
print("Precision (weighted):", precision_score(y_test, ypred, average='weighted'))
print("Recall (weighted):", recall_score(y_test, ypred, average='weighted'))
print("F1 Score (weighted):", f1_score(y_test, ypred, average='weighted'))

cm = confusion_matrix(y_test, ypred)
print("Confusion Matrix:")
print(cm)

"""


"""
# Example inputs (you now pass "Low"/"Medium"/"High" for N, P, K)
N = "Low"
P = "High"
K = "Low"
ph = 6.5
humidity = 80
temperature = 20.52
rainfall = 200.72
predict1 = recommendation(N, P, K, temperature, humidity, ph, rainfall)

N = "Medium"
P = "Medium"
K = "Medium"
ph = 6.5
humidity = 50
temperature = 29.33
rainfall = 276.5
predict2 = recommendation(N, P, K, temperature, humidity, ph, rainfall)

N = "Medium"
P = "Medium"
K = "Medium"
ph = 6.5
humidity = 50
temperature = 28.48
rainfall = 1241.96
predict3 = recommendation(N, P, K, temperature, humidity, ph, rainfall)


if predict1 in reverse_crops_dict:
    crop = reverse_crops_dict[predict1]
    print("{} is a best crop to be cultivated ".format(crop))
else:
    print("Sorry are not able to recommend a proper crop for this environment")

if predict2 in reverse_crops_dict:
    crop = reverse_crops_dict[predict2]
    print("{} is a best crop to be cultivated ".format(crop))
else:
    print("Sorry are not able to recommend a proper crop for this environment")

if predict3 in reverse_crops_dict:
    crop = reverse_crops_dict[predict3]
    print("{} is a best crop to be cultivated ".format(crop))
else:
    print("Sorry are not able to recommend a proper crop for this environment")

"""

"""
if predict in crop_dict:
    crop = crop_dict[predict]
    print("{} is a best crop to be cultivated ".format(crop))
else:
    print("Sorry are not able to recommend a proper crop for this environment")
"""