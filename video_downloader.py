import os
import yt_dlp
from playwright.sync_api import sync_playwright
import argparse

def get_shitpost() -> str:
    # this is definitely a very efficient design and you should definitely not use a better method smh my head
    with sync_playwright() as playwright:
        print("Getting shitpost")
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://shitpoststatus.com/watch")
        page.wait_for_url("https://shitpoststatus.com/watch?v=*")
        youtubelink = "https://youtube.com/" + page.url.split("/")[-1]
        page.close()
        context.close()
        browser.close()
        print(f"Got {youtubelink}")
        return youtubelink

def downloadVideo(dwdir: str):
    link = get_shitpost()
    print(f"Downloading {link}")
    os.chdir(dwdir)
    ydl_opts = {'download_archive': 'archive.txt','format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best','outtmpl': '%(title)s [%(id)s].%(ext)s'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        try: filename = ydl.prepare_filename(info_dict)
        except: filename = None
        ydl.download([link])
    os.chdir("..")
    return filename

def main():
    parser = argparse.ArgumentParser(description="Download a video from shitpoststatus.com")
    parser.add_argument("-o", "--output", help="Output directory", default="temp")
    parser.add_argument("-n", "--num", help="Number of videos to download", default=1, type=int)
    args = parser.parse_args()
    downloaded = {}
    i = 0
    while i < args.num:
        print(f"Downloading video {i+1}/{args.num}")
        filename = downloadVideo(args.output)
        if filename is not None:
            downloaded[i] = filename
            i += 1
    print(downloaded)

if __name__ == "__main__":
    print("Running video downloader manually...")
    main()