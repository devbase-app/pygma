# pygma

## Overview

pygma is a Python-based tool that converts Figma designs into functional Tkinter graphical user interfaces. It fetches frames from a Figma file, lets users select which frames to include, and generates a Python script that recreates the UI using Tkinter.

## Features

- Fetches Figma design data via API
- Detects frames, text, buttons, rectangles, and input fields
- Allows frame selection before generating UI
- Generates a Tkinter-based GUI preserving layout, positions, and sizes
- Exports generated UI code to a Python (.py) file

## Installation

1. Install Python (>=3.7) if not already installed.
2. Install required dependencies:

```sh
pip install requests tkinter
```

3. Clone or download this repository:

```sh
git clone https://github.com/devbase-app/pygma.git
cd pygma
```

## Usage

1. **Run the Application**

   Start pygma by running:

   ```sh
   python pygma.py
   ```

2. **Fetch Figma Design Data**

   Open Figma and copy your File ID (from the URL: https://www.figma.com/file/FILE_ID/...).

   Obtain your Figma API Token from Figma settings.

   Enter both in pygma and click Fetch Design.

3. **Select Frames**

   After fetching, a window will appear listing available frames. Select which frames to include, then click Confirm.

4. **Generate & Preview UI**

   Click Generate UI to render a Tkinter-based version of your design.

5. **Export Code**

   Once satisfied, click Export Code to save a .py file with the generated Tkinter UI.

## Naming Schema in Figma

To ensure that input fields and text are correctly identified, use the following naming conventions in Figma:

- **Input Fields**: Include the word "input" in the name (e.g., "username_input", "password_input").
- **Labels**: Include the word "label" in the name (e.g., "username_label", "password_label").

## Example Generated Code

Example of exported code for a simple Figma frame:

```python
import tkinter as tk

class GeneratedUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Generated UI")
        tk.Label(master, text="My Figma Text", font=("Arial", 12)).place(x=50, y=30, width=200, height=30)
        tk.Button(master, text="Click Me").place(x=50, y=70, width=100, height=30)

    def on_click_me_click(self):
        pass  # Add your click handler here

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratedUI(root)
    root.mainloop()
```

## Troubleshooting

- **No frames detected?** Ensure that your Figma file has properly named frames.
- **UI doesn't match Figma?** Some complex elements (e.g., images) are not yet supported.
- **API Error?** Verify that your Figma token and File ID are correct.

## Contributing

Pull requests are welcome! Feel free to submit issues and feature requests.

## License

This project is licensed under the MIT License.
