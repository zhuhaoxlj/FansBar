# Web Stats Monitor

A Python script that monitors web page statistics every second and saves the data to a CSV file.

## Features

- Monitors webpage metrics (visitors, original posts, followers, following) in real-time
- Records data every second (configurable)
- Saves data to CSV for later analysis
- Works with CSDN user profiles by default
- Uses DrissionPage for browser automation (no Selenium dependency)

## Installation

1. Clone this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the script:

```
python get_fans.py
```

When prompted, enter the URL of the page you want to monitor.

The script will:
- Open a Chrome browser window
- Navigate to the provided URL
- Extract visitor count, original post count, follower count, and following count every second
- Print the data to the console
- Save the data to a CSV file named `fan_data.csv`

Press Ctrl+C to stop the monitoring.

## Customization

- To run the browser in headless mode, set `co.headless = True` in the `setup_browser()` function
- To change the monitoring interval, modify the `interval` parameter in the `monitor_page()` function call
- To run for a specific duration, add a `duration` parameter to the `monitor_page()` function call

## Requirements

- Python 3.6+
- Chrome browser
- Internet connection

## About DrissionPage

DrissionPage is a web automation library that combines the features of Selenium and Requests. It provides a simpler API for web automation and is generally faster than Selenium. 