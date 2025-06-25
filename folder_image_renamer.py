import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class FolderImageRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Image Renamer")
        self.root.geometry("900x600")

        # Initialize variables
        self.current_image = None
        self.current_folder_path = ""
        self.subfolders = []
        self.renamed_folders = []

        # Setup the layout
        self.setup_ui()

    def setup_ui(self):
        # Left: Image Viewer
        self.image_frame = tk.Frame(self.root, width=400, height=600, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.canvas = tk.Canvas(self.image_frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Right: Controls and lists
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top right: Folder info and rename input
        info_frame = tk.Frame(self.right_frame)
        info_frame.pack(pady=10)

        tk.Label(info_frame, text="Original Folder Name:").grid(row=0, column=0, sticky=tk.W)
        self.original_folder_entry = tk.Entry(info_frame, width=30)
        self.original_folder_entry.grid(row=0, column=1, padx=5)

        tk.Label(info_frame, text="Enter New Folder Name:").grid(row=1, column=0, sticky=tk.W)
        self.new_folder_entry = tk.Entry(info_frame, width=30)
        self.new_folder_entry.grid(row=1, column=1, padx=5)

        # Buttons
        button_frame = tk.Frame(self.right_frame)
        button_frame.pack(pady=10)

        self.load_folder_btn = tk.Button(button_frame, text="Select Folder", command=self.load_folder)
        self.load_folder_btn.pack(side=tk.LEFT, padx=5)

        self.next_image_btn = tk.Button(button_frame, text="Next Image", command=self.show_next_image)
        self.next_image_btn.pack(side=tk.LEFT, padx=5)

        self.rename_btn = tk.Button(button_frame, text="Rename Folder", command=self.rename_folder)
        self.rename_btn.pack(side=tk.LEFT, padx=5)

        # Subfolders listbox
        subfolder_frame = tk.Frame(self.right_frame)
        subfolder_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(subfolder_frame, text="Subfolders:").pack()

        self.subfolder_listbox = tk.Listbox(subfolder_frame)
        self.subfolder_listbox.pack(fill=tk.BOTH, expand=True)
        self.subfolder_listbox.bind('<<ListboxSelect>>', self.on_subfolder_select)

        # Renamed folders listbox at the top right
        renamed_frame = tk.Frame(self.right_frame)
        renamed_frame.pack(pady=10, fill=tk.X)

        tk.Label(renamed_frame, text="Renamed Folders:").pack()

        self.renamed_listbox = tk.Listbox(renamed_frame, height=5)
        self.renamed_listbox.pack(fill=tk.X)

        # Initialize image index
        self.image_files = []
        self.image_index = 0

        # Initialize folder data
        self.folder_path = ""
        self.subfolders = []
        self.images = []

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
        self.image_index = 0

    def display_image(self, index):
        if not self.images:
            self.canvas.delete("all")
            self.canvas.create_text(200, 200, text="No images found", fill="black")
            return
        image_path = self.images[index]
        img = Image.open(image_path)
        img.thumbnail((self.canvas.winfo_width(), self.canvas.winfo_height()))
        self.current_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.current_image)

    def show_next_image(self):
        if not self.images:
            return
        self.image_index = (self.image_index + 1) % len(self.images)
        self.display_image(self.image_index)

    def on_subfolder_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            folder_name = self.subfolders[index]
            full_path = os.path.join(self.folder_path, folder_name)
            self.original_folder_entry.delete(0, tk.END)
            self.original_folder_entry.insert(0, folder_name)
            # Load images from selected subfolder if needed
            # For simplicity, assuming images are in main folder
            # Or, if images are inside subfolders, adjust accordingly
            # Here, we keep images from main folder
            # Alternatively, implement loading images from subfolder
            # For now, just display images from main folder
            self.load_images()
            self.display_image(0)

    def rename_folder(self):
        old_name = self.original_folder_entry.get()
        new_name = self.new_folder_entry.get()
        if not old_name or not new_name:
            messagebox.showwarning("Input Error", "Please enter both folder names.")
            return
        old_path = os.path.join(self.folder_path, old_name)
        new_path = os.path.join(self.folder_path, new_name)
        try:
            os.rename(old_path, new_path)
            messagebox.showinfo("Success", f"Renamed '{old_name}' to '{new_name}'")
            # Update folder list
            self.load_subfolders()
            # Add to renamed folders listbox
            self.renamed_listbox.insert(tk.END, new_name)
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderImageRenamer(root)
    root.mainloop()