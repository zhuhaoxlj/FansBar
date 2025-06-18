import time
 
from DrissionPage import ChromiumPage
 
page = ChromiumPage()
page.get('https://www.baidu.com')
print(page.html)
time.sleep(5)
page.quit()