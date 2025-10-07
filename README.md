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

git clone https://github.com/shivakasula48/ClipLogger.git

cd ClipboardManager

Install dependencies
pip install -r requirements.txt

Run the application

`python clipboard.py

`
### Option 2: Build Executable
Install PyInstaller
`pip install pyinstaller
`
Build standalone executable

`pyinstaller --onefile --windowed --name "ClipboardManager" clipboard.py
`

Executable will be in dist/ folder


## 💻 Usage

### GUI Mode (Default)
Run the application to open the graphical interface:
python clipboard.py



**Interface Overview:**
- **Monitoring Toggle**: Start/stop automatic clipboard monitoring
- **Save Current**: Manually save current clipboard content
- **Settings**: Configure retention, filters, and preferences
- **History View**: Browse, restore, and delete saved items
- **Context Menu**: Right-click items for restore/delete options

### CLI Mode
For automation and scripting:
`python clipboard.py --cli
`


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

```bash
ClipboardManager/
├── clipboard.py # Main application file
├── requirements.txt # Python dependencies
├── README.md # Project documentation
├── LICENSE # License information
├── .gitignore # Git ignore rules

└── ClipboardHistory/ # Auto-created on first run
├── clipboard_history.db # SQLite database storing clipboard entries
├── settings.json # User configuration and preferences
├── clipboard_manager.log # Application log file

├── text/                  # Saved text entries (organized by date)  
├── images/                # Saved image entries (organized by date)  
├── files/                 # Saved file paths (organized by date)  
├── urls/                  # Saved URLs (organized by date)  
└── rich_text/             # Saved HTML/RTF entries (organized by date)  


```


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



## 🎯 Future Enhancements

- [ ] Cross-platform support (macOS, Linux)
- [ ] Cloud sync capabilities
- [ ] Advanced search and filtering
- [ ] Plugin system for custom handlers
- [ ] Encryption for sensitive content
- [ ] Import/export functionality
- [ ] Keyboard shortcuts
- [ ] System tray integration



## ⭐ Acknowledgments

- Built with Python and modern Windows APIs
- Uses efficient clipboard monitoring techniques
- Inspired by productivity tools like Ditto and ClipClip

---
