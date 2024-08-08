import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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


    #WARNING THE CREATE_WIDGETS FUNCTION IS FORMATTED BY CHATGPT AS IT'S THE GUI DESIGN AND NOT LOGIC HANDLING
    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

        # URL entry
        ttk.Label(frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_entry = ttk.Entry(frame, width=40)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Fetch Info button
        fetch_button = ttk.Button(frame, text="Fetch Info", command=self.fetch_info)
        fetch_button.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)

        # Title
        ttk.Label(frame, text="Title:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.title_var).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Upload Date
        ttk.Label(frame, text="Upload Date:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Label(frame, textvariable=self.date_var).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        # File Format
        ttk.Label(frame, text="File Format:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.format_combobox = ttk.Combobox(frame, state="readonly")
        self.format_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.format_combobox.bind("<<ComboboxSelected>>", self.update_resolutions)

        # Resolution
        ttk.Label(frame, text="Resolution:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.resolution_combobox = ttk.Combobox(frame, state="readonly")
        self.resolution_combobox.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.resolution_combobox.bind("<<ComboboxSelected>>", self.check_download_availability)

        # Save Location
        ttk.Label(frame, text="Save Location:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.folder_entry = ttk.Entry(frame, width=35)
        self.folder_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        browse_button = ttk.Button(frame, text="Browse", command=self.browse_folder)
        browse_button.grid(row=5, column=2, sticky=tk.E, padx=5, pady=5)

        # Download button
        self.download_button = ttk.Button(frame, text="Download Video", command=self.download_video)
        self.download_button.grid(row=6, column=1, sticky=tk.E, padx=5, pady=5)
        self.download_button.state(['disabled'])

    #Has text box to allow user to paste folder path, and browse button to browse for folder
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    #Get video title and upload time
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

            #Had to consult ChatGPT for this part of the code
            title = info_dict.get('title', 'N/A')
            upload_date = info_dict.get('upload_date', 'N/A')
            if upload_date != 'N/A':
                upload_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%d %B %Y')
            self.formats_info = info_dict.get('formats', [])
            
            
            file_formats = sorted(set(fmt['ext'] for fmt in self.formats_info))
            self.format_combobox['values'] = file_formats
            self.format_combobox.set('')
            self.resolution_combobox.set('')

            #Show title and time of upload
            self.title_var.set(title)
            self.date_var.set(upload_date)

    #Logic to handle available download options
    def update_resolutions(self, event):
        selected_format = self.format_combobox.get()
        if not selected_format:
            self.resolution_combobox['values'] = []
            self.resolution_combobox.set('')
            self.check_download_availability(None)
            return

        #Filter and get unique resolutions for the selected file format
        resolutions = sorted(set(fmt.get('resolution', fmt.get('asr', 'N/A')) 
                                 for fmt in self.formats_info 
                                 if fmt['ext'] == selected_format))
        self.resolution_combobox['values'] = resolutions
        self.resolution_combobox.set('')
        self.check_download_availability(None)

    def check_download_availability(self, event):
        selected_format = self.format_combobox.get()
        selected_resolution = self.resolution_combobox.get()

        #Download button disabled when options are not selected
        if selected_format and selected_resolution:
            format_id = next((fmt['format_id'] for fmt in self.formats_info
                              if fmt['ext'] == selected_format and 
                              (fmt.get('resolution', fmt.get('asr', 'N/A')) == selected_resolution)), None)
            if format_id:
                self.download_button.state(['!disabled'])
            else:
                self.download_button.state(['disabled'])
        else:
            self.download_button.state(['disabled'])

    def download_video(self):
        url = self.url_entry.get()
        selected_format = self.format_combobox.get()
        selected_resolution = self.resolution_combobox.get()
        save_location = self.folder_entry.get()

        if not url or not selected_format or not selected_resolution:
            messagebox.showwarning("Input Error", "Please enter a valid URL and select all options.")
            return

        if not save_location:
            messagebox.showwarning("Input Error", "Please select a save location.")
            return

        # Find the correct format_id for video and audio (both must be downloaded)
        video_format_id = next((fmt['format_id'] for fmt in self.formats_info
                                if fmt['ext'] == selected_format and 
                                (fmt.get('resolution', fmt.get('asr', 'N/A')) == selected_resolution)), None)

        if not video_format_id:
            messagebox.showerror("Error", "No matching format found.")
            return

        # yt-dlp will automatically select the best audio format to combine with the selected video format
        ydl_opts = {
            'format': f'{video_format_id}+bestaudio',  
            'merge_output_format': selected_format,  # Merge them into the selected format
            'outtmpl': f'{save_location}/%(title)s.%(ext)s',  
        }

        #error handle
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

        messagebox.showinfo("Success", "Download and merge completed successfully.")


root = tk.Tk()
app = VideoDownloaderApp(root)
root.mainloop()
