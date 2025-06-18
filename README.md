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

## Configuration

The application uses a configuration file (`config.env`) to store URLs for CSDN and Toutiao platforms. You can edit this file to customize the URLs.

Default configuration:
```
# CSDN 个人主页
CSDN_URL=https://blog.csdn.net/qq_34598061?type=blog
# 今日头条个人主页
TOUTIAO_URL=https://www.toutiao.com/c/user/token/MS4wLjABAAAAYd06xjdpZljEG3tiHeqEreoftdwWiWgqy-8K5cur014/?source=tuwen_detail&entrance_gid=7517216151676568116&log_from=dc1886426211a8_1750259763904 
```

您可以通过以下方法获取配置URL：
1. CSDN URL: 访问您的CSDN博客主页，复制地址栏的URL
2. 头条URL: 访问您的头条账号主页，复制地址栏的URL

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
- Create a menu bar icon in your macOS status bar
- Automatically fetch data from both platforms
- Display the follower counts for CSDN and Toutiao, rotating between them
- Allow you to manually update data through the menu
- Save data to the same CSV files

#### Menu Bar Options

- **CSDN详细数据**: View detailed CSDN statistics (visitors, original posts, followers, following)
- **头条详细数据**: View detailed Toutiao statistics (likes, fans, follows)
- **更新数据**: Manually update the statistics from both platforms

## Customization

- To change the user URLs, edit the `config.env` file
- To change the rotation interval, modify the `rotation_interval` value in the `StatisticsMenuBarApp` class
- To change the update frequency, modify the sleep duration in the `collect_data_periodically` method

## First-time Setup for Notifications

To enable system notifications, you may need to create an Info.plist file:

```
./create_plist.sh
```

This script will create the necessary Info.plist file with CFBundleIdentifier for rumps to send notifications.

## Requirements

- Python 3.6+
- macOS (for menu bar application)
- Chrome browser
- Internet connection

## About DrissionPage

DrissionPage is a web automation library that combines the features of Selenium and Requests. It provides a simpler API for web automation and is generally faster than Selenium. 