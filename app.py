
import customtkinter
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image as ReportLabImage
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import threading
import os
import re
import tempfile

# Modern dark mode with blue as the primary color
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Customize fonts
FONT_FAMILY = "Segoe UI"
HEADING_FONT = (FONT_FAMILY, 16, "bold")
LABEL_FONT = (FONT_FAMILY, 12)
BUTTON_FONT = (FONT_FAMILY, 12, "bold")
ENTRY_FONT = (FONT_FAMILY, 12)

def create_empty_image():
    """Create a small black rectangle image as placeholder"""
    img = Image.new('RGB', (100, 100), color='black')
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 90, 90], outline='white', width=2)
    draw.text((50, 50), "No Image", fill='white', anchor='mm')
    return img

class TaskEntry(customtkinter.CTkFrame):
    def __init__(self, master, delete_callback):
        super().__init__(master)
        self.delete_callback = delete_callback
        self.folder_path = ""  # To store the folder path from the level
        self.empty_image = create_empty_image()  # Store the empty image placeholder
        self.placeholder_path = os.path.join(tempfile.gettempdir(), "placeholder.png")
        self.empty_image.save(self.placeholder_path)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)  # For delete button

        self.task_entry = customtkinter.CTkEntry(self, placeholder_text="Task Question", font=ENTRY_FONT)
        self.task_entry.grid(row=0, column=0, padx=15, pady=(5, 5), sticky="ew")

        self.solution_label = customtkinter.CTkLabel(self, text="Solution File Name:", anchor="w", font=LABEL_FONT)
        self.solution_label.grid(row=1, column=0, padx=15, pady=(5, 5), sticky="ew")

        self.solution_entry = customtkinter.CTkEntry(self, placeholder_text="filename.py", font=ENTRY_FONT)
        self.solution_entry.grid(row=2, column=0, padx=15, pady=(5, 5), sticky="ew")
        self.solution_entry.bind("<FocusOut>", self.load_code_from_file)

        self.image_label = customtkinter.CTkLabel(self, text="Image File:", anchor="w", font=LABEL_FONT)
        self.image_label.grid(row=3, column=0, padx=15, pady=(10, 5), sticky="ew")

        self.image_button = customtkinter.CTkButton(self, text="Choose Image", command=self.choose_image, font=BUTTON_FONT)
        self.image_button.grid(row=4, column=0, padx=15, pady=(5, 5), sticky="ew")

        self.image_path = self.placeholder_path  # Default to placeholder
        self.image_preview_label = customtkinter.CTkLabel(self, text="", width=100, height=100)
        self.image_preview_label.grid(row=5, column=0, padx=15, pady=(5, 10), sticky="ew")
        self.display_image_preview(self.placeholder_path)  # Show placeholder initially

        # Code display section
        self.code_label = customtkinter.CTkLabel(self, text="Code Preview:", anchor="w", font=LABEL_FONT)
        self.code_label.grid(row=6, column=0, padx=15, pady=(10, 5), sticky="ew")

        self.code_textbox = customtkinter.CTkTextbox(self, height=100, font=("Courier", 12))
        self.code_textbox.grid(row=7, column=0, padx=15, pady=(5, 10), sticky="ew")
        self.code_textbox.insert("0.0", "Code will appear here when solution file is specified")
        self.code_textbox.configure(state="disabled")

        self.delete_task_button = customtkinter.CTkButton(self, text="Delete Task", command=self.delete_self, fg_color="#cc0000", hover_color="#aa0000", font=BUTTON_FONT)
        self.delete_task_button.grid(row=0, column=1, padx=5, pady=5, sticky="ne")

    def set_folder_path(self, folder_path):
        """Set the folder path for this task (called from LevelFrame)"""
        self.folder_path = folder_path
        self.load_code_from_file()

    def load_code_from_file(self, event=None):
        """Load code from the specified solution file"""
        if not self.folder_path or not self.solution_entry.get():
            return
            
        solution_file = os.path.join(self.folder_path, self.solution_entry.get())
        
        try:
            with open(solution_file, 'r', encoding='utf-8') as file:
                code_content = file.read()
                
            self.code_textbox.configure(state="normal")
            self.code_textbox.delete("0.0", "end")
            self.code_textbox.insert("0.0", code_content)
            self.code_textbox.configure(state="disabled")
            
        except Exception as e:
            self.code_textbox.configure(state="normal")
            self.code_textbox.delete("0.0", "end")
            self.code_textbox.insert("0.0", f"Error loading code: {str(e)}")
            self.code_textbox.configure(state="disabled")

    def choose_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.image_path = file_path
            self.display_image_preview(file_path)
        else:
            # Use placeholder if no image selected
            self.image_path = self.placeholder_path
            self.display_image_preview(self.placeholder_path)

    def display_image_preview(self, image_path):
        try:
            if image_path == self.placeholder_path:
                img = self.empty_image
            else:
                img = Image.open(image_path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            self.image_preview_label.configure(image=photo, text="")
            self.image_preview_label.image = photo
        except Exception as e:
            self.image_preview_label.configure(text="Error loading image")
            print(f"Error loading image: {e}")
            self.image_path = self.placeholder_path

    def get_task_data(self):
        """Get the code content from the textbox"""
        code_content = self.code_textbox.get("0.0", "end").strip()
        if code_content.startswith("Error") or code_content.startswith("Code will appear"):
            code_content = ""  # Don't include placeholder or error text
            
        return {
            "task": self.task_entry.get(),
            "solution_file": self.solution_entry.get(),
            "image_path": self.image_path if self.image_path != self.placeholder_path else None,
            "code_snippet": code_content
        }

    def clear_task_data(self):
        self.task_entry.delete('0', customtkinter.END)
        self.solution_entry.delete('0', customtkinter.END)
        self.image_path = self.placeholder_path
        self.display_image_preview(self.placeholder_path)
        self.code_textbox.configure(state="normal")
        self.code_textbox.delete("0.0", "end")
        self.code_textbox.insert("0.0", "Code will appear here when solution file is specified")
        self.code_textbox.configure(state="disabled")

    def delete_self(self):
        if self.delete_callback:
            self.delete_callback(self)

class LevelFrame(customtkinter.CTkFrame):
    def __init__(self, master, level_number, delete_callback):
        super().__init__(master)
        self.level_number = level_number
        self.delete_callback = delete_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)

        self.level_label = customtkinter.CTkLabel(self, text=f"Level {level_number}:", anchor="w", font=HEADING_FONT)
        self.level_label.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 5), sticky="ew")

        self.level_name_entry = customtkinter.CTkEntry(self, placeholder_text="Level Name", font=ENTRY_FONT)
        self.level_name_entry.grid(row=1, column=0, columnspan=3, padx=15, pady=(5, 5), sticky="ew")

        self.folder_label = customtkinter.CTkLabel(self, text="Folder:", anchor="w", font=LABEL_FONT)
        self.folder_label.grid(row=2, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="ew")

        self.folder_entry = customtkinter.CTkEntry(self, placeholder_text="Folder Path", font=ENTRY_FONT)
        self.folder_entry.grid(row=3, column=0, columnspan=2, padx=15, pady=(5, 5), sticky="ew")

        self.folder_button = customtkinter.CTkButton(self, text="Browse", width=80, command=self.browse_folder, font=BUTTON_FONT)
        self.folder_button.grid(row=3, column=2, padx=(5, 15), pady=(5, 5), sticky="e")

        # Task Navigation Frame
        self.task_nav_frame = customtkinter.CTkFrame(self)
        self.task_nav_frame.grid(row=4, column=0, columnspan=4, padx=15, pady=(10, 10), sticky="ew")
        self.task_nav_frame.grid_columnconfigure(0, weight=1)
        self.task_nav_frame.grid_columnconfigure(1, weight=1)
        self.task_nav_frame.grid_columnconfigure(2, weight=1)

        self.task_slider = customtkinter.CTkSlider(self.task_nav_frame, from_=1, to=1, number_of_steps=1, command=self.update_task_display)
        self.task_slider.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="ew")

        self.task_label = customtkinter.CTkLabel(self.task_nav_frame, text="Task 1 of 1", font=LABEL_FONT)
        self.task_label.grid(row=1, column=1, padx=10, pady=(0, 5))

        self.prev_task_button = customtkinter.CTkButton(self.task_nav_frame, text="Previous Task", command=self.prev_task, font=BUTTON_FONT)
        self.prev_task_button.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")

        self.next_task_button = customtkinter.CTkButton(self.task_nav_frame, text="Next Task", command=self.next_task, font=BUTTON_FONT)
        self.next_task_button.grid(row=2, column=2, padx=10, pady=(5, 10), sticky="e")

        self.tasks_frame = customtkinter.CTkFrame(self)
        self.tasks_frame.grid(row=5, column=0, columnspan=4, padx=15, pady=(0, 10), sticky="ew")
        self.tasks_frame.grid_columnconfigure(0, weight=1)

        self.task_entries = []
        self.add_task() # Add a default task
        self.current_task_index = 0
        self.update_task_display(1)

        self.add_task_button = customtkinter.CTkButton(self, text="Add Task", command=self.add_task, font=BUTTON_FONT)
        self.add_task_button.grid(row=6, column=0, columnspan=4, padx=10, pady=(5, 10), sticky="ew")

        self.delete_button = customtkinter.CTkButton(self, text="Delete Level", width=120, command=self.delete_self, fg_color="#cc0000", hover_color="#aa0000", font=BUTTON_FONT)
        self.delete_button.grid(row=0, column=3, padx=(5, 15), pady=(15, 5), sticky="ne")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, customtkinter.END)
            self.folder_entry.insert(0, folder_selected)
            # Update all tasks with the new folder path
            for task in self.task_entries:
                task.set_folder_path(folder_selected)

    def add_task(self):
        task_entry = TaskEntry(self.tasks_frame, self.remove_task)
        self.task_entries.append(task_entry)
        self.update_tasks_ui()
        self.task_slider.configure(to=len(self.task_entries), number_of_steps=len(self.task_entries))
        self.current_task_index = len(self.task_entries) - 1
        self.update_task_display(len(self.task_entries))
        
        # Set the folder path if it's already specified
        if self.folder_entry.get():
            task_entry.set_folder_path(self.folder_entry.get())

    def remove_task(self, task_to_remove):
        if task_to_remove in self.task_entries:
            task_index = self.task_entries.index(task_to_remove)
            task_to_remove.destroy()
            self.task_entries.remove(task_to_remove)
            self.update_tasks_ui()
            self.task_slider.configure(to=len(self.task_entries), number_of_steps=len(self.task_entries))
            if self.task_entries:
                self.current_task_index = min(self.current_task_index, len(self.task_entries) - 1)
                self.update_task_display(self.current_task_index + 1)
            else:
                self.current_task_index = 0
                self.update_task_display(0)

    def update_tasks_ui(self):
        for i, task_entry in enumerate(self.task_entries):
            task_entry.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="nsew")
            self.tasks_frame.grid_columnconfigure(0, weight=1)
        self.tasks_frame.update_idletasks()

    def update_task_display(self, task_number):
        if self.task_entries:
            self.current_task_index = int(task_number) - 1
            for i, task_entry in enumerate(self.task_entries):
                if i == self.current_task_index:
                    task_entry.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="ew")
                else:
                    task_entry.grid_forget()
            self.task_label.configure(text=f"Task {self.current_task_index + 1} of {len(self.task_entries)}")
        else:
            self.task_label.configure(text="No tasks added")

    def prev_task(self):
        if self.task_entries:
            self.current_task_index = max(0, self.current_task_index - 1)
            self.task_slider.set(self.current_task_index + 1)
            self.update_task_display(self.current_task_index + 1)

    def next_task(self):
        if self.task_entries:
            self.current_task_index = min(len(self.task_entries) - 1, self.current_task_index + 1)
            self.task_slider.set(self.current_task_index + 1)
            self.update_task_display(self.current_task_index + 1)

    def get_level_data(self):
        tasks_data = [task.get_task_data() for task in self.task_entries]
        return {
            "level_name": self.level_name_entry.get(),
            "folder": self.folder_entry.get(),
            "tasks": tasks_data
        }

    def delete_self(self):
        if self.delete_callback:
            self.delete_callback(self)

def generate_pdf_report(report_data, progress_bar, app, save_path):
    try:
        os.makedirs(save_path, exist_ok=True)
        pdf_filename = f"Skill_{report_data['skill_name']}_Report.pdf"
        full_path = os.path.join(save_path, pdf_filename)

        c = canvas.Canvas(full_path, pagesize=letter)
        c.setTitle(f"Skill {report_data['skill_name']} Report")

        # Setup styles
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']
        header_style = styles['h1']
        level_style = styles['h2']
        task_style = styles['h3']
        solution_style = ParagraphStyle(
            name='SolutionStyle', 
            parent=normal_style, 
            fontName='Helvetica-Bold', 
            fontSize=10, 
            leading=12
        )
        
        # Improved code style with better formatting
        code_style = ParagraphStyle(
            name='CodeStyle',
            parent=normal_style,
            fontName='Courier',
            fontSize=10,
            leading=12,
            backColor="#f0f0f0",
            leftIndent=20,
            rightIndent=20,
            spaceBefore=6,
            spaceAfter=6
        )

        # Adjust spacing
        header_style.spaceAfter = 10
        level_style.spaceAfter = 5
        task_style.spaceAfter = 3
        normal_style.spaceAfter = 2
        solution_style.spaceAfter = 2

        y_position = letter[1] - inch
        line_height = 12

        def draw_paragraph(text, style=normal_style, leading=None):
            nonlocal y_position
            p = Paragraph(text, style)
            width, height = p.wrapOn(c, letter[0] - 2 * inch, letter[1])
            if y_position - height < inch:
                c.showPage()
                y_position = letter[1] - inch
            p.drawOn(c, inch, y_position - height)
            y_position -= height + (leading if leading is not None else style.leading)

        # Draw header with user info
        if report_data.get('user_name') or report_data.get('user_role'):
            user_info = []
            if report_data.get('user_name'):
                user_info.append(f"<b>Name :</b> {report_data['user_name']}")
            if report_data.get('user_role'):
                user_info.append(f"<b>Role:</b> {report_data['user_role']}")
            
            user_style = ParagraphStyle(
                name='UserInfoStyle',
                parent=normal_style,
                fontSize=12,
                leading=14,
                spaceAfter=12
            )
        
        # Draw main header
        draw_paragraph(f"Skill {report_data['skill_name']} Report", header_style, leading=14)
        draw_paragraph("", leading=4)

        for i, level in enumerate(report_data["levels"]):
            # Process folder path to show only last 3 directories
            folder_path = level['folder']
            path_parts = folder_path.replace('\\', '/').split('/')
            shortened_path = '/'.join(path_parts[-3:]) if len(path_parts) >= 3 else folder_path
            
            draw_paragraph(f"Level {i + 1}: {level['level_name']}", level_style)
            draw_paragraph(f"Folder: {shortened_path}", normal_style, leading=normal_style.fontSize * 1.2)
            draw_paragraph("", leading=2)

            for j, task in enumerate(level['tasks']):
                draw_paragraph(f"[{j + 1}] Task: {task['task']}", solution_style)
                draw_paragraph(f"Solution File: {task['solution_file']}", normal_style)

                if task['code_snippet']:
                    # Format the code with proper indentation and newlines
                    formatted_code = task['code_snippet'].replace('\n', '<br/>')
                    formatted_code = formatted_code.replace(' ', '&nbsp;')
                    formatted_code = formatted_code.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
                    draw_paragraph("Code:", normal_style)
                    draw_paragraph(formatted_code, code_style)

                # Always include an image - either the selected one or a placeholder
                try:
                    if task['image_path']:
                        img_path = task['image_path']
                    else:
                        # Create a placeholder image
                        img = create_empty_image()
                        img_path = os.path.join(tempfile.gettempdir(), f"placeholder_{i}_{j}.png")
                        img.save(img_path)
                    
                    reportlab_img = ReportLabImage(img_path)
                    available_width = letter[0] - 2 * inch
                    reportlab_img.drawWidth = min(reportlab_img.drawWidth, available_width)
                    
                    if y_position - reportlab_img.drawHeight < inch:
                        c.showPage()
                        y_position = letter[1] - inch

                    reportlab_img.drawOn(c, inch, y_position - reportlab_img.drawHeight - 0.05 * inch * (72/12))
                    y_position -= (reportlab_img.drawHeight + 0.5 * inch)  # Increased space after image (0.5 inch)
                    
                    # Add extra blank space after image
                    draw_paragraph("", leading=12)

                    # Add a task separator line (thinner than level separator)
                    if j < len(level['tasks']) - 1:  # Don't add after last task in level
                        c.setLineWidth(0.5)  # Thin line
                        c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Light gray
                        c.line(inch * 1.5, y_position - 6, letter[0] - inch * 1.5, y_position - 6)
                        y_position -= 24  # Space after line

                except Exception as e:
                    draw_paragraph(f"Error embedding image: {e}")
                
                # Add significant space between tasks
                draw_paragraph("", leading=24)  # 24 points space between tasks

            # VERY BIG SPACE BETWEEN LEVELS - 1.5 inches (108 points)
            if i < len(report_data["levels"]) - 1:  # Don't add after last level
                y_position -= 1.5 * inch
                if y_position < inch:  # If we're too close to bottom
                    c.showPage()
                    y_position = letter[1] - inch
                
                # Visual separator line between levels - more elaborate
                c.setLineWidth(2.0)  # Thicker line
                c.setStrokeColorRGB(0.7, 0.7, 0.7)  # Blue color
                c.line(inch, y_position, letter[0] - inch, y_position)

                # # Add decorative elements to the line
                # c.setFillColorRGB(0.2, 0.5, 0.8)  # Blue color
                # c.circle(inch, y_position, 5, fill=1)  # Left circle
                # c.circle(letter[0] - inch, y_position, 5, fill=1)  # Right circle

                y_position -= 0.25 * inch  # Space after line
                
                # Optional: Add "Next Level" text
                draw_paragraph("→ Next Level →", 
                    ParagraphStyle(
                        name='Separator',
                        parent=normal_style,
                        fontName='Helvetica-Bold',
                        fontSize=12,
                        textColor='#888888',
                        alignment=1  # Center aligned
                    ),
                    leading=12)
        draw_paragraph("<br/>".join(user_info), user_style)

        c.save()
        messagebox.showinfo("Success", f"PDF generated successfully at:\n{full_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
    finally:
        progress_bar.set(1.0)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Skill Report Data Entry Program")
        self.geometry("750x900")
        self.minsize(700, 700)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Header frame for title and basic info
        self.header_frame = customtkinter.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # User info section
        self.user_info_frame = customtkinter.CTkFrame(self.header_frame)
        self.user_info_frame.grid(row=0, column=0, padx=15, pady=(5, 5), sticky="ew")
        self.user_info_frame.grid_columnconfigure(0, weight=1)
        self.user_info_frame.grid_columnconfigure(1, weight=1)

        self.user_name_label = customtkinter.CTkLabel(self.user_info_frame, text="Your Name :", anchor="w", font=LABEL_FONT)
        self.user_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.user_name_entry = customtkinter.CTkEntry(self.user_info_frame, placeholder_text="Your Name", font=ENTRY_FONT)
        self.user_name_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.user_role_label = customtkinter.CTkLabel(self.user_info_frame, text="Your Role:", anchor="w", font=LABEL_FONT)
        self.user_role_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.user_role_entry = customtkinter.CTkEntry(self.user_info_frame, placeholder_text="Your Role", font=ENTRY_FONT)
        self.user_role_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.skill_label = customtkinter.CTkLabel(self.header_frame, text="Skill Report:", anchor="w", font=HEADING_FONT)
        self.skill_label.grid(row=1, column=0, padx=15, pady=(15, 5), sticky="ew")

        self.skill_entry = customtkinter.CTkEntry(self.header_frame, placeholder_text="Skill Name", font=ENTRY_FONT)
        self.skill_entry.grid(row=2, column=0, padx=15, pady=(5, 10), sticky="ew")

        # Save location frame
        self.save_location_frame = customtkinter.CTkFrame(self.header_frame)
        self.save_location_frame.grid(row=3, column=0, padx=15, pady=(10, 10), sticky="ew")
        self.save_location_frame.grid_columnconfigure(0, weight=1)
        self.save_location_frame.grid_columnconfigure(1, weight=0)

        self.save_location_label = customtkinter.CTkLabel(self.save_location_frame, text="Save Location:", anchor="w", font=LABEL_FONT)
        self.save_location_label.grid(row=0, column=0, padx=0, pady=(5, 0), sticky="ew")

        self.save_location_entry = customtkinter.CTkEntry(self.save_location_frame, placeholder_text="Choose Save Folder", font=ENTRY_FONT, state="readonly")
        self.save_location_entry.grid(row=1, column=0, padx=0, pady=(5, 0), sticky="ew")
        self.save_location_path = os.getcwd()
        self.save_location_entry.insert(0, self.save_location_path)

        self.save_location_button = customtkinter.CTkButton(self.save_location_frame, text="Browse", command=self.browse_save_location, font=BUTTON_FONT)
        self.save_location_button.grid(row=1, column=1, padx=(10, 0), pady=(5, 0), sticky="e")

        # Automation button
        self.automate_button = customtkinter.CTkButton(
            self, 
            text="Auto-Import Course Structure", 
            command=self.import_course_structure,
            font=BUTTON_FONT,
            fg_color="#2b8a3e",
            hover_color="#2f9e44"
        )
        self.automate_button.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")

        # Button to add a new level
        self.add_level_button = customtkinter.CTkButton(self, text="Add New Level", command=self.add_level, font=BUTTON_FONT)
        self.add_level_button.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Frame for level entries with scrollbar
        self.levels_frame = customtkinter.CTkFrame(self)
        self.levels_frame.grid(row=6, column=0, padx=20, pady=(10, 10), sticky="nsew")
        
        # Canvas and scrollbar
        self.levels_canvas = customtkinter.CTkCanvas(self.levels_frame)
        self.levels_scrollbar = customtkinter.CTkScrollbar(self.levels_frame, orientation="vertical", command=self.levels_canvas.yview)
        
        # Configure canvas
        self.levels_canvas.configure(yscrollcommand=self.levels_scrollbar.set)
        self.levels_canvas.bind('<Configure>', lambda e: self.levels_canvas.configure(scrollregion=self.levels_canvas.bbox("all")))
        
        # Mouse wheel binding
        self.levels_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Pack scrollbar and canvas
        self.levels_scrollbar.pack(side="right", fill="y")
        self.levels_canvas.pack(side="left", fill="both", expand=True)
        
        # Inner frame
        self.levels_inner_frame = customtkinter.CTkFrame(self.levels_canvas)
        self.levels_canvas_window = self.levels_canvas.create_window((0, 0), window=self.levels_inner_frame, anchor="nw")
        self.levels_canvas.bind('<Configure>', lambda e: self.levels_canvas.itemconfig(self.levels_canvas_window, width=e.width))
        self.levels_inner_frame.bind("<Configure>", lambda e: self.levels_canvas.configure(scrollregion=self.levels_canvas.bbox("all")))
        self.levels_inner_frame.grid_columnconfigure(0, weight=1)

        self.level_entries = []
        self.add_level()  # Add default level

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.progress_bar.set(0)

        # Generate report button
        self.generate_button = customtkinter.CTkButton(self, text="Generate PDF Report", command=self.generate_report, font=BUTTON_FONT)
        self.generate_button.grid(row=8, column=0, padx=20, pady=(10, 20), sticky="ew")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.delta:
            self.levels_canvas.yview_scroll(-1 * (event.delta // abs(event.delta)), "units")
        else:
            # For touchpad scrolling
            self.levels_canvas.yview_scroll(-1 * event.delta, "units")

    def import_course_structure(self):
        """Automatically import course structure from current directory"""
        base_path = os.getcwd()  # Use current working directory
        print(base_path)
        
        try:
            # Clear existing levels
            for level in self.level_entries[:]:
                self.remove_level(level)
            
            # Find all Day folders (with or without brackets)
            day_folders = []
            for item in os.listdir(base_path):
                if os.path.isdir(os.path.join(base_path, item)):
                    # Match both "Day1" and "Day1 [Description]" patterns
                    day_match = re.match(r'Day(\d+)(?:\s*\[.*\])?', item, re.IGNORECASE)
                    if day_match:
                        day_number = int(day_match.group(1))
                        day_folders.append((day_number, item))
            
            # Sort day folders numerically
            day_folders.sort(key=lambda x: x[0])
            
            if not day_folders:
                messagebox.showwarning("No Day Folders", "No Day folders found in current directory")
                return
                
            # Process each day folder
            for day_number, day_folder in day_folders:
                full_path = os.path.join(base_path, day_folder)
                
                # Extract level name from folder name (e.g., "Day1 [Python Basics]" -> "Python Basics")
                level_name = day_folder
                if '[' in day_folder and ']' in day_folder:
                    level_name = day_folder.split('[')[1].split(']')[0].strip()
                else:
                    # If no description in brackets, use default name
                    level_name = f"Level {day_number}"
                
                # Add new level
                self.add_level()
                new_level = self.level_entries[-1]
                new_level.level_name_entry.insert(0, level_name)
                new_level.folder_entry.insert(0, full_path)
                
                # Find all .py files in the day folder
                py_files = []
                for f in os.listdir(full_path):
                    if f.endswith('.py'):
                        # Try to extract numbers from filename (supports 1.1.py, 1-1.py, etc.)
                        num_match = re.match(r'(\d+)[\.\-](\d+)', f)
                        if num_match:
                            try:
                                main_num = int(num_match.group(1))
                                sub_num = int(num_match.group(2))
                                py_files.append((main_num, sub_num, f))
                            except:
                                pass
                
                # Sort files by their numbers
                py_files.sort()
                py_files = [f[2] for f in py_files]
                
                # Add tasks for each .py file
                for py_file in py_files:
                    file_path = os.path.join(full_path, py_file)
                    
                    # Read first line as task question
                    task_question = ""
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            if first_line.startswith('#') or first_line.startswith('"') or first_line.startswith("'"):
                                task_question = first_line[1:].strip()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                    
                    if not task_question:
                        task_question = f"Complete the exercise in {py_file}"
                    
                    # Add task
                    new_level.add_task()
                    task = new_level.task_entries[-1]
                    task.task_entry.insert(0, task_question)
                    task.solution_entry.insert(0, py_file)
                    task.set_folder_path(full_path)

                    # Look for matching screenshots
                    screenshots_dir = os.path.join(full_path, "Screenshots")
                    if os.path.exists(screenshots_dir):
                        # Extract task number from filename (e.g., "1.1.py" -> "1.1")
                        file_prefix = os.path.splitext(py_file)[0]
                        # Check for image files with matching prefix
                        for img_ext in ['.png', '.jpg', '.jpeg']:
                            img_path = os.path.join(screenshots_dir, file_prefix + img_ext)
                            if os.path.exists(img_path):
                                task.image_path = img_path
                                task.display_image_preview(img_path)
                                break

                    # Look for matching screenshots
                    screenshots_dir = os.path.join(full_path, "Screenshots")
                    if os.path.exists(screenshots_dir):
                        file_prefix = os.path.splitext(py_file)[0]

                        for img_ext in ['.png', '.jpg', '.jpeg']:
                            img_path = os.path.join(screenshots_dir, file_prefix + img_ext)
                            if os.path.exists(img_path):
                                task.image_path = img_path
                                task.display_image_preview(img_path)
                                break


                    

                if new_level.task_entries:
                    first_task = new_level.task_entries[0]
                    new_level.remove_task(first_task)
                    
                    # The placeholder image is already set by default in the TaskEntry constructor
                    
            messagebox.showinfo("Success", f"Imported {len(self.level_entries)} levels with {sum(len(level.task_entries) for level in self.level_entries)} tasks")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import course structure:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def browse_save_location(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.save_location_path = folder_selected
            self.save_location_entry.configure(state="normal")
            self.save_location_entry.delete(0, customtkinter.END)
            self.save_location_entry.insert(0, self.save_location_path)
            self.save_location_entry.configure(state="readonly")

    def add_level(self):
        level_number = len(self.level_entries) + 1
        level_frame = LevelFrame(self.levels_inner_frame, level_number, self.remove_level)
        level_frame.grid(row=level_number - 1, column=0, padx=15, pady=(10, 10), sticky="nsew")
        self.level_entries.append(level_frame)
        self.update_levels_ui()

    def remove_level(self, level_to_remove):
        if level_to_remove in self.level_entries:
            level_to_remove.destroy()
            self.level_entries.remove(level_to_remove)
            self.update_levels_ui()

    def update_levels_ui(self):
        for i, level_frame in enumerate(self.level_entries):
            level_frame.level_label.configure(text=f"Level {i + 1}:")
            level_frame.grid(row=i, column=0, padx=15, pady=(10, 10), sticky="ewn")
        self.levels_inner_frame.update_idletasks()
        total_height = sum(frame.winfo_reqheight() + 20 for frame in self.level_entries) + 20
        self.levels_inner_frame.configure(height=total_height)
        self.levels_canvas.configure(scrollregion=self.levels_canvas.bbox("all"))

    def generate_report(self):
        skill_name = self.skill_entry.get()
        if not skill_name:
            messagebox.showerror("Error", "Please enter the Skill Name.")
            return

        report_data = {
            "skill_name": skill_name,
            "user_name": self.user_name_entry.get(),
            "user_role": self.user_role_entry.get(),
            "levels": []
        }
        
        validation_errors = []
        for level_frame in self.level_entries:
            level_data = level_frame.get_level_data()
            
            if not level_data["level_name"]:
                validation_errors.append(f"Level {level_frame.level_number}: Missing level name")
            if not level_data["folder"]:
                validation_errors.append(f"Level {level_frame.level_number}: Missing folder path")
            if not level_data["tasks"]:
                validation_errors.append(f"Level {level_data.get('level_name', level_frame.level_number)}: No tasks added")
                
            for i, task in enumerate(level_data["tasks"]):
                if not task["task"]:
                    validation_errors.append(f"Level {level_data.get('level_name', level_frame.level_number)} Task {i+1}: Missing task question")
                if not task["solution_file"]:
                    validation_errors.append(f"Level {level_data.get('level_name', level_frame.level_number)} Task {i+1}: Missing solution file")

        if validation_errors:
            messagebox.showerror("Validation Errors", "\n".join(validation_errors))
            return

        for level_frame in self.level_entries:
            level_data = level_frame.get_level_data()
            report_data["levels"].append(level_data)

        try:
            self.generate_button.configure(state="disabled")
            threading.Thread(
                target=generate_pdf_report,
                args=(report_data, self.progress_bar, self, self.save_location_path),
                daemon=True
            ).start()
            self.after(100, self.check_thread)
        except Exception as e:
            messagebox.showerror("Generation Error", f"Failed to start PDF generation: {str(e)}")
            self.generate_button.configure(state="normal")

    def check_thread(self):
        if threading.active_count() > 1:
            self.after(100, self.check_thread)
        else:
            self.generate_button.configure(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()
