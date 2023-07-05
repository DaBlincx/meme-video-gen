import contextlib
import os
import moviepy
import moviepy.editor
import moviepy.video.fx.resize
import time
import configparser
import yt_dlp
import shutil
from playwright.sync_api import sync_playwright

config = configparser.ConfigParser()
try:
    config.read('config.ini')
except Exception:
    print("Config file not found, using default config")
    try:
        shutil.copyfile('config.ini.example', 'config.ini')
        config.read('config.ini')
    except Exception:
        print("Failed to copy default config, check github for example config or clone the repo again")
        input("Press enter to exit")
        exit()
outputDir = config['General']['OutputDir']
tempDir = config['General']['TempDir']
usedDir = config['General']['UsedDir']
maxdw = int(config['General']['MaxDownloads'])
videoHeight = int(config['Video']['Height'])
videoWidth = int(config['Video']['Width'])
videoFps = int(config['Video']['FPS'])
videoBitrate = config['Video']['Bitrate']
renderThreads = int(config['Video']['Threads'])

def get_shitpost() -> str:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://shitpoststatus.com/watch")
        # page.get_by_role("button", name="Play Videos").click()
        # wait for the page to load and redirect using playwright
        page.wait_for_url("https://shitpoststatus.com/watch?v=*")

        # get current page url
        youtubelink = "https://youtube.com/" + page.url.split("/")[-1]
        page.close()
        context.close()
        browser.close()
        return youtubelink

def downloadVideo(dwdir):
    link = get_shitpost()
    print(f"Downloading {link}")
    os.chdir(dwdir)
    ydl_opts = {
        'download_archive': 'archive.txt',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(title)s [%(id)s].%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        try: filename = ydl.prepare_filename(info_dict)
        except: filename = None
        ydl.download([link])

    os.chdir("..")
    return filename

def createMemeClip(file: str):
    memepath = os.path.join(tempDir, file)
    clip = moviepy.editor.VideoFileClip(memepath)
    currentheight = clip.size[1]
    currentwidth = clip.size[0]
    print(f"Creating clip of {file} {clip.size}")
    if currentheight > videoHeight:
        clip = moviepy.video.fx.resize.resize(clip, height=videoHeight)
    if currentwidth > videoWidth:
        clip = moviepy.video.fx.resize.resize(clip, width=videoWidth)
    print(f"New size: {clip.size}")
    clip.set_fps(videoFps)
    clip.set_position(("center", "center"))
    clip.audio.set_fps(videoFps)
    # move meme to used
    #os.rename(memepath, os.path.join(f"{tempDir}/used", file))
    return clip

def createVideo():

    with contextlib.suppress(FileExistsError):
        os.mkdir(outputDir)
    with contextlib.suppress(FileExistsError):
        os.mkdir(tempDir)

    clips = []
    usedfiles = []

    file = downloadVideo(tempDir)
    if file not in usedfiles:
        clips.append(createMemeClip(file))
        usedfiles.append(file)

    content_clip = moviepy.editor.concatenate_videoclips(clips)
    content_clip.set_position(("center", "center"))
    while content_clip.duration < 600:
        file = downloadVideo(tempDir)
        if file not in usedfiles and not None:
            clips.append(createMemeClip(file))
            usedfiles.append(file)
        content_clip = moviepy.editor.concatenate_videoclips(clips)
        content_clip.set_position(("center", "center"))

    background_clip = moviepy.editor.ColorClip(size=(videoWidth, videoHeight), color=[0,0,0], duration=content_clip.duration)

    final_clip = moviepy.editor.CompositeVideoClip([background_clip, content_clip], size=(videoWidth, videoHeight), bg_color=[0,0,0])

    final_clip.set_fps(videoFps)
    final_clip.set_duration(final_clip.duration)

    outputFileName = f"output_{time.strftime('%Y%m%d-%H%M%S')}.mp4"

    final_clip.write_videofile(os.path.join(outputDir, outputFileName), fps=videoFps, bitrate=videoBitrate, threads=renderThreads, preset="ultrafast", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_bitrate="128k")

    for file in usedfiles:
        shutil.move(os.path.join(tempDir, file), os.path.join(usedDir, file))

def main():
    createVideo()

if __name__ == "__main__":
    main()








