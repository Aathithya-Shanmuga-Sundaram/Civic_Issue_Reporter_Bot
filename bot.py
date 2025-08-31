import csv
import os
import exifread
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

CSV_FILE = "reports.csv"

# Create CSV if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ReportID", "User", "ImageFile", "Latitude", "Longitude", "Type", "Priority", "Status"])

# Map issue type to priority
PRIORITY_MAP = {
    "Pothole": "High",
    "Streetlight": "Medium",
    "Trash": "Low",
    "Other": "Medium"
}

# Convert EXIF GPS to decimal
def convert_to_decimal(gps_coord, ref):
    degrees = float(gps_coord[0].num) / float(gps_coord[0].den)
    minutes = float(gps_coord[1].num) / float(gps_coord[1].den)
    seconds = float(gps_coord[2].num) / float(gps_coord[2].den)
    decimal = degrees + (minutes/60) + (seconds/3600)
    if ref in ['S','W']:
        decimal = -decimal
    return decimal

# Extract GPS from image
def get_gps_data(file_path):
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f)
    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
        lat = tags['GPS GPSLatitude'].values
        lon = tags['GPS GPSLongitude'].values
        lat_ref = tags['GPS GPSLatitudeRef'].values
        lon_ref = tags['GPS GPSLongitudeRef'].values
        lat = convert_to_decimal(lat, lat_ref)
        lon = convert_to_decimal(lon, lon_ref)
        return lat, lon
    return None, None

# Save report to CSV
def save_report(user, image_file, lat, lon, issue_type, priority, status="Submitted"):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        report_id = sum(1 for _ in open(CSV_FILE))
        writer.writerow([report_id, user, image_file, lat, lon, issue_type, priority, status])
    return report_id

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 Welcome to CivicWatch!\n\n"
        "Report civic issues like potholes, broken streetlights, or overflowing trash bins.\n\n"
        "📌 To submit a report, use /report\n"
        "📌 To check status of your report, use /my_status <report_id>"
    )
    await update.message.reply_text(msg)

# /report command
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    types = ["Pothole", "Streetlight", "Trash", "Other"]
    markup = ReplyKeyboardMarkup([[t] for t in types], one_time_keyboard=True)
    context.user_data["awaiting_type"] = True  # Set flag
    await update.message.reply_text("Select the type of issue:", reply_markup=markup)

# Handle type selection
async def handle_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_type"):
        issue_type = update.message.text
        context.user_data["type"] = issue_type
        context.user_data["priority"] = PRIORITY_MAP.get(issue_type, "Medium")
        context.user_data["awaiting_type"] = False
        await update.message.reply_text("Now send a photo of the issue as proof:")

# Handle received photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    photo_file = await update.message.photo[-1].get_file()
    image_path = f"{username}_{photo_file.file_id}.jpg"
    await photo_file.download_to_drive(image_path)
    lat, lon = get_gps_data(image_path)
    context.user_data["image_path"] = image_path

    if lat is None:
        # Ask for location
        location_button = KeyboardButton(text="Send Location", request_location=True)
        markup = ReplyKeyboardMarkup([[location_button]], one_time_keyboard=True)
        await update.message.reply_text("No GPS found. Please share your location:", reply_markup=markup)
    else:
        report_id = save_report(username, image_path, lat, lon, context.user_data["type"], context.user_data["priority"])
        await update.message.reply_text(
            f"✅ Report submitted!\n"
            f"ID: {report_id}\n"
            f"Type: {context.user_data['type']}\n"
            f"Priority: {context.user_data['priority']}\n"
            f"Location: {lat}, {lon}\n"
            f"Status: Submitted"
        )

# Handle received location
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    loc = update.message.location
    image_path = context.user_data.get("image_path", "NoImage.jpg")
    report_id = save_report(username, image_path, loc.latitude, loc.longitude, context.user_data["type"], context.user_data["priority"])
    await update.message.reply_text(
        f"✅ Report submitted!\n"
        f"ID: {report_id}\n"
        f"Type: {context.user_data['type']}\n"
        f"Priority: {context.user_data['priority']}\n"
        f"Location: {loc.latitude}, {loc.longitude}\n"
        f"Status: Submitted"
    )

# /my_status command
async def my_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /my_status <report_id>")
        return
    report_id = args[0]
    found = False
    with open(CSV_FILE, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["ReportID"] == report_id:
                if row["User"] == (update.message.from_user.username or update.message.from_user.first_name):
                    await update.message.reply_text(
                        f"Report ID {report_id}\n"
                        f"Type: {row['Type']}\n"
                        f"Priority: {row['Priority']}\n"
                        f"Status: {row['Status']}"
                    )
                    found = True
                    break
    if not found:
        await update.message.reply_text(f"No report found with ID {report_id} for you.")

# Main bot
if __name__ == "__main__":
    TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("my_status", my_status))

    # Message handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_type))  # Only type selection

    print("Bot is running...")
    app.run_polling()

