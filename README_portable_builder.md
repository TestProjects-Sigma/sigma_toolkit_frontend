# 🚀 Sigma's Toolkit Launcher - Portable Builder

**Create a fully portable Python environment for your Sigma's Toolkit Launcher that runs anywhere on Windows without requiring Python installation!**

---

## 📋 Quick Start

### Prerequisites
- Windows 7 or later
- Internet connection (for initial build only)
- ~200MB free disk space

### Installation Steps

1. **Download the Builder**
   ```
   Save build_portable.bat to your Sigma Toolkit directory
   (Same folder containing main.py, README.md, etc.)
   ```

2. **Run the Builder**
   ```
   Double-click: build_portable.bat
   ```

3. **Wait for Completion**
   ```
   The script will automatically:
   ✅ Download Python 3.11.9 (embedded)
   ✅ Install pip and PyQt5
   ✅ Copy your toolkit files
   ✅ Create launcher scripts
   ✅ Test the installation
   ```

4. **Launch Your Portable Toolkit**
   ```
   Navigate to: SigmaToolkitPortable\
   Double-click: Launch_Sigma_Toolkit.bat
   ```

---

## 📁 What Gets Created

After running the builder, you'll have a complete `SigmaToolkitPortable` folder containing:

### 🎯 Main Files
| File | Purpose |
|------|---------|
| `Launch_Sigma_Toolkit.bat` | **Main launcher** - Start your toolkit |
| `Setup_Repair.bat` | **Fix dependencies** - Repair/update packages |
| `Install_App_Requirements.bat` | **Batch installer** - Install all app dependencies safely |
| `Python_Shell.bat` | **Python access** - Open Python command prompt |
| `README_PORTABLE.txt` | **Usage guide** - Complete instructions |

### 📂 Directories
```
SigmaToolkitPortable/
├── python/                    # Portable Python 3.11.9
├── apps/                      # Your Python applications
├── main.py                    # Toolkit launcher
├── README.md                  # Original documentation
└── [launcher files]           # Batch scripts
```

---

## 🎮 How to Use

### Starting the Toolkit
```batch
# Simply double-click:
Launch_Sigma_Toolkit.bat
```
- 🔇 **Silent operation** - No console warnings
- 🚀 **Instant launch** - No installation required
- 📦 **Self-contained** - Everything included

### Adding New Apps
1. Create a subfolder in `apps/`
2. Add your `main.py` file
3. Add `requirements.txt` (optional)
4. Add `readme.md` (optional)
5. Apps appear automatically in the launcher!

### Installing App Dependencies
```batch
# For all apps at once:
Install_App_Requirements.bat

# Features:
✅ Safe installation (no downgrades)
✅ Error tracking and reporting
✅ Skips apps without requirements
✅ Detailed summary
```

### Troubleshooting
```batch
# If something breaks:
Setup_Repair.bat

# For Python access:
Python_Shell.bat
```

---

## 💼 Portable Deployment

### Moving to USB/Other Locations
1. **Copy the entire `SigmaToolkitPortable` folder**
2. **Paste to new location** (USB drive, different PC, etc.)
3. **Run `Launch_Sigma_Toolkit.bat`** from new location
4. **Everything works exactly the same!**

### Distribution
- **Size**: ~150MB total
- **Requirements**: Windows 7+ only
- **Dependencies**: None (completely self-contained)
- **Installation**: Not required

---

## 🔧 Advanced Features

### Safe Dependency Management
The portable version includes smart package management:

```bash
# Traditional pip (risky):
pip install -r requirements.txt

# Our enhanced version (safe):
pip install -r requirements.txt --upgrade-strategy only-if-needed
```

**Benefits:**
- ✅ Never downgrades working packages
- ✅ Only upgrades when beneficial
- ✅ Prevents version conflicts
- ✅ Maintains app compatibility

### Warning Suppression
The launcher automatically suppresses PyQt5 deprecation warnings:
```batch
python.exe -W ignore::DeprecationWarning main.py 2>nul
```

### Multi-App Support
- Each app in its own subfolder
- Independent requirements
- Automatic discovery
- Safe batch installation

---

## 📊 Builder Process Details

### What the Builder Downloads
```
Python 3.11.9 Embedded    (~25MB)
├── Core Python runtime
├── Standard library
└── pip installer

PyQt5 Dependencies        (~50MB)
├── PyQt5==5.15.9
├── Required SIP modules
└── Qt5 libraries

Total Download: ~75MB
Final Size: ~150MB
```

### Directory Structure Created
```
SigmaToolkitPortable/
├── python/                    # Python installation
│   ├── python.exe            # Python interpreter
│   ├── Scripts/              # pip and tools
│   ├── Lib/                  # Standard library
│   └── site-packages/        # Installed packages
├── apps/                     # Your applications
├── main.py                   # Toolkit source
├── requirements.txt          # Dependencies list
├── README.md                 # Original docs
├── launcher_settings.json    # Settings (if exists)
└── *.bat                     # Launcher scripts
```

---

## 🛠️ Customization

### Modifying the Builder
Edit `build_portable.bat` to customize:

```batch
# Change Python version:
set "PYTHON_VERSION=3.11.9"

# Change download URLs:
set "PYTHON_URL=https://www.python.org/ftp/python/..."

# Modify directory names:
set "TOOLKIT_DIR=%~dp0MyCustomName"
```

### Adding Extra Packages
Modify the builder to include additional packages:
```batch
echo Installing additional packages...
"%PYTHON_DIR%\python.exe" -m pip install requests beautifulsoup4
```

---

## ❓ Troubleshooting

### Common Issues

**Q: "Python not found" error**
```
A: Run Setup_Repair.bat to reinstall dependencies
```

**Q: App won't launch**
```
A: 1. Check if main.py exists in app folder
   2. Run Install_App_Requirements.bat
   3. Check Python_Shell.bat for detailed errors
```

**Q: PyQt5 warnings still showing**
```
A: Rebuild with latest builder script (warnings are now suppressed)
```

**Q: Package conflicts**
```
A: Use Install_App_Requirements.bat (never downgrades)
   Manual fix: Setup_Repair.bat
```

### Error Codes
| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Python download failed |
| 2 | PyQt5 installation failed |
| 3 | File copy error |

---

## 🎯 Best Practices

### For App Developers
1. **Always include requirements.txt** for dependencies
2. **Use relative paths** in your applications
3. **Test with portable Python** before distribution
4. **Include readme.md** for documentation

### For Distribution
1. **Test on clean Windows VM** before sharing
2. **Include README_PORTABLE.txt** for users
3. **Compress for sharing** (reduces to ~50MB zip)
4. **Document system requirements** clearly

### For Maintenance
1. **Rebuild monthly** for security updates
2. **Keep original source** separate from portable
3. **Backup settings** before rebuilding
4. **Test all apps** after updates

---

## 📈 Version History

### Latest Features
- ✅ **Safe dependency management** - No more version conflicts
- ✅ **Warning suppression** - Clean console output
- ✅ **Enhanced error reporting** - Better troubleshooting
- ✅ **Automatic testing** - Validates installation
- ✅ **Smart batch installation** - Process all app requirements

### Future Enhancements
- 🔮 **Auto-updater** for the portable environment
- 🔮 **Theme customization** in portable version
- 🔮 **App marketplace** integration
- 🔮 **Executable packaging** option

---

## 📄 License & Credits

This portable builder is designed for personal and educational use. The Sigma's Toolkit Launcher and this portable builder are provided as-is for creating self-contained Python environments.

**Components:**
- Python 3.11.9 (Python Software Foundation)
- PyQt5 (Riverbank Computing)
- Sigma's Toolkit Launcher (Original project)

---

## 🤝 Contributing

Found an issue or want to improve the builder? Here are key areas for enhancement:

- **Cross-platform support** (Linux/macOS versions)
- **Additional package presets** for common use cases
- **GUI builder interface** instead of batch script
- **Automatic dependency resolution** improvements
- **Size optimization** techniques

---

**🚀 Happy coding with your portable Sigma's Toolkit Launcher!**

*Build once, run anywhere, distribute easily.*