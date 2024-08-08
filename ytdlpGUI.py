import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
import yt_dlp
from datetime import datetime

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        sv_ttk.set_theme("dark")
        self.formats_info = []
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        ttk.Label(frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_entry = ttk.Entry(frame, width=40)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        fetch_button = ttk.Button(frame, text="Fetch Info", command=self.fetch_info)
        fetch_button.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)

        ttk.Label(frame, text="Title:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.title_var).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(frame, text="Upload Date:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.date_var).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(frame, text="File Format:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.format_combobox = ttk.Combobox(frame, state="readonly")
        self.format_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.format_combobox.bind("<<ComboboxSelected>>", self.update_resolutions)

        ttk.Label(frame, text="Resolution:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.resolution_combobox = ttk.Combobox(frame, state="readonly")
        self.resolution_combobox.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.resolution_combobox.bind("<<ComboboxSelected>>", self.update_codecs)

        ttk.Label(frame, text="Codec:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.codec_combobox = ttk.Combobox(frame, state="readonly")
        self.codec_combobox.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.download_button = ttk.Button(frame, text="Download Video", command=self.download_video)
        self.download_button.grid(row=6, column=1, sticky=tk.E, padx=5, pady=5)
        self.download_button.state(['disabled'])

    def fetch_info(self):
        url = self.url_entry.get()
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
            if upload_date != 'N/A':
                upload_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%d %B %Y')
            self.formats_info = info_dict.get('formats', [])
            
            file_formats = sorted(set(fmt['ext'] for fmt in self.formats_info))
            self.format_combobox['values'] = file_formats
            self.format_combobox.set('')
            self.resolution_combobox.set('')
            self.codec_combobox.set('')

            self.title_var.set(title)
            self.date_var.set(upload_date)

    def update_resolutions(self, event):
        selected_format = self.format_combobox.get()
        if not selected_format:
            return

        resolutions = sorted(set(fmt.get('resolution', fmt.get('asr', 'N/A')) 
                                 for fmt in self.formats_info 
                                 if fmt['ext'] == selected_format))
        self.resolution_combobox['values'] = resolutions
        self.resolution_combobox.set('')
        self.codec_combobox.set('')

    def update_codecs(self, event):
        selected_format = self.format_combobox.get()
        selected_resolution = self.resolution_combobox.get()
        if not selected_format or not selected_resolution:
            return

        codecs = sorted(set(f"{fmt.get('acodec', '')}/{fmt.get('vcodec', '')}".strip('/')
                            for fmt in self.formats_info 
                            if fmt['ext'] == selected_format and 
                               (fmt.get('resolution', fmt.get('asr', 'N/A')) == selected_resolution)))
        self.codec_combobox['values'] = codecs
        self.codec_combobox.set('')

        if codecs:
            self.download_button.state(['!disabled'])
        else:
            self.download_button.state(['disabled'])

    def download_video(self):
        url = self.url_entry.get()
        selected_format = self.format_combobox.get()
        selected_resolution = self.resolution_combobox.get()
        selected_codec = self.codec_combobox.get()

        if not url or not selected_format or not selected_resolution or not selected_codec:
            messagebox.showwarning("Input Error", "Please enter a valid URL and select all options.")
            return

        format_id = next((fmt['format_id'] for fmt in self.formats_info
                          if fmt['ext'] == selected_format and 
                          (fmt.get('resolution', fmt.get('asr', 'N/A')) == selected_resolution) and 
                          (f"{fmt.get('acodec', '')}/{fmt.get('vcodec', '')}".strip('/') == selected_codec)), None)

        if not format_id:
            messagebox.showerror("Error", "No matching format found.")
            return

        ydl_opts = {'format': format_id}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

        messagebox.showinfo("Success", "Download completed successfully.")

root = tk.Tk()
app = VideoDownloaderApp(root)
root.mainloop()
