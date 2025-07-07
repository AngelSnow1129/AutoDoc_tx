
import os
import sys
import pytest
from bs4 import BeautifulSoup
import pandas as pd

# 将 scraper.py 的路径添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper import extract_data_from_html

@pytest.fixture
def sample_html():
    """
    提供一个 HTML 示例用于测试。
    """
    # 直接返回一个包含 HTML 内容的字符串
    return """
    <html>
        <body>
            <div class="table-row">
                <div class="cell-text">Row 1, Col 1</div>
                <div class="cell-text">Row 1, Col 2</div>
            </div>
            <div class="table-row">
                <div class="cell-text">Row 2, Col 1</div>
                <div class="cell-text">Row 2, Col 2</div>
            </div>
        </body>
    </html>
    """

def test_extract_data_from_html(sample_html):
    """
    测试从 HTML 中提取数据的函数。
    """
    # 调用待测试的函数
    table_data = extract_data_from_html(sample_html)
    
    # 定义预期结果
    expected_data = [
        ["Row 1, Col 1", "Row 1, Col 2"],
        ["Row 2, Col 1", "Row 2, Col 2"]
    ]
    
    # 断言结果是否符合预期
    assert table_data == expected_data

def test_extract_data_from_real_html():
    """
    使用真实的 HTML 文件进行测试。
    """
    # 定义 HTML 文件的路径
    html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../docs/page_source.html'))
    
    # 检查 HTML 文件是否存在
    if not os.path.exists(html_file_path):
        pytest.skip(f"HTML file not found at {html_file_path}")
    
    # 读取 HTML 文件内容
    with open(html_file_path, 'r', encoding='utf-8') as f:
        page_source = f.read()
    
    # 调用待测试的函数
    table_data = extract_data_from_html(page_source)
    
    # 在这里，我们只检查是否成功提取了数据，而不检查具体内容
    assert isinstance(table_data, list)
    assert len(table_data) > 0

    # 如果需要，可以打印提取的数据以进行手动验证
    # print(pd.DataFrame(table_data))
