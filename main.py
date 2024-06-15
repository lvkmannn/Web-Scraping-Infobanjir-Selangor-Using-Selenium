import os
from datetime import datetime

import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

website = 'http://infobanjirjps.selangor.gov.my/water-level-data.html?districtId=1&lang=en'
os.environ['PATH'] += r"C:\SeleniumDrivers\chrome-win64\chrome.exe"
driver = webdriver.Chrome()
driver.get(website)

# Wait for the website to load
time.sleep(3)

# Select district 'All' - dropdown
dropdown = Select(driver.find_element(By.ID, 'comboBxDistrict'))
dropdown.select_by_visible_text('All')

# Wait for the website to load
time.sleep(2)

# Select entries 'All' - dropdown
table_length = Select(driver.find_element(By.NAME, 'tableWaterLevel_length'))
table_length.select_by_visible_text('All')

# Wait for the website to load
time.sleep(2)

# Find table first in order to find selected table row 'tr'
table = driver.find_element(By.ID, 'tableWaterLevel')
matches = table.find_elements(By.TAG_NAME, 'tr')

# Create list to store data
station_id = []
station = []
station_rain = []
district = []
last_updated = []
total_rainfall_hour = []
total_rainfall_day = []
water_level = []

for match in matches[2:]:
    # print(match.text)
    district_name = match.find_element(By.XPATH, './td[4]').text
    district.append(district_name)
    # To view progress
    print(district_name)
    station_id.append(match.find_element(By.XPATH, './td[2]').text)
    station_name = match.find_element(By.XPATH, './td[3]').text
    station.append(station_name)
    last_updated.append(match.find_element(By.XPATH, './td[5]').text)
    water_level.append(match.find_element(By.XPATH, './td[6]').text)

time.sleep(2)

rainfall_button = driver.find_element(By.XPATH, '//*[@id="menu_6"]/a')
rainfall_button.click()

time.sleep(2)

ks_button = driver.find_element(By.XPATH, '//*[@id="rainfallDistrictData"]/div[1]/a[1]')
ks_button.click()

time.sleep(2)

# Wait for the website to load
time.sleep(3)

# Select district 'All' - dropdown
dropdown = Select(driver.find_element(By.ID, 'comboBxDistrict'))
dropdown.select_by_visible_text('All')

# Wait for the website to load
time.sleep(3)

# Select entries 'All' - dropdown
table_length = Select(driver.find_element(By.NAME, 'tableRainfall_length'))
table_length.select_by_visible_text('All')

# Wait for the website to load
time.sleep(2)

# Find table first in order to find selected table row 'tr'
table_2 = driver.find_element(By.ID, 'tableRainfall')
rows = table_2.find_elements(By.TAG_NAME, 'tr')

# Create a dictionary to store rainfall data temporarily
rainfall_data = {}

# Iterate over the rainfall table rows
for row in rows[2:]:
    name = row.find_element(By.XPATH, './td[3]').text
    rainfall_data[name] = {
        'total_rainfall_hour': row.find_element(By.XPATH, './td[12]').text,
        'total_rainfall_day': row.find_element(By.XPATH, './td[13]').text
    }

# Iterate over the water level data
for idx, st in enumerate(station):
    if st in rainfall_data:
        total_rainfall_hour_val = rainfall_data[st]['total_rainfall_hour']
        total_rainfall_day_val = rainfall_data[st]['total_rainfall_day']
    else:
        # If rainfall data is not found, assign empty strings
        total_rainfall_hour_val = ''
        total_rainfall_day_val = ''

    # Append rainfall data to respective lists
    station_rain.append(st)
    total_rainfall_hour.append(total_rainfall_hour_val)
    total_rainfall_day.append(total_rainfall_day_val)

driver.quit()

# Create DataFrame
df = pd.DataFrame({
    'district': district,
    'station_id': station_id,
    'station': station,
    'last_updated': last_updated,
    'total_rainfall_hour': total_rainfall_hour,
    'total_rainfall_day': total_rainfall_day,
    'water_level': water_level
})

df['last_updated'] = pd.to_datetime(df['last_updated'], format='%d/%m/%Y %H:%M:%S')

# Sort the DataFrame by the "last_updated" column in ascending order
df_sorted = df.sort_values(by=['district', 'last_updated'], ascending=[True, True])


# get current date and time
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# convert datetime obj to string
str_current_datetime = str(current_datetime)

df_sorted.to_csv('selangor_weather_{}.csv'.format(str_current_datetime), index=False)
print(df_sorted)
