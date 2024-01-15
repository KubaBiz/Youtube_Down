from yt_dlp import YoutubeDL, utils
import pyperclip
import os
from tkinter import Tk, filedialog


def choose_output_folder():
    root = Tk()
    #root.withdraw()  # Ukrycie głównego okna

    folder_path = filedialog.askdirectory(title="Wybierz folder wyjściowy", initialdir='.')

    return folder_path

def download_youtube_audio(url, output_path='.', output_format='mp3'):
    try:
        ffmpeg_path = '.\\ffmpeg\\bin\\ffmpeg.exe'
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '256',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_path,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            print(f"Download complete! Title: {info_dict['title']}", flush=True)

    except Exception as e:
        print(f"Error function: {e}")

def download_playlist_audio(playlist_url, output_path='.', output_format='mp3'):
    try:
        ffmpeg_path = '.\\ffmpeg\\bin\\ffmpeg.exe'
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_path,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                for video in playlist_info['entries']:
                    try:
                        ydl.download([video['url']])
                    except Exception as e:
                        print(f"Error video: {e}")
                        print(f"Skipping video: {video['title']}")
            except Exception as e:
                print(f"Error playlist: {e}")
                print("Skipping the entire playlist.")

    except Exception as e:
        print(f"Error function: {e}")


def get_clipboard_text():
    input("Skopiuj link (Ctrl+C) i kliknij enter")
    return pyperclip.paste()

if __name__ == "__main__":
    output_directory = choose_output_folder()
    while(True):
        clipboard_text = get_clipboard_text()
        print(f"Skopiowany link: {clipboard_text}")

        video_url = clipboard_text

        #download_playlist_audio(video_url, output_directory)
        download_youtube_audio(video_url, output_directory)