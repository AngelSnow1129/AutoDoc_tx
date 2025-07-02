# core/authenticator.py
import asyncio
from playwright.async_api import async_playwright
from PIL import Image
from pyzbar.pyzbar import decode
import pyotp
import os

async def initial_authentication(auth_file: str, qr_code_path: str = "qrcode.png"):
    """
    执行首次交互式认证流程。
    1. 启动一个有头浏览器，让用户手动登录。
    2. 截取2FA页面的QR码。
    3. 解码QR码以获取TOTP密钥。
    4. 提示用户将密钥存储为环境变量。
    5. 保存浏览器认证状态以供后续使用。
    """
    print("Starting first-time authentication...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("Please log in to Tencent Docs manually in the browser window.")
        print("After you log in and see the QR code for 2FA, please press Enter here.")
        await page.goto("https://docs.qq.com")

        input("Press Enter to continue after the QR code is visible...")

        # 假设QR码在一个可定位的元素中，实际选择器需要根据页面情况调整
        qr_element = page.locator("img[alt='Scan QR code']") # 这是一个假设的选择器
        if not await qr_element.is_visible():
            print("Could not find QR code element. Please adjust the selector in authenticator.py")
            await browser.close()
            return

        await qr_element.screenshot(path=qr_code_path)
        print(f"QR code saved to {qr_code_path}")

        # 解码QR码
        try:
            decoded_qr = decode(Image.open(qr_code_path))
            otp_uri = decoded_qr[0].data.decode("utf-8")
            totp_secret = otp_uri.split('secret=')[1].split('&')[0]
            print("Successfully decoded QR code.")
            print("IMPORTANT: Please save this TOTP secret as an environment variable 'TENCENT_TOTP_SECRET'")
            print(f"Your TOTP Secret: {totp_secret}")

            # 验证TOTP
            totp = pyotp.TOTP(totp_secret)
            verification_code = totp.now()
            print(f"Generated verification code: {verification_code}")
            # 此处需要用户在页面上手动输入验证码以完成登录

        except Exception as e:
            print(f"Failed to decode QR code or generate TOTP: {e}")
            await browser.close()
            return

        print("Once you have successfully logged in, press Enter to save the authentication state.")
        input("Press Enter to continue...")

        await context.storage_state(path=auth_file)
        print(f"Authentication state saved to {auth_file}. You can now run the main application.")
        await browser.close()

if __name__ == '__main__':
    # 运行此脚本以执行首次认证
    asyncio.run(initial_authentication("auth_state.json"))
