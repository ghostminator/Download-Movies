import requests
import tkinter as tk
from tkinter import messagebox
import webbrowser

# Function to search movies with pagination support
def search_yts(query, page=1):
    search_url = f"https://yts.mx/api/v2/list_movies.json?query_term={query}&page={page}"

    response = requests.get(search_url)
    if response.status_code != 200:
        messagebox.showerror("Error", "Failed to fetch data from YTS.")
        return None

    data = response.json()
    if 'data' not in data or 'movies' not in data['data']:
        messagebox.showinfo("No Results", "No movies found.")
        return None

    return data['data']['movies'], data['data']['movie_count'], data['data']['page_number']

# Function to get the magnet link from a movie
def get_magnet_link(movie):
    torrents = movie.get('torrents', [])
    if torrents:
        for torrent in torrents:
            if torrent['quality'] == '1080p':
                return torrent['url']
        return torrents[0]['url']
    return None

class MovieSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YTS Movie Search")

        # Center the window on the screen
        window_width = 600
        window_height = 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate the position to center the window
        position_top = int(screen_height / 2 - window_height / 2)
        position_left = int(screen_width / 2 - window_width / 2)

        root.geometry(f'{window_width}x{window_height}+{position_left}+{position_top}')
        root.configure(bg='#2e2e2e')  # Dark background for the window

        # Variables for pagination and selected movies
        self.page = 1
        self.total_movies = 0
        self.movies = []
        self.selected_movies = []

        # Setup the GUI components
        self.setup_ui()

    def setup_ui(self):
        # Movie Search Query
        self.query_label = tk.Label(self.root, text="Enter movie name:", fg='white', bg='#2e2e2e', font=("Helvetica", 12))
        self.query_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.query_entry = tk.Entry(self.root, width=30, font=("Helvetica", 12))
        self.query_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Search Button
        self.search_button = tk.Button(self.root, text="Search", command=self.search_movies, bg='#333333', fg='white', font=("Helvetica", 14))
        self.search_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Movie Listbox (Allow multiple selections)
        self.movie_listbox = tk.Listbox(self.root, height=10, width=50, font=("Helvetica", 12), bg='#333333', fg='white', selectbackground="#555555", selectmode=tk.MULTIPLE)
        self.movie_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Magnet Link Button
        self.magnet_button = tk.Button(self.root, text="Open Selected Magnet Links", command=self.open_magnet_links, state=tk.DISABLED, bg='#333333', fg='white', font=("Helvetica", 12))
        self.magnet_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Pagination Buttons
        self.prev_button = tk.Button(self.root, text="Previous", command=self.prev_page, state=tk.DISABLED, bg='#333333', fg='white', font=("Helvetica", 12))
        self.prev_button.grid(row=4, column=0, padx=10, pady=10)

        self.next_button = tk.Button(self.root, text="Next", command=self.next_page, state=tk.DISABLED, bg='#333333', fg='white', font=("Helvetica", 12))
        self.next_button.grid(row=4, column=1, padx=10, pady=10)

        # Configure grid to expand properly
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_rowconfigure(4, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Bind the selection event to enable the button
        self.movie_listbox.bind("<<ListboxSelect>>", self.on_movie_select)

    def search_movies(self):
        query = self.query_entry.get()

        if not query:
            messagebox.showerror("Input Error", "Please enter a movie name.")
            return

        # Call the API to search movies
        self.movies, self.total_movies, self.current_page = search_yts(query, self.page)

        if self.movies:
            self.display_movies(self.movies)
            self.update_pagination()
        else:
            self.movie_listbox.delete(0, tk.END)

    def display_movies(self, movies):
        self.movie_listbox.delete(0, tk.END)
        for idx, movie in enumerate(movies):
            title = movie['title']
            year = movie['year']
            rating = movie['rating']
            self.movie_listbox.insert(tk.END, f"{idx+1}. {title} ({year}) - Rating: {rating}")
        self.magnet_button.config(state=tk.DISABLED)  # Keep the button disabled initially

    def open_magnet_links(self):
        # Get the selected indices from the listbox
        selected_indices = self.movie_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Movies Selected", "Please select at least one movie.")
            return

        # Open magnet links for selected movies
        for idx in selected_indices:
            selected_movie = self.movies[idx]
            magnet_link = get_magnet_link(selected_movie)
            if magnet_link:
                # Open the magnet link in the default torrent client
                webbrowser.open(magnet_link)
            else:
                messagebox.showinfo(f"No Magnet Link for {selected_movie['title']}", "No magnet link found for this movie.")

    def on_movie_select(self, event):
        selected_indices = self.movie_listbox.curselection()
        # Enable the magnet button only if at least one movie is selected
        if selected_indices:
            self.magnet_button.config(state=tk.NORMAL)
        else:
            self.magnet_button.config(state=tk.DISABLED)

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.search_movies()

    def next_page(self):
        if self.page * len(self.movies) < self.total_movies:
            self.page += 1
            self.search_movies()

    def update_pagination(self):
        # Enable or disable pagination buttons based on the current page and total movies
        if self.page > 1:
            self.prev_button.config(state=tk.NORMAL)
        else:
            self.prev_button.config(state=tk.DISABLED)

        if self.page * len(self.movies) < self.total_movies:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

# Initialize the Tkinter window
root = tk.Tk()
app = MovieSearchApp(root)
root.mainloop()
