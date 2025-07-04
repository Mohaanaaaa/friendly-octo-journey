import tkinter as tk
from tkinter import filedialog, messagebox, ttk # Import ttk
from PIL import Image, ImageTk
import shutil
import os

class FolderImageRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Image Renamer")
        self.root.geometry("900x600")

        # Variables
        self.folder_path = ""
        self.subfolders = []
        self.images = []
        self.current_image_index = 0
        self.dest_folder_path = ""
        self.current_image_obj = None
        self.zoom_factor = 1.0
        self.original_image = None # Initialize original_image here
        self.image_dropdown_values = tk.StringVar() # Variable to hold dropdown values

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Main frames: left (for tools and image viewer) and right (for controls)
        self.left_panel = tk.Frame(self.root)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.root, width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Inside left_panel: tools_frame on the left, image_frame next to it
        self.tools_frame = tk.Frame(self.left_panel, bd=2, relief=tk.RAISED) # Raised relief for distinction
        self.tools_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5) # Pack to the left, fill vertically

        # Add zoom buttons vertically
        tk.Label(self.tools_frame, text="Image Tools").pack(pady=10) # Optional title for tools
        self.zoom_in_btn = tk.Button(self.tools_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.TOP, padx=5, pady=5) # Pack vertically
        self.zoom_out_btn = tk.Button(self.tools_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.TOP, padx=5, pady=5) # Pack vertically
        self.auto_fit_btn = tk.Button(self.tools_frame, text="Auto Fit", command=self.auto_fit)
        self.auto_fit_btn.pack(side=tk.TOP, padx=5, pady=5) # Pack vertically
        
        # Image Viewer (fills remaining space in left_panel)
        self.image_frame = tk.Frame(self.left_panel, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Pack to the left, expand

        # Canvas for image display
        self.canvas = tk.Canvas(self.image_frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize) # Bind resize event

        # Right: Controls and lists
        # info_frame, dest_frame, subfolder_frame, button_frame, copy_folder_btn, renamed_frame
        # These remain largely the same, just attached to self.right_frame

        # Folder info and renaming
        info_frame = tk.Frame(self.right_frame)
        info_frame.pack(pady=10, fill=tk.X, padx=10)

        tk.Label(info_frame, text="Original Folder Name:").grid(row=0, column=0, sticky=tk.W)
        self.original_folder_entry = tk.Entry(info_frame, width=25)
        self.original_folder_entry.grid(row=0, column=1, padx=5)

        tk.Label(info_frame, text="Enter New Folder Name:").grid(row=1, column=0, sticky=tk.W)
        self.new_folder_entry = tk.Entry(info_frame, width=25)
        self.new_folder_entry.grid(row=1, column=1, padx=5)

        # Destination folder selection
        dest_frame = tk.Frame(self.right_frame)
        dest_frame.pack(pady=10, fill=tk.X, padx=10)
        self.dest_folder_label = tk.Label(dest_frame, text="Destination Folder: Not selected")
        self.dest_folder_label.pack(side=tk.LEFT)

        self.select_dest_btn = tk.Button(dest_frame, text="Select Destination Folder", command=self.select_dest_folder)
        self.select_dest_btn.pack(side=tk.LEFT, padx=5)

        # Subfolders listbox
        subfolder_frame = tk.Frame(self.right_frame)
        subfolder_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        tk.Label(subfolder_frame, text="Subfolders:").pack()

        self.subfolder_listbox = tk.Listbox(subfolder_frame)
        self.subfolder_listbox.pack(fill=tk.BOTH, expand=True)
        self.subfolder_listbox.bind('<<ListboxSelect>>', self.on_subfolder_select)

        # Buttons for main actions
        button_frame = tk.Frame(self.right_frame)
        self.load_folder_btn = tk.Button(button_frame, text="Select Folder", command=self.load_folder)
        self.load_folder_btn.pack(side=tk.LEFT, padx=5)

        # Previous and Next image buttons
        self.prev_button = tk.Button(button_frame, text="◀ Prev", command=self.show_previous_image)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        # Dropdown for image selection
        self.image_selection_dropdown = ttk.Combobox(button_frame, textvariable=self.image_dropdown_values, state="readonly", width=5)
        self.image_selection_dropdown.pack(side=tk.LEFT, padx=5)
        self.image_selection_dropdown.bind("<<ComboboxSelected>>", self.on_image_select_from_dropdown)
        
        self.next_button = tk.Button(button_frame, text="Next ▶", command=self.show_next_image)
        self.next_button.pack(side=tk.LEFT, padx=5)

        button_frame.pack(pady=10, fill=tk.X, padx=10)
        
        # "Copy and Rename Folder" button positioned separately
        self.copy_folder_btn = tk.Button(self.right_frame, text="Copy and Rename Folder", command=self.copy_and_rename_folder, bg='lightblue')
        self.copy_folder_btn.pack(pady=15, padx=10, fill=tk.X)

        # Listbox for copied folders
        renamed_frame = tk.Frame(self.right_frame)
        renamed_frame.pack(pady=10, fill=tk.X, padx=10)

        tk.Label(renamed_frame, text="Copied & Renamed Folders:").pack()

        self.renamed_listbox = tk.Listbox(renamed_frame, height=5)
        self.renamed_listbox.pack(fill=tk.X)

        # Initial message in canvas
        self.canvas.create_text(self.canvas.winfo_reqwidth()/2, self.canvas.winfo_reqheight()/2, text="Select a folder to begin", fill="black", font=("Arial", 16))

        self.update_navigation_buttons_state() # Set initial state of navigation buttons


    def load_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.original_folder_entry.delete(0, tk.END)
            self.original_folder_entry.insert(0, os.path.basename(folder_selected))
            self.load_subfolders()
            self.load_images_from_path(self.folder_path)

    def load_subfolders(self):
        self.subfolders = []
        self.subfolder_listbox.delete(0, tk.END)
        for entry in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, entry)
            if os.path.isdir(full_path):
                self.subfolders.append(entry)
                self.subfolder_listbox.insert(tk.END, entry)

    def load_images_from_path(self, path):
        """Loads image files from a given path and populates the dropdown."""
        self.images = []
        self.current_image_index = 0
        for file_name in sorted(os.listdir(path)): # Sort for consistent order
            full_path = os.path.join(path, file_name)
            if os.path.isfile(full_path):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    self.images.append(full_path)
        
        # Update the dropdown values
        if self.images:
            image_numbers = [str(i + 1) for i in range(len(self.images))]
            self.image_selection_dropdown['values'] = image_numbers
            self.image_selection_dropdown.set(image_numbers[0]) # Set default to first image
            self.load_and_render_current_image() # Initial load and render
        else:
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_reqwidth()/2, self.canvas.winfo_reqheight()/2, text="No images found", fill="black", font=("Arial", 16))
            self.original_image = None
            self.current_image_obj = None # Clear previous image
            self.image_selection_dropdown['values'] = [] # Clear dropdown
            self.image_selection_dropdown.set('') # Clear dropdown selection
        self.update_navigation_buttons_state() # Update state after loading images


    def load_and_render_current_image(self):
        """Loads the current image and renders it, ensuring auto-fit."""
        if not self.images:
            return

        image_path = self.images[self.current_image_index]
        try:
            self.original_image = Image.open(image_path)
            self.auto_fit() # Directly call auto_fit to fit the image to the canvas
        except FileNotFoundError:
            messagebox.showerror("File Error", f"Image file not found: {image_path}")
            self.original_image = None
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_reqwidth()/2, self.canvas.winfo_reqheight()/2, text="Image not found", fill="black", font=("Arial", 16))
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image {image_path}: {e}")
            self.original_image = None
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_reqwidth()/2, self.canvas.winfo_reqheight()/2, text="Error loading image", fill="black", font=("Arial", 16))


    def display_image(self):
        """Prepares and displays the image for the current index."""
        self.load_and_render_current_image()

    def render_image(self):
        """Renders the current original_image onto the canvas with zoom."""
        if self.original_image is None:
            self.canvas.delete("all")
            return

        img = self.original_image.copy()
        width, height = img.size
        new_size = (int(width * self.zoom_factor), int(height * self.zoom_factor))
        
        # Ensure new_size dimensions are positive
        if new_size[0] <= 0 or new_size[1] <= 0:
            new_size = (1, 1) # Fallback to a tiny size to avoid errors

        img = img.resize(new_size, Image.LANCZOS)

        self.current_image_obj = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Fallback for initial canvas size
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = self.canvas.winfo_reqwidth()
            canvas_height = self.canvas.winfo_reqheight()

        self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.current_image_obj, anchor=tk.CENTER)
        
    def zoom_in(self):
        if self.original_image:
            self.zoom_factor *= 1.2
            self.render_image()

    def zoom_out(self):
        if self.original_image:
            self.zoom_factor /= 1.2
            self.render_image()

    def auto_fit(self):
        if not self.original_image:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.original_image.size

        if canvas_width < 1 or canvas_height < 1:
            # Fallback if canvas size is not yet determined
            self.zoom_factor = 1.0
        else:
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            self.zoom_factor = min(width_ratio, height_ratio)
        self.render_image()

    def on_canvas_resize(self, event):
        """Called when the canvas is resized."""
        if self.original_image:
            self.auto_fit() # Re-fit image to new canvas size

    def show_next_image(self):
        if not self.images:
            return
        if self.current_image_index < len(self.images) - 1: # Stop at last image
            self.current_image_index += 1
            self.image_selection_dropdown.set(str(self.current_image_index + 1)) # Update dropdown
            self.display_image()
            self.update_navigation_buttons_state() # Update button state

    def show_previous_image(self):
        if not self.images:
            return
        if self.current_image_index > 0: # Stop at first image
            self.current_image_index -= 1
            self.image_selection_dropdown.set(str(self.current_image_index + 1)) # Update dropdown
            self.display_image()
            self.update_navigation_buttons_state() # Update button state

    def on_image_select_from_dropdown(self, event):
        """Handles selection from the image number dropdown."""
        selected_number_str = self.image_selection_dropdown.get()
        if selected_number_str:
            try:
                selected_index = int(selected_number_str) - 1 # Convert to 0-based index
                if 0 <= selected_index < len(self.images):
                    self.current_image_index = selected_index
                    self.display_image()
                    self.update_navigation_buttons_state() # Update button state
            except ValueError:
                # Should not happen with state="readonly" but good for robustness
                pass

    def update_navigation_buttons_state(self):
        """Enables/disables Next/Previous buttons based on current image index."""
        if not self.images:
            self.next_button.config(state=tk.DISABLED)
            self.prev_button.config(state=tk.DISABLED)
            self.image_selection_dropdown.config(state="disabled")
            return

        self.image_selection_dropdown.config(state="readonly") # Enable dropdown if images exist

        if self.current_image_index == len(self.images) - 1:
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)

        if self.current_image_index == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)


    def on_subfolder_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            folder_name = self.subfolders[index]
            # Update original folder name entry
            self.original_folder_entry.delete(0, tk.END)
            self.original_folder_entry.insert(0, folder_name)
            # Load images of selected subfolder
            subfolder_path = os.path.join(self.folder_path, folder_name)
            self.load_images_from_path(subfolder_path)

    def select_dest_folder(self):
        dest_folder = filedialog.askdirectory()
        if dest_folder:
            self.dest_folder_path = dest_folder
            self.dest_folder_label.config(text=f"Destination Folder: {dest_folder}")

    def copy_and_rename_folder(self):
        if not self.folder_path:
            messagebox.showwarning("No Folder Selected", "Please select a main folder first.")
            return
        if not self.dest_folder_path:
            messagebox.showwarning("No Destination Folder", "Please select a destination folder.")
            return
        old_name = self.original_folder_entry.get().strip()
        new_name = self.new_folder_entry.get().strip()

        if not old_name or not new_name:
            messagebox.showwarning("Input Error", "Please enter both folder names.")
            return

        source_path = os.path.join(self.folder_path, old_name)
        if not os.path.exists(source_path):
            messagebox.showerror("Error", f"The folder '{old_name}' does not exist.")
            return

        target_path = os.path.join(self.dest_folder_path, new_name)
        if os.path.exists(target_path):
            messagebox.showerror("Error", f"The target folder '{new_name}' already exists in destination.")
            return

        try:
            shutil.copytree(source_path, target_path)
            self.renamed_listbox.insert(tk.END, new_name)
            messagebox.showinfo("Success", f"Folder copied to '{target_path}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderImageRenamer(root)
    root.mainloop()