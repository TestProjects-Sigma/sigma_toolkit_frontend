# 🔧 Sigma's Toolkit Launcher

A dynamic, modern frontend for managing and launching your standalone Python applications with ease.

## ✨ Features

- **🔍 Auto-Discovery**: Automatically finds and displays Python apps in subfolders
- **🚀 One-Click Launch**: Launch any app with a single click
- **📦 Smart Dependencies**: Automatically installs requirements when needed
- **📖 Built-in Documentation**: View README files with right-click context menu
- **⚙️ Customizable Interface**: Adjust grid layout, button sizes, and app names
- **🎨 Modern UI**: Clean, professional interface with smooth animations
- **📁 Folder Integration**: Open app folders directly from the launcher
- **💾 Settings Persistence**: Your preferences are automatically saved

## 🚀 Quick Start

### Installation

1. **Install dependencies:**
   ```bash
   pip install PyQt5
   ```

2. **Run the launcher:**
   ```bash
   python main.py
   ```

3. **The launcher automatically creates an `apps` folder** where you can add your applications.

### Adding Your First App

1. **Create a subfolder** in the `apps` directory:
   ```bash
   mkdir apps/my_awesome_tool
   ```

2. **Add your application files:**
   ```
   apps/my_awesome_tool/
   ├── main.py              # Required: Entry point
   ├── requirements.txt     # Optional: Dependencies
   └── readme.md           # Optional: Documentation
   ```

3. **Your app appears instantly** in the launcher!

## 📁 App Structure

Each app in the `apps` folder should follow this structure:

```
apps/
├── calculator/
│   ├── main.py              # ✅ Required: Main entry point
│   ├── requirements.txt     # 📦 Optional: pip dependencies  
│   ├── readme.md           # 📖 Optional: Documentation
│   └── [other files...]    # Any additional files your app needs
├── data_analyzer/
│   ├── main.py
│   ├── requirements.txt
│   └── readme.md
└── image_processor/
    ├── main.py
    └── readme.md
```

### File Descriptions

- **`main.py`** - The entry point for your application. This file will be executed when the app is launched.
- **`requirements.txt`** - Standard pip requirements file. Dependencies are automatically installed when the app is launched.
- **`readme.md`** - Documentation for your app. Viewable through the right-click context menu.

## 🎮 Using the Launcher

### Basic Operations

- **🖱️ Left Click**: Launch an application
- **🖱️ Right Click**: Open context menu with options:
  - 📖 **View README**: Display the app's documentation
  - 📁 **Open Folder**: Open the app's folder in file explorer

### Interface Elements

- **🔧 App Icons**: 
  - 🚀 Ready to run (no dependencies)
  - 📱 Has dependencies (requirements.txt)
- **📖 Documentation Indicator**: Shows when README.md is available
- **⚙️ Settings Button**: Customize the interface
- **🔄 Refresh Button**: Manually refresh the app list

### Customization

Click the **⚙️ Settings** button to customize:

- **Grid Columns** (1-6): Control how many columns of apps to display
- **Button Size** (Small/Medium/Large): Adjust app button sizes
- **Custom Names**: Give your apps friendly display names
  - Example: `ad_password_checker` → `Password Checker`

## 🔧 Advanced Features

### Custom App Names

Transform technical folder names into user-friendly displays:
- `data_analysis_tool` → `Data Analysis Tool`
- `sql_query_builder` → `SQL Query Builder`
- `file_organizer_v2` → `File Organizer V2`

### Smart Dependency Management

- Dependencies are installed automatically when an app is launched
- Only installs when `requirements.txt` is present
- Uses your current Python environment
- Visual indicators show which apps have dependencies

### File System Monitoring

- Automatically detects when new apps are added
- Updates the interface in real-time
- Manual refresh option available if needed

## 📋 Example App Creation

Let's create a simple calculator app:

1. **Create the folder:**
   ```bash
   mkdir apps/calculator
   ```

2. **Create main.py:**
   ```python
   # apps/calculator/main.py
   import tkinter as tk
   from tkinter import ttk
   
   class Calculator:
       def __init__(self):
           self.root = tk.Tk()
           self.root.title("Simple Calculator")
           # Add your calculator logic here...
           
   if __name__ == "__main__":
       Calculator()
   ```

3. **Create requirements.txt (if needed):**
   ```
   # apps/calculator/requirements.txt
   # No external dependencies needed for this example
   ```

4. **Create readme.md:**
   ```markdown
   # Simple Calculator
   
   A basic calculator application built with Tkinter.
   
   ## Features
   - Basic arithmetic operations
   - User-friendly interface
   
   ## Usage
   Launch from Sigma's Toolkit Launcher!
   ```

5. **Launch!** Your calculator now appears in the launcher.

## 🎯 Development Workflow

Perfect for developers managing multiple tools:

1. **Develop** your Python application in its own folder
2. **Copy** the folder to `apps/` when ready
3. **Launch** instantly from the toolkit
4. **Update** by replacing files - changes detected automatically
5. **Document** with README.md for easy reference

## ⚙️ Settings File

Settings are automatically saved to `launcher_settings.json`:

```json
{
  "grid_columns": 3,
  "button_size": "Medium", 
  "custom_names": {
    "data_analyzer": "Data Analyzer Pro",
    "password_tool": "Security Suite"
  }
}
```

## 🔮 Planned Features

- 🔄 **Smart Updates**: Only reinstall changed dependencies
- 📍 **External Paths**: Add apps from other locations
- 🎨 **Themes**: Dark mode and custom color schemes
- 📊 **Usage Stats**: Track your most-used applications
- 📦 **EXE Packaging**: Distribute as standalone executable
- 🔐 **App Permissions**: Control which apps can run
- 📝 **Logging**: Detailed logs for troubleshooting

## 🛠️ Troubleshooting

### Apps Won't Launch
- Ensure `main.py` exists in the app folder
- Check that your Python environment has required permissions
- View error messages in the status bar

### Requirements Installation Fails
- Verify `requirements.txt` format is correct
- Check internet connection for package downloads
- Ensure pip is available in your environment

### Apps Not Appearing
- Check folder structure matches expected format
- Use the 🔄 Refresh button
- Verify the `apps` folder exists and has proper permissions

## 📄 License

This project is designed for personal and educational use. Feel free to modify and extend for your own toolkit needs!

## 🤝 Contributing

Found a bug or have a feature idea? This launcher is designed to be easily extensible. Key areas for enhancement:

- Additional file format support
- More customization options  
- Integration with development tools
- Enhanced error handling

---

**🔧 Sigma's Toolkit Launcher** - Making Python application management simple and elegant.
