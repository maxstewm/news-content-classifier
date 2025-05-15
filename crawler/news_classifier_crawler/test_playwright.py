# test_playwright.py
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # 尝试启动浏览器
        try:
            browser = await p.chromium.launch(headless=True)
            print("Playwright browser launched successfully!")

            # 尝试访问一个页面
            page = await browser.new_page()
            test_url = "http://quotes.toscrape.com/" # 或者你目标网站的一个简单页面
            print(f"Navigating to {test_url}...")
            await page.goto(test_url)
            print(f"Navigated to {page.url}")

            # 打印页面标题作为验证
            title = await page.title()
            print(f"Page title: {title}")

            # 打印页面内容作为验证 (可选)
            # content = await page.content()
            # print(f"Page content snippet:\n{content[:500]}...") # 打印前500字符

            await browser.close()
            print("Browser closed.")

        except Exception as e:
            print(f"!!! An error occurred during Playwright test: {e}")

if __name__ == "__main__":
    asyncio.run(main())