# 벅스 차트 크롤러
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
from pprint import pprint


def get_music_info(music : bs):
    music_info = []
    try:
        music_info.append(int(music.select_one('div.ranking > strong').text))
        music_info.append(music.select_one('p.title > a').text)
        music_info.append(music.select_one('p.artist > a').text)
        music_info.append(music.select_one('a.album').text)
        return music_info
    except Exception as e:
        print(e, 'bugs')

async def get_bugs_chart(headers):
    bugs_url = r'https://music.bugs.co.kr/chart'
    music_infos = { 'rank' : [], 'title' : [], 'singer' : [], 'album' : [] } 
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.get(bugs_url) as resp:
            if resp.status == 200:
                html = await resp.text()
                soup = bs(html, 'lxml')
                try:
                    musics = soup.select('table.list.trackList.byChart > tbody > tr')
                    for music in musics:
                        music_info = get_music_info(music)
                        music_infos['rank'].append(music_info[0])
                        music_infos['title'].append(music_info[1])
                        music_infos['singer'].append(music_info[2])
                        music_infos['album'].append(music_info[3])
                except Exception as e:
                    print(e, 'bugs')
    return { 'bugs' : music_infos }

if __name__ == '__main__':
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    headers = { 'User-Agent' : user_agent }
    chrat_dict = asyncio.run(get_bugs_chart(headers=headers))
    print(chrat_dict)