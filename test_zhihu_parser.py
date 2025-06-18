#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for parsing saved Zhihu HTML files
"""

import os
import sys
from zhihu import parse_html_file

def main():
    """
    Main function to test Zhihu HTML parsing
    """
    # Check if file path is provided
    if len(sys.argv) > 1:
        html_file_path = sys.argv[1]
    else:
        # Default file path
        html_file_path = 'zhihu_page_source.html'

    if not os.path.exists(html_file_path):
        print(f"Error: File not found: {html_file_path}")
        print("Usage: python test_zhihu_parser.py [html_file_path]")
        return 1

    print(f"Parsing Zhihu HTML file: {html_file_path}")
    stats = parse_html_file(html_file_path)
    
    print("\nExtracted Profile Information:")
    print(f"Username: {stats['username']}")
    print(f"Tagline: {stats['tagline']}")
    
    print("\nActivity Stats:")
    print(f"Answers: {stats['answers']}")
    print(f"Articles: {stats['articles']}")
    print(f"Columns: {stats['columns']}")
    print(f"Videos: {stats['videos']}")
    print(f"Collections: {stats['collections']}")
    
    print("\nEngagement Stats:")
    print(f"Upvotes received: {stats['upvotes']}")
    print(f"Thanks received: {stats['thanks']}")
    print(f"Views: {stats['views']}")
    
    print("\nNetwork Stats:")
    print(f"Following: {stats['following']}")
    print(f"Followers: {stats['followers']}")
    
    print("\nRecent Activity:")
    for i, activity in enumerate(stats['recent_activity'], 1):
        print(f"{i}. [{activity['type']}] {activity['title']}")
        if activity['link']:
            print(f"   Link: {activity['link']}")
    
    print(f"\nData complete: {stats['data_complete']}")
    
    # Save data to file
    if stats['data_complete']:
        print("\nData saved to:")
        print(f"- data/zhihu_stats.csv (Basic stats)")
        print(f"- data/zhihu_activity.json (Recent activity)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 