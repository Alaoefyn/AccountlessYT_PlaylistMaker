import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
import pyperclip
import webbrowser
from youtubesearchpython import VideosSearch
from tkinter.scrolledtext import ScrolledText
from ttkthemes import ThemedTk
import threading

# Global variable to store video URLs
video_urls = []

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    match = re.search(r'(v=|youtu\.be/)([^&]+)', url)
    if match:
        return match.group(2)
    else:
        show_message("Error", "Invalid YouTube URL", "error")
        return None
