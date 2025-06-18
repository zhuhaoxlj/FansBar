#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
macOS Menu Bar Application for displaying CSDN and Toutiao statistics
"""

import rumps
import threading
import time
import os
import csv
from datetime import datetime
from csdn import extract_csdn_stats
from toutiao import parse_toutiao_user_stats

toutiao_url = "https://www.toutiao.com/c/user/token/MS4wLjABAAAAYd06xjdpZljEG3tiHeqEreoftdwWiWgqy-8K5cur014/?source=tuwen_detail&entrance_gid=7517216151676568116&log_from=dc1886426211a8_1750259763904"
csdn_url = "https://blog.csdn.net/qq_34598061"

class StatisticsMenuBarApp(rumps.App):
    def __init__(self):
        super(StatisticsMenuBarApp, self).__init__("Stats")
        
        # Initialize data
        self.csdn_data = None
        self.toutiao_data = None
        self.current_display = "csdn"  # Start with CSDN
        self.rotation_interval = 5  # Seconds to display each platform
        
        # Configure menu
        self.menu = ["更新数据", None, "退出"]
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self.collect_data_periodically)
        self.data_thread.daemon = True
        self.data_thread.start()
        
        # Start display rotation thread
        self.display_thread = threading.Thread(target=self.rotate_display)
        self.display_thread.daemon = True
        self.display_thread.start()
    
    def rotate_display(self):
        """Rotate between CSDN and Toutiao data in the menu bar"""
        while True:
            if self.current_display == "csdn" and self.csdn_data:
                self.title = f"CSDN: {self.csdn_data['followers']}"
                self.current_display = "toutiao"
            elif self.current_display == "toutiao" and self.toutiao_data:
                self.title = f"头条: {self.toutiao_data['fans']}"
                self.current_display = "csdn"
            time.sleep(self.rotation_interval)
    
    def collect_data(self):
        """Collect data from both platforms"""
        try:
            # CSDN data
            self.csdn_data = extract_csdn_stats(csdn_url)
            print(f"[CSDN] 粉丝数: {self.csdn_data['followers']}")
            
            # Toutiao data
            self.toutiao_data = parse_toutiao_user_stats(toutiao_url)
            if self.toutiao_data:
                print(f"[头条] 粉丝数: {self.toutiao_data['fans']}")
            
            # Update title immediately after collection
            if self.current_display == "csdn" and self.csdn_data:
                self.title = f"CSDN: {self.csdn_data['followers']}"
            elif self.current_display == "toutiao" and self.toutiao_data:
                self.title = f"头条: {self.toutiao_data['fans']}"
            
        except Exception as e:
            print(f"Error collecting data: {e}")
    
    def collect_data_periodically(self):
        """Collect data periodically"""
        while True:
            self.collect_data()
            # Wait for 30 minutes before collecting again
            time.sleep(30 * 60)
    
    @rumps.clicked("更新数据")
    def update_data(self, _):
        """Manually update data"""
        thread = threading.Thread(target=self.collect_data)
        thread.daemon = True
        thread.start()
        rumps.notification("数据更新", "统计数据", "正在更新数据，请稍等...")
    
    @rumps.clicked("退出")
    def quit_app(self, _):
        """Quit the application"""
        rumps.quit_application()

if __name__ == "__main__":
    StatisticsMenuBarApp().run() 