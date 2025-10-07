# Advanced Clipboard Manager

A powerful, feature-rich clipboard manager for Windows that automatically saves and organizes your clipboard history with advanced features like sensitive content detection, deduplication, and automatic cleanup.

## 🚀 Features

### Core Functionality
- **Multi-format Support**: Text, Rich Text (HTML/RTF), Images, Files, and URLs
- **Automatic Monitoring**: Background clipboard monitoring with efficient sequence number tracking
- **Smart Organization**: Automatic categorization by content type and date
- **Duplicate Prevention**: Content hashing to avoid saving identical items
- **Database Storage**: SQLite database for fast searching and retrieval

### Security & Privacy
- **Sensitive Content Detection**: Automatically skips passwords, tokens, credit cards, and SSNs
- **Content Filtering**: Configurable minimum text length and maximum image size
- **Safe File Handling**: Secure temporary file operations and path sanitization

### User Experience
- **Professional GUI**: Clean Tkinter interface with context menus and settings
- **System Notifications**: Desktop notifications for saved items
- **History Management**: View, restore, and delete clipboard entries
- **Auto Cleanup**: Configurable retention policies by age and count

### Advanced Features
- **Thread-Safe Operations**: Proper database locking and exception handling
- **Comprehensive Logging**: Detailed logging with fallback for executables
- **CLI Mode**: Command-line interface for automation
- **Portable Executable**: Can be compiled to standalone .exe file

## 📋 Requirements

- **Operating System**: Windows 10/11 (Windows-only due to Win32 APIs)
- **Python**: 3.7+ (if running from source)
- **Dependencies**: Listed in `requirements.txt`

## 🛠️ Installation

### Option 1: Run from Source
Clone the repository
git clone https://github.com/yourusername/ClipboardManager.git
cd ClipboardManager

Install dependencies
pip install -r requirements.txt

Run the application
python clipboard.py

text

### Option 2: Build Executable
Install PyInstaller
pip install pyinstaller

Build standalone executable
pyinstaller --onefile --windowed --name "ClipboardManager" clipboard.py

Executable will be in dist/ folder
text

## 💻 Usage

### GUI Mode (Default)
Run the application to open the graphical interface:
python clipboard.py

text

**Interface Overview:**
- **Monitoring Toggle**: Start/stop automatic clipboard monitoring
- **Save Current**: Manually save current clipboard content
- **Settings**: Configure retention, filters, and preferences
- **History View**: Browse, restore, and delete saved items
- **Context Menu**: Right-click items for restore/delete options

### CLI Mode
For automation and scripting:
python clipboard.py --cli

text

### Settings Configuration
Access via the GUI Settings button to configure:
- **Min Text Length**: Minimum characters to save text
- **Max Image Size**: Maximum image size in MB
- **Retention Days**: Auto-delete items older than X days
- **Max Entries**: Maximum number of items to keep
- **Content Filters**: Enable/disable sensitive content detection
- **Notifications**: Toggle desktop notifications
- **Organization**: Enable date-based folder structure

## 📁 File Structure

ClipboardManager/
├── clipboard.py # Main application file
├── requirements.txt # Python dependencies
├── README.md # This file
├── LICENSE # License information
├── .gitignore # Git ignore rules
└── ClipboardHistory/ # Created on first run
├── clipboard_history.db # SQLite database
├── settings.json # User settings
├── clipboard_manager.log # Application logs
├── text/ # Text files by date
├── images/ # Image files by date
├── files/ # Other files by date
├── urls/ # URL files by date
└── rich_text/ # HTML/RTF files by date

text

## 🔧 Technical Details

### Architecture
- **ClipboardManager**: Core logic class handling clipboard operations
- **ClipboardGUI**: Tkinter-based user interface
- **Thread-Safe**: Database operations with proper locking
- **Event-Driven**: Efficient clipboard monitoring using Windows APIs

### Dependencies
- `pyperclip`: Cross-platform clipboard access
- `Pillow`: Image processing and clipboard image handling
- `pywin32`: Windows-specific clipboard and API access
- `plyer`: Cross-platform desktop notifications
- `tkinter`: GUI framework (included with Python)
- `sqlite3`: Database operations (included with Python)

### Supported Content Types
- **Text**: Plain text with UTF-8 encoding
- **Rich Text**: HTML and RTF formatted content
- **Images**: PNG format with size limits
- **Files**: Any file type copied from Windows Explorer
- **URLs**: Automatic URL detection and categorization

## 🛡️ Privacy & Security

- **Local Storage**: All data stored locally on your machine
- **No Network Access**: Application works completely offline
- **Sensitive Data Protection**: Automatic detection and filtering of passwords, tokens, etc.
- **Safe File Operations**: Proper temp file handling and cleanup

## 🐛 Troubleshooting

### Common Issues
1. **"Python not found"**: Install Python and add to PATH
2. **"Module not found"**: Run `pip install -r requirements.txt`
3. **"Access denied" during build**: Close any running instances
4. **Clipboard not detected**: Check Windows clipboard service

### Debug Mode
For troubleshooting, check the log file at:
ClipboardHistory/clipboard_manager.log

text

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Future Enhancements

- [ ] Cross-platform support (macOS, Linux)
- [ ] Cloud sync capabilities
- [ ] Advanced search and filtering
- [ ] Plugin system for custom handlers
- [ ] Encryption for sensitive content
- [ ] Import/export functionality
- [ ] Keyboard shortcuts
- [ ] System tray integration

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/ClipboardManager/issues) page
2. Create a new issue with detailed information
3. Include log files and system information

## ⭐ Acknowledgments

- Built with Python and modern Windows APIs
- Uses efficient clipboard monitoring techniques
- Inspired by productivity tools like Ditto and ClipClip

---

**Made with ❤️ for productivity enthusiasts**
4. .gitignore
text
# Byte-compiled / optimized / DLL files
__pycache__/
*.pyc
*.pyo

# Env files
.env

# PyInstaller artifacts
build/
dist/
*.spec

# User-local config
ClipboardHistory/
clipboard_manager.log

# OS junk
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Temporary files
*.tmp
*.log
5. LICENSE (MIT License)
text
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
