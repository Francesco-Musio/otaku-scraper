#! /usr/bin/python3

import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
import json
import os
import OtakuScraper
from time import sleep

class MainWindow(object):

    def __init__(self):


        self.win = Gtk.Window()
        self.win.set_title('Otaku Scraper')
        self.win.set_default_size(600,480)
        self.win.connect("delete-event", Gtk.main_quit)

        self.vbox = Gtk.VBox()
        self.win.add(self.vbox)
        hbox = Gtk.HBox()
        self.vbox.pack_start(hbox, False, False, 0)
        self.entry = Gtk.Entry()
        hbox.add(self.entry)
        self.search_button = Gtk.Button("Search")
        hbox.pack_start(self.search_button, False, False, 0)
        self.search_button.connect("clicked", self.filterList)

        self.createList()
        self.vbox.add(self.scroll)

        self.win.show_all()

    def createList(self):

        with open('animelist.json', 'r') as f:
            self.fulllist = json.load(f)

        self.animeList = []
        for x in range(0,len(self.fulllist)):
            if x < 10:
                x = '0' + str(x)
            ciao = ((self.fulllist.get(str(x))).get('info')).get('name')
            self.animeList.append(ciao)

        self.animeListShort = self.removeDuplicates(listx = self.animeList)

        self.createTree(listx = self.animeListShort)

    def filterList(self, w):

        newAnimeList = []
        filtro = self.entry.get_text().strip()

        for x in self.animeListShort:
            if filtro in x:
                newAnimeList.append(x)

        self.vbox.remove(self.scroll)

        self.createTree(listx = newAnimeList)

        self.vbox.add(self.scroll)

        self.win.show_all()

    def createTree(self, listx):

        lista = Gtk.ListStore(str)

        for x in listx:
            lista.append([str(x)])

        tree = Gtk.TreeView(lista)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Anime List", renderer, text = 0)
        tree.append_column(column)

        self.selection = tree.get_selection()
        self.selection.connect("changed", self.on_selection_change)

        self.scroll = Gtk.ScrolledWindow()
        view = Gtk.Viewport()
        view.add(tree)
        self.scroll.add(view)

    def on_selection_change(self, selection):

        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected ", model[treeiter][0])

            x = model[treeiter][0]
            count = 0

            for link in self.animeList:
                if x in link:
                    count = count + 1

            if count > 1:
                b = SeasonScreen()
                b.setWin(self.win)
                b.setName(name = x)
                b.setFullList(fulllist = self.fulllist)
                b.exec()

            else:
                a = EpisodeScreen()
                a.setWin(win = self.win)
                a.setTargetAnime(name = model[treeiter][0])
                a.setSeason(season = "1")
                a.setFullList(lista = self.fulllist)
                a.exec()

    def removeDuplicates(self,listx):

        output = []
        seen = set()
        for x in listx:
            if x[-1] == " ":
                x = x[0:(len(x)-1)]
            if x not in seen:
                output.append(x)
                seen.add(x)
        return output


class SeasonScreen(object):

    def setWin(self, win):

        self.win = win

    def setName(self, name):

        self.name = name

    def setFullList(self, fulllist):

        self.fulllist = fulllist

    def exec(self):

        for x in self.win.get_children():
            self.win.remove(x)

        seasonList = []
        for x in range(0,len(self.fulllist)):
            if x < 10:
                x = '0' + str(x)
            ciao = ((self.fulllist.get(str(x))).get('info')).get('name')
            if ciao[-1] == " ":
                ciao = ciao[0:(len(ciao)-1)]
            if self.name == ciao:
                season = ((self.fulllist.get(str(x))).get('info')).get('season')
                if season == "":
                    seasonList.append("1")
                else:
                    seasonList.append(season)

        lista = Gtk.ListStore(str)

        for x in seasonList:
            lista.append(["Season " + str(x)])

        tree = Gtk.TreeView(lista)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Season List", renderer, text = 0)
        tree.append_column(column)

        self.selection = tree.get_selection()
        self.selection.connect("changed", self.on_selection_change)

        self.scroll = Gtk.ScrolledWindow()
        view = Gtk.Viewport()
        view.add(tree)
        self.scroll.add(view)

        self.win.add(self.scroll)

        self.win.show_all()

    def on_selection_change(self, selection):

        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected ", model[treeiter][0])

            x = (model[treeiter][0]).split(" ")
            x = x[-1]

            a = EpisodeScreen()
            a.setWin(self.win)
            a.setTargetAnime(self.name)
            a.setSeason(season = x)
            a.setFullList(lista = self.fulllist)
            a.exec()



class EpisodeScreen(object):

    def setWin(self, win):

        self.win = win

    def setTargetAnime(self, name):

        self.animeName = name

    def setSeason(self, season):

        self.animeSeason = season

    def setFullList(self, lista):

        self.fulllist = lista

    def exec(self):

        #scelta tra guardare e scaricare
        for x in self.win.get_children():
            self.win.remove(x)

        self.win.set_border_width(250)

        vbox = Gtk.VBox()
        self.win.add(vbox)
        label = Gtk.Label("Do you want to Watch or Download?")
        vbox.pack_start(label, False, False, 0)
        hbox = Gtk.HBox(spacing = 40)
        vbox.add(hbox)
        watch_button = Gtk.Button("Watch")
        down_button = Gtk.Button("Download")
        hbox.pack_start(watch_button, False, False, 0)
        hbox.pack_start(down_button, False, False, 0)

        watch_button.connect("clicked", self.watchAnime)
        down_button.connect("clicked", self.downloadAnime)

        self.win.show_all()

    def downloadAnime(self, w):

        for x in self.win.get_children():
            self.win.remove(x)

        label = Gtk.Label("Download in progress..")
        self.win.add(label)

        self.win.show_all()

        targetLink = None
        for i in range(0,len(self.fulllist)):
            if i < 10:
                i = '0' + str(i)
            name = ((self.fulllist.get(str(i))).get('info')).get('name')
            season = ((self.fulllist.get(str(i))).get('info')).get('season')
            if name[-1] == " ":
                name = name[0:(len(name)-1)]
            if name == self.animeName:
                if season == self.animeSeason:
                    targetLink = (self.fulllist.get(str(i))).get('anime_link')

        for x in self.win.get_children():
            self.win.remove(x)

        vbox = Gtk.VBox()
        self.win.add(vbox)
        label = Gtk.Label("Download finished")
        vbox.pack_start(label, False, False, 0)
        button = Gtk.Button("Watch")
        vbox.add(button)

        self.win.show_all()

        OtakuScraper.ScrapeAnime(targetLink = targetLink)


        button.connect("clicked", self.watchAnime)


    def watchAnime(self, w):

        for x in self.win.get_children():
            self.win.remove(x)

        self.win.set_border_width(0)

        with open('anime_json/' + str(self.animeName + '_season_' + str(self.animeSeason) + '.json'), 'r') as f:
            self.animejson = json.load(f)

        self.episodeList = []

        temp = self.animejson.get('episodelist')
        for x in range(1,len(temp)+1):
            if x < 10:
                x = '0' + str(x)
            ciao = temp.get('Ep' + str(x))
            self.episodeList.append(ciao)

        self.episodeList = self.removeDuplicates(listx = self.episodeList)

        lista = Gtk.ListStore(str, str)
        i = 0
        for x in self.episodeList:
            i = i+1
            lista.append([str(i),str(x)])

        tree = Gtk.TreeView(lista)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Episode Number", renderer, text = 0)
        tree.append_column(column)
        column = Gtk.TreeViewColumn(self.animeName + " season " + self.animeSeason, renderer, text = 1)
        tree.append_column(column)

        self.selection = tree.get_selection()
        self.selection.connect("changed", self.on_selection_change)

        self.scroll = Gtk.ScrolledWindow()
        view = Gtk.Viewport()
        view.add(tree)
        self.scroll.add(view)

        self.win.add(self.scroll)

        self.win.show_all()

    def removeDuplicates(self,listx):

        output = []
        seen = set()
        for x in listx:
            if x not in seen:
                output.append(x)
                seen.add(x)
        return output

    def on_selection_change(self, selection):

        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected ", model[treeiter][1])
            os.system("mpv " + model[treeiter][1])






a = MainWindow()
Gtk.main()