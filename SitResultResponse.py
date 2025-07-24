import os
import logging
import traceback
import requests
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8048623528:AAGPn_eB2i8utMdV_ak8YkQZz8MhmOgTJ1Y"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"


# ✅ Download & install chromedriver in pure Python (Railway-safe)
def setup_chromedriver():
    if os.path.exists(CHROMEDRIVER_PATH):
        return  # Already downloaded

    logger.info("⬇️ Downloading chromedriver...")
    url = "https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip"
    response = requests.get(url)
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        zip_ref.extract("chromedriver-linux64/chromedriver")
        os.rename("chromedriver-linux64/chromedriver", CHROMEDRIVER_PATH)
        os.chmod(CHROMEDRIVER_PATH, 0o755)
    logger.info("✅ Chromedriver setup complete")


# ✅ Launch Chrome
def launch_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/google-chrome"

    if not os.path.exists(CHROMEDRIVER_PATH):
        raise FileNotFoundError(f"❌ Chromedriver not found at {CHROMEDRIVER_PATH}")

    service = Service(CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)


# ✅ Fetch Result
def fetch_result(usn: str, dob: str) -> str:
    try:
        setup_chromedriver()
        day, month, year = dob.split("-")

        driver = launch_browser()
        driver.get("https://sims.sit.ac.in/parents/")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(usn)
        Select(driver.find_element(By.ID, "dd")).select_by_value(day.zfill(2) + " ")
        Select(driver.find_element(By.ID, "mm")).select_by_value(month.zfill(2))
        Select(driver.find_element(By.ID, "yyyy")).select_by_value(year)
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        WebDriverWait(driver, 10).until(
            lambda d: ("Invalid" in d.page_source or "incorrect" in d.page_source.lower()) or
                      EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Exam History')]"))(d)
        )

        if "Invalid" in driver.page_source or "incorrect" in driver.page_source.lower():
            driver.quit()
            return "❌ Invalid USN or DOB. Please try again."

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Exam History')]"))
        ).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-data"))
        )

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

    except Exception:
        try:
            driver.quit()
        except:
            pass
        logger.error("❌ Exception in fetch_result", exc_info=True)
        return f"❌ An error occurred while fetching result:\n{traceback.format_exc()}"


# ✅ Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *SIT Result Bot*!\n\nSend your *USN DOB* like:\n\n`1SI22CS082 07-09-2004`",
        parse_mode="Markdown"
    )

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


# ✅ Bot Main
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 SIT Result Bot is now running...")
    app.run_polling()


if __name__ == "__main__":
    main()
