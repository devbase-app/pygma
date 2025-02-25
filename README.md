pygma is a Python tool that converts your Figma designs into functional Tkinter GUIs—automatically. With a simple GUI built using Tkinter, pygma fetches your Figma design data via the Figma API, extracts frames and components, and then generates a basic, ready-to-run Tkinter UI. It's perfect for rapid prototyping and bridging the gap between design and development.

Features
Figma Integration:
Use your Figma API token and File ID to fetch your design data directly.

Automatic Frame Extraction:
Quickly extract frames and components from your Figma design for easy selection.

Tkinter UI Generation:
Automatically generate a basic Tkinter user interface based on your selected design frames.

Code Export:
Export the generated Python code for further customization or integration into your project.

User-Friendly GUI:
Enjoy an intuitive Tkinter-based interface that guides you through the process.

Getting Started
These instructions will help you set up and run pygma on your local machine.

Prerequisites
Python 3.x
Tkinter (usually included with Python)
Requests Library: Install via pip if not already installed:

```
pip install requests
```

Installation
Clone the Repository:

```
git clone https://github.com/devbase-app/pygma.git
cd pygma
```

Install Dependencies:

If you have a requirements.txt, install dependencies with:

```
pip install -r requirements.txt
```
(If not, ensure the requests library is installed.)


Run the application with:

```
python pygma.py
```

Enter Your Figma Credentials:

Figma API Token: Obtain this from your Figma account settings.
Figma File ID: Extract this from your Figma file's URL.
Fetch Design:

Click the "Fetch Design" button to retrieve your Figma design data.

Select Frames:
The tool will display detected frames. Use the checkboxes to select the frames you want to include in your UI.

Generate UI:
Click "Generate UI" to create a preview of your Tkinter interface.

Export Code:
Once satisfied, use "Export Code" to save the auto-generated Python script. You can further customize this code to suit your project's needs.

Contributing
We welcome contributions to pygma! If you'd like to help improve the tool:

Fork the repository.
Create a feature branch.
Commit your changes.
Open a pull request.
For major changes, please open an issue first to discuss what you'd like to change.

License
This project is licensed under the MIT License. See the LICENSE file for details.
