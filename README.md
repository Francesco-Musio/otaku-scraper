#Otaku Scraper

- Disclaimer
- Info
- How To

## Disclaimer

**This repository is a study on how scraping works.**

**I strongly recommend _not_ to use this application, except for pure knowledge of the argument.** 

##Info

The objective of this study is to scrape from information about all the anime in a streaming site and than get to a mp4 link that can be streamed by mpv.

The first step is to scrape the complete list of the anime in the site. This will generate a json with all the links to the single anime pages.

At this poit, the GUI is initialized and allow to navigate in a menu where the user can select the Anime that he wants to watch and download or watch the anime if already downloaded.

Downloading the anime means running a script that obtains all the mp4 links and create a json file with all the info. When the download is finished, the program uses mpv to stream the video. 

##How To

1. Create two new folder in the main folder with these exact names:
	-anime_json
	-temp
2. Run `Sceaper_Anime.py` and wait for it to download the full Anime List
3. Run `Main.py`

When you select an anime, the GUI will give you the option to watch or download the anime.

If it's the first time selecting that particular anime, select the download option. This will create in the `anime_json` folder a `.json` file that contains the anime informations. **Deleting that file means that you have to repeat the download process** 
