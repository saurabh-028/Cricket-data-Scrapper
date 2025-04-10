from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import requests
import sqlite3
from datetime import datetime

def setup_database():
    conn = sqlite3.connect('ipl_commentary.db')
    cursor = conn.cursor()
    
    # Create matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        match_id INTEGER PRIMARY KEY,
        season INTEGER,
        match_name TEXT,
        series_name TEXT,
        venue TEXT,
        date_time TEXT,
        status TEXT DEFAULT 'pending'
    )
    ''')
    
    # Create commentary table 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commentary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        inningsId INTEGER,
        commText TEXT,
        timestamp TEXT,
        ballNbr TEXT,
        event TEXT,
        batTeamName TEXT,
        batsmanStrikerName TEXT,
        batsmanStrikerRuns INTEGER,
        bowlerStrikerName TEXT,
        batTeamScore TEXT,
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
    )
    ''')
    
    conn.commit()
    return conn

def get_cricbuzz_commentary(match_id, inning):
    url = f'https://www.cricbuzz.com/api/cricket-match/{match_id}/full-commentary/{inning}'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('commentary', [])
    except Exception as e:
        print(f"Error fetching commentary: {e}")
        return None

def process_match(match_url, season, conn):
    cursor = conn.cursor()
    match_id = match_url.split('/')[-2]
    
    try:
        # Check if match already exists
        cursor.execute("SELECT 1 FROM matches WHERE match_id = ?", (match_id,))
        if cursor.fetchone():
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

        # Insert match info
        cursor.execute('''
        INSERT INTO matches (match_id, season, match_name, series_name, venue, date_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', 
        (match_id, season, match_name, series_name, venue, date_time, 'processing'))
        conn.commit()

        # Get commentary data
        commentary_data = []
        for inning in [1, 2]:
            data = get_cricbuzz_commentary(match_id, inning)
            if data:
                for comm in data[0].get('commentaryList', []):
                    commentary_data.append({
                        'match_id': match_id,
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
            pd.DataFrame(commentary_data).to_sql('commentary', conn, if_exists='append', index=False)
            cursor.execute("UPDATE matches SET status = 'completed' WHERE match_id = ?", (match_id,))
            conn.commit()
            print(f"Successfully processed match {match_id}")
            return True
        else:
            cursor.execute("UPDATE matches SET status = 'failed' WHERE match_id = ?", (match_id,))
            conn.commit()
            print(f"No commentary data for match {match_id}")
            return False

    except Exception as e:
        print(f"Error processing match {match_id}: {e}")
        cursor.execute("UPDATE matches SET status = 'failed' WHERE match_id = ?", (match_id,))
        conn.commit()
        return False

def process_season(season_year, conn):
    print(f"\nProcessing season: {season_year}")
    
    try:
        # Navigate to season page
        driver.get(f"https://www.cricbuzz.com/cricket-scorecard-archives/{season_year}")
        time.sleep(3)
        
        # Find IPL series
        series_links = driver.find_elements(By.CSS_SELECTOR, ".cb-srs-lst-itm a")
        ipl_link = None
        
        for link in series_links:
            if "Indian Premier League" in link.text:
                ipl_link = link.get_attribute('href')
                break
                
        if not ipl_link:
            print(f"No IPL series found for {season_year}")
            return False
            
        # Get all match URLs from series page
        driver.get(ipl_link)
        time.sleep(3)
        match_elements = driver.find_elements(By.CSS_SELECTOR, ".cb-series-matches a.text-hvr-underline")
        match_urls = [elem.get_attribute('href') for elem in match_elements]
        
        print(f"Found {len(match_urls)} matches for IPL {season_year}")
        
        # Process each match
        for i, url in enumerate(match_urls, 1):
            print(f"\nProcessing match {i}/{len(match_urls)}")
            process_match(url, season_year, conn)
            
        return True
        
    except Exception as e:
        print(f"Error processing season {season_year}: {e}")
        return False

def main():
    conn = setup_database()
    global driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        current_year = datetime.now().year
        for year in range(current_year, 2007, -1):
            if year == 2025:  # Skip 2025 as it's not available yet
                continue
            process_season(year, conn)
            
    finally:
        driver.quit()
        conn.close()
        print("Scraping completed")

if __name__ == "__main__":
    main()