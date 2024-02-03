import time
from yt_dlp import YoutubeDL, utils
import pyperclip
import threading
import os
import re
from tkinter import END, Tk, StringVar, Radiobutton, Label, OptionMenu, Frame, Entry, Button, filedialog, Menu

link_queue = []


def choose_output_options(root):
    # Create variables for checkboxes and entry
    format_var = StringVar(value="mp3")
    resolution_var = StringVar(value="144p")
    link_var = StringVar()

    def on_checkbox_click(*args):
        if format_var.get() == "mp4":
            result_label.config(text=f"Format: {format_var.get()}, Resolution: {resolution_var.get()}, Link: {link_var.get()}")
            resolution_frame.pack_forget()
            result_label.pack_forget()
            buttons_frame.pack_forget()
            resolution_frame.pack(pady=10)
            result_label.pack(pady=10)
            buttons_frame.pack(pady=10)
        else:
            resolution_var.set("144p")
            result_label.config(text=f"Format: {format_var.get()}, Bit Rate: 256kb/s, Link: {link_var.get()}")
            resolution_frame.pack_forget()
            result_label.pack(pady=10)
            buttons_frame.pack(pady=10)

    def on_window_close():
        root.destroy()

    def on_link_entry_change(event):
        if format_var.get() == "mp4":
            result_label.config(text=f"Format: {format_var.get()}, Resolution: {resolution_var.get()}, Link: {link_var.get()}")
        else:
            resolution_var.set("144p")
            result_label.config(text=f"Format: {format_var.get()}, Bit Rate: 256kb/s, Link: {link_var.get()}")

    def on_download_button_click():
        # Create a thread for the background task with arguments
        if not link_var.get() in link_queue:
            link_queue.append(link_var.get())

            temp_text = []
            for widget in progresses_frame.winfo_children():
                temp_text.append(widget.cget("text"))
                widget.destroy()
            
            #Create new labels
            global progresses_labels
            progresses_labels = []
            # Create new labels
            for i in range(len(link_queue)):
                if i<len(temp_text):
                    label = Label(progresses_frame, text=temp_text[i])
                else:
                    label = Label(progresses_frame, text=f"{link_queue[i]}")
                progresses_labels.append(label)
                label.pack(pady=5)
            
            thread = threading.Thread(target=download_video, args=(link_var.get(), format_var.get(), resolution_var.get()))

            # Start the thread
            thread.start()
        #download_video(link_var.get(), format_var.get(), resolution_var.get())
    
    def set_directory():
        folder_path = filedialog.askdirectory(title="Wybierz folder wyjściowy", initialdir='.')
        with open("conf", 'w') as file:
            file.write(folder_path)

    def progress_hook(d, link):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            speed = d['_speed_str']
            eta = d['eta']
            
            root.after(0, update_progress_bars, d, link, d['status'])
            print(f'\rDownloading: {percent} [{speed}] - ETA: {eta} ', end='', flush=True)
        elif d['status'] == 'finished':
            root.after(0, update_progress_bars, d, link, d['status'])
            print('\nMerging video with audio...')
        elif d['status'] == 'error':
            root.after(0, update_progress_bars, d, link, d['status'])
            print(f"\nError: {d['error_message']}")

    def update_progress_bars(d, link, status):
        if status == 'downloading':
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            percent = ansi_escape.sub('', d['_percent_str'])
            speed = ansi_escape.sub('', d['_speed_str'])
            eta = d['eta']
            # print("\n\n")
            # print(link_queue.index(link), len(progresses_labels))
            progresses_label = progresses_labels[link_queue.index(link)]
            progresses_label.config(text=f"Downloading {link}: {percent} [{speed}] - ETA: {eta}")
            return
        # elif status == 'starting':
        #     progresses_label = progresses_labels[link_queue.index(link)]
        #     progresses_label.config(text=f"Downloading {link}: {percent} [{speed}] - ETA: {eta} ")
        #     return
        elif status == 'finished':
            progresses_label = progresses_labels[link_queue.index(link)]
            progresses_label.config(text=f'{link}: Merging video with audio...') 

    def download_video(link, format, resolution):
        with open("conf", 'r') as file:
            output_path = file.read()
        ffmpeg_path = '.\\ffmpeg\\bin\\ffmpeg.exe'
        if format == "mp3": 
            ydl_opts = {
                'format': 'bestaudio[abr=256k]/bestaudio/best',
                'progress_hooks': [lambda d: progress_hook(d, link)],
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format,
                    'preferredquality': '256',
                }],
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
                'quiet': True,
            }
        else:
            resolution_edited = resolution[:-1] 
            ydl_opts = {
                'format': f'bestvideo[ext=mp4][height<={resolution_edited}]+bestaudio[ext=m4a]/bestvideo[height<={resolution_edited}]+bestaudio[abr=256k]/best[height<={resolution_edited}]',
                'progress_hooks': [progress_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'outtmpl': os.path.join(output_path, '%(title)s.%(resolution)s.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
                'quiet': True,
            }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False, process=False)

                if 'entries' in info_dict:
                    for video in info_dict['entries']:
                        try:
                            ydl.download([video['url']])
                        except Exception as e:
                            print(f"Error video: {e}")
                            print(f"Skipping video: {video['title']}")

                else:
                    try:
                        ydl.download([link])
                        #with YoutubeDL(ydl_opts) as ydl:
                            #info_dict = ydl.extract_info(link, download=True)
                        progresses_label = progresses_labels[link_queue.index(link)]
                        progresses_label.config(text=f"Download completed! Title: {info_dict['title']}")
                        print(f"Download completed! Title: {info_dict['title']}", flush=True)
                        link_queue.remove(link)
                    except Exception as e:
                        print(f"Error downloading video: {e}")
                    

        except utils.DownloadError as e:
            print(f"An error occurred: {e}")

    # Set the function to be called when the window is closed
    root.protocol("WM_DELETE_WINDOW", on_window_close)

    def paste_text():  
        clipboard_content = root.clipboard_get()
        link_entry.delete(0, END)
        link_entry.insert(0, clipboard_content)
        on_link_entry_change(None)

    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    context_menu = Menu(root, tearoff=0)
    context_menu.add_command(label="Paste", command=paste_text)


    # Create frames
    link_frame = Frame(root)
    format_frame = Frame(root)
    resolution_frame = Frame(root)
    buttons_frame = Frame(root)
    progresses_frame = Frame(root)


    # Create checkboxes
    link_label = Label(link_frame, text="Enter Video Link:")

    link_entry = Entry(link_frame, textvariable=link_var, width=80)
    link_entry.bind("<Button-3>", show_context_menu)
    # Bind the KeyRelease event to the link_entry widget
    link_entry.bind("<KeyRelease>", on_link_entry_change)
    download_button = Button(buttons_frame, text="Download", command=on_download_button_click)
    set_directory_button = Button(buttons_frame, text="Set Directory", command=set_directory)

    format_label = Label(format_frame, text="Choose Output Format:")
    format_checkbox_mp4 = Radiobutton(format_frame, text="mp3", variable=format_var, value="mp3", command=on_checkbox_click)
    format_checkbox_mp3 = Radiobutton(format_frame, text="mp4", variable=format_var, value="mp4", command=on_checkbox_click)

    resolution_label = Label(resolution_frame, text="Choose Resolution:")
    resolutions = ["2160p", "1440p", "1080p", "720p", "480p", "240p", "144p"]
    resolution_dropdown = OptionMenu(resolution_frame, resolution_var, *resolutions, command=on_checkbox_click)


    link_label.pack(side="left")
    link_entry.pack(side='left')
    download_button.pack(side='left')
    set_directory_button.pack(side='left')

    format_label.pack(side='left')
    format_checkbox_mp4.pack(side="left")
    format_checkbox_mp3.pack(side="left")

    resolution_label.pack(side="left")
    resolution_dropdown.pack(side='left')


    result_label = Label(root, text=f"Format: {format_var.get()}, Bit Rate: 256kb/s, Link: {link_var.get()}", wraplength=700)

    #progresses_label = Label(root, text="Waiting for link")

    link_frame.pack(pady=10)
    format_frame.pack(pady=10)
    resolution_frame.pack_forget()
    result_label.pack(pady=10)
    buttons_frame.pack(pady=10)
    progresses_frame.pack(pady=10)

def main():
    root = Tk()
    root.title("Youtube Down")
    root.geometry("720x480")

    choose_output_options(root)

    root.mainloop()

    print("Tkinter window closed. Exiting the script.")

if __name__ == "__main__":
    main()