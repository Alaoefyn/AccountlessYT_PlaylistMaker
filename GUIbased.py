# Alaoefyn's Playlist Maker

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

# Function to create playlist URL from video IDs
def create_playlist_url(video_ids):
    playlist_url = "http://www.youtube.com/watch_videos?video_ids="
    playlist_url += ','.join(video_ids)
    return playlist_url

# Function to add URL manually
def add_url():
    url = entry.get().strip()
    if url:
        video_id = extract_video_id(url)
        if video_id and video_id not in video_urls:
            video_urls.append(video_id)
            added_urls_textbox.insert(tk.END, url + "\n")
        entry.delete(0, tk.END)
        fetch_video_titles()

# Function to fetch video titles
def fetch_video_titles():
    added_urls_textbox.delete("1.0", tk.END)
    for video_id in video_urls:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        videosSearch = VideosSearch(video_id, limit=1)
        video_title = videosSearch.result()['result'][0]['title']
        added_urls_textbox.insert(tk.END, f"{video_title} - {video_url}\n")

# Function to search YouTube
def search_youtube():
    query = search_entry.get().strip()
    if query:
        search_results_textbox.delete("1.0", tk.END)  # Clear previous search results
        progress_bar.start()
        
        def search_thread():
            videosSearch = VideosSearch(query, limit=5)
            results = videosSearch.result()['result']
            for video in results:
                video_title = video['title']
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                search_results_textbox.insert(tk.END, f"{video_title} - {video_url}\n", 'link')
                search_results_textbox.tag_bind('link', '<Button-1>', lambda e, url=video_url: handle_search_result_click(url))
            progress_bar.stop()
        
        threading.Thread(target=search_thread).start()
    else:
        show_message("Warning", "Please enter a search query.", "warning")

# Function to handle search result click
def handle_search_result_click(url):
    pyperclip.copy(url)
    video_id = extract_video_id(url)
    if video_id and video_id not in video_urls:
        video_urls.append(video_id)
        fetch_video_titles()
    show_message("URL Copied", f"The URL has been copied to clipboard:\n{url}")

# Function to create playlist
def create_playlist():
    if video_urls:
        playlist_url = create_playlist_url(video_urls)
        pyperclip.copy(playlist_url)  # Copy playlist URL to clipboard
        show_message("Playlist URL", f"Playlist URL copied to clipboard:\n{playlist_url}")
        webbrowser.open(playlist_url)  # Open playlist URL in browser
    else:
        show_message("Warning", "No URLs provided.", "warning")

# Function to clear URLs
def clear_urls():
    video_urls.clear()
    added_urls_textbox.delete("1.0", tk.END)

# Function to save URLs to a file
def save_urls():
    filepath = filedialog.asksaveasfilename(defaultextension="txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
    with open(filepath, 'w') as file:
        for url in video_urls:
            file.write(f"https://www.youtube.com/watch?v={url}\n")

# Function to load URLs from a file
def load_urls():
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
    with open(filepath, 'r') as file:
        for line in file:
            url = line.strip()
            video_id = extract_video_id(url)
            if video_id and video_id not in video_urls:
                video_urls.append(video_id)
                added_urls_textbox.insert(tk.END, url + "\n")
    fetch_video_titles()

# Function to remove URL
def remove_url():
    try:
        selected_text = added_urls_textbox.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        video_id = extract_video_id(selected_text)
        if video_id in video_urls:
            video_urls.remove(video_id)
            added_urls_textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
        fetch_video_titles()
    except tk.TclError:
        show_message("Error", "Please select a URL to remove.", "error")

# Function to edit URL
def edit_url():
    try:
        selected_text = added_urls_textbox.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        video_id = extract_video_id(selected_text)
        new_url = entry.get().strip()
        new_video_id = extract_video_id(new_url)
        if video_id in video_urls and new_video_id:
            video_urls[video_urls.index(video_id)] = new_video_id
            added_urls_textbox.delete(tk.SEL_FIRST, tk.SEL_LAST)
            added_urls_textbox.insert(tk.INSERT, new_url + "\n")
            entry.delete(0, tk.END)
        fetch_video_titles()
    except tk.TclError:
        show_message("Error", "Please select a URL to edit.", "error")

# Function to display usage instructions
def show_usage_instructions():
    instructions = """
    Welcome to the Accountless YouTube Playlist Creator!
    
    You do not need an open YouTube account to create a playlist.
    This program helps you by creating a playlist URL from manually entered or searched video URLs.
    
    To use the application, follow these steps:
    
    1. Manually Enter YouTube URLs:
       - Enter a YouTube URL into the text entry field labeled "Enter YouTube URL".
       - Click the "Add URL" button to add the URL to the list.

    2. Remove or Edit URLs:
       - Select a URL from the list and click the "Remove URL" button to remove it.
       - To edit a URL, select it, enter the new URL in the text entry field, and click the "Edit URL" button.

    3. Search YouTube:
       - Enter a search query into the text entry field labeled "Search YouTube".
       - Click the "Search" button to search YouTube for videos related to the query.

    4. Create Playlist:
       - Once you have added URLs or performed a search, click the "Create Playlist" button to generate a playlist URL.

    5. Additional Options:
       - You can clear the list of URLs, save the URLs to a file, load URLs from a file, or copy the playlist URL to the clipboard using the corresponding buttons.
    
    Enjoy creating playlists without needing a YouTube account!
    """

    # Show instructions in a message box
    usage_textbox.delete("1.0", tk.END)
    usage_textbox.insert(tk.END, instructions)

# Function to show message box
def show_message(title, message):
    messagebox.showinfo(title, message)

# Function to preview playlist in a web browser
def preview_playlist():
    if video_urls:
        playlist_url = create_playlist_url(video_urls)
        webbrowser.open(playlist_url)
    else:
        show_message("Warning", "No URLs provided.", "warning")

# Function to sort URLs alphabetically
def sort_urls():
    video_urls.sort()
    fetch_video_titles()

# Function to duplicate selected URL
def duplicate_url():
    try:
        selected_text = added_urls_textbox.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        video_id = extract_video_id(selected_text)
        if video_id:
            video_urls.append(video_id)
            fetch_video_titles()
    except tk.TclError:
        show_message("Error", "Please select a URL to duplicate.", "error")

# Main Tkinter application with ThemedTk
root = ThemedTk(theme="equilux")  # Apply a dark theme (e.g., "equilux")
root.title("Accountless YouTube Playlist Creator")
root.geometry("800x600")

# Notebook for multiple pages
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill=tk.BOTH)

# Page 1: Add URLs Manually
page_manual = ttk.Frame(notebook)
notebook.add(page_manual, text='Add URLs Manually')

label_manual = ttk.Label(page_manual, text="Enter YouTube URL:")
label_manual.pack(pady=5)
entry = ttk.Entry(page_manual, width=50)
entry.pack(pady=5)
button_add_url = ttk.Button(page_manual, text="Add URL", command=add_url)
button_add_url.pack(pady=5)
added_urls_textbox = ScrolledText(page_manual, width=80, height=10)
added_urls_textbox.pack(pady=5)
button_remove_url = ttk.Button(page_manual, text="Remove URL", command=remove_url)
button_remove_url.pack(pady=5)
button_edit_url = ttk.Button(page_manual, text="Edit URL", command=edit_url)
button_edit_url.pack(pady=5)
button_clear_urls = ttk.Button(page_manual, text="Clear URLs", command=clear_urls)
button_clear_urls.pack(pady=5)
button_save_urls = ttk.Button(page_manual, text="Save URLs", command=save_urls)
button_save_urls.pack(pady=5)
button_load_urls = ttk.Button(page_manual, text="Load URLs", command=load_urls)
button_load_urls.pack(pady=5)
button_sort_urls = ttk.Button(page_manual, text="Sort URLs", command=sort_urls)
button_sort_urls.pack(pady=5)
button_duplicate_url = ttk.Button(page_manual, text="Duplicate URL", command=duplicate_url)
button_duplicate_url.pack(pady=5)

# Page 2: Search YouTube
page_search = ttk.Frame(notebook)
notebook.add(page_search, text='Search YouTube')

label_search = ttk.Label(page_search, text="Search YouTube:")
label_search.pack(pady=5)
search_entry = ttk.Entry(page_search, width=50)
search_entry.pack(pady=5)
button_search = ttk.Button(page_search, text="Search", command=search_youtube)
button_search.pack(pady=5)
search_results_textbox = ScrolledText(page_search, width=80, height=10)
search_results_textbox.pack(pady=5)

# Page 3: Create Playlist
page_create = ttk.Frame(notebook)
notebook.add(page_create, text='Create Playlist')

button_create_playlist = ttk.Button(page_create, text="Create Playlist", command=create_playlist)
button_create_playlist.pack(pady=10)
button_preview_playlist = ttk.Button(page_create, text="Preview Playlist", command=preview_playlist)
button_preview_playlist.pack(pady=10)

# Page 4: How to Use
page_usage = ttk.Frame(notebook)
notebook.add(page_usage, text='How to Use')

usage_textbox = ScrolledText(page_usage, width=80, height=20)
usage_textbox.pack(pady=5)
button_show_usage = ttk.Button(page_usage, text="Load Instructions", command=show_usage_instructions)
button_show_usage.pack(pady=10)

# Add a progress bar to indicate URL processing
progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
