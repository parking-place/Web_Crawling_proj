# 메인

import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
from pprint import pprint
import pandas as pd
from datetime import datetime
import time
import os
from crawler.genie_crawler import get_genie_chart
from crawler.bugs_crawler import get_bugs_chart
from crawler.melon_crawler import get_melon_chart

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
headers = { 'User-Agent' : user_agent }

crawlers = [get_bugs_chart, get_genie_chart, get_melon_chart]

async def main():
    global headers
    music_charts_l = await asyncio.gather(*[crawler(headers) for crawler in crawlers])
    music_charts = dict()
    for chart in music_charts_l:
        # print(chart)
        music_charts.update(chart)
    return music_charts

def save_to_csv(site, chart_df):
    d = datetime.now().strftime('%Y-%m-%d-%H')
    file_path = r'./data'
    file_name = r'{}/{}_{}.csv'
    os.makedirs(file_path, exist_ok=True)
    chart_df.to_csv(file_name.format(file_path, d, site), encoding='utf-8-sig', index=False)

if __name__ == '__main__':
    start = time.time()
    charts_dict = asyncio.run(main())
    end = time.time()
    
    
    
    for site, chart_dict in charts_dict.items():
        chart_df = pd.DataFrame(chart_dict)
        chart_df.sort_values('rank', inplace=True)
        chart_df = chart_df[:100]
        save_to_csv(site, chart_df)

    print('time : {:.2f} sec'.format(end-start))