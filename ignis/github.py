import requests
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from PIL import Image

load_dotenv()

def get_cover(url):
    image = requests.get(url).content
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options) if os.getenv("ENVIRONMENT") == 'development' else webdriver.Firefox(options=firefox_options)

    driver.get(url)
    try:
        # take screenshot of page - 1280x640
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'svg'))
        )
        driver.set_window_size(1280, 640)
        image = driver.get_screenshot_as_png()
    finally:
        driver.quit()

    # resize image to 640x320
    image = Image.open(BytesIO(image))
    image = image.resize((640, 320))
    output = BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()
