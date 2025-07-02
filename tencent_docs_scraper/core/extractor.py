# core/extractor.py
import asyncio
from playwright.async_api import async_playwright, Page, Response
import pandas as pd

# 假设目标API端点包含 'api/get_sheet_data'
TARGET_API_ENDPOINT = "api/get_sheet_data"
captured_data = None

async def handle_response(response: Response):
    """监听并捕获包含表格数据的API响应"""
    global captured_data
    if TARGET_API_ENDPOINT in response.url and response.request.method == 'POST':
        print(f"Captured data from: {response.url}")
        try:
            captured_data = await response.json()
        except Exception as e:
            print(f"Error parsing JSON from response: {e}")

async def fetch_sheet_data(url: str, auth_file: str) -> pd.DataFrame:
    """
    启动Playwright，使用认证状态访问腾讯文档，并拦截API获取数据。
    """
    global captured_data
    captured_data = None  # 重置捕获的数据

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=auth_file)
        page = await context.new_page()

        # 注册响应监听器
        page.on("response", handle_response)

        await page.goto(url, wait_until="networkidle")

        # 在这里可以添加一些操作来触发数据加载，如果需要的话
        # 例如：await page.get_by_text("Sheet2").click()
        # 等待数据被捕获，设置一个超时
        for _ in range(10): # 等待最多10秒
            if captured_data:
                break
            await asyncio.sleep(1)

        await browser.close()

        if captured_data:
            # 使用json_normalize处理可能嵌套的JSON
            # 这里的 'data.records' 是一个假设的路径，需要根据实际API响应调整
            try:
                df = pd.json_normalize(captured_data['data']['records'])
                return df
            except KeyError as e:
                print(f"JSON structure unexpected. Key not found: {e}")
                return pd.DataFrame() # 返回空DataFrame
        else:
            print("Failed to capture target API response.")
            return pd.DataFrame()
