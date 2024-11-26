import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import zipfile
import urllib.request
import shutil
import webbrowser

# Global variable to store the path to ffprobe
ffprobe_path = 'ffprobe'  # Default to 'ffprobe', assuming it's in PATH

# Function to check and install dependencies
def check_dependencies():
    try:
        # Check if FFmpeg is installed
        if not is_ffmpeg_installed():
            install_ffmpeg()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install dependencies: {e}")
        sys.exit(1)

# Function to check if FFmpeg is installed
def is_ffmpeg_installed():
    try:
        subprocess.run([ffprobe_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return True
    except FileNotFoundError:
        return False

# Function to install FFmpeg
def install_ffmpeg():
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    ffmpeg_zip = "ffmpeg.zip"
    install_path = os.path.join(os.getcwd(), "ffmpeg")

    try:
        print("Downloading FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)

        print("Extracting FFmpeg...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall(install_path)

        # Find the bin folder inside the extracted FFmpeg directory
        extracted_folders = os.listdir(install_path)
        if not extracted_folders:
            raise Exception("No files found after extracting FFmpeg.")
        ffmpeg_root_folder = os.path.join(install_path, extracted_folders[0])
        ffmpeg_bin = os.path.join(ffmpeg_root_folder, "bin")

        if not os.path.isdir(ffmpeg_bin):
            raise Exception(f"FFmpeg bin folder not found at {ffmpeg_bin}")

        # Add FFmpeg to PATH
        os.environ["PATH"] = ffmpeg_bin + os.pathsep + os.environ["PATH"]

        # Update the global ffprobe_path variable
        global ffprobe_path
        ffprobe_path = os.path.join(ffmpeg_bin, 'ffprobe.exe')

        # Clean up
        os.remove(ffmpeg_zip)
        print("FFmpeg installed and added to PATH.")
    except Exception as e:
        raise Exception(f"Failed to install FFmpeg: {e}")

# Function to get video codec, resolution, duration, and file size information
def get_video_info(file_path):
    try:
        env = os.environ.copy()  # Copy the environment variables
        result = subprocess.run(
            [ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=codec_name,width,height,duration', '-of', 'csv=p=0', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        if result.returncode == 0:
            data = result.stdout.strip().split(',')
            file_size = os.path.getsize(file_path)
            return {
                'codec': data[0],
                'width': int(float(data[1])),
                'height': int(float(data[2])),
                'duration': float(data[3]),
                'size': file_size
            }
        else:
            print(f"ffprobe error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        return None

# GUI Application
class VideoFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Filter App")
        self.root.geometry("600x680")
        self.root.resizable(False, False)  # Disable window resizing

        # Title and description
        title_label = tk.Label(root, text="Video Filter App", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        description_label = tk.Label(
            root,
            text="Select a folder and set your filtering criteria:\nCodec, Resolution, Duration, and File Size.",
            font=("Arial", 10)
        )
        description_label.pack(pady=5)

        # Folder selection
        self.folder_path = tk.StringVar()
        folder_label = tk.Label(root, text="Select Folder:")
        folder_label.pack(pady=5)
        folder_entry = tk.Entry(root, textvariable=self.folder_path, width=50)
        folder_entry.pack(pady=5)
        folder_button = tk.Button(root, text="Browse", command=self.select_folder)
        folder_button.pack(pady=5)

        # Codec selection
        self.codec_var = tk.StringVar()
        codec_label = tk.Label(root, text="Select Codec:")
        codec_label.pack(pady=5)
        self.codec_combobox = ttk.Combobox(root, textvariable=self.codec_var)
        self.codec_combobox['values'] = self.get_common_codecs()
        self.codec_combobox.pack(pady=5)

        # Resolution input
        resolution_label = tk.Label(root, text="Enter Minimum Resolution (e.g., 1920x1080):")
        resolution_label.pack(pady=5)
        self.resolution_entry = tk.Entry(root)
        self.resolution_entry.pack(pady=5)

        # Duration input
        duration_frame = tk.Frame(root)
        duration_frame.pack(pady=5)
        duration_label = tk.Label(duration_frame, text="Duration (seconds):")
        duration_label.pack(side="left")
        self.min_duration_entry = tk.Entry(duration_frame, width=10)
        self.min_duration_entry.pack(side="left", padx=5)
        duration_dash_label = tk.Label(duration_frame, text="to")
        duration_dash_label.pack(side="left")
        self.max_duration_entry = tk.Entry(duration_frame, width=10)
        self.max_duration_entry.pack(side="left", padx=5)

        # File size input
        size_frame = tk.Frame(root)
        size_frame.pack(pady=5)
        size_label = tk.Label(size_frame, text="File Size (MB):")
        size_label.pack(side="left")
        self.min_size_entry = tk.Entry(size_frame, width=10)
        self.min_size_entry.pack(side="left", padx=5)
        size_dash_label = tk.Label(size_frame, text="to")
        size_dash_label.pack(side="left")
        self.max_size_entry = tk.Entry(size_frame, width=10)
        self.max_size_entry.pack(side="left", padx=5)

        # Option to scan for codec, resolution, duration, size, or any combination
        self.scan_options = {
            'codec': tk.BooleanVar(value=False),
            'resolution': tk.BooleanVar(value=False),
            'duration': tk.BooleanVar(value=False),
            'size': tk.BooleanVar(value=False)
        }
        option_label = tk.Label(root, text="Filter by:")
        option_label.pack(pady=5)
        options_frame = tk.Frame(root)
        options_frame.pack(pady=5)
        tk.Checkbutton(
            options_frame, text="Codec", variable=self.scan_options['codec']
        ).pack(side="left", padx=5)
        tk.Checkbutton(
            options_frame, text="Resolution", variable=self.scan_options['resolution']
        ).pack(side="left", padx=5)
        tk.Checkbutton(
            options_frame, text="Duration", variable=self.scan_options['duration']
        ).pack(side="left", padx=5)
        tk.Checkbutton(
            options_frame, text="File Size", variable=self.scan_options['size']
        ).pack(side="left", padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=20)
        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack()

        # Run Button
        run_button = tk.Button(root, text="Run", command=self.filter_videos)
        run_button.pack(pady=10)

        # Output file
        output_label = tk.Label(root, text="Results will be saved in output.txt")
        output_label.pack(pady=5)

        # "Made by Clément GHANEME" Button
        self.website_button = tk.Button(root, text="Made by Clément GHANEME", command=self.open_website)
        self.website_button.pack(pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def get_common_codecs(self):
        return [
            # HAP family codecs
            "hap", "hap_alpha", "hap_q", "hap_q_alpha",
            # ProRes codecs
            "prores", "prores_aw", "prores_ks", "prores_lt", "prores_proxy", "prores_hq",
            # Other codecs
            "h264", "hevc", "vp9", "av1", "mpeg4", "wmv", "theora",
            "vp8", "mpeg2video", "divx", "xvid", "h263", "h261",
            "flv1", "mpeg1video", "huffyuv", "dnxhd", "cinepak", "indeo3",
            "msmpeg4v2", "rv10", "rv20", "svq1", "svq3", "vp6",
            "wmv1", "wmv2", "h265", "vp7", "vp8", "vp9", "av1", "mpeg2video"
        ]

    def filter_videos(self):
        folder = self.folder_path.get()
        codec = self.codec_var.get()
        resolution = self.resolution_entry.get()
        min_duration = self.min_duration_entry.get()
        max_duration = self.max_duration_entry.get()
        min_size = self.min_size_entry.get()
        max_size = self.max_size_entry.get()
        scan_options = self.scan_options

        if not folder:
            messagebox.showerror("Error", "Please select a folder.")
            return

        if scan_options['codec'].get() and not codec:
            messagebox.showerror("Error", "Please specify a codec.")
            return

        if scan_options['resolution'].get() and not resolution:
            messagebox.showerror("Error", "Please specify a resolution.")
            return

        if scan_options['duration'].get():
            try:
                min_duration = float(min_duration) if min_duration else 0
                max_duration = float(max_duration) if max_duration else float('inf')
            except ValueError:
                messagebox.showerror("Error", "Invalid duration values.")
                return
        else:
            min_duration = 0
            max_duration = float('inf')

        if scan_options['size'].get():
            try:
                min_size = float(min_size) * 1_048_576 if min_size else 0  # Convert MB to bytes
                max_size = float(max_size) * 1_048_576 if max_size else float('inf')
            except ValueError:
                messagebox.showerror("Error", "Invalid file size values.")
                return
        else:
            min_size = 0
            max_size = float('inf')

        min_width, min_height = 0, 0
        if scan_options['resolution'].get():
            try:
                min_width, min_height = map(int, resolution.lower().split('x'))
            except ValueError:
                messagebox.showerror("Error", "Invalid resolution format. Use 'WIDTHxHEIGHT'.")
                return

        # Collect all video files
        video_files = []
        for root_dir, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv')):
                    file_path = os.path.join(root_dir, file)
                    video_files.append(file_path)

        total_files = len(video_files)
        if total_files == 0:
            messagebox.showinfo("No Videos Found", "No video files found in the selected folder.")
            return

        # Configure progress bar
        self.progress['maximum'] = total_files
        self.progress['value'] = 0
        self.progress_label.config(text="Processing videos...")
        self.root.update_idletasks()

        # Search for videos
        result_files = []
        for idx, file_path in enumerate(video_files, 1):
            info = get_video_info(file_path)
            if info:
                matches = True

                if scan_options['codec'].get() and codec and info['codec'] != codec:
                    matches = False

                if scan_options['resolution'].get() and (
                    info['width'] < min_width or info['height'] < min_height
                ):
                    matches = False

                if scan_options['duration'].get() and not (min_duration <= info['duration'] <= max_duration):
                    matches = False

                if scan_options['size'].get() and not (min_size <= info['size'] <= max_size):
                    matches = False

                if matches:
                    result_files.append(file_path)

            # Update progress bar
            self.progress['value'] = idx
            self.progress.update_idletasks()
            self.progress_label.config(text=f"Processing {idx}/{total_files} files...")
            self.root.update_idletasks()

        # Save results to output.txt
        with open("output.txt", "w") as f:
            for file in result_files:
                f.write(file + "\n")

        self.progress_label.config(text="Processing completed.")
        messagebox.showinfo("Completed", f"Found {len(result_files)} matching videos. Results saved to output.txt.")

    def open_website(self):
        webbrowser.open("https://clement.business")

# Check dependencies and run the application
if __name__ == "__main__":
    check_dependencies()
    root = tk.Tk()
    app = VideoFilterApp(root)
    root.mainloop()
