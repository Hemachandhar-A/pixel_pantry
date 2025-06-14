from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

# -------------------------------
# PARAMETERS (Modify as needed)
# -------------------------------

import sys

if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    year = ""

if len(sys.argv) > 2:
    desired_state = sys.argv[2]
else:
    desired_state = ""

if len(sys.argv) > 3:
    desired_district = sys.argv[3]
else:
    desired_district = ""

if len(sys.argv) > 4:
    desired_block = sys.argv[4]
else:
    desired_block = ""

if len(sys.argv) > 5:
    city = sys.argv[5]
else:
    city = ""
     


# -------------------------------
# Setup Chrome options
# -------------------------------

# Setup download folder
download_dir =  os.getcwd()

# Create download directory if it doesn't exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Setup Chrome options with download directory
chrome_options = Options()
# Add this to your chrome_options
chrome_options.add_argument("--headless=new")
# Add these lines to your chrome_options
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-quic")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors=yes")

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "safebrowsing.disable_download_protection": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)
actions = ActionChains(driver)

# -------------------------------
# Step 1: Open URL
# -------------------------------
driver.get("https://www.soilhealth.dac.gov.in/piechart")

# -------------------------------
# Step 2: Click the "MacroNutrient(% View)" tab
# -------------------------------
try:
    macro_tab = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "MacroNutrient(% View)")]')))
    macro_tab.click()
    print("Clicked 'MacroNutrient(% View)' tab.")
except Exception as e:
    print(f"Failed to click the tab: {e}")

# -------------------------------
# Step 3: Select year
# -------------------------------
try:
    year_dropdown = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//div[@role="combobox" and contains(@class, "MuiSelect-select") and contains(text(), "2024-25")]'
    )))
    year_dropdown.click()
    year_option = wait.until(EC.element_to_be_clickable((By.XPATH, f'//li[contains(text(), "{year}")]')))
    year_option.click()
    print(f"Selected year: {year}")
except Exception as e:
    print(f"Failed to select year: {e}")

# -------------------------------
# Step 4: Conditional dropdown logic
# -------------------------------
if  desired_district or desired_block:
    # ---- Select State ----
    try:
        state_dropdown = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//div[@role="combobox" and contains(text(), "Select a state")]'
        )))
        state_dropdown.click()

        if desired_state:
            state_option_xpath = f'//li[contains(text(), "{desired_state}")]'
            state_option = wait.until(EC.presence_of_element_located((By.XPATH, state_option_xpath)))
            actions.move_to_element(state_option).perform()
            state_option.click()
            print(f"Selected state: {desired_state}")
        else:
            print("Skipped state selection (no input provided).")

    except Exception as e:
        print(f"Failed in state selection: {e}")

if   desired_block:
    # ---- Select District ----
    try:
        district_dropdown = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//div[@role="combobox" and contains(text(), "Select a district")]'
        )))
        district_dropdown.click()

        if desired_district:
            district_option_xpath = f'//li[contains(text(), "{desired_district}")]'
            district_option = wait.until(EC.presence_of_element_located((By.XPATH, district_option_xpath)))
            actions.move_to_element(district_option).perform()
            district_option.click()
            print(f"Selected district: {desired_district}")
        else:
            print("Skipped district selection (no input provided).")

    except Exception as e:
        print(f"Failed in district selection: {e}")

if city:
    # ---- Select Block ----
    try:
        block_dropdown = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//div[@role="combobox" and contains(text(), "Select a Block")]'
        )))
        block_dropdown.click()

        block_option_xpath = f'//li[contains(text(), "{desired_block}")]'
        block_option = wait.until(EC.presence_of_element_located((By.XPATH, block_option_xpath)))
        actions.move_to_element(block_option).perform()
        block_option.click()
        print(f"Selected block: {desired_block}")

    except Exception as e:
        print(f"Failed in block selection: {e}")

# -------------------------------
# Step 5: Export to CSV
# -------------------------------
try:
    export_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//a[contains(text(), "Export to CSV") and contains(@class, "downloadbtn")]'
    )))
    export_button.click()
    print("Clicked 'Export to CSV' button.")
except Exception as e:
    print(f"Failed to click 'Export to CSV': {e}")

# -------------------------------
# Cleanup
# -------------------------------
time.sleep(3)
driver.quit()


import glob

# Desired new filename
new_filename = f"nutritent_{desired_state}_{desired_district}_{desired_block}.csv"

# Wait for the most recent CSV file in the download directory
timeout = 20  # seconds
file_downloaded = False
downloaded_file = None

for i in range(timeout):
    csv_files = glob.glob(os.path.join(download_dir, "*.csv"))
    if csv_files:
        # Get the most recently created CSV file
        downloaded_file = max(csv_files, key=os.path.getctime)
        file_downloaded = True
        break
    time.sleep(1)

if file_downloaded:
    new_path = os.path.join(download_dir, new_filename)
    os.rename(downloaded_file, new_path)
    print(f"CSV file downloaded and renamed to: {new_filename}")
    
else:
    print("CSV file not found after waiting.")


