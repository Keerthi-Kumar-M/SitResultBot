import os
import time
import logging
import shutil
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8138260389:AAF9VGSAmYS536YTOyMfHgdKpEyMiKcNXmI"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🧠 Launch Chrome headless
def launch_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"

    chromedriver_path = shutil.which("chromedriver")
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

# 🧠 Fetch Result from SIMS Portal
def fetch_result(usn: str, dob: str) -> str:
    try:
        day, month, year = dob.split("-")
        driver = launch_browser()
        driver.get("https://sims.sit.ac.in/parents/")
        time.sleep(2)

        # Fill form
        driver.find_element(By.ID, "username").send_keys(usn)
        Select(driver.find_element(By.ID, "dd")).select_by_value(day.zfill(2) + " ")
        Select(driver.find_element(By.ID, "mm")).select_by_value(month.zfill(2))
        Select(driver.find_element(By.ID, "yyyy")).select_by_value(year)
        time.sleep(1)

        # Submit form
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(3)

        # Check for invalid login
        if "Invalid" in driver.page_source or "incorrect" in driver.page_source.lower():
            driver.quit()
            return "❌ Invalid USN or DOB. Please try again."

        # Wait for "Exam History" link then click
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Exam History')]"))
        ).click()
        time.sleep(3)

        # Parse Results Page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        
        result_blocks = soup.find_all("div", class_="uk-card uk-card-body result-data")
        if not result_blocks:
            return "⚠️ No semester results found."

        final_output = ""
        for card in result_blocks[:6]:
            caption = card.find("caption")
            if not caption:
                continue

            exam_session = caption.text.strip().split("Credits")[0].strip()
            sgpa = cgpa = ""
            for span in caption.find_all("span"):
                val = span.text.strip()
                if "SGPA" in val:
                    sgpa = val.split(":")[1].strip()
                elif "CGPA" in val:
                    cgpa = val.split(":")[1].strip()

            final_output += f"📘 Exam Session: {exam_session}\n🧮 SGPA: {sgpa}\n🎓 CGPA: {cgpa}\n\n"

        return final_output.strip()

    except Exception as e:
        import traceback
        try:
            driver.quit()
        except:
            pass
        return f"❌ An error occurred while fetching result:\n{traceback.format_exc()}"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *SIT Result Bot*!\n\nSend your *USN DOB* like:\n\n`1SI22CS082 07-09-2004`",
        parse_mode="Markdown"
    )

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    chat_id = update.message.chat_id
    logger.info(f"📩 Message from {chat_id}: {msg}")

    try:
        usn, dob = msg.split()
        await update.message.reply_text("🔍 Fetching your result...")
        result = fetch_result(usn, dob)
        await update.message.reply_text(result)
    except ValueError:
        await update.message.reply_text(
            "⚠️ Invalid format. Use:\n`1SI22CS082 07-09-2004`",
            parse_mode="Markdown"
        )

# 🟢 Run the bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 SIT Result Bot is now running...")
    app.run_polling()

if __name__ == "__main__":
    main()
