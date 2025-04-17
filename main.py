from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import requests

from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setting up Firebase Admin SDK
cred = credentials.Certificate("serviceAccount.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

def get_cricbuzz_commentary(match_id, inning):
    url = f'https://www.cricbuzz.com/api/cricket-match/{match_id}/full-commentary/{inning}'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('commentary', [])
        else:
            print(f"API request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching commentary: {e}")
        return None

def process_match(match_url, season):
    match_id = match_url.split('/')[-2]
    match_ref = db.collection('matches').document(match_id)

    try:
        # Check if match already exists
        if match_ref.get().exists:
            print(f"Match {match_id} exists, skipping")
            return True

        # Navigate to match page
        driver.get(match_url)
        time.sleep(3)

        # Get match info
        try:
            match_name = driver.find_element(By.CSS_SELECTOR, "h1.cb-nav-hdr").text.split('-')[0].strip()
            series_name = driver.find_element(By.CSS_SELECTOR, "a[title*='Indian Premier League'] span").text
            venue = driver.find_element(By.CSS_SELECTOR, "a[itemprop='location']").text.replace('\n', ' ')
            date_time = driver.find_element(By.CSS_SELECTOR, "span[itemprop='startDate']").text.replace('LOCAL', '').strip()
        except Exception as e:
            print(f"Error getting match info: {e}")
            return False

        # Store match info in Firestore
        match_data = {
            'match_id': match_id,
            'season': season,
            'match_name': match_name,
            'series_name': series_name,
            'venue': venue,
            'date_time': date_time,
            'status': 'processing'
        }
        match_ref.set(match_data)

        # Get commentary data
        commentary_data = []
        for inning in [1, 2]:
            data = get_cricbuzz_commentary(match_id, inning)
            if data:
                for comm in data[0].get('commentaryList', []):
                    commentary_data.append({
                        'inningsId': comm.get('inningsId'),
                        'commText': comm.get('commText'),
                        'timestamp': comm.get('timestamp'),
                        'ballNbr': comm.get('ballNbr'),
                        'event': comm.get('event'),
                        'batTeamName': comm.get('batTeamName'),
                        'batsmanStrikerName': comm.get('batsmanStriker', {}).get('batName'),
                        'batsmanStrikerRuns': comm.get('batsmanStriker', {}).get('batRuns'),
                        'bowlerStrikerName': comm.get('bowlerStriker', {}).get('bowlName'),
                        'batTeamScore': comm.get('batTeamScore')
                    })

        if commentary_data:
            # Add commentary data to a subcollection
            commentary_ref = match_ref.collection('commentary')
            commentary_data.append({'match_id': match_id})  # Add match_id reference to each entry
            batch = db.batch()
            for entry in commentary_data:
                
                doc_ref = commentary_ref.document()
                batch.set(doc_ref, entry)
            
            # Commit the batch
            batch.commit()

            # Update match status
            match_ref.update({'status': 'completed'})
            print(f"Successfully processed match {match_id}")
            return True
        else:
            match_ref.update({'status': 'failed', 'reason': 'No commentary data'})
            print(f"No commentary data for match {match_id}")
            return False

    except Exception as e:
        print(f"Error processing match {match_id}: {e}")
        match_ref.update({'status': 'failed', 'reason': str(e)})
        return False

def process_season(season_year):
    print(f"\nProcessing season: {season_year}")
    
    try:
        # Navigate to season page
        driver.get(f"https://www.cricbuzz.com/cricket-scorecard-archives/{season_year}")
        time.sleep(10)
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cb-srs-lst-itm"))
        )
        # Find IPL series
        series_links = driver.find_elements(By.CSS_SELECTOR, ".cb-srs-lst-itm a")
        ipl_link = None
        print(f"Found {len(series_links)} series links")
        
        
        for link in series_links:
            if "Indian Premier League" in link.text:
                ipl_link = link.get_attribute('href')
                break
                
        if not ipl_link:
            print(f"No IPL series found for {season_year}")
            return False
            
        # Get all match URLs from series page
        driver.get(ipl_link)
        time.sleep(10)
        match_elements = driver.find_elements(By.CSS_SELECTOR, ".cb-series-matches a.text-hvr-underline")
        match_urls = [elem.get_attribute('href') for elem in match_elements]
        
        print(f"Found {len(match_urls)} matches for IPL {season_year}")
        
        # Process each match
        success_count = 0
        for i, url in enumerate(match_urls, 1):
            print(f"\nProcessing match {i}/{len(match_urls)}")
            if process_match(url, season_year):
                success_count += 1
                
        print(f"Successfully processed {success_count}/{len(match_urls)} matches for season {season_year}")
        return True
        
    except Exception as e:
        print(f"Error processing season {season_year}: {e}")
        return False

def main():
    global driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        current_year = datetime.now().year
        for year in range(current_year, 2007, -1):  # Changed to 2022 to include 2023
            if year == 2025:  # Skip 2025 as it's not available yet
                continue
            process_season(year)
            
    finally:
        driver.quit()
        print("Scraping completed")

if __name__ == "__main__":
    main()