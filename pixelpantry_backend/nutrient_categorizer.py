# nutrient_categorizer.py
import pandas as pd

def categorize_nutrients(filename, state_name):

    state_name = state_name.upper()
    # Load full dataset
    df = pd.read_csv(filename)

    # Filter for the specific state
    state_df = df[df['State'] == state_name].copy()

    if state_df.empty:
        print(f"State '{state_name}' not found in the dataset.")
        return None

    # Convert percentage strings to floats
    def to_float(x):
        return float(x.strip('%'))

    n_columns = ['Nitrogen - High', 'Nitrogen - Medium', 'Nitrogen - Low']
    p_columns = ['Phosphorous - High', 'Phosphorous - Medium', 'Phosphorous - Low']
    k_columns = ['Potassium - High', 'Potassium - Medium', 'Potassium - Low']

    for col in n_columns + p_columns + k_columns:
        state_df[col] = state_df[col].apply(to_float)

    # Function to get dominant category
    def get_category(row, cols):
        values = {cat.split(' - ')[1]: row[cat] for cat in cols}
        return max(values, key=values.get)

    # Apply categorization
    state_df['N'] = state_df.apply(lambda row: get_category(row, n_columns), axis=1)
    state_df['P'] = state_df.apply(lambda row: get_category(row, p_columns), axis=1)
    state_df['K'] = state_df.apply(lambda row: get_category(row, k_columns), axis=1)

    # Keep final columns
    result_df = state_df[['State', 'N', 'P', 'K']]

    return result_df
