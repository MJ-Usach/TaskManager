import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv

class RoundedTaskFrame(tk.Canvas):
    """A canvas-based widget that displays a task in a rounded rectangle"""
    def __init__(self, parent, text, color, **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text
        self.color = color
        self.bg_color = kwargs.get('bg', '#3d3d3d')
        
        self.config(highlightthickness=0, height=35, bg=self.bg_color)
        self.bind("<Configure>", self.draw_rounded_rect)
        
    def draw_rounded_rect(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        if width <= 1:
            return
        
        height = 35
        radius = 8
        
        # Draw rounded rectangle
        self.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, 
                       fill=self.color, outline="")
        self.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, 
                       fill=self.color, outline="")
        self.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, 
                       fill=self.color, outline="")
        self.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, 
                       fill=self.color, outline="")
        
        self.create_rectangle(radius, 0, width-radius, height, fill=self.color, outline="")
        self.create_rectangle(0, radius, width, height-radius, fill=self.color, outline="")
        
        # Draw text - aligned left with padding
        display_text = self.text[:50] + "..." if len(self.text) > 50 else self.text
        self.create_text(15, height/2, text=display_text, fill="#ffffff", 
                        font=("Segoe UI", 9), anchor="w")

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Developer Task Manager")
        self.root.geometry("1400x700")
        
        # Dark mode colors
        self.bg_dark = "#1e1e1e"
        self.bg_secondary = "#2d2d2d"
        self.bg_tertiary = "#3d3d3d"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        
        # Configure root
        self.root.configure(bg=self.bg_dark)
        
        # Column names
        self.columns = ["Pending", "Done", "Discoveries", "In Revision", "Extras"]
        
        # Data file
        self.data_file = "tasks.json"
        self.tasks = self.load_tasks()
        self.task_details = {}
        self.column_frames = {}
        self.task_containers = {}
        
        # Setup UI
        self.setup_ui()
        self.refresh_all_columns()
        
    def setup_ui(self):
        # Title and CSV buttons
        top_frame = tk.Frame(self.root, bg=self.bg_dark)
        top_frame.pack(fill=tk.X)
        
        title_label = tk.Label(top_frame, text="Task Manager", 
                               font=("Segoe UI", 16), bg=self.bg_dark, fg=self.text_color, pady=20)
        title_label.pack(side=tk.LEFT, padx=15)
        
        csv_frame = tk.Frame(top_frame, bg=self.bg_dark)
        csv_frame.pack(side=tk.RIGHT, padx=15, pady=20)
        
        btn_style = {"font": ("Segoe UI", 9), "bd": 0, "cursor": "hand2", "pady": 6, "padx": 12}
        
        tk.Button(csv_frame, text="📥 Import CSV", command=self.import_csv,
                 bg=self.bg_tertiary, fg=self.text_color, 
                 activebackground=self.bg_tertiary, activeforeground=self.text_color,
                 **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(csv_frame, text="📤 Export CSV", command=self.export_csv,
                 bg=self.bg_tertiary, fg=self.text_color,
                 activebackground=self.bg_tertiary, activeforeground=self.text_color,
                 **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Column header colors
        self.header_colors = {
            "Pending": "#e85d75",
            "Done": "#5fb878",
            "Discoveries": "#f9a825",
            "In Revision": "#42a5f5",
            "Extras": "#ab47bc"
        }
        
        # Create 5 columns
        for i, col_name in enumerate(self.columns):
            col_frame = tk.Frame(main_frame, bg=self.bg_secondary, highlightthickness=1, 
                               highlightbackground=self.bg_tertiary)
            col_frame.grid(row=0, column=i, sticky="nsew", padx=6, pady=5)
            main_frame.columnconfigure(i, weight=1)
            main_frame.rowconfigure(0, weight=1)
            
            # Header
            header = tk.Label(col_frame, text=col_name, font=("Segoe UI", 11),
                            bg=self.bg_secondary, fg=self.header_colors[col_name], pady=12)
            header.pack(fill=tk.X)
            
            # Tasks list with scrollbar
            list_frame = tk.Frame(col_frame, bg=self.bg_secondary)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
            
            scrollbar = tk.Scrollbar(list_frame, bg=self.bg_tertiary, troughcolor=self.bg_secondary,
                                   activebackground=self.text_secondary, width=10, 
                                   highlightthickness=0, bd=0)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            canvas = tk.Canvas(list_frame, bg=self.bg_tertiary, highlightthickness=0, bd=0)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=canvas.yview)
            canvas.config(yscrollcommand=scrollbar.set)
            
            tasks_container = tk.Frame(canvas, bg=self.bg_tertiary)
            canvas_window = canvas.create_window((0, 0), window=tasks_container, anchor="nw")
            
            def on_configure(event, c=canvas, w=canvas_window):
                c.configure(scrollregion=c.bbox("all"))
                c.itemconfig(w, width=event.width)
            
            tasks_container.bind("<Configure>", on_configure)
            canvas.bind("<Configure>", lambda e, c=canvas, w=canvas_window: c.itemconfig(w, width=e.width))
            
            self.task_containers[col_name] = tasks_container
            
            # Buttons
            btn_frame = tk.Frame(col_frame, bg=self.bg_secondary)
            btn_frame.pack(fill=tk.X, padx=8, pady=8)
            
            btn_style = {"font": ("Segoe UI", 9), "bd": 0, "highlightthickness": 0,
                        "activebackground": self.bg_tertiary, "cursor": "hand2", "pady": 6}
            
            tk.Button(btn_frame, text="+ Add Task", command=lambda col=col_name: self.add_task(col),
                     bg=self.bg_tertiary, fg=self.header_colors[col_name], 
                     activeforeground=self.header_colors[col_name], **btn_style).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
            
            self.column_frames[col_name] = col_frame
    
    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'tasks' in data:
                        self.task_details = data.get('details', {})
                        return data['tasks']
                    else:
                        return data if isinstance(data, dict) else {col: [] for col in self.columns}
            except:
                return {col: [] for col in self.columns}
        return {col: [] for col in self.columns}
    
    def save_tasks(self):
        with open(self.data_file, 'w') as f:
            json.dump({'tasks': self.tasks, 'details': self.task_details}, f, indent=2)
    def refresh_all_columns(self):
        for col_name in self.columns:
            container = self.task_containers[col_name]
            color = self.header_colors[col_name]
            
            for widget in container.winfo_children():
                widget.destroy()
            
            for idx, task in enumerate(self.tasks.get(col_name, [])):
                task_frame = tk.Frame(container, bg=self.bg_tertiary)
                task_frame.pack(fill=tk.X, padx=5, pady=3)
                
                task_canvas = RoundedTaskFrame(task_frame, task, color, bg=self.bg_tertiary)
                task_canvas.pack(fill=tk.X, expand=True)
                
                task_canvas.bind("<Button-1>", lambda e, col=col_name, i=idx: self.show_task_details(col, i))
                task_canvas.bind("<Double-Button-1>", lambda e, col=col_name, i=idx: self.edit_task(col, i))
                task_canvas.config(cursor="hand2")
    
    def show_task_details(self, column, index):
        if index >= len(self.tasks.get(column, [])):
            return
            
        task = self.tasks[column][index]
        task_key = f"{column}::{task}"
        details = self.task_details.get(task_key, "")
        
        # Create modal dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Task Details")
        dialog.geometry("600x550")
        dialog.transient(self.root)
        dialog.configure(bg=self.bg_secondary)
        dialog.update()
        dialog.grab_set()
        
        # Header
        header_frame = tk.Frame(dialog, bg=self.header_colors[column], highlightthickness=0)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        
        tk.Label(header_frame, text=f"Edit Task - {column}", font=("Segoe UI", 12, "bold"),
                bg=self.header_colors[column], fg="#ffffff", pady=12, padx=15).pack(fill=tk.X)
        
        # Main content frame
        content_frame = tk.Frame(dialog, bg=self.bg_secondary)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Task title section
        title_label_frame = tk.Frame(content_frame, bg=self.bg_secondary)
        title_label_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(title_label_frame, text="Task Title:", font=("Segoe UI", 10),
                bg=self.bg_secondary, fg=self.text_color).pack(side=tk.LEFT)
        
        # Task title entry
        title_frame = tk.Frame(content_frame, bg=self.bg_tertiary, highlightthickness=1,
                              highlightbackground=self.bg_tertiary)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_entry = tk.Entry(title_frame, font=("Segoe UI", 11), bg=self.bg_tertiary,
                              fg=self.text_color, bd=0, insertbackground=self.text_color)
        title_entry.pack(fill=tk.X, padx=10, pady=10)
        title_entry.insert(0, task)
        
        # Column selection dropdown
        column_frame = tk.Frame(content_frame, bg=self.bg_secondary)
        column_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(column_frame, text="Column:", font=("Segoe UI", 10),
                bg=self.bg_secondary, fg=self.text_color).pack(side=tk.LEFT)
        
        column_var = tk.StringVar(value=column)
        column_menu = tk.OptionMenu(column_frame, column_var, *self.columns)
        column_menu.config(font=("Segoe UI", 10), bg=self.bg_tertiary, fg=self.text_color,
                          activebackground=self.bg_tertiary, activeforeground=self.text_color,
                          highlightthickness=0, bd=0, cursor="hand2")
        column_menu["menu"].config(font=("Segoe UI", 10), bg=self.bg_tertiary, fg=self.text_color,
                                   activebackground=self.header_colors[column], activeforeground="#ffffff")
        column_menu.pack(side=tk.LEFT, padx=(10, 0))
        
        # Details label with character count
        details_label_frame = tk.Frame(content_frame, bg=self.bg_secondary)
        details_label_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(details_label_frame, text="Details:", font=("Segoe UI", 10),
                bg=self.bg_secondary, fg=self.text_color).pack(side=tk.LEFT)
        
        char_count_label = tk.Label(details_label_frame, text="(0 chars)", font=("Segoe UI", 9),
                bg=self.bg_secondary, fg=self.text_secondary)
        char_count_label.pack(side=tk.RIGHT)
        
        # Details text area - fixed height
        details_frame = tk.Frame(content_frame, bg=self.bg_tertiary, highlightthickness=1,
                                highlightbackground=self.bg_tertiary, height=180)
        details_frame.pack(fill=tk.X, pady=(0, 15))
        details_frame.pack_propagate(False)
        
        scrollbar = tk.Scrollbar(details_frame, bg=self.bg_tertiary, troughcolor=self.bg_secondary,
                                activebackground=self.text_secondary, width=10, 
                                highlightthickness=0, bd=0)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        details_text = tk.Text(details_frame, font=("Segoe UI", 10), bg=self.bg_tertiary,
                              fg=self.text_color, wrap=tk.WORD, bd=0, padx=10, pady=10,
                              insertbackground=self.text_color, yscrollcommand=scrollbar.set)
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=details_text.yview)
        
        details_text.insert("1.0", details)
        title_entry.focus_set()
        
        # Update character count on text change
        def update_char_count(event=None):
            char_count_label.config(text=f"({len(details_text.get('1.0', 'end-1c'))} chars)")
        
        details_text.bind("<KeyRelease>", update_char_count)
        update_char_count()  # Initial count
        
        # Button frame
        btn_frame = tk.Frame(dialog, bg=self.bg_secondary)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        btn_style = {"font": ("Segoe UI", 9), "bd": 0, "cursor": "hand2", "width": 14, "pady": 8}
        
        def save_all():
            new_title = title_entry.get().strip()
            if not new_title:
                messagebox.showwarning("Warning", "Task title cannot be empty!", parent=dialog)
                return
            
            new_column = column_var.get()
            new_details = details_text.get("1.0", "end-1c").strip()
            old_key = f"{column}::{task}"
            new_key = f"{new_column}::{new_title}"
            
            # Remove from old column
            del self.tasks[column][index]
            
            # Add to new column
            if new_column not in self.tasks:
                self.tasks[new_column] = []
            self.tasks[new_column].append(new_title)
            
            # Update details with new key
            if old_key in self.task_details:
                del self.task_details[old_key]
            self.task_details[new_key] = new_details
            
            self.save_tasks()
            self.refresh_all_columns()
            messagebox.showinfo("Success", "Task saved!", parent=dialog)
            dialog.destroy()
        
        tk.Button(btn_frame, text="💾 Save All", command=save_all,
                 bg=self.header_colors[column], fg="#ffffff", 
                 activebackground=self.header_colors[column],
                 activeforeground="#ffffff", **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Delete Task", command=lambda: (self.delete_task(column, index), dialog.destroy()),
                 bg=self.bg_tertiary, fg="#e85d75",
                 activebackground=self.bg_tertiary,
                 activeforeground="#e85d75", **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg=self.bg_tertiary, fg=self.text_secondary,
                 activebackground=self.bg_tertiary,
                 activeforeground=self.text_color, **btn_style).pack(side=tk.LEFT, padx=5)
    
    def add_task(self, column):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x180")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.bg_secondary)
        
        tk.Label(dialog, text=f"Add to {column}", font=("Segoe UI", 11),
                bg=self.bg_secondary, fg=self.text_color).pack(pady=15)
        
        entry_frame = tk.Frame(dialog, bg=self.bg_secondary)
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        task_entry = tk.Entry(entry_frame, font=("Segoe UI", 10),
                            bg=self.bg_tertiary, fg=self.text_color,
                            insertbackground=self.text_color,
                            bd=0, highlightthickness=1, highlightbackground=self.bg_tertiary)
        task_entry.pack(fill=tk.X, ipady=6, ipadx=8)
        task_entry.focus()
        
        def save_task():
            task_text = task_entry.get().strip()
            if task_text:
                if column not in self.tasks:
                    self.tasks[column] = []
                self.tasks[column].append(task_text)
                self.save_tasks()
                self.refresh_all_columns()
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Task cannot be empty!")
        
        btn_frame = tk.Frame(dialog, bg=self.bg_secondary)
        btn_frame.pack(pady=20)
        
        btn_style = {"font": ("Segoe UI", 9), "bd": 0, "cursor": "hand2", "width": 12, "pady": 8}
        
        tk.Button(btn_frame, text="Save", command=save_task, bg=self.bg_tertiary,
                 fg=self.text_color, activebackground=self.bg_tertiary,
                 activeforeground=self.text_color, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg=self.bg_tertiary, fg=self.text_secondary,
                 activebackground=self.bg_tertiary, activeforeground=self.text_color,
                 **btn_style).pack(side=tk.LEFT, padx=5)
        
        task_entry.bind("<Return>", lambda e: save_task())
    
    def edit_task(self, column, index):
        if index >= len(self.tasks.get(column, [])):
            return
        
        current_task = self.tasks[column][index]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("400x180")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.bg_secondary)
        
        tk.Label(dialog, text=f"Edit in {column}", font=("Segoe UI", 11),
                bg=self.bg_secondary, fg=self.text_color).pack(pady=15)
        
        entry_frame = tk.Frame(dialog, bg=self.bg_secondary)
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        task_entry = tk.Entry(entry_frame, font=("Segoe UI", 9),
                            bg=self.bg_tertiary, fg=self.text_color,
                            insertbackground=self.text_color,
                            bd=0, highlightthickness=1, highlightbackground=self.bg_tertiary)
        task_entry.pack(fill=tk.X, ipady=6, ipadx=8)
        task_entry.insert(0, current_task)
        task_entry.focus()
        task_entry.select_range(0, tk.END)
        
        def save_changes():
            new_text = task_entry.get().strip()
            if new_text:
                old_key = f"{column}::{current_task}"
                new_key = f"{column}::{new_text}"
                if old_key in self.task_details and old_key != new_key:
                    self.task_details[new_key] = self.task_details.pop(old_key)
                
                self.tasks[column][index] = new_text
                self.save_tasks()
                self.refresh_all_columns()
                self.close_detail_panel()
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Task cannot be empty!")
        
        btn_frame = tk.Frame(dialog, bg=self.bg_secondary)
        btn_frame.pack(pady=20)
        
        btn_style = {"font": ("Segoe UI", 9), "bd": 0, "cursor": "hand2", "width": 12, "pady": 8}
        
        tk.Button(btn_frame, text="Save", command=save_changes, bg=self.bg_tertiary,
                 fg=self.text_color, activebackground=self.bg_tertiary,
                 activeforeground=self.text_color, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                 bg=self.bg_tertiary, fg=self.text_secondary,
                 activebackground=self.bg_tertiary, activeforeground=self.text_color,
                 **btn_style).pack(side=tk.LEFT, padx=5)
        
        task_entry.bind("<Return>", lambda e: save_changes())
    
    def delete_task(self, column, index):
        if index >= len(self.tasks.get(column, [])):
            return
        
        task = self.tasks[column][index]
        
        if messagebox.askyesno("Confirm Delete", f"Delete task:\n\n{task}"):
            task_key = f"{column}::{task}"
            if task_key in self.task_details:
                del self.task_details[task_key]
            
            del self.tasks[column][index]
            self.save_tasks()
            self.refresh_all_columns()
            self.close_detail_panel()
    
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Tasks to CSV"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Column', 'Task', 'Details'])
                
                for column in self.columns:
                    for task in self.tasks.get(column, []):
                        task_key = f"{column}::{task}"
                        details = self.task_details.get(task_key, "")
                        writer.writerow([column, task, details])
            
            messagebox.showinfo("Success", f"Tasks exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Import Tasks from CSV"
        )
        
        if not file_path:
            return
        
        try:
            imported_tasks = {col: [] for col in self.columns}
            imported_details = {}
            valid_columns = set(self.columns)
            imported_count = 0
            skipped_count = 0
            duplicate_count = 0
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)
                
                for row in reader:
                    if len(row) >= 2:
                        column = row[0]
                        task = row[1]
                        details = row[2] if len(row) >= 3 else ""
                        
                        if column in valid_columns and task.strip():
                            imported_tasks[column].append(task.strip())
                            if details.strip():
                                task_key = f"{column}::{task.strip()}"
                                imported_details[task_key] = details.strip()
                            imported_count += 1
                        else:
                            skipped_count += 1
            
            if imported_count == 0:
                messagebox.showwarning("Warning", "No valid tasks found in the CSV file.")
                return
            
            # Import dialog
            import_dialog = tk.Toplevel(self.root)
            import_dialog.title("Import Options")
            import_dialog.geometry("400x330")
            import_dialog.transient(self.root)
            import_dialog.grab_set()
            import_dialog.configure(bg=self.bg_secondary)
            
            tk.Label(import_dialog, text="Import Settings", font=("Segoe UI", 12, "bold"),
                    bg=self.bg_secondary, fg=self.text_color).pack(pady=15)
            
            tk.Label(import_dialog, text=f"Found {imported_count} tasks to import",
                    font=("Segoe UI", 10), bg=self.bg_secondary, fg=self.text_secondary).pack(pady=5)
            
            mode_var = tk.StringVar(value="append")
            
            mode_frame = tk.Frame(import_dialog, bg=self.bg_secondary)
            mode_frame.pack(pady=10, padx=20, fill=tk.X)
            
            tk.Label(mode_frame, text="Import Mode:", font=("Segoe UI", 10),
                    bg=self.bg_secondary, fg=self.text_color).pack(anchor=tk.W, pady=5)
            
            tk.Radiobutton(mode_frame, text="Append to existing tasks", variable=mode_var, value="append",
                         font=("Segoe UI", 9), bg=self.bg_secondary, fg=self.text_color,
                         selectcolor=self.bg_tertiary, activebackground=self.bg_secondary,
                         activeforeground=self.text_color, bd=0).pack(anchor=tk.W, padx=20)
            
            tk.Radiobutton(mode_frame, text="Replace all existing tasks", variable=mode_var, value="replace",
                         font=("Segoe UI", 9), bg=self.bg_secondary, fg=self.text_color,
                         selectcolor=self.bg_tertiary, activebackground=self.bg_secondary,
                         activeforeground=self.text_color, bd=0).pack(anchor=tk.W, padx=20)
            
            options_frame = tk.Frame(import_dialog, bg=self.bg_secondary)
            options_frame.pack(pady=5, padx=20, fill=tk.X)
            
            check_duplicates_var = tk.BooleanVar(value=True)
            
            tk.Checkbutton(options_frame, text="Skip duplicate tasks", variable=check_duplicates_var,
                         font=("Segoe UI", 9), bg=self.bg_secondary, fg=self.text_color,
                         selectcolor=self.bg_tertiary, activebackground=self.bg_secondary,
                         activeforeground=self.text_color, bd=0).pack(anchor=tk.W, pady=3)
            
            clear_data_var = tk.BooleanVar(value=False)
            
            tk.Checkbutton(options_frame, text="Clear all current data before import",
                         variable=clear_data_var, font=("Segoe UI", 9),
                         bg=self.bg_secondary, fg="#e85d75",
                         selectcolor=self.bg_tertiary, activebackground=self.bg_secondary,
                         activeforeground="#e85d75", bd=0).pack(anchor=tk.W, pady=3)
            
            result = {"cancelled": True}
            
            def do_import():
                result["cancelled"] = False
                result["mode"] = mode_var.get()
                result["check_duplicates"] = check_duplicates_var.get()
                result["clear_data"] = clear_data_var.get()
                import_dialog.destroy()
            
            def cancel_import():
                import_dialog.destroy()
            
            btn_frame = tk.Frame(import_dialog, bg=self.bg_secondary)
            btn_frame.pack(pady=15)
            
            btn_style = {"font": ("Segoe UI", 9), "bd": 0, "cursor": "hand2", "width": 12, "pady": 8}
            
            tk.Button(btn_frame, text="Import", command=do_import, bg=self.bg_tertiary, 
                     fg=self.text_color, activebackground=self.bg_tertiary,
                     activeforeground=self.text_color, **btn_style).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Cancel", command=cancel_import, 
                     bg=self.bg_tertiary, fg=self.text_secondary,
                     activebackground=self.bg_tertiary, activeforeground=self.text_color,
                     **btn_style).pack(side=tk.LEFT, padx=5)
            
            import_dialog.wait_window()
            
            if result["cancelled"]:
                return
            
            if result["clear_data"]:
                confirm = messagebox.askyesno(
                    "Confirm Clear",
                    "Are you sure you want to delete ALL current tasks?\n\nThis action cannot be undone!",
                    icon='warning'
                )
                if not confirm:
                    return
                self.tasks = {col: [] for col in self.columns}
                self.task_details = {}
            
            if result["mode"] == "replace":
                self.tasks = {col: [] for col in self.columns}
            
            for column in self.columns:
                for task in imported_tasks[column]:
                    if result["check_duplicates"]:
                        if task not in self.tasks[column]:
                            self.tasks[column].append(task)
                            task_key = f"{column}::{task}"
                            if task_key in imported_details:
                                self.task_details[task_key] = imported_details[task_key]
                        else:
                            duplicate_count += 1
                    else:
                        self.tasks[column].append(task)
                        task_key = f"{column}::{task}"
                        if task_key in imported_details:
                            self.task_details[task_key] = imported_details[task_key]
            
            self.save_tasks()
            self.refresh_all_columns()
            
            actual_imported = imported_count - duplicate_count
            message = f"Successfully imported {actual_imported} tasks!"
            
            if duplicate_count > 0:
                message += f"\n{duplicate_count} duplicate(s) were skipped."
            if skipped_count > 0:
                message += f"\n{skipped_count} invalid entries were skipped."
            
            messagebox.showinfo("Success", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV:\n{str(e)}")

def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
