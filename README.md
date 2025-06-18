# Web Stats Monitor

A Python tool that monitors web page statistics and displays them in your macOS menu bar.

## Features

- Monitors webpage metrics from CSDN and Toutiao platforms
- Displays follower counts in the macOS menu bar with automatic rotation
- Records data to CSV files for later analysis
- Uses DrissionPage for browser automation (no Selenium dependency)
- Provides easy access through a system menu bar icon

## Installation

1. Clone this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### Command Line Usage

Run the script to fetch data once:

```
python get_fans.py
```

This will:
- Connect to CSDN and Toutiao platforms
- Extract visitor count, original post count, follower counts, etc.
- Print the data to the console
- Save the data to CSV files (`csdn_stats.csv` and `toutiao_stats.csv`)

### Menu Bar Application

To display stats in your macOS menu bar, run:

```
python menu_bar_app.py
```

This will:
- Create a menu bar icon in your macOS status bar (📊)
- Automatically fetch data from both platforms
- Display the follower counts for CSDN and Toutiao, rotating between them
- Allow you to manually update data through the menu
- Save data to the same CSV files

#### Menu Bar Options

- **更新数据**: Manually update the statistics from both platforms
- **退出**: Quit the menu bar application

## Customization

- To change the user URLs, edit the URL variables in the scripts
- To change the rotation interval, modify the `rotation_interval` value in the `StatisticsMenuBarApp` class
- To change the update frequency, modify the sleep duration in the `collect_data_periodically` method

## Requirements

- Python 3.6+
- macOS (for menu bar application)
- Chrome browser
- Internet connection

## About DrissionPage

DrissionPage is a web automation library that combines the features of Selenium and Requests. It provides a simpler API for web automation and is generally faster than Selenium. 