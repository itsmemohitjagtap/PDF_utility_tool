import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Ghostscript compression function
def compress_pdf(input_file, output_file, target):
    try:
        if target == '2mb':
            dpi = 100
            quality = 60
        elif target == '500kb':
            dpi = 72
            quality = 40
        else:
            dpi = 100
            quality = 60

        gs_command = [
            "gswin64c",  # For Windows; use "gs" for Mac/Linux
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/screen",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dColorImageDownsampleType=/Bicubic",
            "-dGrayImageDownsampleType=/Bicubic",
            f"-dColorImageResolution={dpi}",
            f"-dGrayImageResolution={dpi}",
            f"-dMonoImageResolution={dpi}",
            "-dColorImageFilter=/DCTEncode",
            "-dGrayImageFilter=/DCTEncode",
            f"-dJPEGQ={quality}",
            f"-sOutputFile={output_file}",
            input_file
        ]

        subprocess.run(gs_command, check=True)
        return True
    except Exception as e:
        print(f"Compression failed: {e}")
        return False

# Main App Class
class PDFToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Tool")
        self.root.geometry("500x500")

        self.selected_file = None
        self.selected_image = None
        self.compression_target = tk.StringVar(value="")  # or value="2mb" for default selection
        self.compression_target.set("2mb")  # No default selected

        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()

        self.image_preview_label = None

        self.create_home_screen()

    def create_home_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="PDF Utility Tool", font=("Arial", 16, "bold")).pack(pady=30)

        tk.Button(self.root, text="Compress PDF", font=("Arial", 12),
                  width=25, command=self.create_compress_screen).pack(pady=15)

        tk.Button(self.root, text="Resize Image", font=("Arial", 12),
                  width=25, command=self.create_resize_screen).pack(pady=15)

    def create_compress_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Compress PDF", font=("Arial", 16, "bold")).pack(pady=10)

        self.file_label = tk.Label(self.root, text="No file selected", font=("Arial", 10))
        self.file_label.pack(pady=5)

        tk.Button(self.root, text="Select PDF File", font=("Arial", 12), command=self.select_pdf).pack(pady=20)

        tk.Label(self.root, text="Select target size:", font=("Arial", 11)).pack(pady=5)

        tk.Radiobutton(self.root, text="Compress under 2MB", variable=self.compression_target,
                       value="2mb", font=("Arial", 10)).pack()

        tk.Radiobutton(self.root, text="Compress under 500KB", variable=self.compression_target,
                       value="500kb", font=("Arial", 10)).pack()

        self.compress_btn = tk.Button(self.root, text="Compress and Save", font=("Arial", 12),
                                      command=self.compress_action, state=tk.DISABLED)
        self.compress_btn.pack(pady=20)

        tk.Button(self.root, text="Back", font=("Arial", 10), command=self.create_home_screen).pack(pady=10)

    def create_resize_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Resize Image", font=("Arial", 16, "bold")).pack(pady=10)

        self.image_label = tk.Label(self.root, text="No image selected", font=("Arial", 10))
        self.image_label.pack(pady=5)

        tk.Button(self.root, text="Select Image", font=("Arial", 12), command=self.select_image).pack(pady=15)

        # Frame for width and height inputs in one line
        dimension_frame = tk.Frame(self.root)
        dimension_frame.pack(pady=15)

    # Width input
        tk.Label(dimension_frame, text="Width:", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Entry(dimension_frame, textvariable=self.width_var, width=10).pack(side=tk.LEFT, padx=(5, 40))

    # Height input
        tk.Label(dimension_frame, text="Height:", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Entry(dimension_frame, textvariable=self.height_var, width=10).pack(side=tk.LEFT, padx=5)

        # Image preview
        self.image_preview_label = tk.Label(self.root)
        self.image_preview_label.pack(pady=10)

        tk.Button(self.root, text="Resize and Save", font=("Arial", 12), command=self.resize_image).pack(pady=10)
        tk.Button(self.root, text="Back", font=("Arial", 10), command=self.create_home_screen).pack(pady=10)

    def select_pdf(self):
        file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file:
            self.selected_file = file
            self.file_label.config(text=f"Selected: {os.path.basename(file)}")
            self.compress_btn.config(state=tk.NORMAL)

    def compress_action(self):
        if not self.selected_file or not self.compression_target.get():
            messagebox.showwarning("Missing Info", "Please select a file and compression option.")
            return

        base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
        dir_path = os.path.dirname(self.selected_file)
        output_file = os.path.join(dir_path, f"compressed_{base_name}.pdf")

        success = compress_pdf(self.selected_file, output_file, self.compression_target.get())
        if success:
            messagebox.showinfo("Success", f"Compressed PDF saved as:\n{output_file}")
        else:
            messagebox.showerror("Error", "Compression failed. Check Ghostscript or try again.")

    def select_image(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if file:
            self.selected_image = file
            self.image_label.config(text=f"Selected: {os.path.basename(file)}")

            # Show preview
            img = Image.open(file)
            img.thumbnail((200, 200))
            img_tk = ImageTk.PhotoImage(img)

            self.image_preview_label.img = img_tk
            self.image_preview_label.config(image=img_tk)

    def resize_image(self):
        if not self.selected_image:
            messagebox.showwarning("No image", "Please select an image.")
            return

        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())

            img = Image.open(self.selected_image)
            img = img.resize((width, height), Image.LANCZOS)

            base_name = os.path.splitext(os.path.basename(self.selected_image))[0]
            dir_path = os.path.dirname(self.selected_image)
            output_file = os.path.join(dir_path, f"resized_{base_name}.jpg")
            img.save(output_file)

            messagebox.showinfo("Success", f"Image resized and saved as:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Resize failed:\n{e}")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolApp(root)
    root.mainloop()
