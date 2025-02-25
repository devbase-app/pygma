import tkinter as tk
from tkinter import messagebox, filedialog
import requests

class pygma:
    def __init__(self, master):
        self.master = master
        self.master.title("pygma - Convert Figma Designs to Tkinter GUIs")
        
        # Input fields
        tk.Label(master, text="Figma API Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.token_entry = tk.Entry(master, width=50)
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(master, text="Figma File ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.file_id_entry = tk.Entry(master, width=50)
        self.file_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        self.fetch_button = tk.Button(master, text="Fetch Design", command=self.fetch_design)
        self.fetch_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.generate_button = tk.Button(master, text="Generate UI", command=self.generate_ui, state="disabled")
        self.generate_button.grid(row=3, column=0, pady=10)
        self.export_button = tk.Button(master, text="Export Code", command=self.export_code, state="disabled")
        self.export_button.grid(row=3, column=1, pady=10)
        
        # Internal storage
        self.design_data = None
        self.frames = {}
        self.frame_vars = {}
        self.generated_code = ""
        self.selected_frames = []
        self.generated_elements = []  # Reset for code generation

    def fetch_design(self):
        """Fetches design data from Figma API"""
        token = self.token_entry.get().strip()
        file_id = self.file_id_entry.get().strip()
        
        if not token or not file_id:
            messagebox.showerror("Input Error", "Please provide both the Figma API token and File ID.")
            return
        
        headers = {"X-Figma-Token": token}
        url = f"https://api.figma.com/v1/files/{file_id}"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                messagebox.showerror("API Error", f"Error fetching design data: {response.status_code}")
                return
            self.design_data = response.json()
            self.extract_frames()
            self.open_frame_selector()
            messagebox.showinfo("Success", "Design data fetched successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_frames(self):
        """Extracts frames from the design data"""
        self.frames = {}

        def traverse(node):
            if node.get("type") == "FRAME":
                self.frames[node.get("name", "Unnamed Frame")] = node
            for child in node.get("children", []):
                traverse(child)

        document = self.design_data.get("document", {})
        traverse(document)

    def open_frame_selector(self):
        """Opens a selection window for choosing frames"""
        if hasattr(self, 'frame_selector_window') and self.frame_selector_window:
            self.frame_selector_window.destroy()

        self.frame_selector_window = tk.Toplevel(self.master)
        self.frame_selector_window.title("Select Frames")

        tk.Label(self.frame_selector_window, text="Select Frames:", font=("Arial", 12)).pack(pady=10)

        self.frame_vars = {}
        for frame_name in self.frames:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.frame_selector_window, text=frame_name, variable=var)
            chk.pack(anchor="w", padx=10)
            self.frame_vars[frame_name] = var

        tk.Button(self.frame_selector_window, text="Confirm", command=self.confirm_frame_selection).pack(pady=10)

    def confirm_frame_selection(self):
        """Stores selected frames and enables UI generation"""
        self.selected_frames = [name for name, var in self.frame_vars.items() if var.get()]
        if not self.selected_frames:
            messagebox.showwarning("No Selection", "Please select at least one frame.")
            return

        self.generate_button.config(state="normal")
        self.frame_selector_window.destroy()

    def generate_ui(self):
        """Generates Tkinter UI based on selected Figma frames"""
        if not self.selected_frames:
            messagebox.showerror("Error", "No frames selected.")
            return
        
        ui_window = tk.Toplevel(self.master)
        ui_window.title("Generated Tkinter UI")

        # Create a canvas to hold the design
        canvas = tk.Canvas(ui_window, width=800, height=600, bg="white")
        canvas.pack(fill="both", expand=True)

        self.generated_elements = []  # Reset before generating

        # For each selected frame, create its container and children
        for frame_name in self.selected_frames:
            frame = self.frames.get(frame_name)
            if frame:
                self.create_widgets_from_nodes(frame, canvas, offset_x=0, offset_y=0)

        self.generated_code = self.build_generated_code()
        self.export_button.config(state="normal")

    def create_widgets_from_nodes(self, node, parent, offset_x=0, offset_y=0):
        """Creates UI elements from Figma nodes with coordinate adjustment"""
        abs_bb = node.get("absoluteBoundingBox", {})
        x = int(abs_bb.get("x", 0))
        y = int(abs_bb.get("y", 0))
        width = int(abs_bb.get("width", 100))
        height = int(abs_bb.get("height", 50))
        # Compute local coordinates relative to the parent's origin
        local_x = x - offset_x
        local_y = y - offset_y

        node_type = node.get("type", "")
        
        if node_type == "FRAME":
            # Create a container to represent the frame.
            # Use a light border to visually differentiate the frame.
            bg_color = "white"  # Adjust if Figma design provides a specific background
            frame_container = tk.Frame(parent, width=width, height=height, bg=bg_color, 
                                       highlightbackground="black", highlightthickness=1)
            frame_container.place(x=local_x, y=local_y, width=width, height=height)
            # Process children with this frame's top-left as the new offset.
            for child in node.get("children", []):
                self.create_widgets_from_nodes(child, frame_container, offset_x=x, offset_y=y)
        elif node_type == "TEXT":
            # Use the 'characters' property if available, otherwise fallback to name.
            text_content = node.get("characters", node.get("name", "Text"))
            widget = tk.Label(parent, text=text_content, font=("Arial", 12), bg="white")
            widget.place(x=local_x, y=local_y, width=width, height=height)
            self.generated_elements.append((node.get("name", "Label"), "Label", local_x, local_y, width, height))
        elif node_type == "RECTANGLE":
            # Represent rectangles as frames with a default gray background.
            widget = tk.Frame(parent, bg="gray")
            widget.place(x=local_x, y=local_y, width=width, height=height)
            self.generated_elements.append((node.get("name", "Rectangle"), "Frame", local_x, local_y, width, height))
        elif node_type == "BUTTON":
            widget = tk.Button(parent, text=node.get("name", "Button"))
            widget.place(x=local_x, y=local_y, width=width, height=height)
            self.generated_elements.append((node.get("name", "Button"), "Button", local_x, local_y, width, height))
        elif node_type == "INPUT":
            widget = tk.Entry(parent)
            widget.place(x=local_x, y=local_y, width=width, height=height)
            self.generated_elements.append((node.get("name", "Entry"), "Entry", local_x, local_y, width, height))
        else:
            # For any other type, just process its children.
            for child in node.get("children", []):
                self.create_widgets_from_nodes(child, parent, offset_x, offset_y)

    def build_generated_code(self):
        """Generates Python code representing the Tkinter UI"""
        code = '''import tkinter as tk\n\ndef create_ui():\n    root = tk.Tk()\n    root.title("Auto-generated UI")\n'''
        for name, widget_type, x, y, width, height in self.generated_elements:
            if widget_type == "Label":
                code += f'    tk.Label(root, text="{name}", font=("Arial", 12)).place(x={x}, y={y}, width={width}, height={height})\n'
            elif widget_type == "Frame":
                code += f'    tk.Frame(root, bg="gray").place(x={x}, y={y}, width={width}, height={height})\n'
            elif widget_type == "Button":
                code += f'    tk.Button(root, text="{name}").place(x={x}, y={y}, width={width}, height={height})\n'
            elif widget_type == "Entry":
                code += f'    tk.Entry(root).place(x={x}, y={y}, width={width}, height={height})\n'
        
        code += '\n    root.mainloop()\n\nif __name__ == "__main__":\n    create_ui()'
        return code

    def export_code(self):
        """Exports the generated Tkinter code to a .py file"""
        if not self.generated_code:
            messagebox.showerror("Export Error", "No generated code to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.generated_code)
            messagebox.showinfo("Export Successful", "Code saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = pygma(root)
    root.mainloop()
