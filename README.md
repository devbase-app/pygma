Overview:


pygma is a Python-based tool that converts Figma designs into functional Tkinter graphical user interfaces. It fetches frames from a Figma file, lets users select which frames to include, and generates a Python script that recreates the UI using Tkinter.


Features:

✅ Fetches Figma design data via API

✅ Detects frames, text, buttons, rectangles, and input fields

✅ Allows frame selection before generating UI

✅ Generates a Tkinter-based GUI preserving layout, positions, and sizes

✅ Exports generated UI code to a Python (.py) file


Installation:

Install Python (>=3.7) if not already installed.

Install required dependencies:

```
pip install requests tkinter
```

Clone or download this repository:

```
git clone https://github.com/devbase-app/pygma.git
cd pygma
```

Usage:

1️⃣ Run the Application

Start pygma by running:

```
python pygma.py
```

2️⃣ Fetch Figma Design Data

Open Figma and copy your File ID (from the URL: https://www.figma.com/file/FILE_ID/...).

Obtain your Figma API Token from Figma settings.

Enter both in pygma and click Fetch Design.

3️⃣ Select Frames

After fetching, a window will appear listing available frames. Select which frames to include, then click Confirm.

4️⃣ Generate & Preview UI

Click Generate UI to render a Tkinter-based version of your design.

5️⃣ Export Code

Once satisfied, click Export Code to save a .py file with the generated Tkinter UI.

Example Generated Code

Example of exported code for a simple Figma frame:

```
import tkinter as tk

def create_ui():
    root = tk.Tk()
    root.title("Auto-generated UI")
    tk.Label(root, text="My Figma Text", font=("Arial", 12)).place(x=50, y=30, width=200, height=30)
    tk.Button(root, text="Click Me").place(x=50, y=70, width=100, height=30)
    root.mainloop()

if __name__ == "__main__":
    create_ui()
```

Troubleshooting

No frames detected? Ensure that your Figma file has properly named frames.

UI doesn't match Figma? Some complex elements (e.g., images) are not yet supported.

API Error? Verify that your Figma token and File ID are correct.

Contributing

Pull requests are welcome! Feel free to submit issues and feature requests.

License

This project is licensed under the MIT License.
