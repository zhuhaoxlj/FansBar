#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract specific statistics from a Zhihu user profile page:
- Upvotes (获得71次赞同)
- Likes (获得8次喜欢)
- Collections (224次收藏)
- Following (关注了76)
- Followers (关注者17)
"""

import re
import time
import os
import csv
import json
from datetime import datetime
from bs4 import BeautifulSoup

def extract_zhihu_stats(url, page=None, html_content=None):
    """
    Extract user statistics from a Zhihu user profile page

    Args:
        url (str): URL of the Zhihu profile page
        page: Optional existing browser instance
        html_content: Optional HTML content string (for testing or offline use)

    Returns:
        dict: Dictionary containing extracted statistics
    """
    stats = {
        'upvotes': 0,
        'likes': 0,
        'collections': 0,
        'following': 0,
        'followers': 0,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'site': 'Zhihu',
        'data_complete': False
    }

    try:
        # If HTML content is provided directly, use that
        if html_content:
            print("Using provided HTML content")
        # Otherwise, try to get the page content
        else:
            # Check if we need to create a new browser instance
            close_browser = False
            if page is None:
                try:
                    from DrissionPage import ChromiumPage
                    page = ChromiumPage()
                    close_browser = True
                    print("Created new ChromiumPage instance for Zhihu")
                except ImportError:
                    print("DrissionPage not installed, please install it first.")
                    return stats

            # Navigate to the URL
            print(f"Navigating to Zhihu URL: {url}")
            page.get(url)
            time.sleep(3)  # Allow JavaScript to load
            
            # Save source code to file (optional)
            html_content = page.html
            with open('zhihu_page_source.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Close the browser if we created it
            if close_browser and page:
                try:
                    page.quit()
                    print("Closed ChromiumPage instance")
                except:
                    pass

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Method 1: Extract using meta tags (most reliable)
        try:
            # Extract upvotes and likes using meta tags
            upvotes_meta = soup.find('meta', {'itemprop': 'zhihu:voteupCount'})
            if upvotes_meta and upvotes_meta.get('content'):
                stats['upvotes'] = int(upvotes_meta.get('content'))
            
            likes_meta = soup.find('meta', {'itemprop': 'zhihu:thankedCount'})
            if likes_meta and likes_meta.get('content'):
                stats['likes'] = int(likes_meta.get('content'))
            
            followers_meta = soup.find('meta', {'itemprop': 'zhihu:followerCount'})
            if followers_meta and followers_meta.get('content'):
                stats['followers'] = int(followers_meta.get('content'))
        except Exception as e:
            print(f"Failed to extract data from meta tags: {e}")
        
        # Method 2: Extract from profile card text
        try:
            # Look for collections in side column text
            collections_text = soup.select_one('.css-3n85vb')
            if collections_text:
                text = collections_text.text.strip()
                collections_match = re.search(r'(\d+)\s*次收藏', text)
                if collections_match:
                    stats['collections'] = int(collections_match.group(1))
            
            # Look for following count in NumberBoard
            following_value = soup.select_one('.NumberBoard-itemValue[title]')
            if following_value:
                stats['following'] = int(following_value.text.strip())
        except Exception as e:
            print(f"Failed to extract from profile card: {e}")
        
        # Method 3: Parse the full document text for the numbers
        if stats['upvotes'] == 0 or stats['likes'] == 0 or stats['collections'] == 0 or stats['following'] == 0 or stats['followers'] == 0:
            try:
                html_text = html_content
                
                # Find all required stats in the full HTML content
                upvotes_match = re.search(r'获得\s*(\d+)\s*次赞同', html_text)
                if upvotes_match and stats['upvotes'] == 0:
                    stats['upvotes'] = int(upvotes_match.group(1))
                
                likes_match = re.search(r'获得\s*(\d+)\s*次喜欢', html_text)
                if likes_match and stats['likes'] == 0:
                    stats['likes'] = int(likes_match.group(1))
                
                collections_match = re.search(r'(\d+)\s*次收藏', html_text)
                if collections_match and stats['collections'] == 0:
                    stats['collections'] = int(collections_match.group(1))
                
                following_match = re.search(r'关注了</div><strong[^>]*>(\d+)', html_text)
                if following_match and stats['following'] == 0:
                    stats['following'] = int(following_match.group(1))
                
                followers_match = re.search(r'关注者</div><strong[^>]*>(\d+)', html_text)
                if followers_match and stats['followers'] == 0:
                    stats['followers'] = int(followers_match.group(1))
            except Exception as e:
                print(f"Failed to extract stats from full HTML content: {e}")
            
        # Save data to CSV file
        try:
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            # Prepare CSV file path
            csv_file = os.path.join('data', 'zhihu_stats.csv')
            file_exists = os.path.isfile(csv_file)

            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow([
                        'timestamp', 'upvotes', 'likes', 'collections',
                        'following', 'followers'
                    ])

                writer.writerow([
                    stats['timestamp'],
                    stats['upvotes'],
                    stats['likes'],
                    stats['collections'],
                    stats['following'],
                    stats['followers']
                ])
                print(f"Saved Zhihu stats to {csv_file}")
                
        except Exception as e:
            print(f"Failed to save data to files: {e}")

        # Mark data as complete if we have all the required data
        if stats['upvotes'] > 0 and stats['likes'] > 0 and stats['collections'] > 0 and stats['following'] > 0 and stats['followers'] > 0:
            stats['data_complete'] = True
            print(f"Zhihu data complete: {stats['upvotes']} upvotes, {stats['likes']} likes, {stats['collections']} collections, {stats['following']} following, {stats['followers']} followers")

    except Exception as e:
        print(f"Error extracting Zhihu stats: {e}")
        import traceback
        print(traceback.format_exc())

    return stats


def parse_html_file(html_file_path):
    """
    Parse a saved HTML file and extract Zhihu stats
    
    Args:
        html_file_path (str): Path to the HTML file
        
    Returns:
        dict: Dictionary containing extracted statistics
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        return extract_zhihu_stats(None, html_content=html_content)
    
    except Exception as e:
        print(f"Error parsing HTML file: {e}")
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "followers": 0,
            "site": "Zhihu",
            "data_complete": False
        }


if __name__ == "__main__":
    # Test with saved HTML file if it exists
    html_file = 'zhihu_page_source.html'
    if os.path.exists(html_file):
        print(f"\nParsing saved HTML file {html_file}...")
        stats = parse_html_file(html_file)
        print("\nExtracted from HTML file:")
        print(f"Upvotes: {stats['upvotes']}")
        print(f"Likes: {stats['likes']}")
        print(f"Collections: {stats['collections']}")
        print(f"Following: {stats['following']}")
        print(f"Followers: {stats['followers']}")
        print(f"Data complete: {stats['data_complete']}")
    else:
        # Test with an actual URL
        zhihu_url = "https://www.zhihu.com/people/bu-yi-jue-63"
        stats = extract_zhihu_stats(zhihu_url)
        print("\nExtracted from live page:")
        print(f"Upvotes: {stats['upvotes']}")
        print(f"Likes: {stats['likes']}")
        print(f"Collections: {stats['collections']}")
        print(f"Following: {stats['following']}")
        print(f"Followers: {stats['followers']}")
        print(f"Data complete: {stats['data_complete']}")
