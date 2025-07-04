import tkinter as tk
from tkinter import filedialog, messagebox, ttk
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
        self.original_image = None
        self.image_dropdown_values = tk.StringVar()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Main frames: left (for tools, navigation, and image viewer) and right (for controls)
        self.left_panel = tk.Frame(self.root)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.root, width=450)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Inside left_panel: tools_frame on the left, image_frame next to it
        self.tools_frame = tk.Frame(self.left_panel, bd=2, relief=tk.RAISED)
        self.tools_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Add zoom buttons vertically
        tk.Label(self.tools_frame, text="Image Tools").pack(pady=5)
        self.zoom_in_btn = tk.Button(self.tools_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.TOP, padx=5, pady=5)
        self.zoom_out_btn = tk.Button(self.tools_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.TOP, padx=5, pady=5)
        self.auto_fit_btn = tk.Button(self.tools_frame, text="Auto Fit", command=self.auto_fit)
        self.auto_fit_btn.pack(side=tk.TOP, padx=5, pady=5)
        
        # --- NEW UI ELEMENTS FOR PAGE NAVIGATION (matching tool_1.PNG) ---
        self.page_navigation_frame = tk.Frame(self.left_panel, bd=2, relief=tk.GROOVE)
        self.page_navigation_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.pages_loaded_label = tk.Label(self.page_navigation_frame, text="Pages: 0 of 0 loaded")
        self.pages_loaded_label.pack(pady=(5,0))

        # Frame for "< Page X of Y >"
        nav_buttons_row_frame = tk.Frame(self.page_navigation_frame)
        nav_buttons_row_frame.pack(pady=5)

        self.prev_button = tk.Button(nav_buttons_row_frame, text="<", command=self.show_previous_image)
        self.prev_button.pack(side=tk.LEFT, padx=2)

        self.page_number_label = tk.Label(nav_buttons_row_frame, text="Page 0 of 0", width=12)
        self.page_number_label.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(nav_buttons_row_frame, text=">", command=self.show_next_image)
        self.next_button.pack(side=tk.LEFT, padx=2)

        # Frame for "Goto Page" dropdown
        goto_page_frame = tk.Frame(self.page_navigation_frame)
        goto_page_frame.pack(pady=5)

        tk.Label(goto_page_frame, text="Goto Page").pack(side=tk.LEFT, padx=5)
        self.image_selection_dropdown = ttk.Combobox(goto_page_frame, textvariable=self.image_dropdown_values, state="readonly", width=5)
        self.image_selection_dropdown.pack(side=tk.LEFT, padx=5)
        self.image_selection_dropdown.bind("<<ComboboxSelected>>", self.on_image_select_from_dropdown)
        # --- END NEW UI ELEMENTS ---
        
        # Image Viewer (fills remaining space in left_panel, now below navigation)
        self.image_frame = tk.Frame(self.left_panel, bd=2, relief=tk.SUNKEN)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Canvas for image display
        self.canvas = tk.Canvas(self.image_frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)


        # Right: Controls and lists
        info_frame = tk.Frame(self.right_frame)
        info_frame.pack(pady=10, fill=tk.X, padx=10)

        tk.Label(info_frame, text="Original Folder Name:").grid(row=0, column=0, sticky=tk.W)
        # CHANGED: original_folder_entry to original_folder_label
        self.original_folder_label = tk.Label(info_frame, text="", width=25, anchor="w")
        self.original_folder_label.grid(row=0, column=1, padx=5, sticky=tk.W)

        tk.Label(info_frame, text="Enter New Folder Name:").grid(row=1, column=0, sticky=tk.W)
        self.new_folder_entry = tk.Entry(info_frame, width=25)
        self.new_folder_entry.grid(row=1, column=1, padx=5)
        self.new_folder_entry.bind("<Return>", lambda event: self.copy_and_rename_folder())


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

        self.update_navigation_buttons_state()

    def load_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path = folder_selected
            # CHANGED: Use config for Label
            self.original_folder_label.config(text=os.path.basename(folder_selected))
            self.load_subfolders()
            if self.subfolders:
                self.subfolder_listbox.selection_clear(0, tk.END)
                self.subfolder_listbox.selection_set(0)
                self.subfolder_listbox.activate(0)
                self.subfolder_listbox.event_generate("<<ListboxSelect>>")
            else:
                self.load_images_from_path(self.folder_path)
                self.update_page_info_display()

    def load_subfolders(self):
        self.subfolders = []
        self.subfolder_listbox.delete(0, tk.END)
        for entry in os.listdir(self.folder_path):
            full_path = os.path.join(self.folder_path, entry)
            if os.path.isdir(full_path):
                self.subfolders.append(entry)
                self.subfolder_listbox.insert(tk.END, entry)

    def load_images_from_path(self, path):
        self.images = []
        self.current_image_index = 0
        for file_name in sorted(os.listdir(path)):
            full_path = os.path.join(path, file_name)
            if os.path.isfile(full_path):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    self.images.append(full_path)
        
        if self.images:
            image_numbers = [str(i + 1) for i in range(len(self.images))]
            self.image_selection_dropdown['values'] = image_numbers
            self.image_selection_dropdown.set(image_numbers[0]) 
            self.load_and_render_current_image()
        else:
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_reqwidth()/2, self.canvas.winfo_reqheight()/2, text="No images found", fill="black", font=("Arial", 16))
            self.original_image = None
            self.current_image_obj = None
            self.image_selection_dropdown['values'] = []
            self.image_selection_dropdown.set('')
        self.update_page_info_display()

    def load_and_render_current_image(self):
        if not self.images:
            return

        image_path = self.images[self.current_image_index]
        try:
            self.original_image = Image.open(image_path)
            self.auto_fit()
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

    def render_image(self):
        if self.original_image is None:
            self.canvas.delete("all")
            return

        img = self.original_image.copy()
        width, height = img.size
        new_size = (int(width * self.zoom_factor), int(height * self.zoom_factor))
        
        if new_size[0] <= 0 or new_size[1] <= 0:
            new_size = (1, 1)

        img = img.resize(new_size, Image.LANCZOS)

        self.current_image_obj = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
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
            self.zoom_factor = 1.0
        else:
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            self.zoom_factor = min(width_ratio, height_ratio)
        self.render_image()

    def on_canvas_resize(self, event):
        if self.original_image:
            self.auto_fit()

    def show_next_image(self):
        if not self.images:
            return
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.load_and_render_current_image()
            self.update_page_info_display()

    def show_previous_image(self):
        if not self.images:
            return
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_and_render_current_image()
            self.update_page_info_display()

    def on_image_select_from_dropdown(self, event):
        selected_number_str = self.image_selection_dropdown.get()
        if selected_number_str:
            try:
                selected_index = int(selected_number_str) - 1
                if 0 <= selected_index < len(self.images):
                    self.current_image_index = selected_index
                    self.load_and_render_current_image()
                    self.update_page_info_display()
            except ValueError:
                pass

    def update_page_info_display(self):
        total_images = len(self.images)
        if total_images > 0:
            current_page_num = self.current_image_index + 1
            self.pages_loaded_label.config(text=f"Pages: {total_images} of {total_images} loaded")
            self.page_number_label.config(text=f"Page {current_page_num} of {total_images}")
            self.image_selection_dropdown.set(str(current_page_num))
            self.update_navigation_buttons_state()
        else:
            self.pages_loaded_label.config(text="Pages: 0 of 0 loaded")
            self.page_number_label.config(text="Page 0 of 0")
            self.image_selection_dropdown['values'] = []
            self.image_selection_dropdown.set('')
            self.update_navigation_buttons_state()

    def update_navigation_buttons_state(self):
        if not self.images:
            self.next_button.config(state=tk.DISABLED)
            self.prev_button.config(state=tk.DISABLED)
            self.image_selection_dropdown.config(state="disabled")
            self.image_dropdown_values.set('')
            return

        self.image_selection_dropdown.config(state="readonly")

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
            # CHANGED: Use config for Label
            self.original_folder_label.config(text=folder_name)
            subfolder_path = os.path.join(self.folder_path, folder_name)
            self.load_images_from_path(subfolder_path)

    def select_dest_folder(self):
        dest_folder = filedialog.askdirectory()
        if dest_folder:
            self.dest_folder_path = dest_folder
            self.dest_folder_label.config(text=f"Destination Folder: {dest_folder}")

    def copy_and_rename_folder(self, event=None):
        if not self.folder_path:
            messagebox.showwarning("No Folder Selected", "Please select a main folder first.")
            return
        if not self.dest_folder_path:
            messagebox.showwarning("No Destination Folder", "Please select a destination folder.")
            return
        
        current_subfolder_index = -1
        current_selection = self.subfolder_listbox.curselection()
        if current_selection:
            current_subfolder_index = current_selection[0]
            # CHANGED: Use cget for Label
            old_name = self.original_folder_label.cget("text").strip()
        else:
            # CHANGED: Use cget for Label
            old_name = self.original_folder_label.cget("text").strip()

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

            if current_subfolder_index != -1 and current_subfolder_index < len(self.subfolders) - 1:
                next_subfolder_index = current_subfolder_index + 1
                self.subfolder_listbox.selection_clear(0, tk.END)
                self.subfolder_listbox.selection_set(next_subfolder_index)
                self.subfolder_listbox.activate(next_subfolder_index)
                self.subfolder_listbox.event_generate("<<ListboxSelect>>")
            elif current_subfolder_index == len(self.subfolders) - 1:
                self.folder_path = ""
                self.subfolders = []
                self.images = []
                # CHANGED: Use config for Label
                self.original_folder_label.config(text="")
                self.subfolder_listbox.delete(0, tk.END)
                self.canvas.delete("all")
                self.canvas.create_text(self.canvas.winfo_reqwidth()/2, self.canvas.winfo_reqheight()/2, text="All folders processed!", fill="black", font=("Arial", 16))
                self.original_image = None
                self.current_image_obj = None
                self.image_selection_dropdown['values'] = []
                self.image_selection_dropdown.set('')
                self.update_page_info_display()

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderImageRenamer(root)
    root.mainloop()