# from playwright.async_api import async_playwright
# import asyncio


# def html_converter(file_binary):
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch()
#             page = await browser.new_page()

#         #set html content into page
#         await page.set_content(file_binary)

#         #converted pdf
#         pdf_bytes=await page.pdf(format='A4')

#         #close the browser
#         await browser.close()
        
#         return pdf_bytes

#     except Exception as e:
#         return str(e)
