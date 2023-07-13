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
import random

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
videoLength = int(config['Video']['Length'])
videoLengthInMinutes = config['Video']['LengthInMinutes']
if videoLengthInMinutes == "True": videoLength *= 60
videoHeight = int(config['Video']['Height'])
videoWidth = int(config['Video']['Width'])
videoFps = int(config['Video']['FPS'])
videoBitrate = config['Video']['Bitrate']
videoCodec = config['Video']['Codec']
renderThreads = int(config['Video']['Threads'])
audioCodec = config['Audio']['AudioCodec']
audioBitrate = config['Audio']['AudioBitrate']
watermark = config['Other']['Watermark']
titles = config['Other']['Titles']
usedTitles = config['Other']['UsedTitles']

def get_shitpost() -> str:
    # this is definitely a very efficient design and you should definitely not use a better method smh my head
    with sync_playwright() as playwright:
        print("Getting shitpost")
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

def createMemeClip(file: str):
    memepath = os.path.join(tempDir, file)
    clip = moviepy.editor.VideoFileClip(memepath)
    currentwidth = clip.size[0]
    print(f"Creating clip of {file} {clip.size}")
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

def makeWatermark(duration: int):
    """
    will return an image clip consistion of the watermark image that is as long as duration
    """
    print("Creating watermark")
    watermarkclip = moviepy.editor.ImageClip(watermark).set_duration(duration)
    watermarkclip = watermarkclip.resize(height=videoHeight)
    if watermarkclip.size[0] > videoWidth:
        watermarkclip = moviepy.video.fx.resize.resize(watermarkclip, width=videoWidth)
    watermarkclip = watermarkclip.set_position(("center", "center"))
    return watermarkclip

def writeUsedTitles(title: str):
    try:
        with open(usedTitles, "a") as f:
            f.write(title + "\n")
    except FileNotFoundError:
        with open(usedTitles, "w") as f:
            f.write(title + "\n")

def getDefaultFilename():
    return f"output_{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

def formatCustomFilename(title: str):
    formatted = f"{title}.mp4".encode("utf-8", "ignore").decode()
    for char in ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]:
        formatted = formatted.replace(char, "")
    return getDefaultFilename() if formatted == ".mp4" else formatted

def getOutputFilename():
    if not titles:
        return getDefaultFilename()
    with open(titles, "r") as f:
        titlesfile = f.readlines()
    if titlesfile:
        title = random.choice(titlesfile)
        titlesfile.remove(title)
        if usedTitles: writeUsedTitles(title.strip())
        with open(titles, "a") as f:
            f.writelines(titlesfile)
        return formatCustomFilename(title.strip())
    else:
        return getDefaultFilename()


def tryMakeDirs():
    with contextlib.suppress(FileExistsError):
        os.mkdir(outputDir)
    with contextlib.suppress(FileExistsError):
        os.mkdir(tempDir)
    with contextlib.suppress(FileExistsError):
        os.mkdir(usedDir)

def checkForExistingClips():
    clips, usedfiles = [], []
    alreadyexisting = os.listdir(tempDir)
    random.shuffle(alreadyexisting)
    for file in alreadyexisting:
        if file.endswith(".mp4"):
            newclip = createMemeClip(file)
            print(type(newclip))
            clips.append(newclip)
            usedfiles.append(file)
            curlength = sum(clip.duration for clip in clips)
            print(f"Length: {curlength:.2f}/{videoLength:.2f} seconds ({curlength/videoLength*100:.2f}%)")
            if curlength >= videoLength: break
    return clips, usedfiles

def refreshContentClip(content_clip: moviepy.editor.CompositeVideoClip | moviepy.editor.VideoClip, clips: list[moviepy.editor.VideoClip], usedfiles: list[str]):
    while content_clip.duration < videoLength:
        file = downloadVideo(tempDir)
        while file is None:
            print("Download failed, retrying")
            file = downloadVideo(tempDir)
        if file not in usedfiles and type(file) == str:
            newclip = createMemeClip(file)
            print(type(newclip))
            clips.append(newclip)
            usedfiles.append(file)
            curlength = sum(clip.duration for clip in clips)
            print(f"Length: {curlength:.2f}/{videoLength:.2f} seconds ({curlength/videoLength*100:.2f}%)")
        content_clip = moviepy.editor.concatenate_videoclips(clips).set_position(("center", "center"))
    return content_clip, usedfiles

def createContentClip():
    clips, usedfiles = checkForExistingClips()

    if not clips:
        file = downloadVideo(tempDir)
        if file not in usedfiles and type(file) == str:
            clips.append(createMemeClip(file))
            usedfiles.append(file)
    content_clip = moviepy.editor.concatenate_videoclips(clips).set_position(("center", "center"))

    return refreshContentClip(content_clip, clips, usedfiles)

def createPossibleWatermarkedClip(clips: list[moviepy.editor.VideoClip | moviepy.editor.CompositeVideoClip | moviepy.editor.ImageClip]):
    return moviepy.editor.CompositeVideoClip(clips, size=(videoWidth, videoHeight), bg_color=[0,0,0])

def createFinalClip(content_clip: moviepy.editor.CompositeVideoClip | moviepy.editor.VideoClip, background_clip: moviepy.editor.VideoClip):
    if watermark: final_clip = createPossibleWatermarkedClip([background_clip, content_clip, makeWatermark(content_clip.duration)])
    else: final_clip = createPossibleWatermarkedClip([background_clip, content_clip])
    final_clip.set_fps(videoFps)
    return final_clip

def createClips():
    content_clip, usedfiles = createContentClip()
    background_clip = moviepy.editor.ColorClip(size=(videoWidth, videoHeight), color=[0,0,0], duration=content_clip.duration)
    return createFinalClip(content_clip, background_clip), getOutputFilename(), usedfiles

def writeVideo(final_clip: moviepy.editor.CompositeVideoClip, outputFileName: str):
    final_clip.write_videofile(
        os.path.join(outputDir, outputFileName), 
        fps=videoFps, 
        bitrate=videoBitrate, 
        threads=renderThreads, 
        preset="ultrafast", 
        audio_codec=audioCodec,
        temp_audiofile="temp-audio.m4a", 
        remove_temp=True, 
        codec=videoCodec, 
        audio_bitrate=audioBitrate
    )

def createVideo():
    tryMakeDirs()
    final_clip, outputFileName, usedfiles = createClips()
    writeVideo(final_clip, outputFileName)
    if usedDir: 
        for file in usedfiles: shutil.move(os.path.join(tempDir, file), os.path.join(usedDir, file))

if __name__ == "__main__":
    createVideo()
