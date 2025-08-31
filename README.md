# CivicWatch 🚦

CivicWatch is a **Telegram bot** that empowers citizens to report civic issues (like potholes, broken streetlights, or overflowing trash bins) directly through chat.
It automatically extracts location data (from image GPS or user’s location) and logs the reports into a CSV file for tracking and follow-up.

---

## ✨ Features

* 📸 **Photo-based Reporting** – Upload an image as proof for the issue.
* 🌍 **Automatic GPS Extraction** – Extracts GPS data from image EXIF metadata.
* 📍 **Fallback Location Sharing** – If GPS isn’t found, users can send their live location.
* ⚡ **Priority Mapping** – Issues are automatically tagged with priority:

  * Pothole → High
  * Streetlight → Medium
  * Trash → Low
  * Other → Medium
* 📝 **Persistent Storage** – Saves reports in a `reports.csv` file with details:

  * Report ID
  * User
  * Image file
  * Latitude & Longitude
  * Issue Type
  * Priority
  * Status

---

## 📂 CSV File Structure

Each submitted report is stored in **reports.csv**:

| ReportID | User    | ImageFile         | Latitude | Longitude | Type        | Priority | Status    |
| -------- | ------- | ----------------- | -------- | --------- | ----------- | -------- | --------- |
| 1        | john\_d | john\_abc123.jpg  | 11.0056  | 76.9661   | Pothole     | High     | Submitted |
| 2        | alice   | alice\_xyz789.jpg | 11.0123  | 76.9734   | Streetlight | Medium   | Submitted |

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/civicwatch.git
cd civicwatch
```

### 2. Install dependencies

```bash
pip install python-telegram-bot exifread
```

### 3. Add your bot token

Replace the placeholder with your bot’s token in the script:

```python
TOKEN = "YOUR_BOT_TOKEN"
```

### 4. Run the bot

```bash
python bot.py
```

---

## 💡 Usage

1. Start the bot with `/start`
2. Report an issue with `/report`
3. Select the issue type (Pothole, Streetlight, Trash, Other)
4. Upload a photo of the issue

   * If GPS data is found → Auto-submitted
   * If not → Bot asks for your live location
5. Receive confirmation with **Report ID**
6. Check report status anytime with:

   ```text
   /my_status <report_id>
   ```

---

## 🔐 Example Bot Flow

**User:** `/report`
**Bot:** "Select the type of issue" → (User selects *Pothole*)
**Bot:** "Now send a photo of the issue" → (User uploads photo)
**Bot:** ✅ "Report submitted! ID: 3, Type: Pothole, Priority: High, Status: Submitted"

---

## 🛠️ Tech Stack

* [Python](https://www.python.org/)
* [python-telegram-bot](https://python-telegram-bot.org/)
* [ExifRead](https://pypi.org/project/ExifRead/)

---

## 📌 Future Enhancements

* Admin dashboard for reviewing and updating report statuses
* Database integration (PostgreSQL / MongoDB) instead of CSV
* Email/SMS notifications for updates
* Analytics & Heatmap of reported issues

---

## 🤝 Contributing

Pull requests are welcome!
If you have suggestions for improvements, feel free to open an **issue** or submit a **PR**.
