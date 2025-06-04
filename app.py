import re
import sys
import customtkinter as ctk
from tkinter import filedialog
import threading
import subprocess
import os
from PIL import Image

# Configure appearance
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("dark-blue")  

class SimilarityApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Main window configuration
        self.title("Get Similarity - Image Comparison Tool")
        self.geometry("700x1000")
        self.configure(fg_color="#121212") 
        
        # Variables
        self.source_dir = ""
        self.output_dir = ""
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange all UI elements"""
        # Cover image (if exists)
        self.create_cover_image()
        
        # Threshold slider
        threshold_frame = ctk.CTkFrame(self, fg_color="transparent")
        threshold_frame.pack(pady=(20, 10), padx=55, fill="x")

        self.threshold_label = ctk.CTkLabel(threshold_frame, text="Similarity Threshold: 0.406", anchor="w")
        self.threshold_label.pack(anchor="w", pady=(0, 10), padx=(0, 10))

        self.threshold_slider = ctk.CTkSlider(
            threshold_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=1000,
            width=600,
            height=10,
            command=self.update_threshold_label,
            progress_color="#4a90e2",  
            button_color="#4a90e2",
            button_hover_color="#357abd"
        )
        self.threshold_slider.set(0.406)
        
        self.threshold_slider.pack(side="left", fill="x", expand=True)
        
        # Frame untuk IQA threshold
        iqa_frame = ctk.CTkFrame(self, fg_color="transparent")
        iqa_frame.pack(pady=(10), padx=55, fill="x")

        # Label IQA threshold
        self.iqa_label = ctk.CTkLabel(iqa_frame, text="IQA Threshold: 70.30", anchor="w")
        self.iqa_label.pack(anchor="w", pady=(0, 10), padx=(0, 10))

        # Slider IQA threshold
        self.iqa_slider = ctk.CTkSlider(
            iqa_frame,
            from_=1.0,
            to=100.0,
            number_of_steps=100,
            width=600,
            height=10,
            progress_color="#4a90e2", 
            button_color="#4a90e2",
            button_hover_color="#357abd",
            command=self.update_iqa_label
        )
        self.iqa_slider.set(70.30)
        self.iqa_slider.pack(fill="x")
        
        # Input section
        self.create_input_section()
        
        # Output section
        self.create_output_section()
        
        # Progress label
        self.progress_label = ctk.CTkLabel(self,anchor="w", text="Progress:", font=("Arial", 12))
        self.progress_label.pack(anchor="w", pady=(0, 1), padx=55)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=600, height=2, fg_color="#333", progress_color="#4a90e2")
        self.progress.pack(pady=(30, 10), padx=55, fill="x")
        self.progress.set(0)
        
        # Process button
        self.process_button = ctk.CTkButton(
            self, 
            text="Mulai Proses", 
            command=self.run_similarity_thread,
            fg_color="#4a90e2",
            hover_color="#357abd",
            corner_radius=0,
            width=120,
            height=40
        )
        self.process_button.pack(pady=10)
        
        # Log output
        self.log = ctk.CTkTextbox(
            self, 
            height=180,
            fg_color="#1e1e1e",
            text_color="#e0e0e0",
            border_width=1,
            border_color="#333"
        )
        self.log.pack(padx=20, pady=(0, 20), fill="both", expand=True)
    
    def create_cover_image(self):
        """Create cover image if exists"""
        cover_path = "assets/cover.png"
        if os.path.exists(cover_path):
            img = Image.open(cover_path)
            max_width = 520
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            resized_img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            self.cover_photo = ctk.CTkImage(light_image=resized_img, size=(max_width, new_height))
            self.cover_label = ctk.CTkLabel(self, image=self.cover_photo, text="")
            self.cover_label.pack(pady=(10, 20))
            
    def update_threshold_label(self, value):
        self.threshold_label.configure(text=f"Similarity Threshold: {value:.3f}")
        
    def update_iqa_label(self, value):
        self.iqa_label.configure(text=f"IQA Threshold: {value:.3f}")
        self.iqa_threshold = value 

    def create_input_section(self):
        """Create input folder selection elements"""
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=(0, 10))
        
        ctk.CTkLabel(input_frame, text="Folder Input:").pack(anchor="w", padx=5)
        
        self.input_entry = ctk.CTkEntry(
            input_frame, 
            width=500,
            height=40,
            placeholder_text="Pilih folder input...",
            fg_color="#1e1e1e",
            border_color="#333",
            corner_radius=0
        )
        self.input_entry.pack(side="left", padx=(0, 10))
        
        self.input_button = ctk.CTkButton(
            input_frame, 
            text="Pilih", 
            command=self.select_input_folder,
            fg_color="#333",
            hover_color="#444",
            corner_radius=0,
            width=80,
            height=40
        )
        self.input_button.pack(side="left")
    
    def create_output_section(self):
        """Create output folder selection elements"""
        output_frame = ctk.CTkFrame(self, fg_color="transparent")
        output_frame.pack(pady=(0, 20))
        
        ctk.CTkLabel(output_frame, text="Folder Output:").pack(anchor="w", padx=5)
        
        self.output_entry = ctk.CTkEntry(
            output_frame, 
            width=500,
            height=40,
            placeholder_text="Pilih folder output...",
            fg_color="#1e1e1e",
            border_color="#333",
            corner_radius=0
        )
        self.output_entry.pack(side="left", padx=(0, 10))
        
        self.output_button = ctk.CTkButton(
            output_frame, 
            text="Pilih", 
            command=self.select_output_folder,
            fg_color="#333",
            hover_color="#444",
            corner_radius=0,
            width=80,
            height=40
        )
        self.output_button.pack(side="left")
    
    def select_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_dir = folder
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, folder)
    
    def select_output_folder(self): 
        folder = filedialog.askdirectory()
        if folder:
            output_path = os.path.join(folder, "similarity-generated")
            os.makedirs(output_path, exist_ok=True)  # buat jika belum ada
            
            self.output_dir = output_path
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, output_path)

    
    def run_similarity_thread(self):
        if not self.source_dir or not self.output_dir:
            self.log.insert("end", "❗ Silakan pilih kedua folder terlebih dahulu.\n")
            return
        
        self.process_button.configure(state="disabled", text="Memproses...")
        self.progress.set(0)
        self.log.delete("1.0", "end") 
        
        thread = threading.Thread(target=self.run_similarity_script)
        thread.start()
    
    def run_similarity_script(self):
        try:
            if not os.path.exists("similarity.py"):
                self.log.insert("end", "[ERROR] File similarity.py tidak ditemukan.\n")
                return

            similarity_threshold = f"{self.threshold_slider.get():.6f}"
            quality_threshold = f"{self.iqa_slider.get():.2f}" 

            self.process_button.configure(state="disabled", text="Memproses...")

            process = subprocess.Popen(
                [sys.executable, "similarity.py", self.source_dir, self.output_dir, similarity_threshold, quality_threshold],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):
                self.log.insert("end", line)
                self.log.see("end")

                match_tqdm = re.search(r"(\d+)%\|", line)

                match_eval = re.search(r"Evaluasi kualitas: (\d+)/(\d+)", line)

                if match_tqdm:
                    percent = int(match_tqdm.group(1))
                    self.progress.set(percent / 100)
                    self.progress_label.configure(text=f"Generating Embeddings: {percent}%")

                elif match_eval:
                    current = int(match_eval.group(1))
                    total = int(match_eval.group(2))
                    if total > 0:
                        percent = current / total * 100
                        self.progress.set(percent / 100)
                        self.progress_label.configure(text=f"Evaluasi kualitas: {percent:.1f}%")

            process.stdout.close()
            process.wait()
        except Exception as e:
            self.log.insert("end", f"\n[EXCEPTION] {e}\n")
        finally:
            self.process_button.configure(state="normal", text="Mulai Proses")
            self.progress.set(1.0)

if __name__ == "__main__":
    app = SimilarityApp()
    app.mainloop()