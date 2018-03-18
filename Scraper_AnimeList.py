#! /usr/bin/python3

import webkit_server
import dryscrape
from lxml import html, etree
import sys
import os
from time import sleep
import re
import subprocess
import json

class Session(object):

    def __init__(self, object):

        self.server = webkit_server.Server()
        server_conn = webkit_server.ServerConnection(server=self.server)
        driver = dryscrape.driver.webkit.Driver(connection=server_conn)

        self.browser = dryscrape.Session(base_url = "https://otakustream.tv", driver = driver)
        self.browser.set_attribute('auto_load_images', False)

        self.browser.visit(object)

        self.root = html.fromstring(self.browser.body())

    def getName(self):

        nameNode = self.root.xpath('/html/body/div[2]/div[3]/div/div/div[1]/div/div/article/div[1]/header/h1')
        name = nameNode[0].text
        self.server.kill()
        return name

    def getAnimeFromDaPage(self):

        animeNode = self.root.xpath('/html/body/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]')
        output = []
        for x in animeNode[0]:
            link = x.xpath('./div[1]/div/div[1]/a')
            if not link:
                link = x.xpath('./div[1]/div/i/div[1]/a')
                if not link:
                    link = x.xpath('./div[1]/div/strong/div[1]/a')
            link = link[0]
            output.append(link.get('href'))
        self.server.kill()
        return output


    def getLastPage(self):

        link = self.root.xpath('/html/body/div[2]/div[2]/div/div/div[1]/div/div[3]/div[2]/nav/div/a[9]')
        self.server.kill()
        return link[0].get('href')



def getPageAnime(i):

    if not os.path.exists(baseFolder + '/temp/page' + str(i) + '.json'):

        print("\nPage " + str(i) + ":")

        a = Session(object = "https://otakustream.tv/anime/page/" + str(i) + "/")
        animeLinks = a.getAnimeFromDaPage()

        counter = open(baseFolder + '/temp/counter.txt', 'r')
        base = int(counter.readline())
        counter.close()

        page = {}
        for x in animeLinks:
            print("\n    " + x)
            sleep(3)

            animeSession = Session(object = x)
            animeInfo = animeSession.getName()

            info = animeInfo.split(" (")
            if len(info) > 1:
                animeName = info[0]
                seasonInfo = (info[-1].replace(")","")).split(" ")
                animeSeason = seasonInfo[1]
            else:
                animeName = info[0]
                animeSeason = "1"

            print("        " + animeName)
            print("        " + animeSeason)
                   
            file = str(animeName + 'season ' + str(animeSeason) + '.json')

            number = len(page) + int(base)
            if number < 10:
                number = "0" + str(number)

            ciao = {str(number): {'info': {'name': animeName,  'season': animeSeason}, 'anime_link': str(x)}}

            page = {**page,**ciao}


        #salvare in counter il numero a cui si è arrivato
        counter = open(baseFolder + '/temp/counter.txt', 'w')
        counter.seek(0)
        counter.truncate()
        counter.write(str(int(base + len(page))))
        counter.close()


        with open(baseFolder + '/temp/page' + str(i) + '.json', 'w+') as f:
            json.dump(page, f, indent = 4, sort_keys = True)
            f.close()

    else:
        print("\n!! page " + str(i) + " already scraped !!")    







baseFolder = '/home/lykos/Documents/Python'

if not os.path.exists(baseFolder + '/temp'):
    os.makedirs(baseFolder + '/temp')

if not os.path.exists(baseFolder + '/temp/counter.txt'):
    os.mknod(baseFolder + '/temp/counter.txt')
    counter = open(baseFolder + '/temp/counter.txt', 'w')
    counter.write('0')
    counter.close()


a = Session(object = "https://otakustream.tv/anime/")
print('session initialized')
sleep(5)

lastPageLink = a.getLastPage()
lastPageLink = lastPageLink.split("/")
lastPageNum = lastPageLink[-2]
print('Total Pages:' + lastPageNum)

for i in range(1,(int(lastPageNum)+1)):
    print('\n******************************************')
    try:
        getPageAnime(i = i)
    except webkit_server.EndOfStreamError:
        print("End of Stream Error! Retry...")
        getPageAnime(i = i)
    except webkit_server.InvalidResponseError:
        print("Invalid Response Error! Retry...")
        getPageAnime(i = i)


finaljson = {}
for i in range(1,(int(lastPageNum)+1)):
    with open(baseFolder + '/temp/page' + str(i) + '.json', 'r') as x:
        jsonpage = json.load(x)
        x.close()

    finaljson = {**finaljson,**jsonpage}



with open(baseFolder + '/animelist.json', 'w+') as f:
    json.dump(finaljson, f, indent = 4, sort_keys = True)
    f.close()

