import time
import requests
import calendar

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager


def get_2012_table():
    dropdown = browser.find_element_by_name('year')
    select = Select(dropdown)
    idx_2012 = 10
    select.select_by_index(idx_2012) 
    

def get_target_month_table(month):
    dropdown = browser.find_element_by_name('month')
    select = Select(dropdown)
    idx_month = month - 1
    select.select_by_index(idx_month)
    inputbox = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]/input')
    inputbox.click()  


def move_next_day(day):
    dropdown = browser.find_element_by_name('day')
    select = Select(dropdown)
    select.select_by_index(day)
    inputbox = browser.find_element_by_xpath('/html/body/div[3]/div[2]/table/tbody/tr/td[2]/table/tbody/tr[1]/td[2]/input')
    inputbox.click()


def get_temperature_1day(UTC, num_times):
    dic={}
    for i in UTC:
        for time in range(num_times):
            try:
                td = browser.find_element_by_xpath(f'/html/body/div[3]/div[2]/table/tbody/tr/td[4]/table[3]/tbody/tr[{str(time)}]/td[3]')
                utc = browser.find_element_by_xpath(f'/html/body/div[3]/div[2]/table/tbody/tr/td[4]/table[3]/tbody/tr[{str(time)}]/td[1]')
                
                if i == str(utc.text):
                    dic[i] = int(td.text)
                    break

            except: 
                dic[i] = None

    return pd.DataFrame(dic, index=[1]).T


def interpolate_missing(df):
    list_1=[]
    for i,vals in df.iteritems():
        for val in vals:
            list_1.append(val)
    df2 = pd.DataFrame(list_1)
    df2 = df2.interpolate(limit=None, limit_direction='both')
    df2 = df2.values.reshape(df.T.shape)
    df2 = pd.DataFrame(df2).T
    df2.index += 1
    return df2


def arrange_temps_by_day(temps_1month, month):    
    num_days = calendar.monthrange(2012, month)[1]
    separator = 46 if month in [1, 2, 11, 12] else 44
    
    temps_1month_nextday = temps_1month[separator:]
    temps_1month_nextday = temps_1month_nextday.drop(columns=num_days)

    temps_1month_nextday["0"] = None

    temps_1month_nextday = temps_1month_nextday.reindex(columns=[i for i in range(num_days)])
    temps_1month_nextday.columns = temps_1month_nextday.columns + 1

    temps_1month = pd.concat([temps_1month_nextday, temps_1month], axis=0)
    temps_1month = temps_1month[:48]
    
    return temps_1month


def get_temperature_1month(month):
    num_days = calendar.monthrange(2012, month)[1]
    num_times = 50
    UTC_11_2 = ["01:20","01:50","02:20","02:50","03:20","03:50",
                "04:20","04:50","05:20","05:50","06:20","06:50",
                "07:20","07:50","08:20","08:50","09:20","09:50",
                "10:20","10:50","11:20","11:50","12:20","12:50",
                "13:20","13:50","14:20","14:50","15:20","15:50",
                "16:20","16:50","17:20","17:50","18:20","18:50",
                "19:20","19:50","20:20","20:50","21:20","21:50",
                "22:20","22:50","23:20","23:50","00:20","00:50"]
    
    UTC_5_10 = ["02:20","02:50","03:20","03:50","04:20","04:50",
                "05:20","05:50","06:20","06:50","07:20","07:50",
                "08:20","08:50","09:20","09:50","10:20","10:50",
                "11:20","11:50","12:20","12:50","13:20","13:50",
                "14:20","14:50","15:20","15:50","16:20","16:50",
                "17:20","17:50","18:20","18:50","19:20","19:50",
                "20:20","20:50","21:20","21:50","22:20","22:50",
                "23:20","23:50","00:20","00:50","01:20","01:50"]
    
    UTC = UTC_11_2 if month in [1, 2, 11, 12] else UTC_5_10

    temps_1month = {}
    for day in range(num_days):
        # 1日進める
        move_next_day(day)

        # 時間毎に気温を取得する
        temp_1day = get_temperature_1day(UTC, num_times)

        # 日にち毎に気温をdictに保存する
        temps_1month[day+1] = temp_1day.values.reshape(48,)
        
        
    return pd.DataFrame(temps_1month)


if __name__ == "__main__":
    path = "/home/higuchi-lab/.wdm/drivers/chromedriver/linux64/98.0.4758.102/chromedriver"
    url = "http://www.eurometeo.com/english/condition/city_LSZH/archive_select/meteo_Zurich"

    browser = webdriver.Chrome(executable_path=path)
    browser.get(url)

    get_2012_table()
    get_target_month_table(month=1)

    temps_1month = get_temperature_1month(month=1)
    temps_1month = arrange_temps_by_day(temps_1month, month=1)
    temps_1month = interpolate_missing(temps_1month)
    temps_1month.to_csv("temp1.csv", index=False)




