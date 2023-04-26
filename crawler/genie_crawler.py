# 지니뮤직 차트 크롤러
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
from pprint import pprint



def get_music_info(music : bs):
    music_info =[]
    try:
        music_info.append(int(music.select_one('td.number').text.split('\n')[0].strip()))
        music_info.append(music.select_one('td.info > a.title.ellipsis').text.strip())
        music_info.append(music.select_one('td.info > a.artist.ellipsis').text)
        music_info.append(music.select_one('td.info > a.albumtitle.ellipsis').text)
        return music_info
    except Exception as e:
        print(e, music)

async def get_genie_musics_in_page(url, sess):
    music_infos = { 'rank' : [], 'title' : [], 'singer' : [], 'album' : [] } 
    async with sess.get(url) as resp:
        if resp.status == 200:
            html = await resp.text()
            soup = bs(html, 'lxml')
            try:
                musics = soup.select('tbody > tr.list')
                for music in musics:
                    music_info = get_music_info(music)
                    music_infos['rank'].append(music_info[0])
                    music_infos['title'].append(music_info[1])
                    music_infos['singer'].append(music_info[2])
                    music_infos['album'].append(music_info[3])
            except Exception as e:
                print(e, 'genie')
    return music_infos

async def get_genie_chart(headers):
    genie_base_url = r'https://www.genie.co.kr/chart/top200?ditc=D&ymd=20230426&hh=09&rtm=Y&pg={}'
    music_infos = { 'rank' : [], 'title' : [], 'singer' : [], 'album' : [] } 
    urls = [genie_base_url.format(i) for i in range(1, 5)]
    async with aiohttp.ClientSession(headers=headers) as sess:
        music_infos_l = await asyncio.gather(*[get_genie_musics_in_page(url, sess) for url in urls])
    
    for music_infos_d in music_infos_l:
        for key in music_infos.keys():
            music_infos[key].extend(music_infos_d[key])
    
    return { 'genie': music_infos }