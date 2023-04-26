# 멜론 차트 크롤러
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
from pprint import pprint

def get_music_info(music : bs):
    music_info =[]
    music_info.append(int(music.select_one('span.rank').text))
    music_info.append(music.select_one('div.ellipsis.rank01 > span > a').text)
    music_info.append(music.select_one('div.ellipsis.rank02 > a').text)
    music_info.append(music.select_one('div.ellipsis.rank03 > a').text)
    return music_info

async def get_melon_chart(headers):
    melon_url = r'https://www.melon.com/chart/index.htm'
    
    music_infos = { 'rank' : [], 'title' : [], 'singer' : [], 'album' : [] } 
    
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.get(melon_url) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = bs(html, 'lxml')
                try:
                    musics = soup.select('div.service_list_song > table > tbody > tr')
                    for music in musics:
                        music_info = get_music_info(music)
                        music_infos['rank'].append(music_info[0])
                        music_infos['title'].append(music_info[1])
                        music_infos['singer'].append(music_info[2])
                        music_infos['album'].append(music_info[3])
                except Exception as e:
                    print(e, 'melon')
    return { 'melon' : music_infos }