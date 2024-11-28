# VFAPP

# Video Filter App

A versatile video filtering application built with Python and Tkinter, designed to help users filter video files based on various criteria such as codec, resolution, duration, and file size. This tool is perfect for quickly narrowing down video files in a directory according to specific needs.

## Features

- **Filter by Codec**:
  - Supports a wide range of codecs, including HAP (HAP, HAP-Q), ProRes, H.264, HEVC, VP9, AV1, and many more.
  
- **Filter by Resolution**:
  - Specify a minimum resolution (e.g., 1920x1080) to include only high-resolution videos.

- **Filter by Duration**:
  - Define a range for video duration (e.g., 30 to 300 seconds) to filter videos by length.

- **Filter by File Size**:
  - Specify a range for file size (in MB) to include only videos within a desired size range.

- **Multi-Criteria Filtering**:
  - Combine any or all criteria (codec, resolution, duration, and file size) for precise filtering.

- **User-Friendly Interface**:
  - Intuitive GUI built with Tkinter.
  - Progress bar to track filtering progress.

- **Output Results**:
  - Results are saved to a text file (`output.txt`) for easy reference.


## Installation

### Prerequisites
- Python 3.7 or later
- Required Python libraries:
  - `tkinter` (usually bundled with Python)
  - `ttk`
  - `shutil`
  - `urllib`
  - `zipfile`
  - `webbrowser`

---

## Usage

### 1. Launching the Application
- Run the script using Python:
  ```bash
  python video_filter_app.py
  ```

### 2. Selecting a Folder
- Use the "Browse" button to select the directory containing your video files.

### 3. Setting Filters
- **Codec**: Select the desired codec from the dropdown menu (e.g., `hap`, `prores`, `h264`).
- **Resolution**: Enter the minimum resolution in `WIDTHxHEIGHT` format (e.g., `1920x1080`).
- **Duration**: Specify a duration range (in seconds).
- **File Size**: Specify a size range (in MB).

### 4. Combining Filters
- Use the checkboxes to enable or disable filters:
  - Codec
  - Resolution
  - Duration
  - File Size
- You can combine multiple filters for precise results.

### 5. Running the Filter
- Click "Run" to start the filtering process.
- The progress bar will show the status as videos are processed.

### 6. Viewing Results
- Filtered results are saved to `output.txt` in the same directory as the script.
- A completion message will indicate how many videos matched the criteria.


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


## Development

### Key Libraries
- `subprocess`: For executing FFmpeg commands.
- `os`: File and directory operations.
- `tkinter`: GUI framework.
- `zipfile` & `urllib`: For downloading and extracting FFmpeg.


## Screenshots

![VFAPP](https://github.com/user-attachments/assets/f2a55cfd-e703-41ea-aadd-fbc4c5024ef4)


## Author

**Clément GHANEME**

- [Website](https://clement.business)
- Initial Release : 26/11/2024

## Changelog

## [1.1.0] - 28/11/2024
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

