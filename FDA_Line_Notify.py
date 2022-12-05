#!/usr/bin/env python
# coding: utf-8

# In[2]:


#line bot 平行抓取ver.
import concurrent.futures
import requests
from bs4 import BeautifulSoup
from datetime import date
import datetime
kw_list = ['公告','修正','預告','訂定']
list2 = []
list_set = [] #除去重複的標題
raw = {} #抓取標題、網址、日期


def scrape(kw_list):
    list1 = []
    today = date.today()
    oneday=datetime.timedelta(days=1) 
    yesterday=today-oneday
    y = today.year
    try:
        url = f'https://www.fda.gov.tw/TC/news.aspx?cid=3&y={y}&key={kw_list}&scid=01'
        req = requests.get(url)
        soup = BeautifulSoup(req.text,'html.parser')
        sel = soup.select('tr')

        for i in range(1,2):
            url = f'https://www.fda.gov.tw/TC/news.aspx?cid=3&y={y}&key={kw_list}&scid=01&pn={i}'
            req = requests.get(url)
            soup = BeautifulSoup(req.text,'html.parser')
            sel = soup.select('tr')
            date_all = soup.find_all('td',"'alignCenter'")
            #print(len(sel))
            for j in range(1,(len(sel)-1)*2,2):
                list1.append(date_all[j].text)
            for k in sel:                
                try:
                    index = k.find('td',"'alignCenter'").text
                    title = k.find('a').text
                    href = k.find('a')['href']
                    #index超過10
                    date1 = list1[int(index)-1]
                    if date1 == str(yesterday):#抓取前一天資料
                        raw = {'title':title,'href':f'https://www.fda.gov.tw/TC/{href}','date':date1}
                        list_set.append(raw)          
                   
                except:
                    pass
        
    except:
        print('目前並無相關資料')
    
    return list_set
        
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor: #平行處理
    results = executor.map(scrape,kw_list)
    
    
#print(max(result),len(max(result)))

result = max(results)


list2 = [dict(t) for t in {tuple(d.items()) for d in result}] #刪除重複標題

for i in list2: #寄送Line通知
    #print(f"【{i[date]}】{i[title]},{i[href]}")
    headers = {
        "Authorization": "Bearer " + "Line憑證",
        "Content-Type": "application/x-www-form-urlencoded"}
    params = {"message":f"【{i['date']}】{i['title']},{i['href']}"}
    r = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, params=params)
    print(r.status_code)  #200              





