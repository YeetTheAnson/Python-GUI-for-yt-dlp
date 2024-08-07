import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import yt_dlp

def fetch_info():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Input Error", "Please enter a valid URL.")
        return

    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        title = info_dict.get('title', 'N/A')
        upload_date = info_dict.get('upload_date', 'N/A')
        formats = info_dict.get('formats', [])
        available_formats = "\n".join(
            [f"{fmt['format_id']} - {fmt['resolution']} - {fmt['ext']} - {fmt['acodec']}/{fmt['vcodec']}" for fmt in formats]
        )

        title_var.set(title)
        date_var.set(upload_date)
        formats_var.set(available_formats)

def download_video():
    url = url_entry.get()
    format_id = format_entry.get()
    if not url or not format_id:
        messagebox.showwarning("Input Error", "Please enter a valid URL and format ID.")
        return

    ydl_opts = {'format': format_id}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            messagebox.showinfo("Success", "Download completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("YouTube Video Downloader")
sv_ttk.set_theme("dark")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ttk.Label(frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W)
url_entry = ttk.Entry(frame, width=40)
url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

fetch_button = ttk.Button(frame, text="Fetch Info", command=fetch_info)
fetch_button.grid(row=0, column=2, sticky=tk.E)

ttk.Label(frame, text="Title:").grid(row=1, column=0, sticky=tk.W)
title_var = tk.StringVar()
ttk.Label(frame, textvariable=title_var).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Upload Date:").grid(row=2, column=0, sticky=tk.W)
date_var = tk.StringVar()
ttk.Label(frame, textvariable=date_var).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Available Formats:").grid(row=3, column=0, sticky=tk.W)
formats_var = tk.StringVar()
formats_label = ttk.Label(frame, textvariable=formats_var, wraplength=400, justify=tk.LEFT)
formats_label.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E))

ttk.Label(frame, text="Format ID:").grid(row=4, column=0, sticky=tk.W)
format_entry = ttk.Entry(frame, width=10)
format_entry.grid(row=4, column=1, sticky=tk.W)

download_button = ttk.Button(frame, text="Download Video", command=download_video)
download_button.grid(row=4, column=2, sticky=tk.E)

root.mainloop()
