import os
import sys
import pyperclip
from PIL import ImageGrab
import win32clipboard
import win32con
from datetime import datetime, timedelta
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import json
import re
import hashlib
import tempfile
import shutil
import logging
from urllib.parse import urlparse
from plyer import notification
import platform
import ctypes

class ClipboardManager:
    def __init__(self):
        self.base_folder = "ClipboardHistory"
        self.db_path = os.path.join(self.base_folder, "clipboard_history.db")
        self.settings_path = os.path.join(self.base_folder, "settings.json")
        self.log_path = os.path.join(self.base_folder, "clipboard_manager.log")
        
        # Thread management
        self.monitoring = False
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self.last_content = ""
        self.last_clipboard_sequence = 0
        
        # Database lock for thread safety
        self.db_lock = threading.Lock()
        
        # Sensitive keywords to detect and skip
        self.sensitive_keywords = [
            'password', 'pwd', 'pass:', 'secret', 'ssn', 'card', 'token', 
            'api_key', 'auth', 'login', 'credential', '2fa', 'otp'
        ]
        
        # Default settings
        self.settings = {
            "min_text_length": 3,
            "max_image_size": 10,  # MB
            "auto_monitor": True,
            "organize_by_date": True,
            "show_notifications": True,
            "skip_sensitive": True,
            "retention_days": 30,
            "max_entries": 1000
        }
        
        self.init_logging()
        self.init_folders()
        self.init_database()
        self.load_settings()
        self.cleanup_old_entries()

    def init_logging(self):
        """Initialize logging with fallback for executable"""
        try:
            # Ensure the base folder exists for logging
            os.makedirs(self.base_folder, exist_ok=True)
            
            logging.basicConfig(
                level=logging.INFO,
                filename=self.log_path,
                filemode='a',
                format='%(asctime)s %(levelname)s: %(message)s'
            )
            self.logger = logging.getLogger(__name__)
        except Exception:
            # Fallback to console logging if file logging fails
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s: %(message)s',
                stream=sys.stdout
            )
            self.logger = logging.getLogger(__name__)

    def init_folders(self):
        """Create necessary folders"""
        folders = [
            self.base_folder,
            os.path.join(self.base_folder, "text"),
            os.path.join(self.base_folder, "images"),
            os.path.join(self.base_folder, "files"),
            os.path.join(self.base_folder, "urls"),
            os.path.join(self.base_folder, "rich_text")
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

    def init_database(self):
        """Initialize SQLite database for clipboard history"""
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clipboard_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        content_type TEXT,
                        content_preview TEXT,
                        file_path TEXT,
                        size INTEGER,
                        content_hash TEXT
                    )
                ''')
                conn.commit()
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Database initialization failed: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()

    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Failed to load settings: {e}")

    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Failed to save settings: {e}")

    def get_timestamp(self):
        """Get current timestamp for filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def get_date_folder(self):
        """Get date-based folder path"""
        if self.settings["organize_by_date"]:
            return datetime.now().strftime("%Y-%m-%d")
        return ""

    def show_notification(self, title, message):
        """Show system notification"""
        if self.settings["show_notifications"]:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Clipboard Manager",
                    timeout=3
                )
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Notification failed: {e}")

    def is_url(self, text):
        """Check if text is a URL"""
        try:
            result = urlparse(text.strip())
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def looks_sensitive(self, text):
        """Check if text contains sensitive information"""
        if not self.settings["skip_sensitive"]:
            return False
        
        text_lower = text.lower()
        
        # Check for sensitive keywords
        if any(keyword in text_lower for keyword in self.sensitive_keywords):
            return True
        
        # Check for credit card pattern
        if re.search(r'\b(?:\d{4}[- ]?){3}\d{4}\b', text):
            return True
        
        # Check for social security number pattern
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
            return True
        
        return False

    def get_safe_filename(self, text, max_length=50):
        """Generate safe filename from text"""
        safe_text = text.strip().splitlines()[0] if text else "clip"
        safe_text = re.sub(r'[^a-zA-Z0-9-_]', '_', safe_text)
        return safe_text[:max_length] if len(safe_text) > max_length else safe_text

    def get_content_hash(self, content):
        """Generate hash for content deduplication"""
        if isinstance(content, str):
            return hashlib.md5(content.encode('utf-8')).hexdigest()
        elif isinstance(content, bytes):
            return hashlib.md5(content).hexdigest()
        return None

    def is_duplicate(self, content_hash):
        """Check if content already exists"""
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM clipboard_history WHERE content_hash = ? LIMIT 1', (content_hash,))
                result = cursor.fetchone()
                return result is not None
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Duplicate check failed: {e}")
                return False
            finally:
                if 'conn' in locals():
                    conn.close()

    def save_to_database(self, content_type, content_preview, file_path, size=0, content_hash=None):
        """Save clipboard entry to database"""
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO clipboard_history (timestamp, content_type, content_preview, file_path, size, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now().isoformat(), content_type, content_preview, file_path, size, content_hash))
                conn.commit()
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Database save failed: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()

    def save_text_to_file(self):
        """Save text content with URL detection and rich text support"""
        try:
            txt = pyperclip.paste()
            if not txt or len(txt.strip()) < self.settings["min_text_length"]:
                return False

            # Skip sensitive content
            if self.looks_sensitive(txt):
                if hasattr(self, 'logger'):
                    self.logger.info("Skipped sensitive content")
                return False

            # Check for duplicates
            content_hash = self.get_content_hash(txt)
            if self.is_duplicate(content_hash):
                return False

            date_folder = self.get_date_folder()
            
            # Check if it's a URL
            if self.is_url(txt):
                folder = os.path.join(self.base_folder, "urls", date_folder)
                os.makedirs(folder, exist_ok=True)
                filename = f"url_{self.get_timestamp()}.txt"
                content_type = "URL"
            else:
                folder = os.path.join(self.base_folder, "text", date_folder)
                os.makedirs(folder, exist_ok=True)
                safe_preview = self.get_safe_filename(txt)
                filename = f"text_{self.get_timestamp()}_{safe_preview}.txt"
                content_type = "Text"

            file_path = os.path.join(folder, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(txt)
            
            preview = txt[:100] + "..." if len(txt) > 100 else txt
            self.save_to_database(content_type, preview, file_path, len(txt.encode('utf-8')), content_hash)
            self.show_notification("Clipboard Manager", f"{content_type} saved: {filename}")
            
            return True
        
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Text save failed: {e}")
            return False

    def save_rich_text_to_file(self):
        """Save rich text (HTML/RTF) content"""
        try:
            win32clipboard.OpenClipboard()
            
            try:
                html_data = win32clipboard.GetClipboardData(win32con.CF_HTML)
                if html_data:
                    # Check for duplicates
                    content_hash = self.get_content_hash(html_data)
                    if self.is_duplicate(content_hash):
                        return False

                    date_folder = self.get_date_folder()
                    folder = os.path.join(self.base_folder, "rich_text", date_folder)
                    os.makedirs(folder, exist_ok=True)
                    
                    filename = f"rich_text_{self.get_timestamp()}.html"
                    file_path = os.path.join(folder, filename)
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(html_data)
                    
                    preview = html_data[:100] + "..." if len(html_data) > 100 else html_data
                    self.save_to_database("Rich Text", preview, file_path, len(html_data.encode('utf-8')), content_hash)
                    self.show_notification("Clipboard Manager", f"Rich text saved: {filename}")
                    return True
            except (TypeError, OSError) as e:
                if hasattr(self, 'logger'):
                    self.logger.debug(f"Rich text not available: {e}")
                
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Rich text save failed: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
        return False

    def save_image_to_file(self):
        """Save image content with size filtering"""
        try:
            image = ImageGrab.grabclipboard()
            if image is None:
                return False

            date_folder = self.get_date_folder()
            
            # Direct image data
            if hasattr(image, 'save'):
                # Use temporary file safely
                fd, temp_path = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                
                try:
                    image.save(temp_path)
                    size_mb = os.path.getsize(temp_path) / (1024 * 1024)
                    
                    if size_mb > self.settings["max_image_size"]:
                        return False
                    
                    # Check for duplicates
                    with open(temp_path, 'rb') as f:
                        content_hash = self.get_content_hash(f.read())
                    if self.is_duplicate(content_hash):
                        return False
                    
                    folder = os.path.join(self.base_folder, "images", date_folder)
                    os.makedirs(folder, exist_ok=True)
                    
                    filename = f"image_{self.get_timestamp()}.png"
                    file_path = os.path.join(folder, filename)
                    
                    shutil.move(temp_path, file_path)
                    
                    self.save_to_database("Image", f"Image {image.size}", file_path, os.path.getsize(file_path), content_hash)
                    self.show_notification("Clipboard Manager", f"Image saved: {filename}")
                    return True
                    
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            # List of files
            if isinstance(image, list):
                for path in image:
                    if os.path.isfile(path):
                        return self.save_copied_file(path)
        
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Image save failed: {e}")
        
        return False

    def save_copied_file(self, source_path):
        """Save a file that was copied"""
        try:
            if not os.path.isfile(source_path):
                return False
            
            # Check for duplicates
            with open(source_path, 'rb') as f:
                content_hash = self.get_content_hash(f.read())
            if self.is_duplicate(content_hash):
                return False
                
            date_folder = self.get_date_folder()
            folder = os.path.join(self.base_folder, "files", date_folder)
            os.makedirs(folder, exist_ok=True)
            
            original_name = os.path.basename(source_path)
            filename = f"file_{self.get_timestamp()}_{original_name}"
            file_path = os.path.join(folder, filename)
            
            shutil.copy2(source_path, file_path)
            
            file_size = os.path.getsize(file_path)
            self.save_to_database("File", original_name, file_path, file_size, content_hash)
            self.show_notification("Clipboard Manager", f"File saved: {filename}")
            return True
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"File save failed: {e}")
            return False

    def save_file_from_clipboard(self):
        """Save files from clipboard using win32"""
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            file_list = data.split('\0')
            
            for file_path in file_list:
                file_path = file_path.strip()
                if file_path and os.path.isfile(file_path):
                    if self.save_copied_file(file_path):
                        return True
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"File from clipboard save failed: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
        return False

    def get_clipboard_sequence_number(self):
        """Get Windows clipboard sequence number for efficient monitoring"""
        try:
            return ctypes.windll.user32.GetClipboardSequenceNumber()
        except Exception:
            return 0

    def process_clipboard(self):
        """Process current clipboard content - prevents duplicate saves"""
        try:
            # Try different content types in priority order
            # Only one type will succeed per clipboard event
            if self.save_rich_text_to_file():
                return True
            elif self.save_text_to_file():
                return True
            elif self.save_image_to_file():
                return True
            elif self.save_file_from_clipboard():
                return True
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Clipboard processing failed: {e}")
        
        return False

    def start_monitoring(self):
        """Start clipboard monitoring in background thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self._monitor_thread.start()
        if hasattr(self, 'logger'):
            self.logger.info("Clipboard monitoring started")

    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        self._stop_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2)
        
        if hasattr(self, 'logger'):
            self.logger.info("Clipboard monitoring stopped")

    def _monitor_clipboard(self):
        """Background clipboard monitoring loop with sequence number optimization"""
        while not self._stop_event.is_set():
            try:
                current_sequence = self.get_clipboard_sequence_number()
                
                # Only process if clipboard actually changed
                if current_sequence != self.last_clipboard_sequence:
                    self.process_clipboard()
                    self.last_clipboard_sequence = current_sequence
                    
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Monitoring loop error: {e}")
            
            self._stop_event.wait(0.5)  # More efficient than time.sleep()

    def cleanup_old_entries(self):
        """Clean up old entries based on retention policy"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                
                # Delete by age
                cutoff_date = (datetime.now() - timedelta(days=self.settings["retention_days"])).isoformat()
                cursor.execute('SELECT file_path FROM clipboard_history WHERE timestamp < ?', (cutoff_date,))
                old_files = cursor.fetchall()
                
                # Remove files
                for (file_path,) in old_files:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        if hasattr(self, 'logger'):
                            self.logger.error(f"Failed to remove old file {file_path}: {e}")
                
                # Delete from database
                cursor.execute('DELETE FROM clipboard_history WHERE timestamp < ?', (cutoff_date,))
                
                # Limit total entries
                cursor.execute('''
                    DELETE FROM clipboard_history WHERE id NOT IN (
                        SELECT id FROM clipboard_history ORDER BY timestamp DESC LIMIT ?
                    )
                ''', (self.settings["max_entries"],))
                
                conn.commit()
                deleted_count = cursor.rowcount
                if deleted_count > 0 and hasattr(self, 'logger'):
                    self.logger.info(f"Cleaned up {deleted_count} old entries")
                    
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Cleanup failed: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_history(self, limit=50):
        """Get clipboard history from database"""
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM clipboard_history 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                results = cursor.fetchall()
                return results
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"History retrieval failed: {e}")
                return []
            finally:
                if 'conn' in locals():
                    conn.close()

    def restore_clipboard(self, file_path):
        """Restore content to clipboard"""
        try:
            if file_path.endswith(('.txt', '.html')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                pyperclip.copy(content)
                return True
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Clipboard restore failed: {e}")
        return False

    def delete_entry(self, entry_id, file_path):
        """Delete a clipboard entry"""
        with self.db_lock:
            try:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM clipboard_history WHERE id = ?', (entry_id,))
                conn.commit()
                
                # Remove file
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                return True
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.logger.error(f"Entry deletion failed: {e}")
                return False
            finally:
                if 'conn' in locals():
                    conn.close()

class ClipboardGUI:
    def __init__(self, manager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title("Advanced Clipboard Manager")
        self.root.geometry("900x700")
        
        self.create_widgets()
        self.refresh_history()
        
        # Auto-start monitoring if enabled
        if self.manager.settings["auto_monitor"]:
            self.manager.start_monitoring()
            self.monitor_status.set("Monitoring: ON")

    def create_widgets(self):
        """Create GUI widgets"""
        # Control frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Monitor toggle
        self.monitor_status = tk.StringVar(value="Monitoring: OFF")
        monitor_btn = ttk.Button(control_frame, textvariable=self.monitor_status, 
                                command=self.toggle_monitoring)
        monitor_btn.pack(side=tk.LEFT, padx=5)
        
        # Manual save button
        save_btn = ttk.Button(control_frame, text="Save Current Clipboard", 
                             command=self.manual_save)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Settings button
        settings_btn = ttk.Button(control_frame, text="Settings", 
                                 command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Cleanup button
        cleanup_btn = ttk.Button(control_frame, text="Cleanup Old", 
                                command=self.cleanup_old)
        cleanup_btn.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(control_frame, text="Refresh", 
                                command=self.refresh_history)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # History frame
        history_frame = ttk.LabelFrame(self.root, text="Clipboard History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for history
        columns = ("Time", "Type", "Preview", "Size")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Restore to Clipboard", 
                                     command=self.restore_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        
        self.history_tree.bind("<Button-3>", self.show_context_menu)

    def toggle_monitoring(self):
        """Toggle clipboard monitoring"""
        if self.manager.monitoring:
            self.manager.stop_monitoring()
            self.monitor_status.set("Monitoring: OFF")
        else:
            self.manager.start_monitoring()
            self.monitor_status.set("Monitoring: ON")

    def manual_save(self):
        """Manually save current clipboard"""
        if self.manager.process_clipboard():
            messagebox.showinfo("Success", "Clipboard content saved!")
            self.refresh_history()
        else:
            messagebox.showwarning("Warning", "No new clipboard content found!")

    def cleanup_old(self):
        """Manually trigger cleanup"""
        self.manager.cleanup_old_entries()
        self.refresh_history()
        messagebox.showinfo("Success", "Old entries cleaned up!")

    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("450x400")
        
        # Settings entries
        ttk.Label(settings_window, text="Min Text Length:").pack(anchor=tk.W, padx=10, pady=5)
        min_text_var = tk.StringVar(value=str(self.manager.settings["min_text_length"]))
        ttk.Entry(settings_window, textvariable=min_text_var).pack(fill=tk.X, padx=10)
        
        ttk.Label(settings_window, text="Max Image Size (MB):").pack(anchor=tk.W, padx=10, pady=5)
        max_img_var = tk.StringVar(value=str(self.manager.settings["max_image_size"]))
        ttk.Entry(settings_window, textvariable=max_img_var).pack(fill=tk.X, padx=10)
        
        ttk.Label(settings_window, text="Retention Days:").pack(anchor=tk.W, padx=10, pady=5)
        retention_var = tk.StringVar(value=str(self.manager.settings["retention_days"]))
        ttk.Entry(settings_window, textvariable=retention_var).pack(fill=tk.X, padx=10)
        
        ttk.Label(settings_window, text="Max Entries:").pack(anchor=tk.W, padx=10, pady=5)
        max_entries_var = tk.StringVar(value=str(self.manager.settings["max_entries"]))
        ttk.Entry(settings_window, textvariable=max_entries_var).pack(fill=tk.X, padx=10)
        
        # Checkboxes
        auto_monitor_var = tk.BooleanVar(value=self.manager.settings["auto_monitor"])
        ttk.Checkbutton(settings_window, text="Auto Monitor", 
                       variable=auto_monitor_var).pack(anchor=tk.W, padx=10, pady=5)
        
        organize_date_var = tk.BooleanVar(value=self.manager.settings["organize_by_date"])
        ttk.Checkbutton(settings_window, text="Organize by Date", 
                       variable=organize_date_var).pack(anchor=tk.W, padx=10, pady=5)
        
        show_notif_var = tk.BooleanVar(value=self.manager.settings["show_notifications"])
        ttk.Checkbutton(settings_window, text="Show Notifications", 
                       variable=show_notif_var).pack(anchor=tk.W, padx=10, pady=5)
        
        skip_sensitive_var = tk.BooleanVar(value=self.manager.settings["skip_sensitive"])
        ttk.Checkbutton(settings_window, text="Skip Sensitive Content", 
                       variable=skip_sensitive_var).pack(anchor=tk.W, padx=10, pady=5)
        
        def save_settings():
            try:
                self.manager.settings.update({
                    "min_text_length": int(min_text_var.get()),
                    "max_image_size": float(max_img_var.get()),
                    "retention_days": int(retention_var.get()),
                    "max_entries": int(max_entries_var.get()),
                    "auto_monitor": auto_monitor_var.get(),
                    "organize_by_date": organize_date_var.get(),
                    "show_notifications": show_notif_var.get(),
                    "skip_sensitive": skip_sensitive_var.get()
                })
                self.manager.save_settings()
                settings_window.destroy()
                messagebox.showinfo("Success", "Settings saved!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers!")
        
        ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=10)

    def refresh_history(self):
        """Refresh history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Load history
        history = self.manager.get_history(100)
        for entry in history:
            if len(entry) >= 6:
                entry_id, timestamp, content_type, preview, file_path, size = entry[:6]
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%m/%d %H:%M")
                except Exception:
                    time_str = timestamp[:16]
                
                # Format size
                if size < 1024:
                    size_str = f"{size}B"
                elif size < 1024*1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size/(1024*1024):.1f}MB"
                
                self.history_tree.insert("", tk.END, 
                                       values=(time_str, content_type, preview[:60], size_str),
                                       tags=(entry_id, file_path))

    def show_context_menu(self, event):
        """Show context menu"""
        item = self.history_tree.selection()[0] if self.history_tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)

    def restore_selected(self):
        """Restore selected item to clipboard"""
        selection = self.history_tree.selection()
        if selection:
            item = selection[0]
            tags = self.history_tree.item(item)["tags"]
            if len(tags) >= 2:
                file_path = tags[1]
                if self.manager.restore_clipboard(file_path):
                    messagebox.showinfo("Success", "Content restored to clipboard!")
                else:
                    messagebox.showerror("Error", "Failed to restore content!")

    def delete_selected(self):
        """Delete selected item"""
        selection = self.history_tree.selection()
        if selection:
            if messagebox.askyesno("Confirm", "Delete selected item?"):
                item = selection[0]
                tags = self.history_tree.item(item)["tags"]
                if len(tags) >= 2:
                    entry_id = tags[0]
                    file_path = tags[1]
                    if self.manager.delete_entry(entry_id, file_path):
                        self.refresh_history()
                        messagebox.showinfo("Success", "Item deleted!")
                    else:
                        messagebox.showerror("Error", "Failed to delete item!")

    def on_closing(self):
        """Handle window closing"""
        self.manager.stop_monitoring()
        self.root.destroy()

    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

# Usage
if __name__ == "__main__":
    print("Advanced Clipboard Manager v2.0")
    print("Windows-only application with enhanced security and stability")
    
    try:
        manager = ClipboardManager()
        
        # Check for CLI mode
        if len(sys.argv) > 1 and sys.argv[1] == "--cli":
            print("Running in CLI mode...")
            if manager.process_clipboard():
                print("Clipboard content saved!")
            else:
                print("No new clipboard content found!")
        else:
            # GUI mode
            print("Starting GUI...")
            app = ClipboardGUI(manager)
            app.run()
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")
