# tencent_docs_scraper2/scraper.py

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import os
import time
import tempfile
import shutil

# 定义目标 URL 和输出文件路径
TARGET_URL = "https://docs.qq.com/sheet/DUEZCeEhLc2pZeHBR?tab=uubkzq"
OUTPUT_DIR = "docs"
HTML_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "page_source.html")
CSV_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "tencent_sheet_data.csv")

# 定义二进制文件路径
CHROME_BINARY_PATH = os.path.abspath("../bin/chrome-headless-shell-linux64/chrome-headless-shell")
CHROMEDRIVER_BINARY_PATH = os.path.abspath("../bin/chromedriver-linux64/chromedriver")

def extract_data_from_html(page_source):
    """
    从 HTML 源代码中提取表格数据。
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    table_data = []
    
    # 查找所有可能的行元素
    rows = soup.find_all('div', class_=lambda x: x and ('row' in x or 'table-row' in x))

    for row in rows:
        # 查找行内所有可能的单元格元素
        cells = row.find_all('div', class_=lambda x: x and ('cell' in x or 'cell-text' in x))
        
        # 提取单元格文本
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        
        # 只有在行内有内容时才添加到结果中
        if any(cell_texts):
            table_data.append(cell_texts)
            
    return table_data

def get_sheet_data(target_url, output_dir, html_output_file, csv_output_file):
    """
    使用指定的 Chrome 和 Chromedriver 访问腾讯文档页面，
    提取表格数据并保存为 CSV 文件。
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'")
    options.binary_location = CHROME_BINARY_PATH
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    service = Service(executable_path=CHROMEDRIVER_BINARY_PATH)
    
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        print(f"正在访问目标 URL: {target_url}")
        driver.get(target_url)
        
        print("等待页面加载...")
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "sheet-container"))
        )
        time.sleep(30)

        # 模拟滚动以加载更多内容
        print("模拟滚动页面...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10) # 再次等待内容加载

        print("页面加载完成，正在提取表格内容...")
        page_source = driver.page_source
        
        try:
            tables = pd.read_html(page_source)
            df = tables[0]
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(csv_output_file, index=False, header=False, encoding='utf-8-sig')
            print(f"数据已成功提取并保存到: {csv_output_file}")
        except ValueError:
            print("警告：未能使用 pandas.read_html 提取到任何表格数据。将尝试使用 BeautifulSoup。")
            table_data = extract_data_from_html(page_source)

            if not table_data:
                print("警告：未能提取到任何表格数据。")
                os.makedirs(output_dir, exist_ok=True)
                with open(html_output_file, "w", encoding="utf-8") as f:
                    f.write(page_source)
                print(f"HTML 源代码已保存到: {html_output_file}")
                return

            df = pd.DataFrame(table_data)
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(csv_output_file, index=False, header=False, encoding='utf-8-sig')
            print(f"数据已成功提取并保存到: {csv_output_file}")

    except TimeoutException:
        print("错误：等待页面加载超时。")
        if driver:
            os.makedirs(output_dir, exist_ok=True)
            with open(html_output_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"HTML 源代码已保存到: {html_output_file}")
            for entry in driver.get_log('performance'):
                print(entry)
    except Exception as e:
        print(f"处理页面时发生错误: {e}")
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    get_sheet_data(TARGET_URL, OUTPUT_DIR, HTML_OUTPUT_FILE, CSV_OUTPUT_FILE)
