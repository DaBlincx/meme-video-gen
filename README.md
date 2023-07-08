# Meme/Shitpost Compilation Generator

This project is a Python script that generates shitpost videos by downloading random videos from shitpoststatus.com and combining them into a single video clip. The script utilizes various libraries, including MoviePy for video editing, yt-dlp for downloading YouTube videos, and Playwright for web scraping.

![saul](https://cdn.discordapp.com/emojis/1010754114390605844.webp?size=56) ![omg](https://cdn.discordapp.com/emojis/852418130315313162.gif)

## Table of Contents

- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Other](#other)
  - [Watermark](#watermark)
  - [Video Settings](#video-settings)
  - [Used Videos](#used-videos)
- [FAQ](#faq)

## Configuration

Can be found in `config.ini` (config.example.ini if you just cloned the repo)

| Option | Description |
| ------ | ----------- |
| Output directory | The directory where the final video will be saved.
| Temporary directory | The directory where downloaded videos are stored temporarily.
| Used directory | The directory where used video files are moved.
| Maximum downloads | The maximum number of videos to download.
| Video length | The desired (minimum) length of the final video in seconds or minutes.
| Video resolution | The width and height of the video in pixels.
| Video frame rate | The frame rate of the video in frames per second.
| Video bitrate | The bitrate of the video in kilobits per second.
| Video codec | The video codec to use for encoding the final video.
| Number of rendering threads | The number of threads to use for video rendering.
| (Optional) Watermark image | The path to the watermark image file.
| (Optional) Titles file | A file containing custom titles for the final videos.
| (Optional) Used titles file | A file to store used titles and avoid duplication.

## Dependencies

I have not tested this script on any python version below 3.11.3, but it should work on >=3.9.

The script relies on the following dependencies:

- MoviePy
- yt-dlp
- Playwright
- ffmpeg

You can install these dependencies using the requirements.txt file:

```
pip install -r requirements.txt
```

You will also have to install Chromium for Playwright to work:

```
playwright install chromium
```

## Usage

1. Clone the repository.
2. Install the required dependencies using the commands mentioned above.
3. Customize the configuration in the config.ini file.
4. Run the script using Python:

    ```
    python script.py
    ```
5. Wait and drink some coffee or something you nerd

The script will generate a random shitpost video based on the specified configuration.

## Other

### Watermark
There is a watermark image already included in the repository. If you do not want to use a watermark, you can remove the watermark image path from the configuration file.

### Video Settings
The codec is set to libx264 by default. MoviePy does not support GPU acceleration, so the encoding process will be slow. 

You can also change the number of rendering threads in the configuration file to speed up the process.

### Used Videos

The script will move the used videos to the used directory. 

Maybe I'll add an option to delete them instead in the future.

Also, the script will not download videos that have already been downloaded. This is to avoid duplication. Delete archive.txt in the General>TempDir folder (see config.ini) if you want to possibly download videos that have already been downloaded.

## FAQ

### Why is the script so slow?

The script is slow because it has to download videos from the internet and render them using the CPU because MoviePy does not support GPU accelleration. You can speed up the process by increasing the number of rendering threads in the configuration file.

### What about automatic uploads to YouTube?

Maybe in the future. You can try to implement it yourself if you want and submit a pull request. ![thumbsup](https://cdn.discordapp.com/emojis/1044717814147199107.webp?size=16)

### Why do you use playwright instead of using requests or something?

I haven't tried following redirects using requests/urllib, so I just used playwright because it's easier.

### Will you fix whatever happens when I set MaxDownloads to 0 or below?

No.

### Why is the script so bad?

Touch grass.

### Do you touch grass?

No.

## Contributing

Contributions to this project are welcome! If you have any suggestions, improvements, or bug fixes, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Please note that this script is intended for educational and entertainment purposes only. The creator of this project is not responsible for any misuse or violation of any applicable laws or regulations.
