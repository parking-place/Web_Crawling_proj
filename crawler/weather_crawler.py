import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import re
import asyncio
import aiohttp
import selenium 
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import time
import re
import sys

# url 설정
url = r'https://www.weatheri.co.kr/bygone/bygone01.php'
# user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
# headers = { 'User-Agent' : user_agent }
# 드라이버 경로 설정
driver_path = r'./browserdriver/msedgedriver112_64.exe'
# column name 설정
col_name = ['날짜', '평균기온', '최고기온', '최저기온', '강수량(mm)', '신적설(cm)', '평균풍속(m/s)', '운량(1/10)', '일조시간(hr)', '날씨']


s_date = (1967, 1, 1)
e_date = (2023, 4, 30)

# 출력을 새로고침 해주며 현재날짜 프린트
def print_current(s):
    sys.stdout.write('\r')
    sys.stdout.write('현재 처리중 : ' + s)
    sys.stdout.flush()

# 문자열로 된 날짜를 Timestamp로 변환
def get_time_in_str(date_str):
    y_p = re.compile(r'(\d{4})년')
    m_p = re.compile(r'(\d{1,2})월')
    d_p = re.compile(r'(\d{1,2})일')
    y = y_p.search(date_str).group(1)
    m = m_p.search(date_str).group(1)
    d = d_p.search(date_str).group(1)
    return pd.Timestamp(int(y), int(m), int(d))

# 문자열로 된 숫자를 float로 변환
def get_float_in_str(s):
    if s == '-':
        return 0.0
    else:
        return float(s)

# 웹드라이버 객체를 생성하는 함수
def get_browser(headless=True):
    service = Service(driver_path)
    # 웹드라이버 옵션 설정
    options = webdriver.EdgeOptions()   # EdgeOptions객체 생성
    if headless:
        options.add_argument('headless')    # headless 모드 설정 -> 화면이 안나옴
        options.add_argument("disable-gpu") # GPU 사용 안함

    # webdriver  객체를 만들 때 옵션을 설정
    browser = webdriver.Edge(service=service, options=options)
    
    return browser

# 날씨 데이터를 가져오는 함수
def get_weather_data(browser, s_date, e_date):
    # 날씨 데이터를 담을 딕셔너리 생성
    print_current('날씨 데이터를 담을 딕셔너리 생성')
    weather_data = {}
    for name in col_name:
        weather_data[name] = []
    # 웹드라이버 실행
    print_current('웹드라이버 실행')
    browser.get(url)
    # css selectors
    print_current('css selectors 설정')
    view_bnt_css = 'body > table > tbody > tr > td > form > table > tbody > tr > td > img'
    search_bnt_scc = r'body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(3) > table > tbody > tr:nth-child(2) > td > img'
    tbody_css = r'body > table > tbody > tr > td > form > table:nth-child(2) > tbody > tr > td > table > tbody'
    row_css = r'tr:nth-child({i})'
    # 행 내의 열별 셀렉터
    col_css = {}
    for i, name in enumerate(col_name):
        if i == 0:
            col_css[name] = r'td:nth-child({i}) > b'.format(i=i+1)
        else:
            col_css[name] = r'td:nth-child({i}) > font'.format(i=i+1)
    # 행별 데이터 처리 함수
    print_current('행별 데이터 처리 함수 설정')
    col_func = {}
    for name in col_name:
        if name == '날짜':
            col_func[name] = get_time_in_str
        elif name == '날씨':
            col_func[name] = lambda x: x
        else:
            col_func[name] = get_float_in_str
    
    # 날짜 셀렉터 찾기
    print_current('날짜 셀렉터 처리중')
    s_year_select = browser.find_element(by='name', value='s_year')
    s_month_select = browser.find_element(by='name', value='s_month')
    s_day_select = browser.find_element(by='name', value='s_day')

    e_year_select = browser.find_element(by='name', value='e_year')
    e_month_select = browser.find_element(by='name', value='e_month')
    e_day_select = browser.find_element(by='name', value='e_day')
    
    # 날짜 셀렉터에 시작 날짜 입력하기
    s_year_select.send_keys(s_date[0])
    if s_date[1] != 1:
        s_month_select.send_keys(s_date[1])
    if s_date[2] != 1:
        s_day_select.send_keys(s_date[2])
    # 날짜 셀렉터에 종료 날짜 입력하기
    e_year_select.send_keys(e_date[0])
    e_month_select.send_keys(e_date[1])
    e_day_select.send_keys(e_date[2])
    
    # 날짜선택 후 검색버튼 클릭
    print_current('검색')
    search_bnt = browser.find_element(by='css selector', value=search_bnt_scc)
    search_bnt.click()
    
    # iframe 객체를 찾아서 iframe으로 전환
    print_current('iframe 전환')
    kako_iframe = browser.find_element(by='name', value='kako')
    browser.switch_to.frame(kako_iframe)
    
    # 월별 셀렉터 찾기
    print_current('월별 셀렉터 설정')
    date_select = browser.find_element(by='name', value='start')
    # 월별 셀렉터에서 월별 날짜들 찾기
    starts = date_select.find_elements(by='tag name', value='option')
    # 월별 날짜들의 텍스트만 가져오기
    print_current('월별 텍스트 추출')
    starts = [start.text for start in starts]
    
    for start in starts:
        print_current(start)
        # 월별 셀렉터 찾기
        start_select = browser.find_element(by='name', value='start')
        # 월별 셀렉터에서 월 입력
        start_select.send_keys(start)
        # 월별 검색버튼 찾기
        view_bnt = browser.find_element(by='css selector', value=view_bnt_css)
        # 월별 검색버튼 클릭
        view_bnt.click()
        
        time.sleep(0.05)
        # 표 가져오기
        tbody = browser.find_element(by='css selector', value=tbody_css)
        tobdy_html = tbody.get_attribute('innerHTML')
        tbody_bs = bs(tobdy_html, 'lxml')
        # 각 행별로 데이터 가져오기
        for i in range(1, 32):
            # 행 가져오기
            row = tbody_bs.select_one(row_css.format(i=i+1))
            # 행이 없으면 다음 월로 넘어가기
            if row is None:
                break
            print_current(start + f' {i}일')
            # 각 열별로 데이터 가져오기
            for name in col_name:
                print_current(start + f' {i}일' + f' {name} 처리중')
                # 열 가져오기
                col = row.select_one(col_css[name])
                # 열의 데이터 가져오기 (열별로 함수 적용)
                col_data = col_func[name](col.text)
                # 열의 데이터를 딕셔너리에 추가
                weather_data[name].append(col_data)
    
    # 웹드라이버 종료
    browser.quit()
    # 2월 데이터 크롤링
    browser2 = get_browser()
    weather_data2 = get_2_data(browser2)
    # 전체 데이터에 2월 데이터 추가
    for name in col_name:
        weather_data[name] += weather_data2[name]
    
    print_current('데이터 크롤링 완료')
    # 완성된 날씨 데이터 반환
    return weather_data

# 날씨 데이터를 데이터프레임으로 변환하는 함수
def get_weather_df(weather_data):
    print_current('데이터프레임 생성')
    # 데이터프레임 생성
    weather_df = pd.DataFrame(weather_data)
    print_current('데이터프레임 생성 완료')
    # 날짜를 인덱스로 설정
    weather_df.set_index('날짜', inplace=True)
    # 날짜를 기준으로 정렬
    weather_df.sort_index(inplace=True)
    # 데이터프레임 반환
    return weather_df

# 날씨 데이터를 저장하는 함수
def save_weather_df(df, s_date, e_date, file_path='./data/'):
    print_current('데이터 저장중')
    # ./data/start_end_weather.csv 파일로 저장
    start_date = r'{y}{m:02d}{d:02d}'.format(y=s_date[0], m=s_date[1], d=s_date[2])
    end_date = r'{y}{m:02d}{d:02d}'.format(y=e_date[0], m=e_date[1], d=e_date[2])
    file_name = file_path + r'{start}_{end}_weather.csv'.format(start=start_date, end=end_date)
    df.to_csv(file_name, index=True)
    print_current('데이터 저장 완료')
    
# 날씨 데이터를 가져오는 함수
def load_weather_df(filename = '19670101_20230430_weather.csv', file_path='./data/'):
    print_current('데이터 불러오기')
    # ./data/start_end_weather.csv 파일 불러오기
    file_name = file_path + filename
    df = pd.read_csv(file_name, na_values=np.nan)
    print_current('데이터 불러오기 완료')
    # 날짜를 timestamp로 변환
    df['날짜'] = pd.to_datetime(df['날짜'])
    # 날짜를 인덱스로 설정
    df.set_index('날짜', inplace=True)
    return df

def get_2_data(browser):
    # 시작 날짜, 종료 날짜 설정
    s_date = (2023, 2, 1)
    e_date = (2023, 2, 28)
    # 날씨 데이터를 담을 딕셔너리 생성
    print_current('날씨 데이터를 담을 딕셔너리 생성')
    weather_data = {}
    for name in col_name:
        weather_data[name] = []
    # 웹드라이버 실행
    print_current('웹드라이버 실행')
    browser.get(url)
    # css selectors
    print_current('css selectors 설정')
    view_bnt_css = 'body > table > tbody > tr > td > form > table > tbody > tr > td > img'
    search_bnt_scc = r'body > table:nth-child(4) > tbody > tr:nth-child(3) > td:nth-child(3) > table > tbody > tr:nth-child(2) > td > img'
    tbody_css = r'body > table > tbody > tr > td > form > table:nth-child(2) > tbody > tr > td > table > tbody'
    row_css = r'tr:nth-child({i})'
    # 행 내의 열별 셀렉터
    col_css = {}
    for i, name in enumerate(col_name):
        if i == 0:
            col_css[name] = r'td:nth-child({i}) > b'.format(i=i+1)
        else:
            col_css[name] = r'td:nth-child({i}) > font'.format(i=i+1)
    # 행별 데이터 처리 함수
    print_current('행별 데이터 처리 함수 설정')
    col_func = {}
    for name in col_name:
        if name == '날짜':
            col_func[name] = get_time_in_str
        elif name == '날씨':
            col_func[name] = lambda x: x
        else:
            col_func[name] = get_float_in_str
    
    # 날짜 셀렉터 찾기
    print_current('날짜 셀렉터 처리중')
    s_year_select = browser.find_element(by='name', value='s_year')
    s_month_select = browser.find_element(by='name', value='s_month')
    s_day_select = browser.find_element(by='name', value='s_day')

    e_year_select = browser.find_element(by='name', value='e_year')
    e_month_select = browser.find_element(by='name', value='e_month')
    e_day_select = browser.find_element(by='name', value='e_day')
    
    # 날짜 셀렉터에 시작 날짜 입력하기
    s_year_select.send_keys(s_date[0])
    if s_date[1] != 1:
        s_month_select.send_keys(s_date[1])
    if s_date[2] != 1:
        s_day_select.send_keys(s_date[2])
    # 날짜 셀렉터에 종료 날짜 입력하기
    e_year_select.send_keys(e_date[0])
    e_month_select.send_keys(e_date[1])
    e_day_select.send_keys(e_date[2])
    time.sleep(.1)
    # 날짜선택 후 검색버튼 클릭
    print_current('검색')
    search_bnt = browser.find_element(by='css selector', value=search_bnt_scc)
    search_bnt.click()
    time.sleep(10)
    # iframe 객체를 찾아서 iframe으로 전환
    print_current('iframe 전환')
    kako_iframe = browser.find_element(by='name', value='kako')
    browser.switch_to.frame(kako_iframe)
    
    start = '2023년 2월'
    
    print_current(start)
    
    time.sleep(0.05)
    # 표 가져오기
    tbody = browser.find_element(by='css selector', value=tbody_css)
    tobdy_html = tbody.get_attribute('innerHTML')
    tbody_bs = bs(tobdy_html, 'lxml')
    # 각 행별로 데이터 가져오기
    for i in range(1, 32):
        # 행 가져오기
        row = tbody_bs.select_one(row_css.format(i=i+1))
        # 행이 없으면 다음 월로 넘어가기
        if row is None:
            break
        print_current(start + f' {i}일')
        # 각 열별로 데이터 가져오기
        for name in col_name:
            print_current(start + f' {i}일' + f' {name} 처리중')
            # 열 가져오기
            col = row.select_one(col_css[name])
            # 열의 데이터 가져오기 (열별로 함수 적용)
            col_data = col_func[name](col.text)
            # 열의 데이터를 딕셔너리에 추가
            weather_data[name].append(col_data)
    
    # 웹드라이버 종료
    browser.quit()
    
    print_current('데이터 크롤링 완료')
    # 완성된 날씨 데이터 반환
    return weather_data
