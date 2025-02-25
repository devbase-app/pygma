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
        self.selected_nodes = []

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
            self.generate_button.config(state="normal")
            messagebox.showinfo("Success", "Design data fetched and frames extracted!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_frames(self):
        """Extracts frames and their child elements from the design"""
        self.frames = {}

        def traverse(node):
            if node.get("type") == "FRAME":
                self.frames[node.get("name", "Unnamed Frame")] = node
            for child in node.get("children", []):
                traverse(child)

        document = self.design_data.get("document", {})
        traverse(document)

    def generate_ui(self):
        """Generates a Tkinter UI based on selected Figma frames"""
        if not self.frames:
            messagebox.showerror("Error", "No frames detected.")
            return
        
        ui_window = tk.Toplevel(self.master)
        ui_window.title("Generated Tkinter UI")

        canvas = tk.Canvas(ui_window, width=800, height=600, bg="white")
        canvas.pack(fill="both", expand=True)

        self.selected_nodes = []

        for frame_name, frame in self.frames.items():
            self.create_widgets_from_nodes(frame, canvas)

        self.generated_code = self.build_generated_code()
        self.export_button.config(state="normal")

    def create_widgets_from_nodes(self, node, parent):
        """Creates UI elements from Figma nodes"""
        node_type = node.get("type", "")
        name = node.get("name", "Unnamed")
        x, y = int(node.get("absoluteBoundingBox", {}).get("x", 0)), int(node.get("absoluteBoundingBox", {}).get("y", 0))
        width, height = int(node.get("absoluteBoundingBox", {}).get("width", 100)), int(node.get("absoluteBoundingBox", {}).get("height", 50))

        if node_type == "TEXT":
            widget = tk.Label(parent, text=name, font=("Arial", 12), bg="white")
            widget.place(x=x, y=y, width=width, height=height)
            self.selected_nodes.append((name, "Label", x, y, width, height))

        elif node_type == "RECTANGLE":
            widget = tk.Canvas(parent, width=width, height=height, bg="gray")
            widget.place(x=x, y=y, width=width, height=height)
            self.selected_nodes.append((name, "Canvas", x, y, width, height))

        elif node_type == "BUTTON":
            widget = tk.Button(parent, text=name)
            widget.place(x=x, y=y, width=width, height=height)
            self.selected_nodes.append((name, "Button", x, y, width, height))

        elif node_type == "INPUT":
            widget = tk.Entry(parent)
            widget.place(x=x, y=y, width=width, height=height)
            self.selected_nodes.append((name, "Entry", x, y, width, height))

        for child in node.get("children", []):
            self.create_widgets_from_nodes(child, parent)

    def build_generated_code(self):
        """Builds Python code representing the generated Tkinter UI"""
        code = '''import tkinter as tk\n\ndef create_ui():\n    root = tk.Tk()\n    root.title("Auto-generated UI")\n'''
        for name, widget_type, x, y, width, height in self.selected_nodes:
            if widget_type == "Label":
                code += f'    tk.Label(root, text="{name}", font=("Arial", 12)).place(x={x}, y={y}, width={width}, height={height})\n'
            elif widget_type == "Canvas":
                code += f'    tk.Canvas(root, width={width}, height={height}, bg="gray").place(x={x}, y={y})\n'
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