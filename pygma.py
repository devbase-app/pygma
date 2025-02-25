import tkinter as tk
from tkinter import messagebox, filedialog
import requests

class pygma:
    def __init__(self, master):
        self.master = master
        self.master.title("pygma - Convert Figma Designs to Tkinter GUIs")
        
        # Input fields for Figma API token and File ID
        tk.Label(master, text="Figma API Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.token_entry = tk.Entry(master, width=50)
        self.token_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(master, text="Figma File ID:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.file_id_entry = tk.Entry(master, width=50)
        self.file_id_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Button to fetch design data
        self.fetch_button = tk.Button(master, text="Fetch Design", command=self.fetch_design)
        self.fetch_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Buttons for generating UI and exporting code
        self.generate_button = tk.Button(master, text="Generate UI", command=self.generate_ui, state="disabled")
        self.generate_button.grid(row=3, column=0, pady=10)
        self.export_button = tk.Button(master, text="Export Code", command=self.export_code, state="disabled")
        self.export_button.grid(row=3, column=1, pady=10)
        
        # Internal storage for design data and frame selection
        self.design_data = None
        self.frames = {}
        self.frame_vars = {}
        self.generated_code = ""
        self.frame_selector_window = None
    
    def fetch_design(self):
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
            
            if self.frames:
                self.open_frame_selector()
                self.generate_button.config(state="normal")
                messagebox.showinfo("Success", "Design data fetched and frames extracted!")
            else:
                messagebox.showwarning("No Frames Found", "No frames were detected in the Figma file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")  
    
    def extract_frames(self):
        self.frames = {}
        
        def traverse(node):
            if node.get("type") == "FRAME":
                name = node.get("name", "Unnamed Frame")
                self.frames[name] = node
            for child in node.get("children", []):
                traverse(child)
        
        document = self.design_data.get("document", {}).get("children", [])
        for child in document:
            traverse(child)
        print("Extracted frames:", list(self.frames.keys()))
    
    def open_frame_selector(self):
        if self.frame_selector_window:
            self.frame_selector_window.destroy()
        
        self.frame_selector_window = tk.Toplevel(self.master)
        self.frame_selector_window.title("Select Frames")
        
        tk.Label(self.frame_selector_window, text="Select Frames to include in your UI:", font=("Arial", 12)).pack(padx=10, pady=10)
        
        self.frame_vars = {}
        for frame_name in self.frames:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.frame_selector_window, text=frame_name, variable=var)
            chk.pack(anchor="w", padx=10)
            self.frame_vars[frame_name] = var
    
    def generate_ui(self):
        selected_frames = [name for name, var in self.frame_vars.items() if var.get()]
        if not selected_frames:
            messagebox.showwarning("No Selection", "Please select at least one frame to generate the UI.")
            return
        
        ui_window = tk.Toplevel(self.master)
        ui_window.title("Generated Tkinter UI")
        
        for frame_name in selected_frames:
            frame = tk.Frame(ui_window, borderwidth=2, relief="groove", padx=10, pady=10)
            frame.pack(fill="both", expand=True, padx=10, pady=5)
            label = tk.Label(frame, text=frame_name, font=("Arial", 16))
            label.pack()
        
        self.generated_code = self.build_generated_code(selected_frames)
        messagebox.showinfo("UI Generated", "UI generated successfully! You can now export the code.")
        self.export_button.config(state="normal")
    
    def build_generated_code(self, selected_frames):
        code = '''import tkinter as tk

def create_ui():
    root = tk.Tk()
    root.title("Auto-generated UI from Figma")
'''
        for frame_name in selected_frames:
            var_name = frame_name.replace(" ", "_").lower()
            code += f'''
    frame_{var_name} = tk.Frame(root, borderwidth=2, relief="groove", padx=10, pady=10)
    frame_{var_name}.pack(fill="both", expand=True, padx=10, pady=5)
    label_{var_name} = tk.Label(frame_{var_name}, text="{frame_name}", font=("Arial", 16))
    label_{var_name}.pack()
'''
        code += '''
    root.mainloop()

if __name__ == "__main__":
    create_ui()
'''
        return code
    
    def export_code(self):
        if not self.generated_code:
            messagebox.showerror("Export Error", "No generated code to export.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.generated_code)
                messagebox.showinfo("Export Successful", f"Generated code saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred while saving: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = pygma(root)
    root.mainloop()