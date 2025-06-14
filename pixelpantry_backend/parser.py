import glob
import os
import pandas as pd

# List of downloaded CSVs from your scraper
input_files = glob.glob("*.csv")  # Finds all CSV files in the current directory

for input_file in input_files:
    if "parsed" in input_file:
        continue  # Skip already parsed files if script is run again
    
    try:
        # Find where the actual data starts (header "time" row)
        with open(input_file, "r") as f:
            lines = f.readlines()
        
        # Initialize to handle case when 'time' is not found
        header_line = None
        data_start_idx = 0
        
        # Find where the actual data starts (header "time" row)
        for idx, line in enumerate(lines):
            if line.startswith("time"):
                header_line = line.strip()
                data_start_idx = idx
                break
        
        if not header_line:
            print(f" Skipping {input_file} - No 'time' header found.")
            continue
        
        # Detect if this CSV is weather or humidity based on header columns
        if "temperature" in header_line or "windspeed" in header_line:
            output_file = "weather_parsed.csv"
        elif "humidity" in header_line:
            output_file = "humidity_parsed.csv"
        else:
            output_file = f"unknown_parsed_{input_file}"
        
        # Use pandas to read the data and remove rows with NaN values
        # Skip rows before the header line
        df = pd.read_csv(input_file, skiprows=data_start_idx)
        
        # Count rows before removal
        rows_before = len(df)
        
        # Drop rows with any NaN values
        df_clean = df.dropna()
        
        # Count rows after removal
        rows_after = len(df_clean)
        rows_removed = rows_before - rows_after
        
        # Save the cleaned data to the output file
        if os.path.exists(output_file):
            # Append without header if file exists
            df_clean.to_csv(output_file, mode='a', header=False, index=False)
        else:
            # Create new file with header
            df_clean.to_csv(output_file, index=False)
        
        print(f"!!!Parsed {input_file} to {output_file} - Removed {rows_removed} rows with NaN values")
        
        # Delete the original file
        os.remove(input_file)
        print(f" Deleted {input_file}")
    
    except Exception as e:
        print(f" Error processing {input_file}: {str(e)}")

print("\n\n All files parsed and cleaned successfully!")