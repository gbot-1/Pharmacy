# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os 
import shutil
import platform
import atexit

class HTMLToPNGConverter:
    def __init__(self, wait_time=5):
        self.wait_time = wait_time
        self.driver = None
        self.service = None
        self._setup_driver()
        # Register cleanup function to run when program exits
        atexit.register(self.cleanup)
    
    def _setup_driver(self):
        """Initialize Chrome driver once"""
        # Setting up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")
        
        try:
            # print("Setting up ChromeDriver...")
            
            # Clear existing problematic ChromeDriver cache
            cache_path = os.path.join(os.path.expanduser("~"), ".wdm")
            chrome_cache = os.path.join(cache_path, "drivers", "chromedriver")
            if os.path.exists(chrome_cache):
                print("Clearing existing ChromeDriver cache...")
                shutil.rmtree(chrome_cache)
            
            # Get driver path
            driver_path = self._get_driver_path()
            # print(f"Using ChromeDriver: {driver_path}")
            
            # Create service
            self.service = Service(executable_path=driver_path)
            
            # Initialize the driver once
            # print("Starting Chrome browser...")
            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
            
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise
    
    def _get_driver_path(self):
        """Get the correct ChromeDriver path"""
        if platform.machine().endswith('64'):
            driver_path = ChromeDriverManager().install()
            driver_dir = os.path.dirname(driver_path)
            actual_driver = os.path.join(driver_dir, "chromedriver.exe")
            
            if not os.path.exists(actual_driver):
                for root, dirs, files in os.walk(driver_dir):
                    if "chromedriver.exe" in files:
                        actual_driver = os.path.join(root, "chromedriver.exe")
                        break
            
            if not os.path.exists(actual_driver):
                raise Exception(f"ChromeDriver executable not found. Expected at: {actual_driver}")
            
            return actual_driver
        else:
            return ChromeDriverManager().install()
    
    def convert_single(self, html_file_path, output_png_path):
        """Convert a single HTML file to PNG"""
        try:
            if not self.driver:
                raise Exception("Driver not initialized")
            
            # print(f"Converting {html_file_path} to {output_png_path}")
            
            # Navigate to the HTML file
            self.driver.get("file://" + html_file_path)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for content to fully load
            # print(f"Waiting {self.wait_time} seconds for content to load...")
            time.sleep(self.wait_time)
            
            # Take screenshot
            self.driver.save_screenshot(output_png_path)
            print(f"Screenshot saved: {output_png_path}")
            
        except Exception as e:
            print(f"Error converting {html_file_path}: {e}")
            raise
    
    def convert_multiple(self, file_pairs):
        """
        Convert multiple HTML files to PNG
        file_pairs: list of tuples [(html_path, png_path), ...]
        """
        for html_path, png_path in file_pairs:
            self.convert_single(html_path, png_path)
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                print("Chrome driver closed.")
            except:
                pass

# Convenience functions for backwards compatibility
def save_svg_to_png(html_file_path, output_png_path, wait_time=5):
    """Single conversion function - creates and destroys driver each time"""
    converter = HTMLToPNGConverter(wait_time)
    try:
        converter.convert_single(html_file_path, output_png_path)
    finally:
        converter.cleanup()

def convert_multiple_html_to_png(file_pairs, wait_time=5):
    """
    Efficient batch conversion function
    file_pairs: list of tuples [(html_path, png_path), ...]
    """
    converter = HTMLToPNGConverter(wait_time)
    try:
        converter.convert_multiple(file_pairs)
    finally:
        converter.cleanup()