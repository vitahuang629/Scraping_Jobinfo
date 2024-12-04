import json
import streamlit as st
from scraping_104 import get_job_data  # 假設這是你的爬取函數

# 設定頁面標題
st.title('Job Search')

# 在側邊欄獲取搜尋條件
keyword = st.text_input('Enter job keyword', 'Data Scientist')  # 預設為 "Data Scientist"
current_page = st.number_input('Page number', min_value=1, value=1)

# 按鈕觸發爬取職缺資料
if st.button('Search'):
    if keyword:
        st.write(f"Searching for '{keyword}' on page {current_page}...")
        
        # 呼叫爬取函數並確保返回的資料是字典格式
        job_data = get_job_data(keyword, current_page)
        
        # 如果返回的資料是 JSON 字符串，則需要解析它
        if isinstance(job_data, str):
            job_data = json.loads(job_data)  # 解析 JSON 字符串為字典

        # 顯示搜尋結果
        if job_data:
            st.write(f"Found {len(job_data)} jobs:")
            for job in job_data:
                # 確保 job 是字典，並且有 'name' 等關鍵字段
                if isinstance(job, dict):
                    st.write(f"**{job.get('name', 'No Name')}**")
                    st.write(f"Company: {job.get('company_name', 'N/A')}")
                    st.write(f"Location: {job.get('location', 'N/A')}")
                    st.write(f"Experience: {job.get('work_experience', 'N/A')}")
                    st.write(f"Education: {job.get('education_experience', 'N/A')}")
                    st.write(f"Salary: {job.get('paid', 'N/A')}")
                    st.write(f"Posted on: {job.get('posted_date', 'N/A')}")
                    st.write(f"[Job link]({job.get('url', '#')})")
                    st.write("---")
                else:
                    st.write("Invalid job data format.")
        else:
            st.write("No jobs found.")
    else:
        st.warning("Please enter a keyword.")