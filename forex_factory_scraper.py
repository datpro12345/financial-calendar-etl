import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pytz import timezone
from datetime import datetime

# Function to convert time from UTC to Ho Chi Minh time
def convert_to_hcm(date_str, time_str):
    utc_zone = timezone('UTC')
    hcm_zone = timezone('Asia/Ho_Chi_Minh')
    utc_time = datetime.strptime(date_str + ' ' + time_str, '%b.%d.%Y %I:%M%p').replace(tzinfo=utc_zone)
    hcm_time = utc_time.astimezone(hcm_zone)
    return hcm_time

# Function to scrape Forex Factory calendar data
def scrape_forex_factory(url):
    # Setup Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Load the webpage
        driver.get(url)
        
        # Wait for the calendar table to load
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'calendar__table'))
        )
        
        # Get the page source and parse it with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the calendar table
        table = soup.find('table', class_='calendar__table')
        
        if not table:
            raise ValueError("Could not find the calendar table on the page.")
        
        # Lists to hold data
        titles, countries, dates, times, impacts, forecasts, previous, urls = [], [], [], [], [], [], [], []
        
        # Loop through table rows and extract data
        for row in table.find_all('tr', class_='calendar__row'):
            title_tag = row.find('td', class_='calendar__event')
            country_tag = row.find('td', class_='calendar__country')
            datetime_tag = row.get('data-event-datetime')
            impact_tag = row.find('td', class_='impact')
            forecast_tag = row.find('td', class_='forecast')
            previous_tag = row.find('td', class_='previous')
            url_tag = row.find('a', class_='calendar__detail')
            
            if not all([title_tag, country_tag, datetime_tag, impact_tag, forecast_tag, previous_tag, url_tag]):
                continue
            
            title = title_tag.text.strip()
            country = country_tag.find('span')['title']
            datetime_split = datetime_tag.split(' ')
            date = datetime_split[0]
            time = ' '.join(datetime_split[1:])
            impact = impact_tag.find('span')['title']
            forecast = forecast_tag.text.strip()
            previous_val = previous_tag.text.strip()
            event_url = 'https://www.forexfactory.com' + url_tag['href']
            
            titles.append(title)
            countries.append(country)
            dates.append(date)
            times.append(time)
            impacts.append(impact)
            forecasts.append(forecast)
            previous.append(previous_val)
            urls.append(event_url)
        
        # Create a DataFrame
        df = pd.DataFrame({
            'Title': titles,
            'Country': countries,
            'Date': dates,
            'Time': times,
            'Impact': impacts,
            'Forecast': forecasts,
            'Previous': previous,
            'URL': urls
        })
        
        return df
    
    finally:
        driver.quit()

# Function to automate the conversion process
def automate_csv_conversion(df, output_path):
    # Filter the dataframe based on the specified conditions
    filtered_df = df[(df['Country'].isin(['EUR', 'GBP', 'USD'])) & (df['Impact'] == 'High')]

    # Apply the conversion to the filtered dataframe
    filtered_df['HCM_Start'] = filtered_df.apply(lambda row: convert_to_hcm(row['Date'], row['Time']), axis=1)
    filtered_df['HCM_End'] = filtered_df['HCM_Start'] + pd.Timedelta(hours=1)  # Assuming events last for 1 hour

    # Create a new dataframe for Google Calendar CSV format with HCM time
    calendar_hcm_df = pd.DataFrame({
        'Subject': filtered_df['Title'],
        'Start Date': filtered_df['HCM_Start'].dt.strftime('%m/%d/%Y'),
        'Start Time': filtered_df['HCM_Start'].dt.strftime('%H:%M'),
        'End Date': filtered_df['HCM_End'].dt.strftime('%m/%d/%Y'),
        'End Time': filtered_df['HCM_End'].dt.strftime('%H:%M'),
        'Description': 'Forecast: ' + filtered_df['Forecast'] + ' | Previous: ' + filtered_df['Previous'] + ' | ' + filtered_df['URL'],
        'Location': filtered_df['Country']
    })

    # Save the new dataframe to a CSV file
    calendar_hcm_df.to_csv(output_path, index=False)
    print(f"Google Calendar CSV file saved to {output_path}")

# Example usage
url = 'https://www.forexfactory.com/calendar?month=aug.2024&permalink=true&impacts=3&event_types=1,2,3,4,5,7,8,9,10,11&currencies=5,9,6'
df = scrape_forex_factory(url)
output_path = '/Users/datpro/Documents/gitdatpro/ff-transform-data/transformed_ff_calendar_aug2024.csv'
automate_csv_conversion(df, output_path)
