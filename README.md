# **IPL Commentary Data Scraper**  
*A web scraper to fetch cricket commentary data from Cricbuzz for all IPL seasons*  

---

## **📌 Project Overview**  
This project scrapes **IPL match commentary data** from [Cricbuzz](https://www.cricbuzz.com/) for analysis. It includes:  
✅ **Automated scraping** of all IPL seasons  
✅ **Structured data storage** in CSV/Firebase  
✅ **Virtual Machine (VM) setup** for scheduled runs  

---

## **📂 Data Snapshot**  
The fetched data includes:  
| Column | Description | Example |
|--------|-------------|---------|
| `date_time` | Match date & time | `Apr 05, 08:00 PM` |
| `series_name` | Tournament name | `Indian Premier League, 2017` |
| `match_id` | Unique match ID | `18121` |
| `match_name` | Teams playing | `SRH vs RCB` |
| `status` | Match status | `completed` |
| `venue` | Stadium name | `Rajiv Gandhi Intl. Stadium` |
| `season` | IPL season year | `2017` |
| `commText` | Commentary text | `"Cutting to Kedar Jadhav, sprays it down..."` |
| `event` | Ball event (wicket, 4, 6) | `NONE`, `WICKET` |
| `batsmanStrikerName` | Batsman on strike | `Kedar Jadhav` |
| `batTeamName` | Batting team | `RCB` |
| `bowlerStrikerName` | Current bowler | `Bhuvneshwar` |
| `timestamp` | Unix timestamp | `1.491412e+12` |
| `ballNbr` | Ball number in over | `50.0` |

*(See sample data in the table above.)*  

---

## **⚙️ Setup Instructions**  

### **1️⃣ Prerequisites**  
- Python 3.8+  
- Chrome browser installed  
- `pip` for package management  

### **2️⃣ Installation**  
```bash
# Clone the repo
git clone https://github.com/your-username/ipl-commentary-scraper.git
cd ipl-commentary-scraper

# Install dependencies
pip install -r requirements.txt
```

### **3️⃣ Configure ChromeDriver**  
#### **Option 1: Automatic (Recommended)**  
The script uses `webdriver-manager` to auto-download ChromeDriver.  

#### **Option 2: Manual Setup**  
1. Download [ChromeDriver](https://chromedriver.chromium.org/) matching your Chrome version.  
2. Place `chromedriver.exe` in the project folder.  

---

## **🚀 Running the Scraper**  
```bash
python main.py
```
**Output:**  
- CSV files per season (`IPL_2017.csv`, `IPL_2018.csv`, etc.)  
- Optional: Firebase upload  

---

## **🔥 Firebase Integration**  
To store data in **Firebase Realtime Database**:  
1. Set up a Firebase project at [Firebase Console](https://console.firebase.google.com/).  
2. Add your Firebase config in `firebase_config.json`:  
```json
{
  "apiKey": "YOUR_API_KEY",
  "authDomain": "YOUR_PROJECT.firebaseapp.com",
  "databaseURL": "https://YOUR_PROJECT.firebaseio.com",
  "projectId": "YOUR_PROJECT_ID",
  "storageBucket": "YOUR_BUCKET.appspot.com"
}
```
3. Run:  
```bash
python upload_to_firebase.py
```

*(Replace `YOUR_*` values with your Firebase credentials.)*  

---

## **🖥️ Virtual Machine (VM) Setup**  
A **Google Cloud/AWS VM** was configured for scheduled scraping:  
- **OS:** Ubuntu 20.04 LTS  
- **Cron Job:** Runs scraper weekly  
```bash
# Edit crontab
crontab -e

# Add this line (runs every Sunday at 2 AM)
0 2 * * 0 /usr/bin/python3 /path/to/scraper.py >> /var/log/ipl_scraper.log
```

---

## **📊 Future Improvements**  
- [ ] Add **real-time live match** scraping  
- [ ] Integrate **data visualization** (Power BI/Tableau)  
- [ ] Expand to **other cricket leagues** (BBL, PSL)  

---

## **📜 License**  
This project is for **educational use only**.  

---

**🔗 GitHub Repo:** [github.com/your-username/ipl-commentary-scraper](https://github.com/your-username/ipl-commentary-scraper)  
**📧 Contact:** [your-email@example.com](mailto:your-email@example.com)  

---

*(Replace placeholder links with your actual repo/contact info.)* 🚀