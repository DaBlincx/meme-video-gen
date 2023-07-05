# Shitpost Compilation Generator

This project is a Python script that generates shitpost videos by downloading random videos from shitpoststatus.com and combining them into a single video clip. The script utilizes various libraries, including MoviePy for video editing, yt-dlp for downloading YouTube videos, and Playwright for web scraping.

## Configuration

The script uses a configuration file (config.ini) to specify various settings:

- Output directory: The directory where the final video will be saved.
- Temporary directory: The directory where downloaded videos are stored temporarily.
- Used directory: The directory where used video files are moved.
- Maximum downloads: The maximum number of videos to download.
- Video length: The desired length of the final video in seconds or minutes.
- Video resolution: The width and height of the video in pixels.
- Video frame rate: The frame rate of the video in frames per second.
- Video bitrate: The bitrate of the video in kilobits per second.
- Video codec: The video codec to use for encoding the final video.
- Number of rendering threads: The number of threads to use for video rendering.
- Watermark image: The path to the watermark image file. (Optional)
- Titles file: A file containing custom titles for the final videos. (Optional)
- Used titles file: A file to store used titles and avoid duplication. (Optional)

## Dependencies

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
2. Install the required dependencies using the command mentioned above.
3. Customize the configuration in the config.ini file, including the output directory, video settings, and watermark image path.
4. Run the script using Python:

```
python script.py
```

The script will generate a random shitpost video based on the specified configuration.

## Contributing

Contributions to this project are welcome! If you have any suggestions, improvements, or bug fixes, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code according to your needs.

## Disclaimer

Please note that this script is intended for educational and entertainment purposes only. Make sure to comply with the terms of service of the website from which you are downloading videos. The creators of this project are not responsible for any misuse or violation of any applicable laws or regulations.