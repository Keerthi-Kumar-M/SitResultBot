import os
import logging
import traceback
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Your Telegram Bot Token
BOT_TOKEN = "8148134144:AAHJXMpnO-vjYNd6es23aPEYSUWHT_3uBOU"

# 📋 Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_chrome_driver():
    """Create and configure Chrome WebDriver with robust options"""
    try:
        chrome_options = Options()
        
        # Essential headless options
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-javascript")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36")
        
        # Memory and performance optimizations
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        
        # Set binary location
        chrome_options.binary_location = "/usr/bin/google-chrome"
        
        # Create service
        service = Service("/usr/local/bin/chromedriver")
        
        logger.info("🚀 Creating Chrome WebDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        logger.info("✅ Chrome WebDriver created successfully")
        return driver
        
    except Exception as e:
        logger.error(f"❌ Failed to create Chrome driver: {str(e)}")
        raise


def validate_inputs(usn: str, dob: str) -> tuple:
    """Validate and parse USN and DOB inputs"""
    try:
        # Validate USN format (basic check)
        if not usn or len(usn) < 8:
            raise ValueError("USN must be at least 8 characters long")
        
        # Parse and validate DOB
        if not dob or len(dob.split("-")) != 3:
            raise ValueError("DOB must be in DD-MM-YYYY format")
        
        day, month, year = dob.split("-")
        
        # Basic validation
        if not (1 <= int(day) <= 31):
            raise ValueError("Day must be between 1 and 31")
        if not (1 <= int(month) <= 12):
            raise ValueError("Month must be between 1 and 12")
        if not (1900 <= int(year) <= 2030):
            raise ValueError("Year must be between 1900 and 2030")
        
        return day.zfill(2), month.zfill(2), year
        
    except ValueError as e:
        raise ValueError(f"Invalid input format: {str(e)}")


def fetch_sit_result(usn: str, dob: str) -> str:
    """Fetch SIT result with improved error handling and retry logic"""
    driver = None
    
    try:
        logger.info(f"🔍 Fetching result for USN: {usn}")
        
        # Validate inputs
        day, month, year = validate_inputs(usn, dob)
        
        # Create driver
        driver = create_chrome_driver()
        
        # Navigate to SIT portal
        logger.info("🌐 Navigating to SIT portal...")
        driver.get("https://sims.sit.ac.in/parents/")
        
        # Wait for login form
        logger.info("⏳ Waiting for login form...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Fill login form
        logger.info("📝 Filling login form...")
        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "username").send_keys(usn)
        
        # Select date of birth
        Select(driver.find_element(By.ID, "dd")).select_by_value(day + " ")
        Select(driver.find_element(By.ID, "mm")).select_by_value(month)
        Select(driver.find_element(By.ID, "yyyy")).select_by_value(year)
        
        # Submit form
        logger.info("🚀 Submitting login form...")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # Wait for response and check for errors
        logger.info("⏳ Waiting for login response...")
        time.sleep(3)
        
        # Check for invalid credentials
        page_source = driver.page_source.lower()
        if "invalid" in page_source or "incorrect" in page_source or "error" in page_source:
            return "❌ Invalid USN or Date of Birth. Please check your credentials and try again."
        
        # Look for exam history link
        try:
            logger.info("🔍 Looking for Exam History link...")
            exam_history_link = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Exam History')]"))
            )
            exam_history_link.click()
            logger.info("✅ Clicked on Exam History")
        except TimeoutException:
            return "❌ Could not find Exam History. Please check if you have any results available."
        
        # Wait for results to load
        logger.info("⏳ Waiting for results to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-data"))
        )
        
        # Parse results
        logger.info("📊 Parsing results...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        result_blocks = soup.find_all("div", class_="uk-card uk-card-body result-data")
        
        if not result_blocks:
            return "⚠️ No semester results found in your account."
        
        # Format results
        final_output = f"🎓 *Results for {usn}*\n\n"
        
        for i, card in enumerate(result_blocks[:6], 1):  # Limit to 6 semesters
            try:
                caption = card.find("caption")
                if not caption:
                    continue
                
                # Extract exam session
                exam_session = caption.text.strip().split("Credits")[0].strip()
                
                # Extract SGPA and CGPA
                sgpa = cgpa = "N/A"
                for span in caption.find_all("span"):
                    text = span.text.strip()
                    if "SGPA" in text and ":" in text:
                        sgpa = text.split(":")[1].strip()
                    elif "CGPA" in text and ":" in text:
                        cgpa = text.split(":")[1].strip()
                
                final_output += f"📘 *Semester {i}*\n"
                final_output += f"📅 Session: {exam_session}\n"
                final_output += f"🧮 SGPA: {sgpa}\n"
                final_output += f"🎯 CGPA: {cgpa}\n\n"
                
            except Exception as e:
                logger.warning(f"⚠️ Error parsing result block {i}: {str(e)}")
                continue
        
        if final_output.strip() == f"🎓 *Results for {usn}*":
            return "⚠️ Could not parse any results. Please try again later."
        
        final_output += "✅ *Results fetched successfully!*"
        return final_output.strip()
        
    except TimeoutException:
        logger.error("⏰ Timeout while fetching results")
        return "⏰ Request timed out. The SIT portal might be slow. Please try again."
        
    except WebDriverException as e:
        logger.error(f"🌐 WebDriver error: {str(e)}")
        return "🌐 Browser error occurred. Please try again in a few minutes."
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return f"❌ An unexpected error occurred. Please try again.\n\nError: {str(e)}"
        
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("🔒 Browser closed successfully")
            except Exception as e:
                logger.warning(f"⚠️ Error closing browser: {str(e)}")


# 🤖 Telegram Bot Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
👋 *Welcome to SIT Result Bot!*

🎓 Get your SIT exam results instantly!

📝 *How to use:*
Send your USN and Date of Birth in this format:
`1SI22CS082 07-09-2004`

📋 *Format:*
• USN: Your university seat number
• DOB: DD-MM-YYYY format

🔒 *Privacy:* Your data is not stored and is only used to fetch results.

💡 *Example:*
`1SI22CS082 07-09-2004`

🚀 Ready to get your results? Send your details now!
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
🆘 *SIT Result Bot Help*

📝 *Usage:*
Send: `USN DOB`
Example: `1SI22CS082 07-09-2004`

📋 *Format Requirements:*
• USN: Your university seat number
• DOB: DD-MM-YYYY format (Day-Month-Year)

❓ *Common Issues:*
• Make sure USN is correct
• Use DD-MM-YYYY format for date
• Check if you have results available
• Try again if portal is slow

🔄 *Commands:*
/start - Start the bot
/help - Show this help message

💬 *Need more help?* Contact your system administrator.
    """
    
    await update.message.reply_text(
        help_message,
        parse_mode="Markdown"
    )


async def handle_result_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle result fetch requests"""
    message_text = update.message.text.strip()
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    
    logger.info(f"📩 Request from user {user_id} in chat {chat_id}: {message_text}")
    
    try:
        # Parse input
        parts = message_text.split()
        if len(parts) != 2:
            await update.message.reply_text(
                "⚠️ *Invalid format!*\n\n"
                "Please send in this format:\n"
                "`USN DOB`\n\n"
                "Example: `1SI22CS082 07-09-2004`",
                parse_mode="Markdown"
            )
            return
        
        usn, dob = parts
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔍 *Fetching your results...*\n\n"
            "⏳ This may take 30-60 seconds\n"
            "🌐 Connecting to SIT portal...",
            parse_mode="Markdown"
        )
        
        # Fetch results
        result = fetch_sit_result(usn.upper(), dob)
        
        # Send result
        await processing_msg.edit_text(result, parse_mode="Markdown")
        
        logger.info(f"✅ Successfully processed request for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error handling request from user {user_id}: {str(e)}")
        await update.message.reply_text(
            "❌ *Error processing your request*\n\n"
            "Please check your format and try again:\n"
            "`USN DOB`\n\n"
            "Example: `1SI22CS082 07-09-2004`",
            parse_mode="Markdown"
        )


def main():
    """Main function to run the bot"""
    try:
        logger.info("🤖 Starting SIT Result Bot...")
        
        # Create application
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_result_request)
        )
        
        logger.info("✅ Bot handlers registered successfully")
        logger.info("🚀 SIT Result Bot is now running...")
        
        # Start polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {str(e)}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()