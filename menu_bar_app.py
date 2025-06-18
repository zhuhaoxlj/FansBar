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
        
        # Initialize detailed menu items
        self.csdn_details_menu = rumps.MenuItem("CSDN详细数据")
        self.csdn_visitors_item = rumps.MenuItem("访问量: 加载中...")
        self.csdn_originals_item = rumps.MenuItem("原创: 加载中...")
        self.csdn_followers_item = rumps.MenuItem("粉丝: 加载中...")
        self.csdn_following_item = rumps.MenuItem("关注: 加载中...")
        
        self.toutiao_details_menu = rumps.MenuItem("头条详细数据")
        self.toutiao_likes_item = rumps.MenuItem("获赞: 加载中...")
        self.toutiao_fans_item = rumps.MenuItem("粉丝: 加载中...")
        self.toutiao_follows_item = rumps.MenuItem("关注: 加载中...")
        
        # Add items to submenus
        self.csdn_details_menu.add(self.csdn_visitors_item)
        self.csdn_details_menu.add(self.csdn_originals_item)
        self.csdn_details_menu.add(self.csdn_followers_item)
        self.csdn_details_menu.add(self.csdn_following_item)
        
        self.toutiao_details_menu.add(self.toutiao_likes_item)
        self.toutiao_details_menu.add(self.toutiao_fans_item)
        self.toutiao_details_menu.add(self.toutiao_follows_item)
        
        # Configure menu - 完全清除默认菜单并使用我们自己的菜单项
        self.menu.clear()  # 清除默认菜单
        self.menu.add(self.csdn_details_menu)
        self.menu.add(self.toutiao_details_menu)
        self.menu.add(None)  # 分隔符
        self.menu.add("更新数据")
        # 不添加退出选项，因为rumps已经默认添加了一个
        
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
    
    def update_menu_items(self):
        """Update the menu items with current data"""
        if self.csdn_data:
            self.csdn_visitors_item.title = f"访问量: {self.csdn_data['visitors']}"
            self.csdn_originals_item.title = f"原创: {self.csdn_data['originals']}"
            self.csdn_followers_item.title = f"粉丝: {self.csdn_data['followers']}"
            self.csdn_following_item.title = f"关注: {self.csdn_data['following']}"
            
        if self.toutiao_data:
            self.toutiao_likes_item.title = f"获赞: {self.toutiao_data['likes']}"
            self.toutiao_fans_item.title = f"粉丝: {self.toutiao_data['fans']}"
            self.toutiao_follows_item.title = f"关注: {self.toutiao_data['follows']}"
    
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
            
            # Update menu items with new data
            self.update_menu_items()
            
            # Update title immediately after collection
            if self.current_display == "csdn" and self.csdn_data:
                self.title = f"CSDN: {self.csdn_data['followers']}"
            elif self.current_display == "toutiao" and self.toutiao_data:
                self.title = f"头条: {self.toutiao_data['fans']}"
            
            # Try to show notification when data is updated
            try:
                rumps.notification(
                    title="数据已更新", 
                    subtitle="粉丝统计", 
                    message=f"CSDN: {self.csdn_data['followers']} 粉丝, 头条: {self.toutiao_data['fans'] if self.toutiao_data else '未知'} 粉丝"
                )
            except Exception as e:
                print(f"无法显示通知: {e}")
                # 通知失败不影响主要功能
            
        except Exception as e:
            print(f"Error collecting data: {e}")
            import traceback
            print(traceback.format_exc())
    
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
        try:
            rumps.notification("数据更新", "统计数据", "正在更新数据，请稍等...")
        except Exception as e:
            print(f"无法显示通知: {e}")

if __name__ == "__main__":
    StatisticsMenuBarApp().run()