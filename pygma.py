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
        self.generated_elements = []  # For code generation

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
        """Generates Tkinter UI based on selected Figma frames,
           sizing the window to the design and adjusting widget positions accordingly."""
        if not self.selected_frames:
            messagebox.showerror("Error", "No frames selected.")
            return

        # Calculate the global bounding box for all selected frames
        global_min_x, global_min_y = float('inf'), float('inf')
        global_max_x, global_max_y = 0, 0
        
        for frame_name in self.selected_frames:
            frame = self.frames.get(frame_name)
            if frame:
                bb = frame.get("absoluteBoundingBox", {})
                x = int(bb.get("x", 0))
                y = int(bb.get("y", 0))
                w = int(bb.get("width", 100))
                h = int(bb.get("height", 50))
                global_min_x = min(global_min_x, x)
                global_min_y = min(global_min_y, y)
                global_max_x = max(global_max_x, x + w)
                global_max_y = max(global_max_y, y + h)
        
        canvas_width = global_max_x - global_min_x
        canvas_height = global_max_y - global_min_y

        ui_window = tk.Toplevel(self.master)
        ui_window.title("Generated Tkinter UI")
        ui_window.geometry(f"{canvas_width}x{canvas_height}")

        canvas = tk.Canvas(ui_window, width=canvas_width, height=canvas_height, bg="white")
        canvas.pack(fill="both", expand=True)

        self.generated_elements = []  # Reset before generation

        # Use the global minimum as the offset so the design aligns to (0,0)
        for frame_name in self.selected_frames:
            frame = self.frames.get(frame_name)
            if frame:
                self.create_widgets_from_nodes(frame, canvas, (global_min_x, global_min_y))
        
        self.generated_code = self.build_generated_code()
        self.export_button.config(state="normal")

    def create_widgets_from_nodes(self, node, parent, base_offset):
        """
        Creates UI elements from Figma nodes with coordinate adjustment.
        base_offset is a tuple (offset_x, offset_y) used to normalize coordinates.
        """
        abs_bb = node.get("absoluteBoundingBox", {})
        node_abs_x = int(abs_bb.get("x", 0))
        node_abs_y = int(abs_bb.get("y", 0))
        width = int(abs_bb.get("width", 100))
        height = int(abs_bb.get("height", 50))
        local_x = node_abs_x - base_offset[0]
        local_y = node_abs_y - base_offset[1]

        node_type = node.get("type", "")
        if node_type == "FRAME":
            # Create a container frame for the Figma frame
            bg_color = "white"  # Default background; adjust if design specifies otherwise
            frame_container = tk.Frame(parent, width=width, height=height, bg=bg_color,
                                       highlightbackground="black", highlightthickness=1)
            frame_container.place(x=local_x, y=local_y, width=width, height=height)
            self.generated_elements.append((node.get("name", "Frame"), "Frame", local_x, local_y, width, height))
            # For children, use this node's absolute position as the new base offset
            new_base_offset = (node_abs_x, node_abs_y)
            for child in node.get("children", []):
                self.create_widgets_from_nodes(child, frame_container, new_base_offset)
        # Check if the text node should be an input field (using a naming convention)    
        elif node_type == "TEXT":
            if "input" in node.get("name", "").lower():
                widget = tk.Entry(parent)
                widget.place(x=local_x, y=local_y, width=width, height=height)
                self.generated_elements.append((node.get("name", "Entry"), "Entry", local_x, local_y, width, height))
            else:
                text_content = node.get("characters", node.get("name", "Text"))
                widget = tk.Label(parent, text=text_content, font=("Arial", 12), bg="white")
                widget.place(x=local_x, y=local_y, width=width, height=height)
                self.generated_elements.append((node.get("name", "Label"), "Label", local_x, local_y, width, height))
        elif node_type == "RECTANGLE":
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
            # For any other node type, process its children using the same base offset
            for child in node.get("children", []):
                self.create_widgets_from_nodes(child, parent, base_offset)

    def build_generated_code(self):
        """Generates Python code representing the Tkinter UI based on generated elements."""
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
        """Exports the generated Tkinter code to a .py file."""
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
