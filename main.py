import contextlib
import os
import moviepy
import moviepy.editor
import moviepy.video.fx.resize
import time
import configparser
import shutil
from playwright.sync_api import sync_playwright
import random

import video_downloader as vd

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
videoAmount = int(config['General']['VideoAmount'])
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
        title = getDefaultFilename()
        if usedTitles: writeUsedTitles(title)
        return title

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
        file = vd.downloadVideo(tempDir)
        while file is None:
            print("Download failed, retrying")
            file = vd.downloadVideo(tempDir)
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
        file = vd.downloadVideo(tempDir)
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

def removeLeftoverFiles(removelater: list[str]):
    print("Moving leftover files to used folder")
    for file in removelater:
        try: shutil.move(os.path.join(tempDir, file), os.path.join(usedDir, file))
        except PermissionError as e: print(f"Failed to move {file} to used folder (do it manually): {e}")
        except FileExistsError:
            try:
                # rename to name (number).ext and increase that number if that file also already exists
                i = 1
                while True:
                    newname = f"{os.path.splitext(file)[0]} ({i}){os.path.splitext(file)[1]}"
                    try:
                        shutil.move(os.path.join(tempDir, file), os.path.join(usedDir, newname))
                        break
                    except FileExistsError:
                        i += 1
            except PermissionError as e: print(f"Failed to move {file} to used folder (do it manually): {e}")

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
    removelater = []
    if usedDir: 
        for file in usedfiles: 
            try: shutil.move(os.path.join(tempDir, file), os.path.join(usedDir, file))
            except (PermissionError, FileExistsError): removelater.append(file)
    return removelater

if __name__ == "__main__":
    print("Starting (this may take a while)")
    removelater = []
    if videoAmount >= 1:
        for i in range(videoAmount):
            removelater.extend(createVideo())
            print(f"Finsihed video {i+1}/{videoAmount}")
    elif videoAmount == -1:
        while True:
            try:
                removelater.extend(createVideo())
                print("Starting new video")
            except KeyboardInterrupt:
                break
    else:
        print("No videos to create because videoCount is 0 (lmao why would you do that ??)")
    if removelater:
        removeLeftoverFiles(removelater)


