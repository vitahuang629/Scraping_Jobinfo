from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# 期待元素出現要透過什麼方式指定，通常與 EC、WebDriverWait 一起使用
from selenium.webdriver.common.by import By
# 加入行為鍊 ActionChain (在 WebDriver 中模擬滑鼠移動、點擊、拖曳、按右鍵出現選單，以及鍵盤輸入文字、按下鍵盤上的按鈕等)
from selenium.webdriver.common.action_chains import ActionChains
# 加入鍵盤功能 (例如 Ctrl、Alt 等)
from selenium.webdriver.common.keys import Keys
# 強制等待 (執行期間休息一下)
from time import sleep
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
today = datetime.now().strftime("%m/%d")
import re
import json


def get_job_data(keyword: str, area_param: str, current_page: int = 1):
    # 啟動瀏覽器工具的選項
    search_key = keyword
    my_options = webdriver.ChromeOptions()
    # my_options.add_argument("--headless") #不開啟實體瀏覽器背景執行
    my_options.add_argument("--start-maximized") #最大化視窗
    my_options.add_argument("--incognito") #開啟無痕模式
    my_options.add_argument("--disable-popup-blocking") #禁用彈出攔截
    my_options.add_argument("--disable-notifications") #取消通知
    my_options.add_argument("--auto-open-devtools-for-tabs")  
    # 使用 Chrome 的 WebDriver
    #my_service = Service(executable_path="./chromedriver.exe")
    driver = webdriver.Chrome(options = my_options)
    
    driver = webdriver.Chrome(options = my_options)
    driver.get("https://www.104.com.tw/jobs/search/?area=6001001000,6001002000&keyword=Data+scientist&mode=s&page=1&order=15")
    sleep(3)

    current_page = 1
    all_job_links = []  # 用來存放所有頁面的職位資料
    
    while current_page <=2:
        print(f"正在爬取第 {current_page} 頁的資料...")
        
        # 動態載入目前頁面的URL
        url = f"https://www.104.com.tw/jobs/search/?area={area_param}&keyword={keyword}&mode=s&page={current_page}&order=15"
        #url = "https://www.104.com.tw/jobs/search/?area=6001001000,6001002000&keyword=Data+scientist&mode=s&page=1&order=15"
        driver.get(url)
        sleep(3)
        try:
            # 等待按鈕可見且可點擊
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#app > div > div.header.bg-white.position-sticky.w-100 > div.header__tabs.position-relative.border-bottom.bg-white > div > div > div:nth-child(2) > div > div:nth-child(4) > button"))
            )
            # 點擊按鈕
            button.click()
            print("Button clicked successfully!")
        except Exception as e:
            print(f"Failed to click the button: {e}")
        sleep(3)  # 等待頁面加載完成
    
        try:
            # 抓取該頁的職位、地點、經驗等資訊
            job_elements = driver.find_elements(By.CSS_SELECTOR, "div.info.info-detailed > div > h2 > a")
            if not job_elements:  # 如果該頁無職位元素，停止爬取
                print("沒有更多資料，爬取結束！")
                break
            print(area_param)
            job_urls = [job.get_attribute('href') for job in job_elements]
            company_elements = driver.find_elements(By.CSS_SELECTOR, "div.info-company.font-weight-bold.mb-1.info-mode-summary > a")
            companies = [company.text for company in company_elements]
            location_elements = driver.find_elements(By.CSS_SELECTOR, "div.info-tags.mr-0.d-flex.flex-wrap > div:nth-child(1) > a")
            locations = [location.text for location in location_elements]
            experience_elements = driver.find_elements(By.CSS_SELECTOR, "div.info-tags.mr-0.d-flex.flex-wrap > div:nth-child(2) > a")
            experiences = [experience.text for experience in experience_elements]
            ed_experience_elements = driver.find_elements(By.CSS_SELECTOR, "div.info-tags.mr-0.d-flex.flex-wrap > div:nth-child(3) > a")
            ed_experiences = [ed_experience.text for ed_experience in ed_experience_elements]
            paid_elements = driver.find_elements(By.CSS_SELECTOR, "div.info-tags.mr-0.d-flex.flex-wrap > div:nth-child(4) > a")
            paids = [paid_elements.text for paid_elements in paid_elements]
            post_date_elements = driver.find_elements(By.CSS_SELECTOR, "div.job-mobile__date.mt-1.t4")
            post_dates = [post_date.text for post_date in post_date_elements]
            
            # 將本頁的職位資料一一整理並存入 all_job_links
            for i, job in enumerate(job_elements):
                #print(f"Adding job with keyword: {search_key}")
                job_name = job.text
                job_url = job.get_attribute('href')
                company_text = companies[i] if i < len(companies) else None
                location_text = locations[i] if i < len(locations) else None
                experience_text = experiences[i] if i < len(experiences) else None
                ed_experience_text = ed_experiences[i] if i < len(ed_experiences) else None
                paid_text = paids[i] if i < len(paids) else None
                post_date_text = post_dates[i] if i < len(post_dates) else None
                if post_date_text == today:
                    all_job_links.append({
                    "name": job_name,
                    "company_name": company_text,
                    "url": job_url,
                    "location": location_text,
                    "work_experience": experience_text,
                    "education_experience": ed_experience_text,
                    "paid": paid_text,
                    "posted_date": post_date_text
                })
            
            # 移動到下一頁
            current_page += 1
    
        except Exception as e:
            print(f"在第 {current_page} 頁爬取時發生錯誤：{e}")
            break
    
    all_job_links = [
        {**job, "id": re.search(r'job%2F(\w+)%', job['url']).group(1) if re.search(r'job%2F(\w+)%', job['url']) else None}
        for job in all_job_links
    ]
    all_job_links = [{**job, "search_key": search_key} for job in all_job_links]

    json_data = json.dumps(all_job_links, indent=4, ensure_ascii=False)

    return json_data
# 將結果轉換為DataFrame並保存
#job_detail = pd.DataFrame(all_job_links)
#job_detail['id'] = job_detail['url'].apply(lambda x: re.search(r'job%2F(\w+)%', x).group(1) if re.search(r'job%2F(\w+)%', x) else None)
#job_detail.to_csv("job_data.csv", index=False)
#print("所有頁面爬取完成，資料已保存到 job_data.csv")
