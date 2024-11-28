# VFAPP

## Video Filter App

A versatile video filtering application built with Python and Tkinter, designed to help users filter video files based on various criteria such as codec, resolution, duration, file size, bitrate, framerate, display aspect ratio, color space, and bit depth. This tool is perfect for quickly narrowing down video files in a directory according to specific needs.

---

## Features

### **Filtering Options**

- **Filter by Codec**:
  - Supports a wide range of codecs, including HAP (HAP, HAP-Q), ProRes, H.264, HEVC, VP9, AV1, and many more.
  
- **Filter by Resolution**:
  - Specify a range for resolution (e.g., 1920x1080 to 3840x2160) to include only high-resolution videos.

- **Filter by Duration**:
  - Define a range for video duration (e.g., 30 to 300 seconds) to filter videos by length.

- **Filter by File Size**:
  - Specify a range for file size (in MB) to include only videos within a desired size range.

- **Filter by Bitrate**:
  - Specify a range for average bitrate (in kbps).
  - Filter videos based on bitrate mode (Variable or Constant).

- **Filter by Framerate** (New!):
  - Specify a range for framerate (e.g., 24 to 60 fps).

- **Filter by Display Aspect Ratio** (New!):
  - Specify a display aspect ratio (e.g., 16:9).

- **Filter by Color Space** (New!):
  - Choose from a list of color spaces such as:
    - sRGB, Adobe RGB, Rec. 709, Rec. 2020, DCI-P3, YUV, and more.

- **Filter by Bit Depth** (New!):
  - Specify a range for bit depth (e.g., 8 to 16 bits).

- **Multi-Criteria Filtering**:
  - Combine any or all criteria for precise filtering.

---

### **User Interface Enhancements**

- **User-Friendly Interface**:
  - Intuitive GUI built with Tkinter.
  - Progress bar to track filtering progress.

- **Detailed Tooltips**:
  - Tooltips on filters explain their purpose and usage.
  - Tooltips on results table columns indicate sorting options.

---

### **Results Management**

- **View Filtered Results**:
  - Display filtered results in a sortable table directly within the app.
  - Columns include:
    - File Name
    - File Size (in MB)
    - Format
    - Codec
    - Bitrate (in kbps)
    - Bitrate Mode (Variable or Constant)
    - Framerate
    - Display Aspect Ratio
    - Color Space
    - Bit Depth

- **Sortable Columns**:
  - Click any column header to sort results:
    - Alphabetical sorting for text-based columns (e.g., Name, Codec, Bitrate Mode).
    - Numerical sorting for numeric columns (e.g., Size, Bitrate, Framerate).
  - Sorting toggles between ascending and descending order.

- **File Management Options**:
  - Open a video file or its containing folder.
  - Copy video files to a new location.
  - Delete files (with confirmation prompt).

- **Export to CSV**:
  - Export filtered results as a CSV file, including all displayed columns for easy data analysis.

---

## Installation

### Prerequisites

- Python 3.7 or later
- Required Python libraries:
  - `tkinter` (usually bundled with Python)
  - `subprocess`
  - `os`
  - `shutil`
  - `urllib`
  - `zipfile`
  - `webbrowser`
  - `csv`

---

## Usage

### 1. Launching the Application
- Run the script using Python:
  ```bash
  python VFAPP.py
  ```

### 2. Selecting a Folder
- Use the "Browse" button to select the directory containing your video files.

### 3. Setting Filters
- **Codec**: Select the desired codec from the dropdown menu (e.g., `hap`, `prores`, `h264`).
- **Resolution**: Enter the resolution range in `WIDTHxHEIGHT` format (e.g., `1920x1080` to `3840x2160`).
- **Duration**: Specify a duration range (in seconds).
- **File Size**: Specify a size range (in MB).
- **Bitrate**: Specify a bitrate range (in kbps) and choose between Variable or Constant bitrate mode.
- **Framerate**: Enter the framerate range (in fps).
- **Display Aspect Ratio**: Enter the aspect ratio (e.g., `16:9`).
- **Color Space**: Select a color space from the dropdown menu.
- **Bit Depth**: Specify a range for bit depth.

### 4. Combining Filters
- Use the checkboxes to enable or disable filters:
  - Codec
  - Resolution
  - Duration
  - File Size
  - Bitrate
  - Bitrate Mode
  - Framerate
  - Display Aspect Ratio
  - Color Space
  - Bit Depth
- Combine multiple filters for precise results.

### 5. Running the Filter
- Click "Run" to start the filtering process.
- The progress bar will show the status as videos are processed.

### 6. Viewing Results
- After filtering is complete:
  - Open the results in a sortable table.
  - Interact with each file:
    - Open the video.
    - Open its containing folder.
    - Copy or delete the file.
  - Export the results as a CSV file for further analysis.

---

## Supported Codecs

### HAP Family
- `hap`
- `hap_alpha`
- `hap_q`
- `hap_q_alpha`

### ProRes Family
- `prores`
- `prores_aw`
- `prores_ks`
- `prores_lt`
- `prores_proxy`
- `prores_hq`

### Other Codecs
- `h264`
- `hevc`
- `vp9`
- `av1`
- `mpeg4`
- `wmv`
- `vp8`
- `mpeg2video`
- `divx`
- `xvid`
- `h263`
- `h261`
- `flv1`
- `mpeg1video`
- `huffyuv`
- `dnxhd`
- `cinepak`
- `indeo3`
- `msmpeg4v2`
- `rv10`
- `rv20`
- `svq1`
- `svq3`
- `vp6`
- `wmv1`
- `wmv2`

---

## Development

### Key Libraries

- `subprocess`: For executing FFmpeg commands.
- `os`: File and directory operations.
- `tkinter`: GUI framework.
- `zipfile` & `urllib`: For downloading and extracting FFmpeg.
- `csv`: For exporting results as a CSV file.

---

## Screenshots

![Screenshot_3](https://github.com/user-attachments/assets/72db33cc-516e-470e-89be-ef4312e3e144)

![Screenshot_4](https://github.com/user-attachments/assets/c4d71af0-7003-44bb-9747-2905fbfaccb4)

---

## Author

**Clément GHANEME**

- [Website](https://clement.business)
- Initial Release: 26/11/2024

## Changelog

### [1.2.0] - 28/11/2024

#### Added

**Framerate Filtering:**

- Added input fields to specify minimum and maximum framerate (in fps).
- Enhanced the filtering logic to include these new options.
- Framerate information is displayed in the results table.

**Display Aspect Ratio Filtering:**

- Added input field for specifying display aspect ratio (e.g., 16:9).
- Aspect ratio is automatically calculated if not explicitly provided by the video metadata.

**Color Space Filtering:**

- Added a dropdown list to filter videos by color space. Supported color spaces include:
  - sRGB, Adobe RGB, ProPhoto RGB, Rec. 709, Rec. 2020, DCI-P3, Apple RGB, CMYK, YUV, and more.
- Color space information is displayed in the results table.

**Bit Depth Filtering:**

- Added input fields to specify minimum and maximum bit depth.
- Bit depth is inferred from video pixel format if not explicitly provided in metadata.
- Bit depth information is displayed in the results table.

**Enhanced Results Table:**

- New columns added for:
  - Framerate
  - Display Aspect Ratio (DAR)
  - Color Space
  - Bit Depth
- Existing columns such as Name, Size, Codec, Bitrate, and Bitrate Mode remain sortable.

#### Improvements

- Default window size set to 700x860 for better usability.
- Aligned input fields in the GUI to improve readability and symmetry.
- Enhanced progress bar and status messages to better reflect the current processing state.
- Added tooltips for all new filters and table columns, providing clearer descriptions.

#### Fixed

- Corrected issues with color space retrieval. Color space is now inferred and displayed as expected (e.g., YUV, RGB).
- Aspect ratio is calculated dynamically when not explicitly provided, ensuring accurate filtering and display.

#### Export Enhancements

- CSV export now includes all newly added parameters (Framerate, DAR, Color Space, and Bit Depth).
- Error handling improved to ensure smooth export even when certain metadata is missing.

---

### [1.1.0] - 28/11/2024
### Added
- **Bitrate Filtering**:
  - Added input fields to specify minimum and maximum bitrate (in kbps).
  - Introduced a filter to distinguish between **variable** and **constant** bitrate modes.
  - Enhanced the filtering logic to include these new options.

- **Bitrate and Bitrate Mode in Results Table**:
  - Displayed the **bitrate** (in kbps) and whether it's **variable** or **constant** for each video in the results table.

- **Sortable Columns in Results Table**:
  - Added functionality to **sort results** by clicking on column headers.
  - Sorting is **context-aware**:
    - Alphabetical sorting for text-based columns (e.g., Name, Codec, Bitrate Mode).
    - Numerical sorting for numeric columns (e.g., Size, Bitrate).
  - Sorting toggles between ascending and descending order on repeated clicks.

- **Export to CSV**:
  - Added an "Export to CSV" button in the results window.
  - Users can export the filtered results into a CSV file containing:
    - File Name, File Path, File Size, Format, Codec, Bitrate (kbps), and Bitrate Mode.
  - Includes error handling to ensure smooth export even in edge cases.

- **Tooltips for Main Filters**:
  - Added **detailed tooltips** for each main filter checkbox to guide users on their functionality:
    - Codec
    - Resolution
    - Duration
    - File Size
    - Bitrate
    - Bitrate Mode

- **Tooltips for Sorting in Results Table**:
  - Added tooltips to each column header in the results table explaining the sorting functionality.
  - Example: "Click to sort by Codec".

### Improvements
- Enhanced the **results display** by adding more relevant information (e.g., Bitrate and Bitrate Mode).
- Formatted numeric values (e.g., size and bitrate) to two decimal places for improved readability.
- Optimized the **Treeview layout** in the results table to better fit the additional columns.
- Updated the **progress bar and status messages** to reflect the current processing state more accurately.

