import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import os


class FolderImageRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Image Renamer")
        self.root.geometry("900x600")  # Slightly smaller window

        # Variables
        self.folder_path = ""
        self.subfolders = []
        self.images = []
        self.current_image_index = 0
        self.dest_folder_path = ""
        self.current_image_obj = None
        self.zoom_factor = 1.0  # For zooming

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Left: Image Viewer (smaller than before)
        self.image_frame = tk.Frame(self.root, width=500, height=600, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame for tools above the canvas
        self.tools_frame = tk.Frame(self.image_frame)
        self.tools_frame.pack(side=tk.LEFT, fill=tk.X)

        # Add zoom buttons
        self.zoom_in_btn = tk.Button(self.tools_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.zoom_out_btn = tk.Button(self.tools_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.auto_fit_btn = tk.Button(self.tools_frame, text="Auto Fit", command=self.auto_fit)
        self.auto_fit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Canvas for image display
        self.canvas = tk.Canvas(self.image_frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Right: Controls and lists
        self.right_frame = tk.Frame(self.root, width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

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

        self.next_image_btn = tk.Button(button_frame, text="Next Image", command=self.show_next_image)
        self.next_image_btn.pack(side=tk.LEFT, padx=5)

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

    def load_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            self.original_folder_entry.delete(0, tk.END)
            self.original_folder_entry.insert(0, os.path.basename(folder_selected))
            self.load_subfolders()
            self.load_images()
            self.display_image(0)

    def load_subfolders(self):
        self.subfolders = []
        self.subfolder_listbox.delete(0, tk.END)
        for entry in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, entry)
            if os.path.isdir(full_path):
                self.subfolders.append(entry)
                self.subfolder_listbox.insert(tk.END, entry)

    def load_images(self):
            self.images = []
            for file in os.listdir(self.folder_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    self.images.append(os.path.join(self.folder_path, file))
            self.current_image_index = 0
            if self.images:
                self.load_current_image()

    def load_current_image(self):
            from PIL import Image
            image_path = self.images[self.current_image_index]
            self.original_image = Image.open(image_path)
            self.zoom_factor = 1.0  # Reset zoom when new image loads
            self.render_image()


    def display_image(self, index):
        from PIL import Image, ImageTk
        if not self.images:
            self.canvas.delete("all")
            self.canvas.create_text(250, 200, text="No images found", fill="black", font=("Arial", 16))
            return
        image_path = self.images[index]
        #img = Image.open(image_path)
        self.original_image = Image.open(image_path)
        self.zoom_factor = 1.0  # Reset zoom factor when loading new image
        self.render_image()
        
        #Resize to fit canvas
        #canvas_width = self.canvas.winfo_width()
        #canvas_height = self.canvas.winfo_height()
        #if canvas_width < 10 or canvas_height < 10:
            # Default size if not yet rendered
           ##canvas_height = 400
        #img.thumbnail((canvas_width, canvas_height))
        #self.current_image = ImageTk.PhotoImage(img)
        #self.canvas.delete("all")
        #self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.current_image)
    
    def render_image(self):
        from PIL import Image, ImageTk
        # Resize based on current zoom factor
        img = self.original_image.copy()
        width, height = img.size
        new_size = (int(width * self.zoom_factor), int(height * self.zoom_factor))
        img = img.resize(new_size, Image.LANCZOS)

        # Store the current image object
        self.current_image_obj = ImageTk.PhotoImage(img)

        # Clear previous images
        self.canvas.delete("all")
        # Center image on canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = 500
            canvas_height = 400
        self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.current_image_obj, anchor=tk.CENTER)
        
    def zoom_in(self):
        self.zoom_factor *= 1.2  # Increase zoom
        self.render_image()

    def zoom_out(self):
        self.zoom_factor /= 1.2  # Decrease zoom
        self.render_image()

    def auto_fit(self):
        # Fit image to canvas size
        from PIL import Image
        if not hasattr(self, 'original_image'):
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width, img_height = self.original_image.size

        if canvas_width < 1 or canvas_height < 1:
            # Default fallback
            self.zoom_factor = 1.0
        else:
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            self.zoom_factor = min(width_ratio, height_ratio)
        self.render_image()

    def show_next_image(self):
        if not self.images:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.display_image(self.current_image_index)

    def on_subfolder_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            folder_name = self.subfolders[index]
            # Update original folder name entry
            self.original_folder_entry.delete(0, tk.END)
            self.original_folder_entry.insert(0, folder_name)
            # Load first image of selected subfolder
            self.load_images_from_subfolder(folder_name)
            self.display_image(0)

    def load_images_from_subfolder(self, subfolder_name):
        subfolder_path = os.path.join(self.folder_path, subfolder_name)
        self.images = []
        for file in os.listdir(subfolder_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.images.append(os.path.join(subfolder_path, file))
        self.current_image_index = 0

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
    # Ensure PIL is available
    from PIL import Image, ImageTk
    root = tk.Tk()
    app = FolderImageRenamer(root)
    root.mainloop()