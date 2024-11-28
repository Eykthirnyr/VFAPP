import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import zipfile
import urllib.request
import shutil
import webbrowser
import csv
import json

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

# Updated get_video_info function
def get_video_info(file_path):
    try:
        env = os.environ.copy()  # Copy the environment variables
        result = subprocess.run(
            [ffprobe_path, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=codec_name,width,height,duration,bit_rate,r_frame_rate,display_aspect_ratio,sample_aspect_ratio,color_space,bits_per_raw_sample,pix_fmt', '-of', 'json', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        if result.returncode == 0:
            ffprobe_data = json.loads(result.stdout)
            # Extract stream info
            stream = ffprobe_data['streams'][0]
            # Now extract the fields with proper handling
            codec_name = stream.get('codec_name', 'Unknown')
            width = int(stream.get('width', 0))
            height = int(stream.get('height', 0))
            duration = float(stream.get('duration', 0))
            bit_rate = int(stream.get('bit_rate', 0)) if stream.get('bit_rate') else 0
            r_frame_rate = stream.get('r_frame_rate', '0/1')
            display_aspect_ratio = stream.get('display_aspect_ratio', 'Unknown')
            sample_aspect_ratio = stream.get('sample_aspect_ratio', 'Unknown')
            color_space = stream.get('color_space', 'Unknown')
            bits_per_raw_sample = stream.get('bits_per_raw_sample', 'N/A')
            pix_fmt = stream.get('pix_fmt', 'Unknown')

            # Calculate framerate
            if r_frame_rate != 'N/A':
                num, denom = r_frame_rate.split('/')
                framerate = float(num) / float(denom) if float(denom) != 0 else 0
            else:
                framerate = 0

            file_size = os.path.getsize(file_path)
            # Check if bitrate is variable or constant
            bitrate_mode = 'Constant' if bit_rate != 0 else 'Variable'
            # Handle missing bitrate
            bitrate = bit_rate if bit_rate != 0 else 0

            # Handle bit depth
            if bits_per_raw_sample != 'N/A' and bits_per_raw_sample.isdigit():
                bit_depth = int(bits_per_raw_sample)
            else:
                # Attempt to infer bit depth from pix_fmt
                bit_depth = infer_bit_depth_from_pix_fmt(pix_fmt)

            # Infer color space from pix_fmt
            color_space = infer_color_space_from_pix_fmt(pix_fmt)

            # Calculate display aspect ratio if it's 'Unknown' or '0:1' or 'N/A'
            if display_aspect_ratio in ['Unknown', '0:1', 'N/A']:
                gcd = lambda a, b: gcd(b, a % b) if b else a
                ratio_gcd = gcd(width, height)
                display_aspect_ratio = f"{width // ratio_gcd}:{height // ratio_gcd}"

            return {
                'codec': codec_name,
                'width': width,
                'height': height,
                'duration': duration,
                'bitrate': bitrate,
                'bitrate_mode': bitrate_mode,
                'size': file_size,
                'framerate': framerate,
                'display_aspect_ratio': display_aspect_ratio,
                'color_space': color_space,
                'bit_depth': bit_depth
            }
        else:
            print(f"ffprobe error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        return None

# Function to infer bit depth from pixel format
def infer_bit_depth_from_pix_fmt(pix_fmt):
    # Common pixel formats and their bit depths
    pix_fmt_bit_depth = {
        'yuv420p': 8,
        'yuv422p': 8,
        'yuv444p': 8,
        'yuv420p10le': 10,
        'yuv422p10le': 10,
        'yuv444p10le': 10,
        'yuv420p12le': 12,
        'yuv422p12le': 12,
        'yuv444p12le': 12,
        'yuv420p16le': 16,
        'yuv422p16le': 16,
        'yuv444p16le': 16,
        'rgb24': 8,
        'rgba': 8,
        'rgb48le': 16,
        'gbrp': 8,
        'gbrp10le': 10,
        'gbrp12le': 12,
        'gbrp16le': 16,
        # Add more mappings as needed
    }
    return pix_fmt_bit_depth.get(pix_fmt, 0)

# Function to infer color space from pixel format
def infer_color_space_from_pix_fmt(pix_fmt):
    # Mapping of pix_fmt to color space
    pix_fmt_color_space = {
        'yuv420p': 'YUV',
        'yuv422p': 'YUV',
        'yuv444p': 'YUV',
        'yuv420p10le': 'YUV',
        'yuv422p10le': 'YUV',
        'yuv444p10le': 'YUV',
        'yuv420p12le': 'YUV',
        'yuv422p12le': 'YUV',
        'yuv444p12le': 'YUV',
        'yuv420p16le': 'YUV',
        'yuv422p16le': 'YUV',
        'yuv444p16le': 'YUV',
        'nv12': 'YUV',
        'rgb24': 'RGB',
        'rgba': 'RGB',
        'rgb48le': 'RGB',
        'gbrp': 'RGB',
        'gbrp10le': 'RGB',
        'gbrp12le': 'RGB',
        'gbrp16le': 'RGB',
        # Add more mappings as needed
    }
    return pix_fmt_color_space.get(pix_fmt, 'Unknown')

# Tooltip class
class ToolTip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tw = None

    def enter(self, event=None):
        x = y = 0
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        # Create a toplevel window
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # Remove all window decorations
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw, text=self.text, justify='left',
            background='#ffffe0', relief='solid', borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tw:
            self.tw.destroy()

# GUI Application
class VideoFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Filter App")
        self.root.geometry("700x860")
        self.root.resizable(False, False)  # Disable window resizing

        # Title and description
        title_label = tk.Label(root, text="Video Filter App", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        description_label = tk.Label(
            root,
            text="Select a folder and set your filtering criteria:\nCodec, Resolution, Framerate, Duration, File Size, Bitrate, Display Aspect Ratio, Color Space, and Bit Depth.",
            font=("Arial", 10)
        )
        description_label.pack(pady=5)

        # Main frame for alignment
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10)

        # Folder selection
        self.folder_path = tk.StringVar()
        folder_frame = tk.Frame(main_frame)
        folder_frame.pack(pady=5, fill='x')
        folder_label = tk.Label(folder_frame, text="Select Folder:", width=20, anchor='w')
        folder_label.pack(side='left', padx=5)
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, width=50)
        folder_entry.pack(side='left', padx=5)
        folder_button = tk.Button(folder_frame, text="Browse", command=self.select_folder)
        folder_button.pack(side='left', padx=5)

        # Codec selection
        codec_frame = tk.Frame(main_frame)
        codec_frame.pack(pady=5, fill='x')
        codec_label = tk.Label(codec_frame, text="Select Codec:", width=20, anchor='w')
        codec_label.pack(side='left', padx=5)
        self.codec_var = tk.StringVar()
        self.codec_combobox = ttk.Combobox(codec_frame, textvariable=self.codec_var, width=47)
        self.codec_combobox['values'] = self.get_common_codecs()
        self.codec_combobox.pack(side='left', padx=5)

        # Resolution input
        resolution_frame = tk.Frame(main_frame)
        resolution_frame.pack(pady=5, fill='x')
        resolution_label = tk.Label(resolution_frame, text="Resolution (WxH):", width=20, anchor='w')
        resolution_label.pack(side='left', padx=5)
        self.min_resolution_entry = tk.Entry(resolution_frame, width=15)
        self.min_resolution_entry.pack(side='left', padx=5)
        resolution_dash_label = tk.Label(resolution_frame, text="to")
        resolution_dash_label.pack(side='left')
        self.max_resolution_entry = tk.Entry(resolution_frame, width=15)
        self.max_resolution_entry.pack(side='left', padx=5)

        # Framerate input
        framerate_frame = tk.Frame(main_frame)
        framerate_frame.pack(pady=5, fill='x')
        framerate_label = tk.Label(framerate_frame, text="Framerate (fps):", width=20, anchor='w')
        framerate_label.pack(side='left', padx=5)
        self.min_framerate_entry = tk.Entry(framerate_frame, width=15)
        self.min_framerate_entry.pack(side='left', padx=5)
        framerate_dash_label = tk.Label(framerate_frame, text="to")
        framerate_dash_label.pack(side='left')
        self.max_framerate_entry = tk.Entry(framerate_frame, width=15)
        self.max_framerate_entry.pack(side='left', padx=5)

        # Duration input
        duration_frame = tk.Frame(main_frame)
        duration_frame.pack(pady=5, fill='x')
        duration_label = tk.Label(duration_frame, text="Duration (seconds):", width=20, anchor='w')
        duration_label.pack(side='left', padx=5)
        self.min_duration_entry = tk.Entry(duration_frame, width=15)
        self.min_duration_entry.pack(side='left', padx=5)
        duration_dash_label = tk.Label(duration_frame, text="to")
        duration_dash_label.pack(side='left')
        self.max_duration_entry = tk.Entry(duration_frame, width=15)
        self.max_duration_entry.pack(side='left', padx=5)

        # File size input
        size_frame = tk.Frame(main_frame)
        size_frame.pack(pady=5, fill='x')
        size_label = tk.Label(size_frame, text="File Size (MB):", width=20, anchor='w')
        size_label.pack(side='left', padx=5)
        self.min_size_entry = tk.Entry(size_frame, width=15)
        self.min_size_entry.pack(side='left', padx=5)
        size_dash_label = tk.Label(size_frame, text="to")
        size_dash_label.pack(side='left')
        self.max_size_entry = tk.Entry(size_frame, width=15)
        self.max_size_entry.pack(side='left', padx=5)

        # Bitrate input
        bitrate_frame = tk.Frame(main_frame)
        bitrate_frame.pack(pady=5, fill='x')
        bitrate_label = tk.Label(bitrate_frame, text="Bitrate (kbps):", width=20, anchor='w')
        bitrate_label.pack(side='left', padx=5)
        self.min_bitrate_entry = tk.Entry(bitrate_frame, width=15)
        self.min_bitrate_entry.pack(side='left', padx=5)
        bitrate_dash_label = tk.Label(bitrate_frame, text="to")
        bitrate_dash_label.pack(side='left')
        self.max_bitrate_entry = tk.Entry(bitrate_frame, width=15)
        self.max_bitrate_entry.pack(side='left', padx=5)

        # Bitrate mode selection
        bitrate_mode_frame = tk.Frame(main_frame)
        bitrate_mode_frame.pack(pady=5, fill='x')
        bitrate_mode_label = tk.Label(bitrate_mode_frame, text="Bitrate Mode:", width=20, anchor='w')
        bitrate_mode_label.pack(side='left', padx=5)
        self.bitrate_mode_var = tk.StringVar()
        self.bitrate_mode_var.set("Any")  # Default value
        bitrate_mode_options_frame = tk.Frame(bitrate_mode_frame)
        bitrate_mode_options_frame.pack(side='left')
        ttk.Radiobutton(
            bitrate_mode_options_frame, text="Any", variable=self.bitrate_mode_var, value="Any"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            bitrate_mode_options_frame, text="Variable", variable=self.bitrate_mode_var, value="Variable"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            bitrate_mode_options_frame, text="Constant", variable=self.bitrate_mode_var, value="Constant"
        ).pack(side="left", padx=5)

        # Display Aspect Ratio input
        dar_frame = tk.Frame(main_frame)
        dar_frame.pack(pady=5, fill='x')
        dar_label = tk.Label(dar_frame, text="Display Aspect Ratio:", width=20, anchor='w')
        dar_label.pack(side='left', padx=5)
        self.dar_entry = tk.Entry(dar_frame, width=15)
        self.dar_entry.pack(side='left', padx=5)
        ToolTip(self.dar_entry, "Enter aspect ratio (e.g., 16:9). Leave blank for any.")

        # Color Space input
        color_space_frame = tk.Frame(main_frame)
        color_space_frame.pack(pady=5, fill='x')
        color_space_label = tk.Label(color_space_frame, text="Color Space:", width=20, anchor='w')
        color_space_label.pack(side='left', padx=5)
        self.color_space_var = tk.StringVar()
        self.color_space_combobox = ttk.Combobox(color_space_frame, textvariable=self.color_space_var, width=47)
        self.color_space_combobox['values'] = self.get_color_spaces()
        self.color_space_combobox.current(0)  # Set "Any" as default
        self.color_space_combobox.pack(side='left', padx=5)

        # Bit Depth input
        bit_depth_frame = tk.Frame(main_frame)
        bit_depth_frame.pack(pady=5, fill='x')
        bit_depth_label = tk.Label(bit_depth_frame, text="Bit Depth:", width=20, anchor='w')
        bit_depth_label.pack(side='left', padx=5)
        self.min_bit_depth_entry = tk.Entry(bit_depth_frame, width=15)
        self.min_bit_depth_entry.pack(side='left', padx=5)
        bit_depth_dash_label = tk.Label(bit_depth_frame, text="to")
        bit_depth_dash_label.pack(side='left')
        self.max_bit_depth_entry = tk.Entry(bit_depth_frame, width=15)
        self.max_bit_depth_entry.pack(side='left', padx=5)

        # Option to scan for codec, resolution, duration, size, bitrate, or any combination
        options_label = tk.Label(main_frame, text="Filter by:")
        options_label.pack(pady=5)
        options_frame1 = tk.Frame(main_frame)
        options_frame1.pack(pady=5, fill='x')
        options_frame2 = tk.Frame(main_frame)
        options_frame2.pack(pady=5, fill='x')

        self.scan_options = {
            'codec': tk.BooleanVar(value=False),
            'resolution': tk.BooleanVar(value=False),
            'duration': tk.BooleanVar(value=False),
            'size': tk.BooleanVar(value=False),
            'bitrate': tk.BooleanVar(value=False),
            'bitrate_mode': tk.BooleanVar(value=False),
            'framerate': tk.BooleanVar(value=False),
            'dar': tk.BooleanVar(value=False),
            'color_space': tk.BooleanVar(value=False),
            'bit_depth': tk.BooleanVar(value=False)
        }

        codec_checkbox = tk.Checkbutton(
            options_frame1, text="Codec", variable=self.scan_options['codec']
        )
        codec_checkbox.pack(side="left", padx=5)
        resolution_checkbox = tk.Checkbutton(
            options_frame1, text="Resolution", variable=self.scan_options['resolution']
        )
        resolution_checkbox.pack(side="left", padx=5)
        duration_checkbox = tk.Checkbutton(
            options_frame1, text="Duration", variable=self.scan_options['duration']
        )
        duration_checkbox.pack(side="left", padx=5)
        size_checkbox = tk.Checkbutton(
            options_frame1, text="File Size", variable=self.scan_options['size']
        )
        size_checkbox.pack(side="left", padx=5)
        bitrate_checkbox = tk.Checkbutton(
            options_frame1, text="Bitrate", variable=self.scan_options['bitrate']
        )
        bitrate_checkbox.pack(side="left", padx=5)
        bitrate_mode_checkbox = tk.Checkbutton(
            options_frame1, text="Bitrate Mode", variable=self.scan_options['bitrate_mode']
        )
        bitrate_mode_checkbox.pack(side="left", padx=5)

        framerate_checkbox = tk.Checkbutton(
            options_frame2, text="Framerate", variable=self.scan_options['framerate']
        )
        framerate_checkbox.pack(side="left", padx=5)
        dar_checkbox = tk.Checkbutton(
            options_frame2, text="Aspect Ratio", variable=self.scan_options['dar']
        )
        dar_checkbox.pack(side="left", padx=5)
        color_space_checkbox = tk.Checkbutton(
            options_frame2, text="Color Space", variable=self.scan_options['color_space']
        )
        color_space_checkbox.pack(side="left", padx=5)
        bit_depth_checkbox = tk.Checkbutton(
            options_frame2, text="Bit Depth", variable=self.scan_options['bit_depth']
        )
        bit_depth_checkbox.pack(side="left", padx=5)

        # Add tooltips to the checkboxes
        ToolTip(codec_checkbox, "Filter videos by codec (e.g., h264, prores).")
        ToolTip(resolution_checkbox, "Filter videos by resolution range.")
        ToolTip(duration_checkbox, "Filter videos by duration range (in seconds).")
        ToolTip(size_checkbox, "Filter videos by file size range (in MB).")
        ToolTip(bitrate_checkbox, "Filter videos by bitrate range (in kbps).")
        ToolTip(bitrate_mode_checkbox, "Filter videos by bitrate mode (Variable or Constant).")
        ToolTip(framerate_checkbox, "Filter videos by framerate range (in fps).")
        ToolTip(dar_checkbox, "Filter videos by Display Aspect Ratio.")
        ToolTip(color_space_checkbox, "Filter videos by Color Space.")
        ToolTip(bit_depth_checkbox, "Filter videos by Bit Depth.")

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.pack(pady=20)
        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack()

        # Run Button
        run_button = tk.Button(root, text="Run", command=self.filter_videos)
        run_button.pack(pady=10)
        ToolTip(run_button, "Click to start filtering videos based on selected criteria.")

        # View Results Button (initially disabled)
        self.view_results_button = tk.Button(root, text="View Results", command=self.view_results)
        self.view_results_button.pack(pady=5)
        self.view_results_button.config(state="disabled")

        # Output file
        output_label = tk.Label(root, text="Results will be saved in output.txt")
        output_label.pack(pady=5)

        # "Made by Clément GHANEME" Button
        self.website_button = tk.Button(root, text="Made by Clément GHANEME", command=self.open_website)
        self.website_button.pack(pady=10)

        # Store results
        self.result_files_info = []

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

    def get_color_spaces(self):
        return [
            "Any",
            "sRGB",
            "Adobe RGB",
            "ProPhoto RGB",
            "Rec. 709",
            "Rec. 2020",
            "DCI-P3",
            "Apple RGB",
            "CMYK",
            "CMY",
            "Gray",
            "YUV",
            "CIEXYZ",
            "CIE Lab (L*a*b*)",
            "CIE Luv",
            "HSV",
            "HSL",
            "HSB",
            "YCbCr",
            "YIQ",
            "YPbPr",
            "NTSC RGB",
            "PAL/SECAM RGB",
            "ACES",
            "Linear RGB"
        ]

    def filter_videos(self):
        folder = self.folder_path.get()
        codec = self.codec_var.get()
        min_resolution = self.min_resolution_entry.get()
        max_resolution = self.max_resolution_entry.get()
        min_duration = self.min_duration_entry.get()
        max_duration = self.max_duration_entry.get()
        min_size = self.min_size_entry.get()
        max_size = self.max_size_entry.get()
        min_bitrate = self.min_bitrate_entry.get()
        max_bitrate = self.max_bitrate_entry.get()
        bitrate_mode = self.bitrate_mode_var.get()
        min_framerate = self.min_framerate_entry.get()
        max_framerate = self.max_framerate_entry.get()
        dar = self.dar_entry.get()
        color_space = self.color_space_var.get()
        min_bit_depth = self.min_bit_depth_entry.get()
        max_bit_depth = self.max_bit_depth_entry.get()
        scan_options = self.scan_options

        if not folder:
            messagebox.showerror("Error", "Please select a folder.")
            return

        if scan_options['codec'].get() and not codec:
            messagebox.showerror("Error", "Please specify a codec.")
            return

        if scan_options['resolution'].get() and not (min_resolution or max_resolution):
            messagebox.showerror("Error", "Please specify minimum and/or maximum resolution.")
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

        if scan_options['bitrate'].get():
            try:
                min_bitrate = float(min_bitrate) * 1000 if min_bitrate else 0  # Convert kbps to bps
                max_bitrate = float(max_bitrate) * 1000 if max_bitrate else float('inf')
            except ValueError:
                messagebox.showerror("Error", "Invalid bitrate values.")
                return
        else:
            min_bitrate = 0
            max_bitrate = float('inf')

        # Framerate inputs
        if scan_options['framerate'].get():
            try:
                min_framerate = float(min_framerate) if min_framerate else 0
                max_framerate = float(max_framerate) if max_framerate else float('inf')
            except ValueError:
                messagebox.showerror("Error", "Invalid framerate values.")
                return
        else:
            min_framerate = 0
            max_framerate = float('inf')

        # Bit Depth inputs
        if scan_options['bit_depth'].get():
            try:
                min_bit_depth = int(min_bit_depth) if min_bit_depth else 0
                max_bit_depth = int(max_bit_depth) if max_bit_depth else float('inf')
            except ValueError:
                messagebox.showerror("Error", "Invalid bit depth values.")
                return
        else:
            min_bit_depth = 0
            max_bit_depth = float('inf')

        # Resolution inputs
        if scan_options['resolution'].get():
            # Min resolution
            if min_resolution:
                try:
                    min_width, min_height = map(int, min_resolution.lower().split('x'))
                except ValueError:
                    messagebox.showerror("Error", "Invalid minimum resolution format. Use 'WIDTHxHEIGHT'.")
                    return
            else:
                min_width, min_height = 0, 0
            # Max resolution
            if max_resolution:
                try:
                    max_width, max_height = map(int, max_resolution.lower().split('x'))
                except ValueError:
                    messagebox.showerror("Error", "Invalid maximum resolution format. Use 'WIDTHxHEIGHT'.")
                    return
            else:
                max_width, max_height = float('inf'), float('inf')
        else:
            min_width, min_height = 0, 0
            max_width, max_height = float('inf'), float('inf')

        # Display Aspect Ratio
        if scan_options['dar'].get():
            if dar:
                dar = dar.strip()
            else:
                messagebox.showerror("Error", "Please specify a Display Aspect Ratio.")
                return
        else:
            dar = None

        # Color Space
        if scan_options['color_space'].get():
            if color_space == "Any":
                color_space = None
        else:
            color_space = None

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

        # Clear previous results
        self.result_files_info = []

        # Search for videos
        for idx, file_path in enumerate(video_files, 1):
            info = get_video_info(file_path)
            if info:
                matches = True

                if scan_options['codec'].get() and codec and info['codec'] != codec:
                    matches = False

                if scan_options['resolution'].get() and (
                    info['width'] < min_width or info['width'] > max_width or
                    info['height'] < min_height or info['height'] > max_height
                ):
                    matches = False

                if scan_options['duration'].get() and not (min_duration <= info['duration'] <= max_duration):
                    matches = False

                if scan_options['size'].get() and not (min_size <= info['size'] <= max_size):
                    matches = False

                if scan_options['bitrate'].get() and not (min_bitrate <= info['bitrate'] <= max_bitrate):
                    matches = False

                if scan_options['bitrate_mode'].get():
                    if bitrate_mode != "Any" and info['bitrate_mode'].lower() != bitrate_mode.lower():
                        matches = False

                if scan_options['framerate'].get() and not (min_framerate <= info['framerate'] <= max_framerate):
                    matches = False

                if scan_options['dar'].get():
                    if dar and info['display_aspect_ratio'] != dar:
                        matches = False

                if scan_options['color_space'].get():
                    if color_space and info['color_space'].lower() != color_space.lower():
                        matches = False

                if scan_options['bit_depth'].get() and not (min_bit_depth <= info['bit_depth'] <= max_bit_depth):
                    matches = False

                if matches:
                    self.result_files_info.append({'path': file_path, 'info': info})

            # Update progress bar
            self.progress['value'] = idx
            self.progress.update_idletasks()
            self.progress_label.config(text=f"Processing {idx}/{total_files} files...")
            self.root.update_idletasks()

        # Save results to output.txt
        with open("output.txt", "w") as f:
            for result in self.result_files_info:
                f.write(result['path'] + "\n")

        self.progress_label.config(text="Processing completed.")
        messagebox.showinfo("Completed", f"Found {len(self.result_files_info)} matching videos. Results saved to output.txt.")

        # Enable View Results button
        self.view_results_button.config(state="normal")

    def view_results(self):
        if not self.result_files_info:
            messagebox.showinfo("No Results", "No matching videos to display.")
            return

        # Create a new top-level window
        results_window = tk.Toplevel(self.root)
        results_window.title("Filtered Videos")
        results_window.geometry("1000x600")

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(results_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a Treeview widget
        columns = ("Name", "Size (MB)", "Format", "Codec", "Bitrate (kbps)", "Bitrate Mode", "Framerate", "DAR", "Color Space", "Bit Depth")
        tree = ttk.Treeview(results_window, columns=columns, show='headings', yscrollcommand=scrollbar.set)
        tree.pack(expand=True, fill='both')

        # Configure the scrollbar
        scrollbar.config(command=tree.yview)

        # Define headings
        for col in columns:
            tree.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(tree, _col, False))
            tree.column(col, anchor='w')

        # Insert data into the treeview
        for result in self.result_files_info:
            file_path = result['path']
            info = result['info']
            file_name = os.path.basename(file_path)
            file_size_mb = f"{info['size'] / 1_048_576:.2f}"
            file_format = os.path.splitext(file_name)[1].lstrip('.').upper()
            codec = info['codec']
            bitrate_kbps = f"{info['bitrate'] / 1000:.2f}"
            bitrate_mode = info['bitrate_mode']
            framerate = f"{info['framerate']:.2f}"
            dar = info['display_aspect_ratio']
            color_space = info['color_space']
            bit_depth = info['bit_depth']

            tree.insert("", tk.END, values=(
                file_name,
                file_size_mb,
                file_format,
                codec,
                bitrate_kbps,
                bitrate_mode,
                framerate,
                dar,
                color_space,
                bit_depth
            ), tags=(file_path,))

        # Bind double-click event to open file
        def on_double_click(event):
            item = tree.identify('item', event.x, event.y)
            if item:
                file_path = tree.item(item, 'tags')[0]
                os.startfile(file_path)

        tree.bind("<Double-1>", on_double_click)

        # Add buttons
        buttons_frame = tk.Frame(results_window)
        buttons_frame.pack(pady=10)

        open_file_button = tk.Button(buttons_frame, text="Open File", command=lambda: self.open_selected_file(tree))
        open_file_button.pack(side="left", padx=5)

        open_folder_button = tk.Button(buttons_frame, text="Open Containing Folder", command=lambda: self.open_selected_folder(tree))
        open_folder_button.pack(side="left", padx=5)

        copy_button = tk.Button(buttons_frame, text="Copy File", command=lambda: self.copy_selected_file(tree))
        copy_button.pack(side="left", padx=5)

        delete_button = tk.Button(buttons_frame, text="Delete File", command=lambda: self.delete_selected_file(tree))
        delete_button.pack(side="left", padx=5)

        export_button = tk.Button(buttons_frame, text="Export to CSV", command=lambda: self.export_to_csv())
        export_button.pack(side="left", padx=5)

    def treeview_sort_column(self, tv, col, reverse):
        # Get the data to sort
        data_list = [(tv.set(k, col), k) for k in tv.get_children('')]
        # Try to convert data to float for numerical sorting
        try:
            data_list.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data_list.sort(reverse=reverse)
        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(data_list):
            tv.move(k, '', index)
        # Reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def open_selected_file(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file.")
            return
        file_path = tree.item(selected_item[0], 'tags')[0]
        os.startfile(file_path)

    def open_selected_folder(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file.")
            return
        file_path = tree.item(selected_item[0], 'tags')[0]
        folder_path = os.path.dirname(file_path)
        os.startfile(folder_path)

    def copy_selected_file(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file.")
            return
        file_path = tree.item(selected_item[0], 'tags')[0]
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if destination:
            try:
                shutil.copy(file_path, destination)
                messagebox.showinfo("Success", f"File copied to {destination}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {e}")

    def delete_selected_file(self, tree):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a file.")
            return
        file_path = tree.item(selected_item[0], 'tags')[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {os.path.basename(file_path)}?")
        if confirm:
            try:
                os.remove(file_path)
                tree.delete(selected_item[0])
                messagebox.showinfo("Deleted", "File deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")

    def export_to_csv(self):
        if not self.result_files_info:
            messagebox.showwarning("No Data", "No data available to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                    fieldnames = [
                        'File Path', 'File Name', 'Size (MB)', 'Format', 'Codec',
                        'Bitrate (kbps)', 'Bitrate Mode', 'Framerate', 'DAR', 'Color Space', 'Bit Depth'
                    ]
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    for result in self.result_files_info:
                        info = result['info']
                        writer.writerow({
                            'File Path': result['path'],
                            'File Name': os.path.basename(result['path']),
                            'Size (MB)': f"{info['size'] / 1_048_576:.2f}",
                            'Format': os.path.splitext(result['path'])[1].lstrip('.').upper(),
                            'Codec': info['codec'],
                            'Bitrate (kbps)': f"{info['bitrate'] / 1000:.2f}",
                            'Bitrate Mode': info['bitrate_mode'],
                            'Framerate': f"{info['framerate']:.2f}",
                            'DAR': info['display_aspect_ratio'],
                            'Color Space': info['color_space'],
                            'Bit Depth': info['bit_depth']
                        })
                messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")

    def open_website(self):
        webbrowser.open("https://clement.business")

# Check dependencies and run the application
if __name__ == "__main__":
    check_dependencies()
    root = tk.Tk()
    app = VideoFilterApp(root)
    root.mainloop()
