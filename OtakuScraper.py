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

class CreateSession(object):

    def __init__(self, object):

        self.server = webkit_server.Server()
        server_conn = webkit_server.ServerConnection(server=self.server)
        driver = dryscrape.driver.webkit.Driver(connection=server_conn)

        self.baseUrl = "https://otakustream.tv"
        self.browser = dryscrape.Session(base_url = self.baseUrl, driver = driver)
        self.browser.set_attribute('auto_load_images', False)
        self.browser.set_attribute('javascript_can_open_windows', False)
        self.browser.set_attribute('plugins_enabled', False)

        x = object.split("/")
        a = x.index("otakustream.tv")
        del x[0:a+1]
        epPage = '/'.join(x)
        epPage = "/" + epPage

        self.browser.visit(epPage)

    def getRoot(self):

        return html.fromstring(self.browser.body())

    def getName(self, root):

        nameNode = root.xpath('/html/body/div[2]/div[3]/div/div/div[1]/div/div/article/div[1]/header/h1')
        name = nameNode[0].text
        return name


    def getCards(self, root):

        div = root.xpath("//*[@id='accordion']")
        cards = []
        for child in div:
            x = child
            for child in x:
                cards.append(child)
        return cards

    def getEpisodeList(self, card):

        episodeList = []
        placeHolder = card
        button = self.browser.at_xpath('//*[@id="load_more_episodes"]')
        if button is not None:
            sleep(3)
            button = self.browser.at_xpath('/html/body/div[3]/div/div/div[1]/button')
            button.click()
            button = self.browser.at_xpath('//*[@id="load_more_episodes"]')
            button.click()
            print("loading full episode list...")
            sleep(3)
            root = self.getRoot()
            newCards = self.getCards(root = root)
            placeHolder = newCards[0]

        ul = placeHolder.find('.//ul')
        allow = True
        for link in ul.iter('li'):
            if link.find('a') is None:
                episodeList.append("None")
                allow = False
            else:
                episodeList.append(link.find('a').get('href'))

        if allow:
            episodeList = self.removeDuplicates(listx = episodeList)

        self.server.kill()
        return episodeList

    def removeDuplicates(self, listx):

        output = []
        seen = set()
        for x in listx:
            if x not in seen:
                output.append(x)
                seen.add(x)
        return output

    def getEpisodeLink(self):
        
        frame = self.browser.at_xpath("/html/body/div[2]/div[3]/div/div/div/div/div[1]/article/div/div[3]/div[1]/div/div/iframe")
        if frame is None:
            frame = self.browser.at_xpath('/html/body/div[2]/div[3]/div/div/div/div/div[1]/article/div/div[3]/div[1]/div/iframe')
        frame = frame['src'].replace("%3A",":")
        frame = frame.replace("%2F","/")

        x = subprocess.getoutput("curl " + self.baseUrl + frame)
        links = re.findall('"((http|ftp)s?://.*?)"', x)

        rvLink = None
        linkType = None
        for x in links:
            x = str(x)
            splitted1 = x.split(",")
            splitted2 = splitted1[0].split("'")
            if rvLink is None:
                if "rapidvideo" in splitted2[1]:
                    linkType = "rapidvideo"
                    rvLink = splitted2[1]
                elif "openload" in splitted2[1]:
                    linkType = "oload"
                    rvLink = splitted2[1]

        print(rvLink)

        if linkType == "rapidvideo":
            return self.rapidVideoHandler(rvLink = rvLink)
        elif linkType == "oload":
            return self.oLoadHandler(rvLink = rvLink)
        else:
            return "None"

        self.server.kill()

    def rapidVideoHandler(self, rvLink):

        self.server.kill()
        self.server = webkit_server.Server()
        server_conn = webkit_server.ServerConnection(server=self.server)
        driver = dryscrape.driver.webkit.Driver(connection=server_conn)

        browser2 = dryscrape.Session(base_url = rvLink, driver = driver)
        browser2.set_attribute('auto_load_images', False)
        browser2.visit(rvLink)
        cicle = True
        count = 0

        while cicle:

            print("try n. " + str(count+1) + ":")
            browser2.visit(rvLink)
            sleep(2)

            links = re.findall('"((http|ftp)s?://.*?)"', browser2.body())
            for x in links:
                x = str(x)
                splitted1 = x.split(",")
                splitted2 = splitted1[0].split("'")
                if ".mp4" in splitted2[1]:
                    print(splitted2[1])
                    self.server.kill()
                    return splitted2[1]
            count = count + 1
            print("failed")
            if count>=10:
                cicle = False

        print("Error finding mp4 Link")

    def oLoadHandler(self, rvLink):

        self.server.kill()
        self.server = webkit_server.Server()
        server_conn = webkit_server.ServerConnection(server=self.server)
        driver = dryscrape.driver.webkit.Driver(connection=server_conn)

        browser2 = dryscrape.Session(base_url = rvLink, driver = driver)
        browser2.set_attribute('auto_load_images', False)
        browser2.set_attribute('javascript_can_open_windows', False)
        browser2.set_attribute('plugins_enabled', False)
        browser2.visit(rvLink)
        overlay = browser2.at_xpath('//*[@id="videooverlay"]')
        overlay.click()
        print("clicked overlay")
        a = browser2.at_xpath('//*[@id="olvideo_html5_api"]')
        finalLink = "https://oload.site" + a['src']
        print(finalLink)
        self.server.kill()
        return finalLink




        



class EpisodeHandler(object):

    def __init__(self, object):

        self.episodeList = object
        print("Extract Episode Links...")
        self.linksToVideos = []
        for episode in self.episodeList:
            self.linksToVideos.append(self.extractLink(episode = episode))


    def extractLink(self, episode):
        
        try:
            episodeSess = CreateSession(object = episode)
            print(episode)
            link = episodeSess.getEpisodeLink()
        except webkit_server.EndOfStreamError:
            print("End of Stream Error! Retry...")
            link = self.extractLink(episode = episode)
        except webkit_server.InvalidResponseError:
            print("Invalid Response Error! Retry...")
            link = self.extractLink(episode = episode)
        return link

    def getLinkList(self):

        return self.linksToVideos


def ScrapeAnime(targetLink):

    print(targetLink)
    animeLink = str(targetLink)
    a = CreateSession(object = animeLink)
    bodyRoot = a.getRoot()
    print("Root Found")
    animeCod = a.getName(root = bodyRoot)
    info = animeCod.split(" (")
    if len(info) > 1:
        animeName = info[0]
        seasonInfo = (info[1].replace(")","")).split(" ")
        animeSeason = seasonInfo[1]
    else:
        animeName = info[0]
        animeSeason = "1"

    print("\nAnime Name: " + animeName)
    print("Anime season: " + str(animeSeason))


    print("******************************************************")
    sleep(10)
    cards = a.getCards(root = bodyRoot)
    episodeList = a.getEpisodeList(card = cards[0])
    episodeList.reverse()
    print("\nEpisode List:")
    for i in range(0,len(episodeList)):
        print(episodeList[i])
    print("*******************************************************")
    print("\nScraping Episode Links:")
    episodeLinks = EpisodeHandler(object = episodeList)
    linkToVideos = episodeLinks.getLinkList()

    print("***************************************")
    print("\nExport Json...")

    episodeDict = {}
    i = 0
    for x in linkToVideos:
        i = i + 1
        if i < 10:
            number = "0" + str(i)
        else:
            number= str(i)
        episodeDict['Ep' + number] = str(x)


    ciao = {'info': {'name': animeName, 'season': animeSeason}, 'episodelist': episodeDict}

    if animeName[-1] == " ":
            animeName = animeName[0:(len(animeName)-1)]

    with open('anime_json/' + str(animeName + '_season_' + str(animeSeason) + '.json'), 'w+') as f:
        json.dump(ciao, f, indent = 4, sort_keys = True)





#/html/body/div[2]/div[3]/div/div/div/div/div[1]/article/div/div[3]/div[1]/div/iframe
#/html/body/div[2]/div[3]/div/div/div/div/div[1]/article/div/div[3]/div[1]/div/div/iframe