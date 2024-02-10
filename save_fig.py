# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

def save_svg_to_png(html_file_path, output_png_path):
    # Setting up Chrome options for headless mode (no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    # Setting up Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Load the HTML file
    driver.get("file://" + html_file_path)

    # Wait for the map to load completely. Adjust the time as necessary.
    time.sleep(3)  # Adjust this depending on the load time of your map

    # Save screenshot as PNG
    driver.save_screenshot(output_png_path)

    # Close the browser
    driver.quit()

# # Import necessary libraries for Selenium
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# def save_svg_to_png(html_file_path, output_png_path):
#     # Setting up Chrome options for headless mode
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--window-size=1920x1080")
#     # Other options as needed
    
#     # Setting up Chrome WebDriver
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

#     # Load the HTML file
#     driver.get("file://" + html_file_path)

#     # Efficiently wait for the SVG to load
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))

#     # Save screenshot as PNG
#     driver.save_screenshot(output_png_path)

#     # Close the browser
#     driver.quit()