import pandas as pd

# Step 1: Load dataset
crop_data = pd.read_csv('crop_data.csv')

# Step 2: Categorize function
def categorize(value, nutrient):
    if nutrient == 'N':
        if value < 240:
            return 'Low'
        elif value <= 480:
            return 'Medium'
        else:
            return 'High'
    elif nutrient == 'P':
        if value < 11:
            return 'Low'
        elif value <= 22:
            return 'Medium'
        else:
            return 'High'
    elif nutrient == 'K':
        if value < 110:
            return 'Low'
        elif value <= 280:
            return 'Medium'
        else:
            return 'High'

# Step 3: Replace values in-place
crop_data['N'] = crop_data['N'].apply(lambda x: categorize(x, 'N'))
crop_data['P'] = crop_data['P'].apply(lambda x: categorize(x, 'P'))
crop_data['K'] = crop_data['K'].apply(lambda x: categorize(x, 'K'))

# Step 4: Save the final matrix (optional)
crop_data.to_csv('encoded_crop_data.csv', index=False)

print(crop_data.head())
