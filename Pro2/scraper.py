# Pro2/scraper.py

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

# 定义目标 URL 和输出文件路径
TARGET_URL = "https://zh.wikipedia.org/wiki/%E5%90%84%E5%9B%BD%E4%BA%BA%E5%8F%A3%E5%88%97%E8%A1%A8"
OUTPUT_DIR = "docs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "population_data.csv")

def extract_population_data() -> pd.DataFrame:
    """
    使用 Selenium 控制浏览器，从维基百科页面提取人口数据表格。
    """
    # 配置 WebDriver (使用无头模式，不在屏幕上显示浏览器窗口)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 初始化 WebDriver
    with webdriver.Chrome(options=options) as driver:
        print(f"正在访问目标 URL: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        table_data = []
        headers = []
        
        try:
            # 打印页面标题用于调试
            print(f"页面标题: {driver.title}")

            # 使用更稳定和具体的 XPath 选择器来定位表格
            # 这个 XPath 选择了页面上第一个 class 包含 'wikitable' 的表格
            table_locator = (By.XPATH, "(//table[contains(@class, 'wikitable')])[1]")
            table = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(table_locator)
            )
            
            print("成功定位到数据表格，开始提取内容...")
            
            # 提取表头 (th 标签)
            header_elements = table.find_elements(By.TAG_NAME, "th")
            headers = [header.text.strip() for header in header_elements]
            
            # 提取所有数据行 (tr 标签)
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # 遍历每一行，提取单元格数据 (td 标签)
            for row in rows[1:]: # 跳过表头行
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    table_data.append(row_data)

        except TimeoutException:
            print("错误：等待页面或表格元素加载超时。")
            # 保存页面源代码以供调试
            page_source_path = os.path.join(OUTPUT_DIR, "page_source.html")
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"页面源代码已保存到: {page_source_path}")
            return pd.DataFrame()
            
        except Exception as e:
            print(f"提取过程中发生错误: {e}")
            return pd.DataFrame()

    if table_data:
        print(f"成功提取 {len(table_data)} 行数据。")
        # 创建 DataFrame
        df = pd.DataFrame(table_data, columns=headers[:len(table_data[0])]) # 确保列数匹配
        return df
    else:
        print("未能提取到任何数据。")
        return pd.DataFrame()

def save_to_csv(df: pd.DataFrame, path: str):
    """将 DataFrame 保存到 CSV 文件。"""
    if df.empty:
        print("数据为空，不执行保存操作。")
        return
    
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False, encoding='utf-8-sig')
        print(f"数据已成功保存到: {path}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

if __name__ == "__main__":
    # 执行数据提取
    population_df = extract_population_data()
    
    # 保存结果
    save_to_csv(population_df, OUTPUT_FILE)
