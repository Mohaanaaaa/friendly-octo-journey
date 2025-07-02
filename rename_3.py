import tkinter as tk
from tkinter import filedialog, messagebox
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

        # For image viewer enhancements
        self.zoom_level = 1.0
        self.rotation_angle = 0

        # Setup UI
        self.setup_ui()

        # Add image viewer tools panel
        self.add_image_tools_panel()

    def setup_ui(self):
        # (Your existing setup_ui code here, unchanged)
        # ...
        pass

    def add_image_tools_panel(self):
        # Create tools frame at top-left corner
        self.tools_frame = tk.Frame(self.root, bg='white', bd=2, relief=tk.RAISED)
        self.tools_frame.place(x=10, y=10)

        # Navigation buttons
        self.btn_prev_image = tk.Button(self.tools_frame, text="←", command=self.show_prev_image)
        self.btn_prev_image.pack(padx=2, pady=2)

        self.page_label = tk.Label(self.tools_frame, text="Page 0 of 0")
        self.page_label.pack(padx=2, pady=2)

        self.btn_next_image = tk.Button(self.tools_frame, text="→", command=self.show_next_image)
        self.btn_next_image.pack(padx=2, pady=2)

        # Zoom buttons
        self.btn_zoom_in = tk.Button(self.tools_frame, text="Zoom In", command=self.zoom_in)
        self.btn_zoom_in.pack(padx=2, pady=2)

        self.btn_zoom_out = tk.Button(self.tools_frame, text="Zoom Out", command=self.zoom_out)
        self.btn_zoom_out.pack(padx=2, pady=2)

        # Rotate buttons
        self.btn_rotate_left = tk.Button(self.tools_frame, text="Rotate ←", command=self.rotate_left)
        self.btn_rotate_left.pack(padx=2, pady=2)

        self.btn_rotate_right = tk.Button(self.tools_frame, text="Rotate →", command=self.rotate_right)
        self.btn_rotate_right.pack(padx=2, pady=2)

        # Initialize label
        self.update_image_page_label()

    def display_image(self, index):
        from PIL import Image, ImageTk
        if not self.images:
            self.canvas.delete("all")
            self.canvas.create_text(250, 200, text="No images found", fill="black", font=("Arial", 16))
            return
        image_path = self.images[index]
        img = Image.open(image_path)

        # Apply zoom
        width, height = img.size
        new_size = (int(width * self.zoom_level), int(height * self.zoom_level))
        img = img.resize(new_size, Image.ANTIALIAS)

        # Apply rotation
        img = img.rotate(self.rotation_angle, expand=True)

        self.current_display_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        # Center image on canvas
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        self.canvas.create_image(c_width//2, c_height//2, image=self.current_display_image, anchor='center')

    def show_prev_image(self):
        if not self.images:
            return
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.reset_transformations()
        self.update_image_page_label()
        self.display_image(self.current_image_index)

    def show_next_image(self):
        if not self.images:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.reset_transformations()
        self.update_image_page_label()
        self.display_image(self.current_image_index)

    def update_image_page_label(self):
        total = len(self.images)
        current = self.current_image_index + 1 if self.images else 0
        self.page_label.config(text=f"{current} of {total}")

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.display_image(self.current_image_index)

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.display_image(self.current_image_index)

    def rotate_left(self):
        self.rotation_angle -= 15
        self.display_image(self.current_image_index)

    def rotate_right(self):
        self.rotation_angle += 15
        self.display_image(self.current_image_index)

    def reset_transformations(self):
        self.zoom_level = 1.0
        self.rotation_angle = 0

    # Your existing methods...
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
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.images.append(os.path.join(self.folder_path, file))
        self.current_image_index = 0

    def display_image(self, index):
        from PIL import Image, ImageTk
        if not self.images:
            self.canvas.delete("all")
            self.canvas.create_text(250, 200, text="No images found", fill="black", font=("Arial", 16))
            return
        image_path = self.images[index]
        img = Image.open(image_path)
        # Resize to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10:
            # Default size if not yet rendered
            canvas_width = 500
            canvas_height = 400
        img.thumbnail((canvas_width, canvas_height))
        self.current_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width/2, canvas_height/2, image=self.current_image)

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