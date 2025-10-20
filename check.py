#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Scanner GUI - Fixed Version for PyInstaller
Phiên bản đã sửa lỗi ordinal 380
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import subprocess
import os
import sys
import json
import datetime
import threading
import csv
import re
import webbrowser
import urllib.parse
from pathlib import Path

# Fix for Windows Registry access
import winreg

# PDF Report Generator
try:
    from pdf_reporter import PDFReporter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PDF export not available. Install reportlab to enable.")

# Fix for ctypes on Windows
try:
    import ctypes
    from ctypes import wintypes
except ImportError:
    ctypes = None

class SystemScannerGUI:
    def __init__(self, root):
        """Khởi tạo giao diện GUI"""
        self.root = root
        self.root.title("System Security Scanner")

        # Debug: Show PDF export availability
        print("=" * 70)
        print("SYSTEM SECURITY SCANNER - Starting...")
        print(f"PDF Export Available: {PDF_AVAILABLE}")
        if PDF_AVAILABLE:
            print("  ✓ ReportLab library is installed")
            print("  ✓ PDF export button will be functional")
        else:
            print("  ✗ ReportLab library not found")
            print("  ✗ PDF export button will be disabled")
            print("  → Install with: pip install reportlab pillow")
        print("=" * 70)

        # Modern color scheme
        self.colors = {
            'primary': '#2563eb',      # Blue
            'primary_dark': '#1e40af',
            'success': '#10b981',      # Green
            'warning': '#f59e0b',      # Orange
            'danger': '#ef4444',       # Red
            'bg_light': '#f8fafc',     # Light gray
            'bg_card': '#ffffff',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'border': '#e2e8f0'
        }

        # Set modern window size and constraints
        self.center_window(1100, 750)

        # Set minimum window size (prevents content from being obscured)
        self.root.minsize(800, 600)

        # Make window resizable
        self.root.resizable(True, True)

        # Biến lưu trữ kết quả
        self.scan_results = {
            'vpn': [],
            'chat': [],
            'remote': [],
            'security': {},
            'system': {},
            'kaspersky': False
        }

        # Tạo giao diện
        self.setup_ui()

        # Kiểm tra quyền admin (safe mode)
        self.check_admin_safe()

    def center_window(self, width, height):
        """Căn giữa cửa sổ trên màn hình"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def check_admin_safe(self):
        """Kiểm tra quyền admin một cách an toàn"""
        try:
            if ctypes:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                if not is_admin:
                    self.status_label.config(
                        text="⚠️  Recommendation: Run as Administrator for complete results",
                        fg=self.colors['warning']
                    )
        except:
            # Nếu không kiểm tra được thì bỏ qua
            pass
    
    def setup_ui(self):
        """Thiết lập giao diện người dùng - Modern Design"""
        # Configure root window
        self.root.configure(bg=self.colors['bg_light'])

        # Modern Style Configuration
        style = ttk.Style()
        style.theme_use('clam')

        # Configure modern button style
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       relief='flat',
                       padding=(20, 10))

        style.configure('Secondary.TButton',
                       font=('Segoe UI', 9),
                       borderwidth=1,
                       relief='flat',
                       padding=(15, 8))

        # Configure label styles
        style.configure('Title.TLabel',
                       font=('Segoe UI', 20, 'bold'),
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_light'])

        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['bg_light'])

        style.configure('Status.TLabel',
                       font=('Segoe UI', 9),
                       background=self.colors['bg_light'])

        # Configure frame styles
        style.configure('Card.TFrame',
                       background=self.colors['bg_card'],
                       borderwidth=1,
                       relief='solid')

        # Configure notebook style
        style.configure('TNotebook',
                       background=self.colors['bg_light'],
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       font=('Segoe UI', 10),
                       padding=(20, 10),
                       borderwidth=0)

        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_light'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Header section
        header_frame = tk.Frame(main_container, bg=self.colors['bg_light'])
        header_frame.pack(fill='x', pady=(0, 20))

        # Title
        title_label = tk.Label(header_frame,
                              text="System Security Scanner",
                              font=('Segoe UI', 24, 'bold'),
                              fg=self.colors['text_primary'],
                              bg=self.colors['bg_light'])
        title_label.pack(anchor='w')

        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Comprehensive security audit tool for Windows systems",
                                 font=('Segoe UI', 10),
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['bg_light'])
        subtitle_label.pack(anchor='w')

        # Action bar
        action_frame = tk.Frame(main_container, bg=self.colors['bg_card'], relief='solid', borderwidth=1)
        action_frame.pack(fill='x', pady=(0, 15))

        action_inner = tk.Frame(action_frame, bg=self.colors['bg_card'])
        action_inner.pack(padx=15, pady=15)

        # Define consistent button dimensions
        button_width = 18  # Characters width for consistent sizing
        button_height = 2  # Height in text lines

        # Scan button with modern styling
        self.scan_button = tk.Button(action_inner,
                                     text="🔍  Start System Scan",
                                     command=self.start_scan,
                                     font=('Segoe UI', 10, 'bold'),
                                     bg=self.colors['primary'],
                                     fg='white',
                                     activebackground=self.colors['primary_dark'],
                                     activeforeground='white',
                                     relief='flat',
                                     cursor='hand2',
                                     width=button_width,
                                     height=button_height)
        self.scan_button.pack(side='left', padx=(0, 10))

        # Export TXT button
        self.export_txt_button = tk.Button(action_inner,
                                          text="📄  Export TXT",
                                          command=self.export_txt,
                                          font=('Segoe UI', 10),
                                          bg='white',
                                          fg=self.colors['text_primary'],
                                          activebackground=self.colors['bg_light'],
                                          relief='solid',
                                          borderwidth=1,
                                          cursor='hand2',
                                          state='disabled',
                                          width=button_width,
                                          height=button_height)
        self.export_txt_button.pack(side='left', padx=5)

        # Export CSV button
        self.export_csv_button = tk.Button(action_inner,
                                          text="📊  Export CSV",
                                          command=self.export_csv,
                                          font=('Segoe UI', 10),
                                          bg='white',
                                          fg=self.colors['text_primary'],
                                          activebackground=self.colors['bg_light'],
                                          relief='solid',
                                          borderwidth=1,
                                          cursor='hand2',
                                          state='disabled',
                                          width=button_width,
                                          height=button_height)
        self.export_csv_button.pack(side='left', padx=5)

        # Export PDF button (new)
        self.export_pdf_button = tk.Button(action_inner,
                                          text="📑  Export PDF",
                                          command=self.export_pdf,
                                          font=('Segoe UI', 10),
                                          bg='white',
                                          fg=self.colors['text_primary'],
                                          activebackground=self.colors['bg_light'],
                                          relief='solid',
                                          borderwidth=1,
                                          cursor='hand2',
                                          state='disabled' if not PDF_AVAILABLE else 'disabled',
                                          width=button_width,
                                          height=button_height)
        self.export_pdf_button.pack(side='left', padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(main_container, mode='indeterminate', length=300)
        self.progress.pack(fill='x', pady=(0, 10))

        # Status label
        self.status_label = tk.Label(main_container,
                                    text="Ready to scan system",
                                    font=('Segoe UI', 9),
                                    fg=self.colors['success'],
                                    bg=self.colors['bg_light'],
                                    anchor='w')
        self.status_label.pack(fill='x', pady=(0, 15))

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)

        # Create tabs
        self.create_tabs()

        # Initialize undo/redo system
        self.init_undo_system()

        # Setup context menus for text widgets
        self.setup_context_menus()

        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def create_tabs(self):
        """Tạo các tab với thiết kế hiện đại và responsive"""
        # Summary tab
        self.summary_frame = tk.Frame(self.notebook, bg=self.colors['bg_light'])
        self.notebook.add(self.summary_frame, text="📊  Overview")

        # Stats cards container with grid layout for responsiveness
        cards_container = tk.Frame(self.summary_frame, bg=self.colors['bg_light'])
        cards_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Configure grid weights for responsive behavior
        cards_container.grid_columnconfigure(0, weight=1, minsize=200)
        cards_container.grid_columnconfigure(1, weight=1, minsize=200)
        cards_container.grid_columnconfigure(2, weight=1, minsize=200)
        cards_container.grid_rowconfigure(0, weight=0)
        cards_container.grid_rowconfigure(1, weight=0)

        # Create stat cards with responsive grid layout
        stats_data = [
            {'title': 'VPN Applications', 'var': 'vpn_count_label', 'icon': '🔐', 'color': '#6366f1', 'row': 0, 'col': 0},
            {'title': 'Chat Applications', 'var': 'chat_count_label', 'icon': '💬', 'color': '#8b5cf6', 'row': 0, 'col': 1},
            {'title': 'Remote Control', 'var': 'remote_count_label', 'icon': '🖥️', 'color': '#ec4899', 'row': 0, 'col': 2},
        ]

        # Store references for stat cards
        self.stat_cards = {}

        # Create top row cards (VPN, Chat, Remote)
        for stat in stats_data:
            card, count_label = self.create_stat_card(cards_container, stat['title'], stat['icon'], stat['color'])
            card.grid(row=stat['row'], column=stat['col'], sticky='nsew', padx=(0, 10) if stat['col'] < 2 else 0, pady=(0, 10))
            setattr(self, stat['var'], count_label)
            self.stat_cards[stat['var']] = count_label

        # Bottom row - Total and Kaspersky (2 cards, centered)
        # Total card
        total_card, total_label = self.create_stat_card(cards_container, 'Total Applications', '📊', self.colors['primary'])
        total_card.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=(0, 5), pady=0)
        self.total_count_label = total_label

        # Kaspersky card
        kaspersky_card, kaspersky_label = self.create_stat_card(cards_container, 'Kaspersky Antivirus', '🛡️', '#10b981')
        kaspersky_card.grid(row=1, column=2, sticky='nsew', padx=(5, 0), pady=0)
        self.kaspersky_label = kaspersky_label

        # Detail tab
        self.detail_frame = tk.Frame(self.notebook, bg=self.colors['bg_light'])
        self.notebook.add(self.detail_frame, text="📝  Details")

        self.detail_text = scrolledtext.ScrolledText(self.detail_frame,
                                                     wrap=tk.WORD,
                                                     width=80, height=20,
                                                     font=('Consolas', 10),
                                                     bg='#ffffff',
                                                     fg=self.colors['text_primary'],
                                                     relief='flat',
                                                     borderwidth=0)
        self.detail_text.pack(fill='both', expand=True, padx=15, pady=15)

        # Security tab
        self.security_frame = tk.Frame(self.notebook, bg=self.colors['bg_light'])
        self.notebook.add(self.security_frame, text="🔒  Security")

        self.security_text = scrolledtext.ScrolledText(self.security_frame,
                                                       wrap=tk.WORD,
                                                       width=80, height=20,
                                                       font=('Consolas', 10),
                                                       bg='#ffffff',
                                                       fg=self.colors['text_primary'],
                                                       relief='flat',
                                                       borderwidth=0)
        self.security_text.pack(fill='both', expand=True, padx=15, pady=15)

        # System tab
        self.system_frame = tk.Frame(self.notebook, bg=self.colors['bg_light'])
        self.notebook.add(self.system_frame, text="💻  System")

        self.system_text = scrolledtext.ScrolledText(self.system_frame,
                                                     wrap=tk.WORD,
                                                     width=80, height=20,
                                                     font=('Consolas', 10),
                                                     bg='#ffffff',
                                                     fg=self.colors['text_primary'],
                                                     relief='flat',
                                                     borderwidth=0)
        self.system_text.pack(fill='both', expand=True, padx=15, pady=15)

    def create_stat_card(self, parent, title, icon, color):
        """Create a modern stat card - Returns (card, count_label)"""
        card = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)

        # Card inner padding (responsive - reduced for smaller windows)
        inner = tk.Frame(card, bg='white')
        inner.pack(fill='both', expand=True, padx=10, pady=10)

        # Icon and title row
        header = tk.Frame(inner, bg='white')
        header.pack(fill='x', pady=(0, 5))

        icon_label = tk.Label(header,
                             text=icon,
                             font=('Segoe UI', 16),  # Smaller icon for responsiveness
                             bg='white')
        icon_label.pack(side='left', padx=(0, 5))

        title_label = tk.Label(header,
                              text=title,
                              font=('Segoe UI', 9),  # Smaller font
                              fg=self.colors['text_secondary'],
                              bg='white',
                              anchor='w',
                              wraplength=150,  # Aggressive wrapping
                              justify='left')
        title_label.pack(side='left', fill='x', expand=True)

        # Count label (responsive with wrapping)
        count_label = tk.Label(inner,
                              text="0",
                              font=('Segoe UI', 20, 'bold'),  # Smaller but still prominent
                              fg=color,
                              bg='white',
                              anchor='w',
                              wraplength=180,  # Allow wrapping for long text
                              justify='left')
        count_label.pack(fill='x', expand=True)

        return card, count_label

    def init_undo_system(self):
        """Initialize undo/redo system for text widgets"""
        self.undo_stacks = {}  # Stores undo history for each widget
        self.redo_stacks = {}  # Stores redo history for each widget
        self.max_undo_levels = 50  # Maximum undo levels

        # Initialize stacks for text widgets (will be populated after widgets are created)
        self.undo_stacks = {}
        self.redo_stacks = {}

    def setup_context_menus(self):
        """Setup right-click context menus for text widgets"""
        # List of text widgets that should have context menus
        self.text_widgets = [
            self.detail_text,
            self.security_text,
            self.system_text
        ]

        # Initialize undo/redo stacks for each text widget
        for text_widget in self.text_widgets:
            widget_id = str(text_widget)
            self.undo_stacks[widget_id] = []
            self.redo_stacks[widget_id] = []

        # Setup context menu for each text widget
        for text_widget in self.text_widgets:
            self.add_context_menu(text_widget)

    def add_context_menu(self, text_widget):
        """Add context menu to a text widget"""
        context_menu = tk.Menu(text_widget, tearoff=0)

        # Add menu items
        context_menu.add_command(label="Undo", command=lambda: self.undo_text(text_widget))
        context_menu.add_command(label="Redo", command=lambda: self.redo_text(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=lambda: self.cut_text(text_widget))
        context_menu.add_command(label="Copy", command=lambda: self.copy_text(text_widget))
        context_menu.add_command(label="Paste", command=lambda: self.paste_text(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: self.select_all_text(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Search on Web", command=lambda: self.search_on_web(text_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Clear", command=lambda: self.clear_text(text_widget))

        # Bind right-click event
        text_widget.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu, text_widget))

    def show_context_menu(self, event, context_menu, text_widget):
        """Show context menu at cursor position"""
        try:
            # Update menu item states based on current selection
            has_selection = bool(text_widget.tag_ranges(tk.SEL))
            clipboard_content = self.root.clipboard_get()
            has_clipboard = bool(clipboard_content)
        except:
            has_selection = False
            has_clipboard = False

        # Check undo/redo availability
        widget_id = str(text_widget)
        has_undo = widget_id in self.undo_stacks and len(self.undo_stacks[widget_id]) > 0
        has_redo = widget_id in self.redo_stacks and len(self.redo_stacks[widget_id]) > 0

        # Enable/disable menu items based on context
        context_menu.entryconfig("Undo", state=tk.NORMAL if has_undo else tk.DISABLED)
        context_menu.entryconfig("Redo", state=tk.NORMAL if has_redo else tk.DISABLED)
        context_menu.entryconfig("Cut", state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.entryconfig("Copy", state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.entryconfig("Paste", state=tk.NORMAL if has_clipboard else tk.DISABLED)
        context_menu.entryconfig("Search on Web", state=tk.NORMAL if has_selection else tk.DISABLED)

        # Show the context menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass
        finally:
            context_menu.grab_release()

    def cut_text(self, text_widget):
        """Cut selected text to clipboard"""
        try:
            if text_widget.tag_ranges(tk.SEL):
                text_widget.event_generate("<<Cut>>")
        except:
            pass

    def copy_text(self, text_widget):
        """Copy selected text to clipboard"""
        try:
            if text_widget.tag_ranges(tk.SEL):
                text_widget.event_generate("<<Copy>>")
        except:
            pass

    def paste_text(self, text_widget):
        """Paste text from clipboard - improved to prevent double pasting"""
        try:
            # Get current clipboard content
            clipboard_content = self.root.clipboard_get()
            if not clipboard_content:
                return

            # Store current state for undo
            self.store_undo_state(text_widget)

            # If there's selected text, delete it first
            if text_widget.tag_ranges(tk.SEL):
                text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)

            # Get current cursor position
            cursor_pos = text_widget.index(tk.INSERT)

            # Insert clipboard content at cursor position
            text_widget.insert(cursor_pos, clipboard_content)

            # Update cursor position to end of inserted text
            new_cursor_pos = text_widget.index(f"{cursor_pos}+{len(clipboard_content)}c")
            text_widget.mark_set(tk.INSERT, new_cursor_pos)
            text_widget.see(tk.INSERT)

        except tk.TclError:
            # Clipboard is empty or unavailable
            pass
        except Exception:
            # Fallback to standard paste if our method fails
            try:
                text_widget.event_generate("<<Paste>>")
            except:
                pass

    def select_all_text(self, text_widget):
        """Select all text in widget"""
        try:
            text_widget.tag_add(tk.SEL, "1.0", tk.END)
            text_widget.mark_set(tk.INSERT, "1.0")
            text_widget.see(tk.INSERT)
        except:
            pass

    def clear_text(self, text_widget):
        """Clear all text in widget"""
        try:
            text_widget.delete("1.0", tk.END)
        except:
            pass

    def search_on_web(self, text_widget):
        """Search selected text on the web"""
        try:
            if text_widget.tag_ranges(tk.SEL):
                selected_text = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
                if selected_text:
                    # Clean up the text for web search
                    search_query = selected_text.replace('\n', ' ').replace('\r', ' ')
                    # Limit search query length
                    if len(search_query) > 100:
                        search_query = search_query[:97] + "..."

                    # URL encode the search query
                    encoded_query = urllib.parse.quote_plus(search_query)
                    search_url = f"https://www.google.com/search?q={encoded_query}"

                    # Open in default web browser
                    webbrowser.open(search_url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not search on web: {str(e)}")

    def get_selected_text(self, text_widget):
        """Get currently selected text from widget"""
        try:
            if text_widget.tag_ranges(tk.SEL):
                return text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            return ""
        except:
            return ""

    def store_undo_state(self, text_widget):
        """Store current text state for undo functionality"""
        try:
            widget_id = str(text_widget)
            current_content = text_widget.get("1.0", tk.END + "-1c")
            cursor_pos = text_widget.index(tk.INSERT)

            # Initialize stacks if not exists
            if widget_id not in self.undo_stacks:
                self.undo_stacks[widget_id] = []
            if widget_id not in self.redo_stacks:
                self.redo_stacks[widget_id] = []

            # Store the state
            state = {
                'content': current_content,
                'cursor': cursor_pos
            }

            # Add to undo stack
            self.undo_stacks[widget_id].append(state)

            # Limit undo stack size
            if len(self.undo_stacks[widget_id]) > self.max_undo_levels:
                self.undo_stacks[widget_id].pop(0)

            # Clear redo stack when new action is performed
            self.redo_stacks[widget_id].clear()

        except Exception:
            pass

    def undo_text(self, text_widget):
        """Undo last text operation"""
        try:
            widget_id = str(text_widget)

            if widget_id in self.undo_stacks and self.undo_stacks[widget_id]:
                # Store current state in redo stack
                current_content = text_widget.get("1.0", tk.END + "-1c")
                current_cursor = text_widget.index(tk.INSERT)

                redo_state = {
                    'content': current_content,
                    'cursor': current_cursor
                }

                if widget_id not in self.redo_stacks:
                    self.redo_stacks[widget_id] = []

                self.redo_stacks[widget_id].append(redo_state)

                # Restore previous state
                previous_state = self.undo_stacks[widget_id].pop()

                # Temporarily disable undo tracking
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", previous_state['content'])
                text_widget.mark_set(tk.INSERT, previous_state['cursor'])
                text_widget.see(tk.INSERT)

        except Exception:
            pass

    def redo_text(self, text_widget):
        """Redo last undone text operation"""
        try:
            widget_id = str(text_widget)

            if widget_id in self.redo_stacks and self.redo_stacks[widget_id]:
                # Store current state in undo stack
                current_content = text_widget.get("1.0", tk.END + "-1c")
                current_cursor = text_widget.index(tk.INSERT)

                undo_state = {
                    'content': current_content,
                    'cursor': current_cursor
                }

                self.undo_stacks[widget_id].append(undo_state)

                # Restore next state
                next_state = self.redo_stacks[widget_id].pop()

                # Temporarily disable undo tracking
                text_widget.delete("1.0", tk.END)
                text_widget.insert("1.0", next_state['content'])
                text_widget.mark_set(tk.INSERT, next_state['cursor'])
                text_widget.see(tk.INSERT)

        except Exception:
            pass

    def setup_keyboard_shortcuts(self):
        """Setup comprehensive keyboard shortcuts for text operations"""
        # Bind keyboard shortcuts to text widgets
        for text_widget in self.text_widgets:
            # Basic operations
            text_widget.bind("<Control-a>", lambda event: self.handle_shortcut(event, self.select_all_text))
            text_widget.bind("<Control-c>", lambda event: self.handle_shortcut(event, self.copy_text))
            text_widget.bind("<Control-x>", lambda event: self.handle_shortcut(event, self.cut_text_with_undo))
            text_widget.bind("<Control-v>", lambda event: self.handle_shortcut(event, self.paste_text))

            # Undo/Redo
            text_widget.bind("<Control-z>", lambda event: self.handle_shortcut(event, self.undo_text))
            text_widget.bind("<Control-y>", lambda event: self.handle_shortcut(event, self.redo_text))
            text_widget.bind("<Control-Shift-Z>", lambda event: self.handle_shortcut(event, self.redo_text))

            # Additional text editor shortcuts
            text_widget.bind("<Control-d>", lambda event: self.handle_shortcut(event, self.duplicate_line))
            text_widget.bind("<Control-l>", lambda event: self.handle_shortcut(event, self.select_line))
            text_widget.bind("<Control-k>", lambda event: self.handle_shortcut(event, self.delete_line))
            text_widget.bind("<Control-Shift-K>", lambda event: self.handle_shortcut(event, self.delete_line))

            # Navigation shortcuts
            text_widget.bind("<Control-Home>", lambda event: self.handle_shortcut(event, self.goto_start))
            text_widget.bind("<Control-End>", lambda event: self.handle_shortcut(event, self.goto_end))
            text_widget.bind("<Control-Left>", lambda event: self.handle_shortcut(event, self.word_left))
            text_widget.bind("<Control-Right>", lambda event: self.handle_shortcut(event, self.word_right))

            # Find functionality
            text_widget.bind("<Control-f>", lambda event: self.handle_shortcut(event, self.find_text))

        # Global keyboard shortcuts for the main window
        self.root.bind("<Control-a>", lambda event: self.handle_global_select_all())

    def handle_shortcut(self, event, action_func):
        """Handle keyboard shortcut and prevent default behavior where needed"""
        try:
            action_func(event.widget)
            return "break"  # Prevent default behavior
        except Exception:
            pass

    def handle_global_select_all(self):
        """Handle global Ctrl+A shortcut"""
        # Find the currently focused widget
        focused_widget = self.root.focus_get()
        if focused_widget in self.text_widgets:
            self.select_all_text(focused_widget)

    def cut_text_with_undo(self, text_widget):
        """Cut text with undo support"""
        try:
            if text_widget.tag_ranges(tk.SEL):
                self.store_undo_state(text_widget)
                text_widget.event_generate("<<Cut>>")
        except:
            pass

    def duplicate_line(self, text_widget):
        """Duplicate current line"""
        try:
            self.store_undo_state(text_widget)
            current_pos = text_widget.index(tk.INSERT)
            line_start = text_widget.index(f"{current_pos} linestart")
            line_end = text_widget.index(f"{current_pos} lineend")
            line_text = text_widget.get(line_start, line_end)

            text_widget.mark_set(tk.INSERT, line_end)
            text_widget.insert(tk.INSERT, "\n" + line_text)
        except:
            pass

    def select_line(self, text_widget):
        """Select current line"""
        try:
            current_pos = text_widget.index(tk.INSERT)
            line_start = text_widget.index(f"{current_pos} linestart")
            line_end = text_widget.index(f"{current_pos} lineend+1c")

            text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            text_widget.tag_add(tk.SEL, line_start, line_end)
            text_widget.mark_set(tk.INSERT, line_end)
        except:
            pass

    def delete_line(self, text_widget):
        """Delete current line"""
        try:
            self.store_undo_state(text_widget)
            current_pos = text_widget.index(tk.INSERT)
            line_start = text_widget.index(f"{current_pos} linestart")
            line_end = text_widget.index(f"{current_pos} lineend+1c")

            text_widget.delete(line_start, line_end)
        except:
            pass

    def goto_start(self, text_widget):
        """Go to start of document"""
        try:
            text_widget.mark_set(tk.INSERT, "1.0")
            text_widget.see(tk.INSERT)
        except:
            pass

    def goto_end(self, text_widget):
        """Go to end of document"""
        try:
            text_widget.mark_set(tk.INSERT, tk.END)
            text_widget.see(tk.INSERT)
        except:
            pass

    def word_left(self, text_widget):
        """Move cursor to previous word"""
        try:
            current_pos = text_widget.index(tk.INSERT)
            prev_word_start = text_widget.index(f"{current_pos} -1c wordstart")
            text_widget.mark_set(tk.INSERT, prev_word_start)
            text_widget.see(tk.INSERT)
        except:
            pass

    def word_right(self, text_widget):
        """Move cursor to next word"""
        try:
            current_pos = text_widget.index(tk.INSERT)
            next_word_start = text_widget.index(f"{current_pos} +1c wordstart")
            text_widget.mark_set(tk.INSERT, next_word_start)
            text_widget.see(tk.INSERT)
        except:
            pass

    def find_text(self, text_widget):
        """Open find dialog"""
        try:
            search_text = tk.simpledialog.askstring("Find", "Enter text to find:")
            if search_text:
                self.perform_find(text_widget, search_text)
        except:
            pass

    def perform_find(self, text_widget, search_text):
        """Perform text search"""
        try:
            # Clear previous selections
            text_widget.tag_remove(tk.SEL, "1.0", tk.END)

            # Start search from current position
            start_pos = text_widget.index(tk.INSERT)
            pos = text_widget.search(search_text, start_pos, tk.END)

            if pos:
                # Found text
                end_pos = f"{pos}+{len(search_text)}c"
                text_widget.tag_add(tk.SEL, pos, end_pos)
                text_widget.mark_set(tk.INSERT, end_pos)
                text_widget.see(pos)
            else:
                # Search from beginning if not found
                pos = text_widget.search(search_text, "1.0", start_pos)
                if pos:
                    end_pos = f"{pos}+{len(search_text)}c"
                    text_widget.tag_add(tk.SEL, pos, end_pos)
                    text_widget.mark_set(tk.INSERT, end_pos)
                    text_widget.see(pos)
                else:
                    messagebox.showinfo("Find", f"'{search_text}' not found.")
        except:
            pass

    def start_scan(self):
        """Bắt đầu quét hệ thống"""
        self.scan_button.config(state='disabled')
        self.export_txt_button.config(state='disabled')
        self.export_csv_button.config(state='disabled')
        
        self.clear_results()
        
        self.progress.start()
        self.status_label.config(text="🔍 Starting system scan...", fg=self.colors['primary'])
        
        # Run scan in separate thread
        scan_thread = threading.Thread(target=self.perform_scan)
        scan_thread.daemon = True
        scan_thread.start()
    
    def clear_results(self):
        """Xóa kết quả cũ"""
        self.detail_text.delete(1.0, tk.END)
        self.security_text.delete(1.0, tk.END)
        self.system_text.delete(1.0, tk.END)
        self.scan_results = {
            'vpn': [],
            'chat': [],
            'remote': [],
            'security': {},
            'system': {},
            'kaspersky': False
        }
    
    def safe_path_exists(self, path):
        """Kiểm tra path tồn tại một cách an toàn"""
        try:
            return os.path.exists(path)
        except:
            return False
    
    def safe_subprocess_run(self, cmd, timeout=5):
        """Chạy subprocess một cách an toàn"""
        try:
            if sys.platform == "win32":
                # Sử dụng CREATE_NO_WINDOW để ẩn console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=timeout,
                    startupinfo=startupinfo
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=timeout
                )
            return result
        except subprocess.TimeoutExpired:
            return None
        except:
            return None

    def get_all_drives(self):
        """Lấy tất cả các ổ đĩa có sẵn trên hệ thống"""
        drives = []
        try:
            # Kiểm tra từ A: đến Z:
            for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                drive_path = f"{drive_letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(drive_path)
        except:
            # Fallback: ít nhất trả về ổ C:
            drives = ["C:\\"]

        return drives

    def is_app_match(self, item_name, pattern):
        """
        Kiểm tra xem tên item có khớp với pattern của app không
        Sử dụng logic matching chính xác hơn để tránh false positives
        """
        # Loại bỏ khoảng trắng và ký tự đặc biệt
        item_clean = item_name.strip().replace(" ", "").replace("-", "").replace("_", "")
        pattern_clean = pattern.strip().replace(" ", "").replace("-", "").replace("_", "")

        # 1. Exact match (chính xác nhất)
        if item_clean == pattern_clean:
            return True

        # 2. Exact match với tên thư mục (ví dụ: "Discord" trong "C:\Users\User\AppData\Local\Discord")
        if item_name == pattern:
            return True

        # 3. Pattern match with word boundaries - chỉ match khi pattern là từ độc lập
        # Tạo regex pattern với word boundaries
        regex_pattern = r'\b' + re.escape(pattern) + r'\b'
        if re.search(regex_pattern, item_name, re.IGNORECASE):
            return True

        # 4. Check if pattern is at start or end of item name (cho các trường hợp như "skypefordesktop")
        if item_clean.startswith(pattern_clean) or item_clean.endswith(pattern_clean):
            # Nhưng phải đảm bảo rằng nó không phải là substring ngẫu nhiên
            # Pattern phải chiếm ít nhất 70% của tên
            if len(pattern_clean) >= len(item_clean) * 0.7:
                return True

        # 5. Special case: cho phép match với tên có version numbers hoặc edition
        # Ví dụ: "discord" match với "discordcanary", "skype" match với "skypefordesktop"
        if pattern_clean in item_clean:
            # Kiểm tra xem có phải là match hợp lý không
            pattern_pos = item_clean.find(pattern_clean)

            # Case 1: Pattern ở đầu (ví dụ: "discord" trong "discordcanary")
            if pattern_pos == 0:
                if len(item_clean) > len(pattern_clean):
                    # Cho phép match nếu:
                    # - Có số sau pattern (discord2, teams3)
                    # - Có từ khóa phổ biến (discordcanary, skypefordesktop, teamspeak)
                    remaining = item_clean[len(pattern_clean):]
                    common_suffixes = ['canary', 'beta', 'alpha', 'desktop', 'fordesktop', 'client',
                                     'viewer', 'admin', 'manager', 'pro', 'free', 'business',
                                     'personal', 'streamer', 'speak', 'speak3', 'meet', 'meetings']

                    if (remaining.isdigit() or  # Chỉ có số
                        any(remaining.startswith(suffix) for suffix in common_suffixes) or  # Có suffix hợp lệ
                        len(remaining) <= 3):  # Hoặc rất ngắn (có thể là version)
                        return True
                else:
                    return True

            # Case 2: Pattern ở cuối (ít phổ biến nhưng vẫn cần check)
            elif pattern_pos + len(pattern_clean) == len(item_clean):
                if pattern_pos > 0:
                    prefix = item_clean[:pattern_pos]
                    common_prefixes = ['microsoft', 'google', 'adobe', 'real', 'tight', 'ultra',
                                     'tiger', 'free', 'gnu', 'open']
                    if any(prefix.endswith(pfx) for pfx in common_prefixes):
                        return True
                else:
                    return True

        return False

    def is_valid_app_installation(self, app_name, path, app_type='chat'):
        """
        Kiểm tra xem path có phải là cài đặt hợp lệ của app hay không
        Tránh false positives như SkypeSrv trong Office hoặc Session Storage trong VS Code
        """
        path_lower = path.lower()
        app_name_lower = app_name.lower()

        # Danh sách các thư mục/path patterns không phải cài đặt thực sự
        invalid_patterns = {
            # Office và Microsoft suite
            'microsoft office', 'office16', 'office15', 'office14', 'office365',
            # Developer tools và IDE
            'visual studio', 'vscode', 'code', 'session storage', 'local storage',
            'cache', 'temp', 'temporary', 'logs', 'log files',
            # Browser data
            'google\\chrome', 'mozilla\\firefox', 'microsoft\\edge',
            'appdata\\local\\google', 'appdata\\local\\mozilla',
            # System và Windows
            'system32', 'syswow64', 'windows\\system32', 'program files\\windows',
            # Development folders
            'node_modules', '.vs', '.vscode', 'bin', 'obj', 'debug', 'release',
            # Temporary và cache folders
            'webcache', 'browsercache', 'cookies', 'history',
            # User files và documents (tránh legitimate app names)
            '\\desktop\\temp', '\\desktop\\cache', 'desktop\\temp', 'desktop\\cache',
            '\\documents\\my ', '\\downloads\\', '\\pictures\\', '\\videos\\', '\\music\\'
        }

        # Kiểm tra nếu là file (không phải thư mục) - thường không phải app installation
        if os.path.isfile(path) and not path_lower.endswith('.exe'):
            return False

        # Kiểm tra các file extensions không hợp lệ
        invalid_extensions = {'.txt', '.log', '.tmp', '.cache', '.dat', '.dll', '.sys'}
        path_ext = os.path.splitext(path_lower)[1]
        if path_ext in invalid_extensions:
            return False

        # Kiểm tra các pattern không hợp lệ
        for invalid_pattern in invalid_patterns:
            if invalid_pattern in path_lower:
                return False

        # Các trường hợp đặc biệt cho từng app
        app_specific_checks = {
            'skype': self._validate_skype_path,
            'session': self._validate_session_path,
            'teams': self._validate_teams_path,
            'discord': self._validate_discord_path,
            'telegram': self._validate_telegram_path,
            'zoom': self._validate_zoom_path,
        }

        # Tìm app checker phù hợp
        checker_key = None
        for key in app_specific_checks:
            if key in app_name_lower:
                checker_key = key
                break

        # Chạy checker cụ thể nếu có - kết quả này có độ ưu tiên cao nhất
        if checker_key and checker_key in app_specific_checks:
            specific_result = app_specific_checks[checker_key](path, path_lower)
            # Nếu specific validator trả về kết quả rõ ràng, dùng kết quả đó
            return specific_result

        # Kiểm tra chung: path phải chứa tên app như một thư mục độc lập hoặc legitimate path
        path_parts = path_lower.replace('\\', '/').split('/')
        app_base_name = app_name_lower.split()[0]  # Lấy từ đầu tiên

        # Trước tiên kiểm tra các legitimate installation patterns
        legitimate_patterns = [
            f'program files\\{app_base_name}',
            f'program files (x86)\\{app_base_name}',
            f'appdata\\local\\{app_base_name}',
            f'appdata\\roaming\\{app_base_name}',
            f'local\\programs\\{app_base_name}',
            f'programs\\{app_base_name}',
            f'microsoft\\{app_base_name}',  # For Microsoft apps like Teams, Skype
            # Additional patterns for multi-word app names
            'program files\\microsoft\\skype',
            'appdata\\roaming\\telegram',
            'local\\programs\\signal',
        ]

        for pattern in legitimate_patterns:
            if pattern in path_lower:
                return True

        # Thêm patterns cho multi-word applications
        app_full_name = app_name_lower.replace(' ', '')
        if (f'program files\\{app_full_name}' in path_lower or
            f'appdata\\local\\{app_full_name}' in path_lower or
            f'appdata\\roaming\\{app_full_name}' in path_lower):
            return True

        # Path phải có ít nhất một part chứa tên app
        for part in path_parts:
            if part == app_base_name or part.startswith(app_base_name):
                # Kiểm tra part không phải là part của path không hợp lệ
                # Ví dụ: "signal" trong "signal_processing.dll" không hợp lệ
                if (part.endswith('.dll') or part.endswith('.sys') or
                    part.endswith('.tmp') or part.endswith('.log')):
                    continue
                return True

        return False

    def _validate_skype_path(self, path, path_lower):
        """Validate Skype installation paths"""
        # Skype hợp lệ
        valid_skype_patterns = [
            'skype for desktop',
            'skypefordesktop',
            'microsoft\\skype',
            '\\skype\\',
            'program files\\skype'
        ]

        # Skype không hợp lệ (như SkypeSrv trong Office)
        invalid_skype_patterns = [
            'skypesrv',
            'office16',
            'office15',
            'microsoft office',
            'lync',
            'communicator'
        ]

        # Kiểm tra invalid trước
        for invalid in invalid_skype_patterns:
            if invalid in path_lower:
                return False

        # Kiểm tra valid patterns
        return any(valid in path_lower for valid in valid_skype_patterns)

    def _validate_session_path(self, path, path_lower):
        """Validate Session messenger paths"""
        # Session không hợp lệ (như Session Storage)
        invalid_session_patterns = [
            'session storage',
            'local storage',
            'webstorage',
            'browser',
            'cache',
            'temp',
            'vscode',
            'code\\session'
        ]

        # Kiểm tra invalid patterns
        for invalid in invalid_session_patterns:
            if invalid in path_lower:
                return False

        # Session hợp lệ: phải là executable hoặc là app directory với đúng structure
        if path_lower.endswith('.exe'):
            return 'session' in os.path.basename(path_lower)
        elif os.path.isdir(path):
            # Kiểm tra có exe file trong thư mục không
            try:
                for item in os.listdir(path):
                    if item.lower().endswith('.exe') and 'session' in item.lower():
                        return True
                # Nếu không có exe, kiểm tra xem có phải là app directory không
                # Session desktop thường có structure: session-desktop hoặc Programs/session-desktop
                if ('session-desktop' in path_lower or
                    'session desktop' in path_lower or
                    (path_lower.endswith('session') and 'programs' in path_lower)):
                    return True
            except:
                pass

        return False

    def _validate_teams_path(self, path, path_lower):
        """Validate Microsoft Teams paths"""
        # Teams hợp lệ
        valid_teams_patterns = [
            'microsoft\\teams',
            'program files\\microsoft\\teams',
            'local\\microsoft\\teams'
        ]

        return any(valid in path_lower for valid in valid_teams_patterns)

    def _validate_discord_path(self, path, path_lower):
        """Validate Discord paths"""
        # Discord hợp lệ
        valid_discord_patterns = [
            'local\\discord',
            'local\\discordcanary',
            'local\\discordptb',
            'program files\\discord'
        ]

        return any(valid in path_lower for valid in valid_discord_patterns)

    def _validate_telegram_path(self, path, path_lower):
        """Validate Telegram paths"""
        # Telegram hợp lệ
        valid_telegram_patterns = [
            'telegram desktop',
            'roaming\\telegram',
            'program files\\telegram'
        ]

        return any(valid in path_lower for valid in valid_telegram_patterns)

    def _validate_zoom_path(self, path, path_lower):
        """Validate Zoom paths"""
        # Zoom hợp lệ
        valid_zoom_patterns = [
            'roaming\\zoom',
            'program files\\zoom',
            'local\\zoom'
        ]

        # Zoom không hợp lệ
        invalid_zoom_patterns = [
            'cache',
            'temp',
            'browser'
        ]

        # Kiểm tra invalid trước
        for invalid in invalid_zoom_patterns:
            if invalid in path_lower:
                return False

        return any(valid in path_lower for valid in valid_zoom_patterns)

    def normalize_app_name(self, app_name):
        """
        Chuẩn hóa tên app để phát hiện duplicate tốt hơn
        VD: "Zalo" và "ZaloPC" sẽ được chuẩn hóa thành "zalo"
        """
        # Loại bỏ các từ khóa phổ biến và chuẩn hóa
        name_lower = app_name.lower()

        # Mapping các tên app variations
        app_mappings = {
            'zalopc': 'zalo',
            'discord canary': 'discord',
            'discord ptb': 'discord',
            'discordcanary': 'discord',
            'discordptb': 'discord',
            'microsoft teams': 'teams',
            'teams-insider': 'teams',
            'skype for desktop': 'skype',
            'skypefordesktop': 'skype',
            'telegram desktop': 'telegram',
            'whatsapp desktop': 'whatsapp',
            'signal desktop': 'signal',
            'element desktop': 'element',
            'session desktop': 'session',
        }

        # Kiểm tra mappings
        for variant, canonical in app_mappings.items():
            if variant in name_lower:
                return canonical

        # Loại bỏ các từ khóa phổ biến
        common_suffixes = ['desktop', 'for desktop', 'client', 'app', 'messenger']
        normalized = name_lower
        for suffix in common_suffixes:
            normalized = normalized.replace(f' {suffix}', '').replace(suffix, '')

        # Loại bỏ khoảng trắng và ký tự đặc biệt
        normalized = normalized.replace(' ', '').replace('-', '').replace('_', '')

        return normalized.strip()

    def is_better_installation_path(self, path1, path2):
        """
        So sánh 2 installation paths để xác định cái nào tốt hơn
        Thứ tự ưu tiên:
        1. Program Files > AppData
        2. Shorter path (thường là main installation)
        3. Không có version/variant names
        """
        path1_lower = path1.lower()
        path2_lower = path2.lower()

        # Ưu tiên Program Files và Programs folder
        if ('program files' in path1_lower or '\\programs\\' in path1_lower) and 'appdata' in path2_lower:
            return True
        if 'appdata' in path1_lower and ('program files' in path2_lower or '\\programs\\' in path2_lower):
            return False

        # Ưu tiên path ngắn hơn (main installation)
        if len(path1) < len(path2):
            return True
        if len(path2) < len(path1):
            return False

        # Ưu tiên path không có variant names
        variant_keywords = ['canary', 'ptb', 'beta', 'alpha', 'insider', 'dev']
        path1_has_variant = any(keyword in path1_lower for keyword in variant_keywords)
        path2_has_variant = any(keyword in path2_lower for keyword in variant_keywords)

        if not path1_has_variant and path2_has_variant:
            return True
        if path1_has_variant and not path2_has_variant:
            return False

        # Nếu tất cả đều bằng nhau, giữ nguyên (path1 không tốt hơn)
        return False

    def get_excluded_directories(self):
        """Lấy danh sách thư mục nên bỏ qua khi quét"""
        return {
            # System directories
            "windows", "system32", "syswow64", "winsxs", "drivers",
            "boot", "recovery", "documents and settings", "$recycle.bin",
            "system volume information", "config.msi", "msocache",
            # Common cache/temp directories
            "temp", "tmp", "cache", "logs", "log", "backup", "backups",
            # Development/IDE folders that may contain false positives
            "node_modules", ".git", ".svn", ".vs", ".vscode", "__pycache__",
            # Virtual machine and container directories
            "virtualbox", "vmware", "docker", "hyper-v"
        }

    def scan_directory_for_apps(self, directory, app_patterns, max_depth=3, current_depth=0):
        """
        Quét thư mục tìm ứng dụng dựa trên pattern matching
        directory: Thư mục cần quét
        app_patterns: Dict {app_name: [patterns]} - patterns có thể là tên folder hoặc tên file exe
        max_depth: Độ sâu tối đa để quét (tránh quét quá sâu)
        current_depth: Độ sâu hiện tại
        """
        found_apps = []
        excluded_dirs = self.get_excluded_directories()

        if current_depth >= max_depth:
            return found_apps

        try:
            # Kiểm tra quyền truy cập thư mục và existence
            if not os.path.exists(directory) or not os.access(directory, os.R_OK):
                return found_apps

            # Tránh symbolic links để tránh infinite loops
            if os.path.islink(directory):
                return found_apps

            items = os.listdir(directory)
            # Giới hạn số lượng items để tránh quét quá lâu
            if len(items) > 1000:
                items = items[:1000]

            for item in items:
                try:
                    item_path = os.path.join(directory, item)
                    item_lower = item.lower()

                    # Bỏ qua các thư mục hệ thống
                    if item_lower in excluded_dirs:
                        continue

                    # Bỏ qua hidden folders và system folders
                    if item.startswith('.') or item.startswith('$'):
                        continue

                    # Tránh symbolic links
                    if os.path.islink(item_path):
                        continue

                    if os.path.isdir(item_path):
                        # Kiểm tra tên thư mục có khớp với app pattern không (sử dụng exact matching)
                        for app_name, patterns in app_patterns.items():
                            for pattern in patterns:
                                if self.is_app_match(item_lower, pattern.lower()):
                                    # Thêm validation để tránh false positives
                                    if self.is_valid_app_installation(app_name, item_path):
                                        found_apps.append({
                                            'name': app_name,
                                            'path': item_path,
                                            'type': 'Application Directory',
                                            'match_type': 'directory_name'
                                        })
                                    break
                            # Break outer loop if found
                            else:
                                continue
                            break

                        # Quét sâu hơn nếu chưa đạt max_depth
                        if current_depth < max_depth - 1:
                            try:
                                found_apps.extend(
                                    self.scan_directory_for_apps(
                                        item_path, app_patterns, max_depth, current_depth + 1
                                    )
                                )
                            except (PermissionError, OSError, RecursionError):
                                # Bỏ qua thư mục không có quyền truy cập hoặc lỗi recursion
                                continue

                    elif os.path.isfile(item_path) and item_lower.endswith('.exe'):
                        # Kiểm tra tên file exe có khớp với app pattern không (sử dụng exact matching)
                        exe_name = os.path.splitext(item_lower)[0]  # Loại bỏ .exe extension
                        for app_name, patterns in app_patterns.items():
                            for pattern in patterns:
                                if self.is_app_match(exe_name, pattern.lower()):
                                    # Thêm validation để tránh false positives
                                    if self.is_valid_app_installation(app_name, item_path):
                                        found_apps.append({
                                            'name': app_name,
                                            'path': item_path,
                                            'type': 'Executable File',
                                            'match_type': 'exe_name'
                                        })
                                    break
                            # Break outer loop if found
                            else:
                                continue
                            break

                except (PermissionError, OSError, UnicodeDecodeError):
                    # Bỏ qua lỗi với từng item cụ thể
                    continue

        except (PermissionError, OSError, UnicodeDecodeError, RecursionError):
            # Bỏ qua các lỗi truy cập directory
            pass

        return found_apps

    def scan_system_wide(self, app_patterns, max_depth=3):
        """
        Quét toàn bộ hệ thống tìm ứng dụng
        app_patterns: Dict {app_name: [patterns]}
        max_depth: Độ sâu tối đa để quét
        """
        all_found_apps = []
        drives = self.get_all_drives()

        for drive in drives:
            try:
                # Ưu tiên quét các thư mục phổ biến trước với độ sâu tối đa
                priority_dirs = [
                    os.path.join(drive, "Program Files"),
                    os.path.join(drive, "Program Files (x86)"),
                    os.path.join(drive, "ProgramData")
                ]

                # Thêm AppData directories cho user hiện tại
                username = os.environ.get('USERNAME', 'User')
                user_dirs = [
                    os.path.join(drive, "Users", username, "AppData", "Local"),
                    os.path.join(drive, "Users", username, "AppData", "Local", "Programs"),
                    os.path.join(drive, "Users", username, "AppData", "Roaming"),
                ]

                all_priority_dirs = priority_dirs + user_dirs

                # Quét các thư mục ưu tiên với depth cao hơn
                for priority_dir in all_priority_dirs:
                    if os.path.exists(priority_dir):
                        found_apps = self.scan_directory_for_apps(
                            priority_dir, app_patterns, max_depth
                        )
                        all_found_apps.extend(found_apps)

                # Quét thư mục Users với depth thấp hơn để tìm các user khác
                users_dir = os.path.join(drive, "Users")
                if os.path.exists(users_dir):
                    found_apps = self.scan_directory_for_apps(
                        users_dir, app_patterns, max_depth=max_depth+1  # Tăng 1 level cho Users
                    )
                    all_found_apps.extend(found_apps)

                # Quét root của drive với độ sâu hạn chế hơn
                root_found = self.scan_directory_for_apps(
                    drive, app_patterns, max_depth=2
                )
                all_found_apps.extend(root_found)

            except Exception:
                continue

        # Loại bỏ duplicates và ưu tiên directory over exe files
        app_groups = {}

        # Nhóm các apps theo tên
        for app in all_found_apps:
            app_name = app['name']
            if app_name not in app_groups:
                app_groups[app_name] = []
            app_groups[app_name].append(app)

        unique_apps = []
        for app_name, apps in app_groups.items():
            if len(apps) == 1:
                # Chỉ có 1 detection, thêm luôn
                unique_apps.append(apps[0])
            else:
                # Có nhiều detections, ưu tiên theo thứ tự:
                # 1. Application Directory
                # 2. Executable File
                directory_apps = [app for app in apps if app['type'] == 'Application Directory']
                exe_apps = [app for app in apps if app['type'] == 'Executable File']

                if directory_apps:
                    # Ưu tiên directory, chọn path ngắn nhất (thường là root installation)
                    best_dir = min(directory_apps, key=lambda x: len(x['path']))
                    unique_apps.append(best_dir)
                elif exe_apps:
                    # Nếu không có directory, chọn exe file
                    best_exe = min(exe_apps, key=lambda x: len(x['path']))
                    unique_apps.append(best_exe)

        return unique_apps
    
    def perform_scan(self):
        """Thực hiện quét hệ thống toàn diện"""
        try:
            # Hiển thị thông tin về phạm vi quét
            drives = self.get_all_drives()
            drive_list = ", ".join(drives)
            self.update_status(f"Bắt đầu quét toàn hệ thống trên các ổ đĩa: {drive_list}")

            self.update_status("Đang quét ứng dụng VPN trên toàn hệ thống...")
            self.scan_vpn_apps()

            self.update_status("Đang quét ứng dụng Chat trên toàn hệ thống...")
            self.scan_chat_apps()

            self.update_status("Đang quét ứng dụng Remote Control trên toàn hệ thống...")
            self.scan_remote_apps()

            self.update_status("Đang kiểm tra Kaspersky...")
            self.check_kaspersky()

            self.update_status("Đang kiểm tra cấu hình bảo mật...")
            self.check_security_config()

            self.update_status("Đang thu thập thông tin hệ thống...")
            self.collect_system_info()

            self.update_status("Đang tổng hợp kết quả quét...")
            self.root.after(0, self.display_results)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi quét: {str(e)}"))
        finally:
            self.root.after(0, self.scan_complete)
    
    def update_status(self, message):
        """Cập nhật status label thread-safe"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def scan_vpn_apps(self):
        """Quét VPN applications toàn hệ thống"""
        self.update_status("Đang quét VPN applications trên toàn hệ thống...")

        # Định nghĩa patterns để tìm VPN apps (sử dụng tên chính xác và specific hơn)
        vpn_patterns = {
            "NordVPN": ["nordvpn"],
            "ExpressVPN": ["expressvpn"],
            "Surfshark": ["surfshark"],
            "CyberGhost": ["cyberghost"],
            "ProtonVPN": ["protonvpn", "proton vpn"],
            "Windscribe": ["windscribe"],
            "HotspotShield": ["hotspotshield", "hotspot shield"],
            "TunnelBear": ["tunnelbear"],
            "PrivateInternetAccess": ["privateinternetaccess", "private internet access"],
            "Psiphon": ["psiphon3", "psiphon"],  # Thêm psiphon3 để tránh false positive
            "Lantern": ["getlantern", "lantern-installer"],  # Sử dụng tên cụ thể hơn
            "Hide.me": ["hide.me", "hideme"],
            "Betternet": ["betternet"],
            "OpenVPN": ["openvpn", "openvpn-gui"],
            "TAP-Windows": ["tap-windows"],
            "FortiClient": ["forticlient"],
            "Cisco AnyConnect": ["cisco anyconnect", "anyconnect"],
            "SoftEther": ["softether vpn", "softether"],
            "WireGuard": ["wireguard"],
            "IPVanish": ["ipvanish"],
            "Mullvad": ["mullvad", "mullvadvpn"],
            "PureVPN": ["purevpn"],
            "VyprVPN": ["vyprvpn"],
            "AtlasVPN": ["atlasvpn"],
            "VPN Unlimited": ["vpn unlimited", "keepsolid"],
            "StrongVPN": ["strongvpn"],
            "Private Tunnel": ["private tunnel", "privatetunnel"]
        }

        # Quét toàn bộ hệ thống
        found_vpn_apps = self.scan_system_wide(vpn_patterns, max_depth=3)

        # Thêm vào kết quả
        for app in found_vpn_apps:
            self.scan_results['vpn'].append({
                'name': app['name'],
                'path': app['path'],
                'type': 'VPN Application',
                'detection_method': app.get('match_type', 'pattern_match')
            })

        # Kiểm tra TAP-Windows adapter trên tất cả các ổ đĩa
        drives = self.get_all_drives()
        for drive in drives:
            tap_path = os.path.join(drive, "Program Files", "TAP-Windows")
            tap_path_x86 = os.path.join(drive, "Program Files (x86)", "TAP-Windows")

            if self.safe_path_exists(tap_path):
                self.scan_results['vpn'].append({
                    'name': 'TAP-Windows (OpenVPN)',
                    'path': tap_path,
                    'type': 'VPN Network Adapter',
                    'detection_method': 'direct_check'
                })
            elif self.safe_path_exists(tap_path_x86):
                self.scan_results['vpn'].append({
                    'name': 'TAP-Windows (OpenVPN)',
                    'path': tap_path_x86,
                    'type': 'VPN Network Adapter',
                    'detection_method': 'direct_check'
                })
    
    def scan_chat_apps(self):
        """Quét chat applications toàn hệ thống"""
        self.update_status("Đang quét Chat applications trên toàn hệ thống...")

        # Định nghĩa patterns để tìm chat apps với nhiều variations
        chat_patterns = {
            "Discord": ["discord"],  # Đơn giản hóa để dễ match hơn
            "Zalo": ["zalo", "zalopc"],  # Thêm zalopc pattern
            "Skype": ["skype"],
            "Microsoft Teams": ["teams", "microsoft teams"],
            "Telegram": ["telegram"],
            "WhatsApp": ["whatsapp"],
            "Slack": ["slack"],
            "Zoom": ["zoom"],
            "Viber": ["viber"],
            "WeChat": ["wechat"],
            "Line": ["line desktop", "line for desktop"],
            "KakaoTalk": ["kakaotalk"],
            "Facebook Messenger": ["messenger"],
            "Signal": ["signal"],
            "Element": ["element"],
            "Threema": ["threema"],
            "Wire": ["wire"],
            "Jami": ["jami"],
            "Tox": ["qtox", "utox"],
            "Session": ["session"],
            "Wickr": ["wickr"],
            "Keybase": ["keybase"],
            "Mumble": ["mumble"],
            "TeamSpeak": ["teamspeak"],
            "Ventrilo": ["ventrilo"],
            "Jitsi": ["jitsi"],
            "Rocket.Chat": ["rocket.chat", "rocketchat"],
            "Mattermost": ["mattermost"],
            "Franz": ["franz"],
            "Ferdi": ["ferdi"],
            "Rambox": ["rambox"],
            "Ferdium": ["ferdium"]
        }

        # Trước tiên, kiểm tra các đường dẫn phổ biến trực tiếp
        self.check_common_chat_paths()

        # Sau đó quét toàn bộ hệ thống
        found_chat_apps = self.scan_system_wide(chat_patterns, max_depth=4)  # Tăng depth

        # Thêm tất cả apps tìm được với enhanced duplicate checking
        for app in found_chat_apps:
            app_name = app['name']
            app_path = app['path']

            # Chuẩn hóa tên app để kiểm tra duplicate tốt hơn
            normalized_name = self.normalize_app_name(app_name)

            # Kiểm tra duplicate dựa trên:
            # 1. Path giống nhau (exact match)
            # 2. Tên app chuẩn hóa giống nhau (để tránh Zalo + ZaloPC)
            is_duplicate = False
            existing_to_replace = None

            for i, existing in enumerate(self.scan_results['chat']):
                existing_normalized = self.normalize_app_name(existing['name'])

                # Duplicate nếu path giống nhau
                if existing['path'].lower() == app_path.lower():
                    is_duplicate = True
                    break

                # Duplicate nếu tên app chuẩn hóa giống nhau
                if existing_normalized == normalized_name:
                    # Ưu tiên path tốt hơn (Program Files > AppData)
                    if self.is_better_installation_path(app_path, existing['path']):
                        existing_to_replace = i
                    else:
                        is_duplicate = True
                    break

            if not is_duplicate:
                if existing_to_replace is not None:
                    # Thay thế installation kém hơn bằng installation tốt hơn
                    self.scan_results['chat'][existing_to_replace] = {
                        'name': app_name,
                        'path': app_path,
                        'type': 'Communication App',
                        'detection_method': app.get('match_type', 'pattern_match')
                    }
                else:
                    # Thêm app mới
                    self.scan_results['chat'].append({
                        'name': app_name,
                        'path': app_path,
                        'type': 'Communication App',
                        'detection_method': app.get('match_type', 'pattern_match')
                    })

    def check_common_chat_paths(self):
        """Kiểm tra các đường dẫn cài đặt phổ biến cho chat apps"""
        # Danh sách các path phổ biến để kiểm tra trực tiếp
        common_paths = [
            # Discord
            (os.path.expanduser("~\\AppData\\Local\\Discord"), "Discord"),
            (os.path.expanduser("~\\AppData\\Local\\DiscordCanary"), "Discord Canary"),
            (os.path.expanduser("~\\AppData\\Local\\DiscordPTB"), "Discord PTB"),

            # Zalo
            (os.path.expanduser("~\\AppData\\Local\\Programs\\Zalo"), "Zalo"),
            (os.path.expanduser("~\\AppData\\Local\\ZaloPC"), "Zalo"),
            ("C:\\Program Files\\Zalo", "Zalo"),
            ("C:\\Program Files (x86)\\Zalo", "Zalo"),

            # Teams
            (os.path.expanduser("~\\AppData\\Local\\Microsoft\\Teams"), "Microsoft Teams"),
            ("C:\\Program Files\\Microsoft\\Teams", "Microsoft Teams"),
            ("C:\\Program Files (x86)\\Microsoft\\Teams", "Microsoft Teams"),

            # Skype
            (os.path.expanduser("~\\AppData\\Local\\Microsoft\\SkypeForDesktop"), "Skype"),
            ("C:\\Program Files\\Microsoft\\Skype for Desktop", "Skype"),

            # Telegram
            (os.path.expanduser("~\\AppData\\Roaming\\Telegram Desktop"), "Telegram"),

            # WhatsApp
            (os.path.expanduser("~\\AppData\\Local\\WhatsApp"), "WhatsApp"),

            # Slack
            (os.path.expanduser("~\\AppData\\Local\\slack"), "Slack"),

            # Zoom
            (os.path.expanduser("~\\AppData\\Roaming\\Zoom"), "Zoom"),

            # Viber
            (os.path.expanduser("~\\AppData\\Local\\Viber"), "Viber"),
        ]

        for path, app_name in common_paths:
            if self.safe_path_exists(path):
                # Sử dụng cùng logic duplicate checking như system-wide scan
                normalized_name = self.normalize_app_name(app_name)
                is_duplicate = False
                existing_to_replace = None

                for i, existing in enumerate(self.scan_results['chat']):
                    existing_normalized = self.normalize_app_name(existing['name'])

                    # Duplicate nếu path giống nhau
                    if existing['path'].lower() == path.lower():
                        is_duplicate = True
                        break

                    # Duplicate nếu tên app chuẩn hóa giống nhau
                    if existing_normalized == normalized_name:
                        # Ưu tiên path tốt hơn
                        if self.is_better_installation_path(path, existing['path']):
                            existing_to_replace = i
                        else:
                            is_duplicate = True
                        break

                if not is_duplicate:
                    if existing_to_replace is not None:
                        # Thay thế installation kém hơn
                        self.scan_results['chat'][existing_to_replace] = {
                            'name': app_name,
                            'path': path,
                            'type': 'Communication App',
                            'detection_method': 'common_path_check'
                        }
                    else:
                        # Thêm app mới
                        self.scan_results['chat'].append({
                            'name': app_name,
                            'path': path,
                            'type': 'Communication App',
                            'detection_method': 'common_path_check'
                        })
    
    def scan_remote_apps(self):
        """Quét remote control applications toàn hệ thống"""
        self.update_status("Đang quét Remote Control applications trên toàn hệ thống...")

        # Định nghĩa patterns để tìm remote control apps (sử dụng tên chính xác để tránh false positive)
        remote_patterns = {
            "TeamViewer": ["teamviewer"],
            "AnyDesk": ["anydesk"],
            "UltraViewer": ["ultraviewer"],
            "LogMeIn": ["logmein", "logmein client"],
            "RealVNC": ["realvnc", "vnc viewer", "vnc-viewer"],
            "TightVNC": ["tightvnc"],
            "Radmin": ["radmin viewer", "radmin"],
            "Chrome Remote Desktop": ["chrome remote desktop", "remoting_host"],
            "Microsoft Remote Desktop": ["microsoft remote desktop", "remote desktop connection"],
            "Splashtop": ["splashtop streamer", "splashtop business", "splashtop"],
            "Parsec": ["parsec"],
            "NoMachine": ["nomachine"],
            "Ammyy Admin": ["ammyy admin", "ammyy"],
            "ShowMyPC": ["showmypc"],
            "DWService": ["dwservice", "dwagent"],
            "RemotePC": ["remotepc"],
            "GoToMyPC": ["gotomypc"],
            "VNC Connect": ["vnc connect", "vnc-connect"],
            "UltraVNC": ["ultravnc"],
            "TigerVNC": ["tigervnc"],
            "RustDesk": ["rustdesk"],
            "Remmina": ["remmina"],
            "Windows Remote Assistance": ["remote assistance", "msra"],
            "ConnectWise Control": ["connectwise control", "screenconnect"],
            "Remote Utilities": ["remote utilities", "ru server", "ru viewer"],
            "PCAnywhere": ["pcanywhere", "symantec pcanywhere"],
            "DameWare": ["dameware mini remote control", "dameware"],
            "LiteManager": ["litemanager free", "litemanager pro", "litemanager"],
            "NetSupport": ["netsupport manager", "netsupport"],
            "Remote Desktop Manager": ["remote desktop manager", "devolutions rdm"],
            "Supremo": ["supremo"],
            "ISL Online": ["isl online", "isl alwayson", "islonline"],
            "BeyondTrust": ["beyondtrust remote support", "beyondtrust"],
            "LogMeIn Rescue": ["logmein rescue", "rescue lens"],
            "Bomgar": ["bomgar representative console", "bomgar"],
            "Mikogo": ["mikogo"],
            "Jump Desktop": ["jump desktop"],
            "Remote Desktop Plus": ["remote desktop plus"],
            "VNC Personal": ["vnc personal"],
            "Distant Desktop": ["distant desktop"],
            "Microsoft Quick Assist": ["quick assist"],
            "Windows Remote Desktop": ["remote desktop", "mstsc"]
        }

        # Quét toàn bộ hệ thống
        found_remote_apps = self.scan_system_wide(remote_patterns, max_depth=3)

        # Thêm vào kết quả
        for app in found_remote_apps:
            self.scan_results['remote'].append({
                'name': app['name'],
                'path': app['path'],
                'type': 'Remote Control Software',
                'detection_method': app.get('match_type', 'pattern_match')
            })
    
    def check_kaspersky(self):
        """Kiểm tra Kaspersky"""
        kaspersky_found = False
        
        kaspersky_dirs = [
            "C:\\Program Files\\Kaspersky Lab",
            "C:\\Program Files (x86)\\Kaspersky Lab"
        ]
        
        for dir_path in kaspersky_dirs:
            if self.safe_path_exists(dir_path):
                kaspersky_found = True
                break
        
        if not kaspersky_found:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    "SOFTWARE\\KasperskyLab")
                winreg.CloseKey(key)
                kaspersky_found = True
            except:
                pass
        
        self.scan_results['kaspersky'] = kaspersky_found
    
    def check_security_config(self):
        """Kiểm tra cấu hình bảo mật"""
        security_info = {}
        
        # Check file extensions
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced")
            value, _ = winreg.QueryValueEx(key, "HideFileExt")
            security_info['file_extensions'] = "Hidden" if value == 1 else "Visible"
            winreg.CloseKey(key)
        except:
            security_info['file_extensions'] = "Unknown"
        
        # Check Guest account
        result = self.safe_subprocess_run(['net', 'user', 'guest'])
        if result and result.stdout:
            if 'Account active' in result.stdout:
                if 'No' in result.stdout:
                    security_info['guest_account'] = "Disabled"
                else:
                    security_info['guest_account'] = "Enabled"
            else:
                security_info['guest_account'] = "Unknown"
        else:
            security_info['guest_account'] = "Check Failed"
        
        # Check AutoPlay
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\AutoplayHandlers")
            try:
                value, _ = winreg.QueryValueEx(key, "DisableAutoplay")
                security_info['autoplay'] = "Disabled" if value == 1 else "Enabled"
            except:
                security_info['autoplay'] = "Enabled (Default)"
            winreg.CloseKey(key)
        except:
            security_info['autoplay'] = "Enabled (Default)"
        
        # Get MAC Address
        result = self.safe_subprocess_run(['getmac', '/fo', 'csv', '/nh'])
        if result and result.stdout:
            lines = result.stdout.strip().split('\n')
            if lines and lines[0]:
                mac_info = lines[0].split(',')
                if len(mac_info) >= 1:
                    security_info['mac_address'] = mac_info[0].strip('"')
                else:
                    security_info['mac_address'] = "Not found"
            else:
                security_info['mac_address'] = "Not found"
        else:
            security_info['mac_address'] = "Check Failed"
        
        # Check Windows Firewall status
        security_info['firewall_status'] = self.check_windows_firewall()

        # Check if critical ports are blocked
        security_info['port_blocking'] = self.check_port_blocking()

        # Check unused network interfaces
        security_info['network_interfaces'] = self.check_network_interfaces()

        self.scan_results['security'] = security_info

    def check_windows_firewall(self):
        """Kiểm tra trạng thái Windows Firewall"""
        firewall_status = {
            'domain': 'Unknown',
            'private': 'Unknown',
            'public': 'Unknown',
            'overall': 'Unknown'
        }

        try:
            # Check firewall status using netsh
            result = self.safe_subprocess_run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], timeout=10)
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                current_profile = None

                for line in lines:
                    line = line.strip()
                    if 'Domain Profile' in line:
                        current_profile = 'domain'
                    elif 'Private Profile' in line:
                        current_profile = 'private'
                    elif 'Public Profile' in line:
                        current_profile = 'public'
                    elif 'State' in line and current_profile:
                        if 'ON' in line.upper():
                            firewall_status[current_profile] = 'Enabled'
                        elif 'OFF' in line.upper():
                            firewall_status[current_profile] = 'Disabled'

                # Determine overall status
                if all(status == 'Enabled' for status in [firewall_status['domain'], firewall_status['private'], firewall_status['public']]):
                    firewall_status['overall'] = 'Enabled (All Profiles)'
                elif all(status == 'Disabled' for status in [firewall_status['domain'], firewall_status['private'], firewall_status['public']]):
                    firewall_status['overall'] = 'Disabled (All Profiles)'
                elif any(status == 'Enabled' for status in [firewall_status['domain'], firewall_status['private'], firewall_status['public']]):
                    firewall_status['overall'] = 'Partially Enabled'
                else:
                    firewall_status['overall'] = 'Unknown'
        except Exception as e:
            firewall_status['overall'] = f'Check Failed: {str(e)}'

        return firewall_status

    def is_port_in_range_or_list(self, port, port_spec):
        """Check if a port is in a port specification (can be single, list, or range)"""
        port_str = str(port)
        port_spec = port_spec.strip()

        # Exact match
        if port_spec == port_str:
            return True

        # Comma-separated list (e.g., "135,139,445")
        if ',' in port_spec:
            ports_list = [p.strip() for p in port_spec.split(',')]
            if port_str in ports_list:
                return True

        # Port range (e.g., "135-139")
        if '-' in port_spec:
            try:
                parts = port_spec.split('-')
                if len(parts) == 2:
                    start_port = int(parts[0].strip())
                    end_port = int(parts[1].strip())
                    if start_port <= port <= end_port:
                        return True
            except ValueError:
                pass

        return False

    def check_port_blocking(self):
        """Kiểm tra các cổng 135, 136, 137, 138, 139, 445 có bị chặn không"""
        ports_to_check = [135, 136, 137, 138, 139, 445]
        port_status = {}

        for port in ports_to_check:
            port_status[port] = {
                'blocked': 'Unknown',
                'details': '',
                'listening': False,
                'firewall_blocked': False
            }

        # First check if ports are listening (both TCP and UDP)
        try:
            netstat_result = self.safe_subprocess_run(['netstat', '-ano'], timeout=10)
            if netstat_result and netstat_result.stdout:
                for port in ports_to_check:
                    port_str = str(port)
                    lines = netstat_result.stdout.split('\n')
                    tcp_listening = False
                    udp_listening = False

                    for line in lines:
                        if f':{port_str} ' in line or f':{port_str}\t' in line:
                            if line.strip().startswith('TCP'):
                                tcp_listening = True
                            elif line.strip().startswith('UDP'):
                                udp_listening = True

                    port_status[port]['listening'] = tcp_listening or udp_listening
                    port_status[port]['tcp_listening'] = tcp_listening
                    port_status[port]['udp_listening'] = udp_listening
        except:
            pass

        # Check firewall rules using PowerShell (more reliable when available)
        powershell_success = False
        try:
            for port in ports_to_check:
                # Check for blocking rules on this specific port
                ps_cmd = f'powershell -Command "$rules = Get-NetFirewallPortFilter | Where-Object {{$_.LocalPort -eq \'{port}\'}} | Get-NetFirewallRule | Where-Object {{$_.Enabled -eq \'True\' -and $_.Direction -eq \'Inbound\'}}; if ($rules) {{ $rules | ForEach-Object {{ Write-Output (\\"{{0}}|{{1}}\\" -f $_.Action, $_.Name) }} }}"'
                result = self.safe_subprocess_run(ps_cmd, timeout=10)

                if result and result.returncode == 0 and result.stdout and not result.stderr:
                    powershell_success = True
                    lines = result.stdout.strip().split('\n')
                    has_block = False

                    for line in lines:
                        if '|' in line:
                            action = line.split('|')[0].strip()
                            if action == 'Block':
                                has_block = True
                                break

                    # If there's a block rule, the port is blocked
                    if has_block:
                        port_status[port]['firewall_blocked'] = True
        except:
            powershell_success = False

        # Fallback to netsh if PowerShell fails
        if not powershell_success:
            try:
                result = self.safe_subprocess_run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], timeout=30)
                if result and result.stdout:
                    rules = result.stdout

                    # Split by rule entries
                    rule_entries = rules.split('\n\n')

                    for port in ports_to_check:
                        port_str = str(port)

                        for entry in rule_entries:
                            # Check if this rule applies to our port
                            if f'LocalPort:' in entry and port_str in entry:
                                # Parse the entry for direction and action
                                is_inbound = 'Direction:' in entry and 'In' in entry
                                is_block = 'Action:' in entry and 'Block' in entry
                                is_enabled = 'Enabled:' in entry and 'Yes' in entry

                                # Check if the port number matches exactly
                                for line in entry.split('\n'):
                                    if 'LocalPort:' in line:
                                        # Extract port specification from the line
                                        port_part = line.split('LocalPort:')[1].strip()
                                        # Use helper function to check if port matches
                                        if self.is_port_in_range_or_list(port, port_part):
                                            if is_inbound and is_block and is_enabled:
                                                port_status[port]['firewall_blocked'] = True
                                                break
            except:
                pass

        # Determine final status for each port
        for port in ports_to_check:
            listening = port_status[port]['listening']
            tcp_listening = port_status[port].get('tcp_listening', False)
            udp_listening = port_status[port].get('udp_listening', False)
            firewall_blocked = port_status[port]['firewall_blocked']

            # Build protocol info
            protocol_info = []
            if tcp_listening:
                protocol_info.append('TCP')
            if udp_listening:
                protocol_info.append('UDP')
            protocol_str = '/'.join(protocol_info) if protocol_info else ''

            if firewall_blocked:
                port_status[port]['blocked'] = 'Yes'
                if protocol_str:
                    port_status[port]['details'] = f'Blocked by firewall (listening on {protocol_str})'
                else:
                    port_status[port]['details'] = 'Blocked by firewall rule'
            elif listening:
                port_status[port]['blocked'] = 'No'
                if protocol_str:
                    port_status[port]['details'] = f'Port is listening ({protocol_str}) and not blocked'
                else:
                    port_status[port]['details'] = 'Port is listening and not blocked'
            else:
                port_status[port]['blocked'] = 'Not listening'
                port_status[port]['details'] = 'Port not in use (safe)'

        return port_status

    def check_network_interfaces(self):
        """Kiểm tra các interface mạng không sử dụng có bị tắt không"""
        interfaces = {
            'all_interfaces': [],
            'enabled_interfaces': [],
            'disabled_interfaces': [],
            'unused_enabled': [],
            'summary': 'Unknown'
        }

        try:
            # Get all network adapters using PowerShell
            ps_cmd = 'powershell -Command "Get-NetAdapter | Select-Object Name, Status, InterfaceDescription | ConvertTo-Csv -NoTypeInformation"'
            result = self.safe_subprocess_run(ps_cmd, timeout=15)

            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Skip header
                    for i in range(1, len(lines)):
                        line = lines[i].strip()
                        if line:
                            # Parse CSV line
                            parts = line.split(',')
                            if len(parts) >= 3:
                                name = parts[0].strip('"')
                                status = parts[1].strip('"')
                                description = parts[2].strip('"')

                                interface_info = {
                                    'name': name,
                                    'status': status,
                                    'description': description
                                }

                                interfaces['all_interfaces'].append(interface_info)

                                # Categorize interface status
                                # "Disabled" = administratively disabled by user
                                # "Disconnected" = enabled but no connection (unused but enabled!)
                                # "Up" = enabled and connected (in use)
                                # "Not Present" = hardware not present but driver installed

                                if status == 'Disabled':
                                    # Truly disabled - good for security
                                    interfaces['disabled_interfaces'].append(interface_info)
                                elif status == 'Up':
                                    # Enabled and connected - in use
                                    interfaces['enabled_interfaces'].append(interface_info)
                                else:
                                    # Disconnected, Not Present, etc. - enabled but not in use
                                    # These are UNUSED BUT ENABLED - security concern!
                                    interfaces['enabled_interfaces'].append(interface_info)
                                    interfaces['unused_enabled'].append(interface_info)

                    # Generate summary
                    total = len(interfaces['all_interfaces'])
                    enabled = len(interfaces['enabled_interfaces'])
                    disabled = len(interfaces['disabled_interfaces'])
                    unused_enabled_count = len(interfaces['unused_enabled'])

                    if unused_enabled_count > 0:
                        interfaces['summary'] = f'{unused_enabled_count} unused interface(s) still enabled'
                    else:
                        interfaces['summary'] = 'All unused interfaces are disabled'

                    interfaces['total_count'] = total
                    interfaces['enabled_count'] = enabled
                    interfaces['disabled_count'] = disabled
                    interfaces['unused_enabled_count'] = unused_enabled_count
                else:
                    interfaces['summary'] = 'No network adapters found'
            else:
                interfaces['summary'] = 'Check Failed - No output'
        except Exception as e:
            interfaces['summary'] = f'Check Failed: {str(e)}'

        return interfaces

    def get_windows_edition(self):
        """Get Windows edition (Home, Pro, Enterprise, etc.)"""
        edition = ""

        # Method 1: Registry ProductName with SKU mapping
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")

            # Try to get EditionID first (more reliable)
            try:
                edition_id, _ = winreg.QueryValueEx(key, "EditionID")
                if edition_id:
                    edition = self.map_edition_sku_to_friendly_name(str(edition_id))
                    if edition:
                        winreg.CloseKey(key)
                        return edition
            except:
                pass

            # Fallback to ProductName
            try:
                product_name, _ = winreg.QueryValueEx(key, "ProductName")
                if product_name:
                    product_name_str = str(product_name)
                    # Check for internal SKU names first
                    edition = self.map_edition_sku_to_friendly_name(product_name_str)
                    if not edition:
                        # Extract edition from ProductName (e.g., "Windows 11 Pro" -> "Pro")
                        product_parts = product_name_str.split()
                        for part in reversed(product_parts):
                            if part.lower() in ['home', 'pro', 'enterprise', 'education', 'professional']:
                                edition = part.capitalize()
                                break
            except:
                pass
            winreg.CloseKey(key)
        except:
            pass

        # Method 2: PowerShell Get-WindowsEdition (Windows 10/11)
        if not edition:
            try:
                ps_cmd = 'powershell -Command "Get-WindowsEdition -Online | Select-Object Edition | ConvertTo-Csv -NoTypeInformation"'
                result = self.safe_subprocess_run(ps_cmd, timeout=10)
                if result and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        edition_line = lines[1].strip().strip('"')
                        if edition_line and edition_line != "Edition":
                            raw_edition = edition_line.replace('Edition', '').strip()
                            edition = self.map_edition_sku_to_friendly_name(raw_edition)
                            if not edition:
                                edition = raw_edition
            except:
                pass

        # Method 3: WMIC OS Caption
        if not edition:
            try:
                result = self.safe_subprocess_run(['wmic', 'os', 'get', 'caption', '/value'], timeout=10)
                if result and result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Caption='):
                            caption = line.split('=', 1)[1].strip()
                            # Check for internal SKU names first
                            edition = self.map_edition_sku_to_friendly_name(caption)
                            if not edition:
                                # Extract edition from caption
                                caption_lower = caption.lower()
                                if 'home' in caption_lower:
                                    edition = 'Home'
                                elif 'pro' in caption_lower or 'professional' in caption_lower:
                                    edition = 'Pro'
                                elif 'enterprise' in caption_lower:
                                    edition = 'Enterprise'
                                elif 'education' in caption_lower:
                                    edition = 'Education'
                            break
            except:
                pass

        # Method 4: PowerShell Get-CimInstance Win32_OperatingSystem
        if not edition:
            try:
                ps_cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object Caption | ConvertTo-Csv -NoTypeInformation"'
                result = self.safe_subprocess_run(ps_cmd, timeout=10)
                if result and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        caption_line = lines[1].strip().strip('"')
                        # Check for internal SKU names first
                        edition = self.map_edition_sku_to_friendly_name(caption_line)
                        if not edition:
                            caption_lower = caption_line.lower()
                            if 'home' in caption_lower:
                                edition = 'Home'
                            elif 'pro' in caption_lower or 'professional' in caption_lower:
                                edition = 'Pro'
                            elif 'enterprise' in caption_lower:
                                edition = 'Enterprise'
                            elif 'education' in caption_lower:
                                edition = 'Education'
            except:
                pass

        return edition

    def map_edition_sku_to_friendly_name(self, sku_name):
        """Map Windows internal SKU names to user-friendly edition names"""
        if not sku_name:
            return ""

        sku_lower = sku_name.lower()

        # Windows SKU to Edition mapping
        sku_mappings = {
            # Windows 11/10 Home variants
            'coresinglelanguage': 'Home',
            'core': 'Home',
            'corecountryspecific': 'Home',
            'coren': 'Home N',
            'home': 'Home',
            'homesinglelan': 'Home',

            # Windows 11/10 Pro variants
            'professional': 'Pro',
            'pro': 'Pro',
            'professionaln': 'Pro N',
            'pron': 'Pro N',
            'professionalworkstation': 'Pro for Workstations',
            'professionalworkstationn': 'Pro for Workstations N',
            'proworkstation': 'Pro for Workstations',

            # Windows 11/10 Enterprise variants
            'enterprise': 'Enterprise',
            'enterprisen': 'Enterprise N',
            'enterpriseg': 'Enterprise G',
            'enterprisegn': 'Enterprise G N',
            'enterprises': 'Enterprise S',
            'enterprisesn': 'Enterprise S N',
            'enterpriseltsc': 'Enterprise LTSC',
            'enterpriseltsbn': 'Enterprise LTSB N',

            # Windows 11/10 Education variants
            'education': 'Education',
            'educationn': 'Education N',
            'professionalstudent': 'Education',
            'professionalstudentn': 'Education N',

            # Other variants
            'serverrdsh': 'Enterprise for Virtual Desktops',
            'iotuap': 'IoT Core',
            'ppipro': 'Team',
            'embedded': 'Embedded',
            'mobile': 'Mobile',
            'mobilenterprise': 'Mobile Enterprise'
        }

        # Direct mapping check
        if sku_lower in sku_mappings:
            return sku_mappings[sku_lower]

        # Partial matching for complex names
        for sku_key, friendly_name in sku_mappings.items():
            if sku_key in sku_lower:
                return friendly_name

        # Check if the input string contains recognizable edition names
        if 'coresinglelanguage' in sku_lower or 'single language' in sku_lower:
            return 'Home'
        elif 'professional' in sku_lower or 'pro' in sku_lower:
            return 'Pro'
        elif 'enterprise' in sku_lower:
            return 'Enterprise'
        elif 'education' in sku_lower:
            return 'Education'
        elif 'home' in sku_lower or 'core' in sku_lower:
            return 'Home'

        return ""

    def get_windows_version(self):
        """Get Windows OS name and version using multiple methods"""
        os_name = "Unknown"
        os_version = "Unknown"

        try:
            # Method 1: Use sys.getwindowsversion() if available
            if hasattr(sys, 'getwindowsversion'):
                win_ver = sys.getwindowsversion()
                major, minor, build = win_ver.major, win_ver.minor, win_ver.build

                # Map version numbers to Windows names
                if major == 10:
                    if build >= 22000:
                        base_name = "Microsoft Windows 11"
                    else:
                        base_name = "Microsoft Windows 10"
                    os_version = f"{major}.{minor}.{build}"
                elif major == 6:
                    if minor == 3:
                        base_name = "Microsoft Windows 8.1"
                    elif minor == 2:
                        base_name = "Microsoft Windows 8"
                    elif minor == 1:
                        base_name = "Microsoft Windows 7"
                    elif minor == 0:
                        base_name = "Microsoft Windows Vista"
                    else:
                        base_name = f"Microsoft Windows {major}.{minor}"
                    os_version = f"{major}.{minor}.{build}"
                else:
                    base_name = f"Microsoft Windows {major}.{minor}"
                    os_version = f"{major}.{minor}.{build}"

                # Get Windows edition and append to base name
                if major >= 6:  # Vista and later support editions
                    edition = self.get_windows_edition()
                    if edition:
                        os_name = f"{base_name} {edition}"
                    else:
                        os_name = base_name
                else:
                    os_name = base_name
        except:
            pass

        # Method 2: PowerShell detailed OS info
        if os_name == "Unknown":
            try:
                ps_cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber | ConvertTo-Csv -NoTypeInformation"'
                result = self.safe_subprocess_run(ps_cmd, timeout=15)
                if result and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        data_line = lines[1].strip('"')
                        parts = [p.strip('"') for p in data_line.split('","')]
                        if len(parts) >= 3:
                            os_name = parts[0]  # Caption includes edition
                            version_info = parts[1]
                            build_info = parts[2]
                            if version_info and build_info:
                                os_version = f"{version_info}.{build_info}"
                            elif version_info:
                                os_version = version_info
            except:
                pass

        # Method 3: Registry method for detailed info
        if os_name == "Unknown":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                try:
                    product_name, _ = winreg.QueryValueEx(key, "ProductName")
                    if product_name:
                        os_name = str(product_name)
                except:
                    pass

                try:
                    current_version, _ = winreg.QueryValueEx(key, "CurrentVersion")
                    build_number, _ = winreg.QueryValueEx(key, "CurrentBuildNumber")
                    if current_version and build_number:
                        os_version = f"{current_version}.{build_number}"
                except:
                    pass

                winreg.CloseKey(key)
            except:
                pass

        # Method 4: Use platform module as fallback
        if os_name == "Unknown":
            try:
                import platform
                os_name = platform.system()
                if os_name == "Windows":
                    release = platform.release()
                    version = platform.version()
                    os_name = f"Microsoft Windows {release}"
                    os_version = version
            except:
                pass

        # Method 5: Try systeminfo command
        if os_name == "Unknown" or os_version == "Unknown":
            try:
                result = self.safe_subprocess_run(['systeminfo'], timeout=15)
                if result and result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'OS Name:' in line and os_name == "Unknown":
                            os_name = line.split(':', 1)[1].strip()
                        elif 'OS Version:' in line and os_version == "Unknown":
                            os_version = line.split(':', 1)[1].strip()
                            break
            except:
                pass

        return os_name, os_version

    def get_bios_info(self):
        """Get BIOS version and release date using multiple methods"""
        bios_version = "Unknown"

        # Method 1: PowerShell Get-WmiObject Win32_BIOS
        try:
            ps_cmd = 'powershell -Command "Get-WmiObject -Class Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate | ConvertTo-Csv -NoTypeInformation"'
            result = self.safe_subprocess_run(ps_cmd, timeout=15)
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:  # Header + data line
                    data_line = lines[1].strip('"')
                    parts = [p.strip('"') for p in data_line.split('","')]
                    if len(parts) >= 2:
                        version = parts[0]
                        release_date = parts[1]

                        # Parse PowerShell date format
                        if version and version != '':
                            if release_date and release_date != '' and len(release_date) >= 8:
                                try:
                                    year = release_date[:4]
                                    month = release_date[4:6]
                                    day = release_date[6:8]
                                    formatted_date = f"{day}/{month}/{year}"
                                    bios_version = f"{version} (Release Date: {formatted_date})"
                                except:
                                    bios_version = version
                            else:
                                bios_version = version
        except:
            pass

        # Method 2: PowerShell Get-CimInstance Win32_BIOS (newer method)
        if bios_version == "Unknown":
            try:
                ps_cmd = 'powershell -Command "Get-CimInstance -ClassName Win32_BIOS | Select-Object SMBIOSBIOSVersion, ReleaseDate | ConvertTo-Csv -NoTypeInformation"'
                result = self.safe_subprocess_run(ps_cmd, timeout=15)
                if result and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) >= 2:
                        data_line = lines[1].strip('"')
                        parts = [p.strip('"') for p in data_line.split('","')]
                        if len(parts) >= 1 and parts[0]:
                            bios_version = parts[0]
            except:
                pass

        # Method 3: Registry method
        if bios_version == "Unknown":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
                try:
                    version, _ = winreg.QueryValueEx(key, "BIOSVersion")
                    if version:
                        bios_version = str(version)
                except:
                    try:
                        version, _ = winreg.QueryValueEx(key, "SystemBiosVersion")
                        if version:
                            bios_version = str(version)
                    except:
                        pass
                winreg.CloseKey(key)
            except:
                pass

        # Method 4: WMIC with different timeout and retry
        if bios_version == "Unknown":
            try:
                result = self.safe_subprocess_run(['wmic', 'bios', 'get', 'smbiosbiosversion,releasedate', '/format:list'], timeout=15)
                if result and result.stdout:
                    lines = result.stdout.split('\n')
                    version = None
                    release_date = None

                    for line in lines:
                        line = line.strip()
                        if line.startswith('SMBIOSBIOSVersion=') and '=' in line:
                            version_part = line.split('=', 1)[1].strip()
                            if version_part:
                                version = version_part
                        elif line.startswith('ReleaseDate=') and '=' in line:
                            date_part = line.split('=', 1)[1].strip()
                            if date_part and len(date_part) >= 8:
                                try:
                                    year = date_part[:4]
                                    month = date_part[4:6]
                                    day = date_part[6:8]
                                    release_date = f"{day}/{month}/{year}"
                                except:
                                    release_date = date_part[:8]

                    if version:
                        if release_date:
                            bios_version = f"{version} (Release Date: {release_date})"
                        else:
                            bios_version = version
            except:
                pass

        # Method 5: Alternative WMIC formats
        if bios_version == "Unknown":
            wmic_commands = [
                ['wmic', 'bios', 'get', 'version', '/value'],
                ['wmic', 'bios', 'get', 'smbiosbiosversion'],
                ['wmic', 'bios', 'get', 'name,version'],
                ['wmic', 'computersystem', 'get', 'model,manufacturer']
            ]

            for cmd in wmic_commands:
                try:
                    result = self.safe_subprocess_run(cmd, timeout=10)
                    if result and result.stdout:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            line = line.strip()
                            if 'Version=' in line and '=' in line:
                                version_part = line.split('=', 1)[1].strip()
                                if version_part:
                                    bios_version = version_part
                                    break
                            elif line and line not in ['SMBIOSBIOSVersion', 'Version', 'Name', 'Model', 'Manufacturer']:
                                if len(line) > 3:  # Avoid empty or very short lines
                                    bios_version = line
                                    break
                        if bios_version != "Unknown":
                            break
                except:
                    continue

        # Method 6: msinfo32 as last resort (though it may require GUI)
        if bios_version == "Unknown":
            try:
                result = self.safe_subprocess_run(['msinfo32', '/report', 'C:\\temp_sysinfo.txt'], timeout=20)
                if result:
                    try:
                        with open('C:\\temp_sysinfo.txt', 'r', encoding='utf-16') as f:
                            content = f.read()
                            for line in content.split('\n'):
                                if 'BIOS Version' in line or 'BIOS Version/Date' in line:
                                    parts = line.split('\t')
                                    if len(parts) > 1:
                                        bios_version = parts[1].strip()
                                        break
                        os.remove('C:\\temp_sysinfo.txt')
                    except:
                        pass
            except:
                pass

        return bios_version

    def get_system_type(self):
        """Get system architecture (x64 or x86)"""
        try:
            # Method 1: Check PROCESSOR_ARCHITECTURE environment variable
            arch = os.environ.get('PROCESSOR_ARCHITECTURE', '').upper()
            if arch == 'AMD64':
                return "x64-based PC"
            elif arch == 'X86':
                return "x86-based PC"

            # Method 2: Use platform.machine()
            import platform
            machine = platform.machine().upper()
            if machine in ['AMD64', 'X86_64']:
                return "x64-based PC"
            elif machine in ['I386', 'I686', 'X86']:
                return "x86-based PC"

            # Method 3: Check if running on 64-bit Python
            import struct
            bits = struct.calcsize("P") * 8
            if bits == 64:
                return "x64-based PC"
            else:
                return "x86-based PC"
        except:
            return "Unknown"

    def collect_system_info(self):
        """Thu thập thông tin hệ thống"""
        system_info = {}

        # Basic system info
        system_info['computer_name'] = os.environ.get('COMPUTERNAME', 'Unknown')
        system_info['username'] = os.environ.get('USERNAME', 'Unknown')
        system_info['scan_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get enhanced OS information
        os_name, os_version = self.get_windows_version()
        system_info['os_name'] = os_name
        system_info['os_version'] = os_version

        # Get BIOS information
        system_info['bios_version'] = self.get_bios_info()

        # Get system type
        system_info['system_type'] = self.get_system_type()

        self.scan_results['system'] = system_info
    
    def display_results(self):
        """Hiển thị kết quả"""
        # Update summary
        vpn_count = len(self.scan_results['vpn'])
        chat_count = len(self.scan_results['chat'])
        remote_count = len(self.scan_results['remote'])
        total_count = vpn_count + chat_count + remote_count
        
        # Update count labels (show only numbers - titles are in card headers)
        self.vpn_count_label.config(text=str(vpn_count))
        self.chat_count_label.config(text=str(chat_count))
        self.remote_count_label.config(text=str(remote_count))
        self.total_count_label.config(text=str(total_count))

        # Kaspersky status
        kaspersky_status = "Installed" if self.scan_results['kaspersky'] else "Not Installed"
        kaspersky_color = self.colors['danger'] if self.scan_results['kaspersky'] else self.colors['success']
        self.kaspersky_label.config(text=kaspersky_status, fg=kaspersky_color)
        
        # Update detail tab
        self.detail_text.insert(tk.END, "=" * 50 + "\n")
        self.detail_text.insert(tk.END, "CHI TIẾT QUÉT HỆ THỐNG\n")
        self.detail_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Display VPN Apps
        self.detail_text.insert(tk.END, "[1] VPN APPLICATIONS\n")
        self.detail_text.insert(tk.END, "-" * 30 + "\n")
        if self.scan_results['vpn']:
            for app in self.scan_results['vpn']:
                self.detail_text.insert(tk.END, f"✓ {app['name']}\n")
                self.detail_text.insert(tk.END, f"  Path: {app['path']}\n\n")
        else:
            self.detail_text.insert(tk.END, "Không tìm thấy ứng dụng VPN\n\n")
        
        # Display Chat Apps
        self.detail_text.insert(tk.END, "[2] CHAT APPLICATIONS\n")
        self.detail_text.insert(tk.END, "-" * 30 + "\n")
        if self.scan_results['chat']:
            for app in self.scan_results['chat']:
                self.detail_text.insert(tk.END, f"✓ {app['name']}\n")
                self.detail_text.insert(tk.END, f"  Path: {app['path']}\n\n")
        else:
            self.detail_text.insert(tk.END, "Không tìm thấy ứng dụng Chat\n\n")
        
        # Display Remote Apps
        self.detail_text.insert(tk.END, "[3] REMOTE CONTROL APPLICATIONS\n")
        self.detail_text.insert(tk.END, "-" * 30 + "\n")
        if self.scan_results['remote']:
            for app in self.scan_results['remote']:
                self.detail_text.insert(tk.END, f"✓ {app['name']}\n")
                self.detail_text.insert(tk.END, f"  Path: {app['path']}\n\n")
        else:
            self.detail_text.insert(tk.END, "Không tìm thấy ứng dụng Remote Control\n\n")
        
        # Update security tab
        self.display_security_info()
        
        # Update system tab
        self.display_system_info()
    
    def display_security_info(self):
        """Hiển thị thông tin bảo mật"""
        self.security_text.insert(tk.END, "=" * 50 + "\n")
        self.security_text.insert(tk.END, "KIỂM TRA BẢO MẬT\n")
        self.security_text.insert(tk.END, "=" * 50 + "\n\n")
        
        security = self.scan_results['security']
        
        # File extensions
        ext_status = security.get('file_extensions', 'Unknown')
        ext_icon = "✓" if ext_status == "Visible" else "✗"
        self.security_text.insert(tk.END, f"{ext_icon} File Extensions: {ext_status}\n")
        if ext_status == "Hidden":
            self.security_text.insert(tk.END, "  ⚠️ Khuyến nghị: Bật hiển thị file extension\n")
        self.security_text.insert(tk.END, "\n")
        
        # Guest account
        guest_status = security.get('guest_account', 'Unknown')
        guest_icon = "✓" if guest_status == "Disabled" else "✗"
        self.security_text.insert(tk.END, f"{guest_icon} Guest Account: {guest_status}\n")
        if guest_status == "Enabled":
            self.security_text.insert(tk.END, "  ⚠️ Khuyến nghị: Vô hiệu hóa Guest account\n")
        self.security_text.insert(tk.END, "\n")
        
        # AutoPlay
        autoplay_status = security.get('autoplay', 'Unknown')
        autoplay_icon = "✓" if autoplay_status == "Disabled" else "✗"
        self.security_text.insert(tk.END, f"{autoplay_icon} AutoPlay: {autoplay_status}\n")
        if autoplay_status != "Disabled":
            self.security_text.insert(tk.END, "  ⚠️ Khuyến nghị: Tắt AutoPlay\n")
        self.security_text.insert(tk.END, "\n")
        
        # MAC Address
        mac = security.get('mac_address', 'Unknown')
        self.security_text.insert(tk.END, f"MAC Address: {mac}\n\n")

        # Windows Firewall Status
        self.security_text.insert(tk.END, "=" * 50 + "\n")
        self.security_text.insert(tk.END, "WINDOWS FIREWALL\n")
        self.security_text.insert(tk.END, "=" * 50 + "\n")

        firewall = security.get('firewall_status', {})
        overall_status = firewall.get('overall', 'Unknown')
        firewall_icon = "✓" if 'Enabled' in overall_status else "✗"
        self.security_text.insert(tk.END, f"{firewall_icon} Firewall Status: {overall_status}\n")

        if firewall.get('domain') != 'Unknown':
            domain_icon = "✓" if firewall.get('domain') == 'Enabled' else "✗"
            self.security_text.insert(tk.END, f"  {domain_icon} Domain Profile: {firewall.get('domain', 'Unknown')}\n")

        if firewall.get('private') != 'Unknown':
            private_icon = "✓" if firewall.get('private') == 'Enabled' else "✗"
            self.security_text.insert(tk.END, f"  {private_icon} Private Profile: {firewall.get('private', 'Unknown')}\n")

        if firewall.get('public') != 'Unknown':
            public_icon = "✓" if firewall.get('public') == 'Enabled' else "✗"
            self.security_text.insert(tk.END, f"  {public_icon} Public Profile: {firewall.get('public', 'Unknown')}\n")

        if 'Disabled' in overall_status or 'Partially' in overall_status:
            self.security_text.insert(tk.END, "  ⚠️ Khuyến nghị: Bật Windows Firewall cho tất cả các profile\n")
        self.security_text.insert(tk.END, "\n")

        # Port Blocking Status
        self.security_text.insert(tk.END, "=" * 50 + "\n")
        self.security_text.insert(tk.END, "KIỂM TRA CHẶN CỔNG (PORTS)\n")
        self.security_text.insert(tk.END, "=" * 50 + "\n")

        port_blocking = security.get('port_blocking', {})
        critical_ports = [135, 136, 137, 138, 139, 445]

        for port in critical_ports:
            port_info = port_blocking.get(port, {})
            blocked_status = port_info.get('blocked', 'Unknown')
            details = port_info.get('details', '')

            if blocked_status == 'Yes':
                icon = "✓"
                status_text = "Blocked"
            elif blocked_status == 'Not listening':
                icon = "✓"
                status_text = "Not listening (Safe)"
            elif blocked_status == 'No':
                icon = "✗"
                status_text = "Listening (Vulnerable)"
            else:
                icon = "?"
                status_text = blocked_status

            self.security_text.insert(tk.END, f"{icon} Port {port}: {status_text}\n")
            if details:
                self.security_text.insert(tk.END, f"  → {details}\n")

            if blocked_status == 'No':
                # Check if it's a UDP issue
                tcp_listening = port_info.get('tcp_listening', False)
                udp_listening = port_info.get('udp_listening', False)

                if udp_listening and not tcp_listening:
                    self.security_text.insert(tk.END, f"  ⚠️ Khuyến nghị: Chặn cổng {port} (UDP) để tăng cường bảo mật\n")
                    self.security_text.insert(tk.END, f"  💡 Lưu ý: Cần tạo rule chặn UDP, không chỉ TCP\n")
                elif tcp_listening and udp_listening:
                    self.security_text.insert(tk.END, f"  ⚠️ Khuyến nghị: Chặn cổng {port} (TCP & UDP) để tăng cường bảo mật\n")
                else:
                    self.security_text.insert(tk.END, f"  ⚠️ Khuyến nghị: Chặn cổng {port} để tăng cường bảo mật\n")

        self.security_text.insert(tk.END, "\n")
        self.security_text.insert(tk.END, "💡 Lưu ý: Một số cổng sử dụng cả TCP và UDP. Đảm bảo chặn cả hai protocol.\n")
        self.security_text.insert(tk.END, "\n")

        # Network Interfaces Status
        self.security_text.insert(tk.END, "=" * 50 + "\n")
        self.security_text.insert(tk.END, "NETWORK INTERFACES\n")
        self.security_text.insert(tk.END, "=" * 50 + "\n")

        network_interfaces = security.get('network_interfaces', {})
        summary = network_interfaces.get('summary', 'Unknown')

        total_count = network_interfaces.get('total_count', 0)
        enabled_count = network_interfaces.get('enabled_count', 0)
        disabled_count = network_interfaces.get('disabled_count', 0)
        unused_enabled_count = network_interfaces.get('unused_enabled_count', 0)

        if total_count > 0:
            self.security_text.insert(tk.END, f"Tổng số interfaces: {total_count}\n")
            self.security_text.insert(tk.END, f"  • Enabled: {enabled_count}\n")
            self.security_text.insert(tk.END, f"  • Disabled: {disabled_count}\n")
            self.security_text.insert(tk.END, f"  • Unused but enabled: {unused_enabled_count}\n\n")

            summary_icon = "✓" if unused_enabled_count == 0 else "✗"
            self.security_text.insert(tk.END, f"{summary_icon} Status: {summary}\n")

            if unused_enabled_count > 0:
                self.security_text.insert(tk.END, "  ⚠️ Khuyến nghị: Tắt các network interface không sử dụng\n\n")
                self.security_text.insert(tk.END, "  Unused Enabled Interfaces:\n")
                for interface in network_interfaces.get('unused_enabled', []):
                    self.security_text.insert(tk.END, f"    • {interface.get('name', 'Unknown')} - {interface.get('description', 'Unknown')}\n")

            # List all interfaces
            self.security_text.insert(tk.END, "\n  Chi tiết tất cả interfaces:\n")
            for interface in network_interfaces.get('all_interfaces', []):
                name = interface.get('name', 'Unknown')
                status = interface.get('status', 'Unknown')
                description = interface.get('description', 'Unknown')
                status_icon = "✓" if status == 'Up' else "○"
                self.security_text.insert(tk.END, f"    {status_icon} {name} ({status})\n")
                self.security_text.insert(tk.END, f"      {description}\n")
        else:
            self.security_text.insert(tk.END, f"Status: {summary}\n")

        self.security_text.insert(tk.END, "\n")

    def display_system_info(self):
        """Hiển thị thông tin hệ thống"""
        self.system_text.insert(tk.END, "=========================================================\n")
        self.system_text.insert(tk.END, "SYSTEM INFORMATION\n")
        self.system_text.insert(tk.END, "=========================================================\n")

        system = self.scan_results['system']
        self.system_text.insert(tk.END, f"Computer Name: {system.get('computer_name', 'Unknown')}\n")
        self.system_text.insert(tk.END, f"Username: {system.get('username', 'Unknown')}\n")
        self.system_text.insert(tk.END, f"OS Name: {system.get('os_name', 'Unknown')}\n")
        self.system_text.insert(tk.END, f"OS Version: {system.get('os_version', 'Unknown')}\n")
        self.system_text.insert(tk.END, f"BIOS Version: {system.get('bios_version', 'Unknown')}\n")
        self.system_text.insert(tk.END, f"System Type: {system.get('system_type', 'Unknown')}\n")
        self.system_text.insert(tk.END, f"Scan Time: {system.get('scan_time', 'Unknown')}\n")
        self.system_text.insert(tk.END, "=======================================================\n")
    
    def scan_complete(self):
        """Hoàn thành quét"""
        print("[DEBUG] scan_complete() called")  # Debug output
        self.progress.stop()
        self.scan_button.config(state='normal')
        self.export_txt_button.config(state='normal')
        self.export_csv_button.config(state='normal')
        if PDF_AVAILABLE:
            print(f"[DEBUG] PDF_AVAILABLE is True, enabling PDF button")  # Debug output
            self.export_pdf_button.config(state='normal')
            print(f"[DEBUG] PDF button state after enabling: {self.export_pdf_button.cget('state')}")  # Debug output
        else:
            print(f"[DEBUG] PDF_AVAILABLE is False, PDF button remains disabled")  # Debug output
        self.status_label.config(text="✓ Scan completed successfully!", fg=self.colors['success'])
    
    def export_txt(self):
        """Xuất báo cáo TXT"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"scan_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("SYSTEM SECURITY SCAN REPORT\n")
                    f.write("=" * 60 + "\n\n")
                    
                    system = self.scan_results['system']
                    f.write("SYSTEM INFORMATION\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Computer Name: {system.get('computer_name', 'Unknown')}\n")
                    f.write(f"Username: {system.get('username', 'Unknown')}\n")
                    f.write(f"OS Name: {system.get('os_name', 'Unknown')}\n")
                    f.write(f"OS Version: {system.get('os_version', 'Unknown')}\n")
                    f.write(f"BIOS Version: {system.get('bios_version', 'Unknown')}\n")
                    f.write(f"System Type: {system.get('system_type', 'Unknown')}\n")
                    f.write(f"Scan Time: {system.get('scan_time', 'Unknown')}\n\n")
                    
                    f.write("SUMMARY\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"VPN Applications: {len(self.scan_results['vpn'])}\n")
                    f.write(f"Chat Applications: {len(self.scan_results['chat'])}\n")
                    f.write(f"Remote Control Apps: {len(self.scan_results['remote'])}\n")
                    f.write(f"Kaspersky: {'INSTALLED' if self.scan_results['kaspersky'] else 'NOT INSTALLED'}\n\n")

                    # Security Information
                    security = self.scan_results['security']
                    f.write("SECURITY INFORMATION\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"File Extensions: {security.get('file_extensions', 'Unknown')}\n")
                    f.write(f"Guest Account: {security.get('guest_account', 'Unknown')}\n")
                    f.write(f"AutoPlay: {security.get('autoplay', 'Unknown')}\n")
                    f.write(f"MAC Address: {security.get('mac_address', 'Unknown')}\n\n")

                    # Windows Firewall
                    f.write("WINDOWS FIREWALL\n")
                    f.write("-" * 40 + "\n")
                    firewall = security.get('firewall_status', {})
                    f.write(f"Overall Status: {firewall.get('overall', 'Unknown')}\n")
                    f.write(f"Domain Profile: {firewall.get('domain', 'Unknown')}\n")
                    f.write(f"Private Profile: {firewall.get('private', 'Unknown')}\n")
                    f.write(f"Public Profile: {firewall.get('public', 'Unknown')}\n\n")

                    # Port Blocking
                    f.write("PORT BLOCKING STATUS\n")
                    f.write("-" * 40 + "\n")
                    port_blocking = security.get('port_blocking', {})
                    for port in [135, 136, 137, 138, 139, 445]:
                        port_info = port_blocking.get(port, {})
                        blocked = port_info.get('blocked', 'Unknown')
                        details = port_info.get('details', '')
                        f.write(f"Port {port}: {blocked}")
                        if details:
                            f.write(f" ({details})")
                        f.write("\n")
                    f.write("\n")

                    # Network Interfaces
                    f.write("NETWORK INTERFACES\n")
                    f.write("-" * 40 + "\n")
                    network_interfaces = security.get('network_interfaces', {})
                    f.write(f"Total Interfaces: {network_interfaces.get('total_count', 0)}\n")
                    f.write(f"Enabled: {network_interfaces.get('enabled_count', 0)}\n")
                    f.write(f"Disabled: {network_interfaces.get('disabled_count', 0)}\n")
                    f.write(f"Unused but Enabled: {network_interfaces.get('unused_enabled_count', 0)}\n")
                    f.write(f"Summary: {network_interfaces.get('summary', 'Unknown')}\n\n")

                    if network_interfaces.get('all_interfaces'):
                        f.write("Interface Details:\n")
                        for interface in network_interfaces.get('all_interfaces', []):
                            f.write(f"  - {interface.get('name', 'Unknown')} ({interface.get('status', 'Unknown')})\n")
                            f.write(f"    {interface.get('description', 'Unknown')}\n")
                        f.write("\n")

                    # Details
                    for category, title in [('vpn', 'VPN APPLICATIONS'), 
                                           ('chat', 'CHAT APPLICATIONS'),
                                           ('remote', 'REMOTE CONTROL APPLICATIONS')]:
                        f.write(f"{title}\n")
                        f.write("-" * 40 + "\n")
                        if self.scan_results[category]:
                            for app in self.scan_results[category]:
                                f.write(f"[FOUND] {app['name']}\n")
                                f.write(f"  Path: {app['path']}\n\n")
                        else:
                            f.write(f"No {category} applications found\n\n")
                
                messagebox.showinfo("Success", f"Báo cáo đã được xuất ra:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khi xuất báo cáo TXT:\n{str(e)}")
    
    def export_csv(self):
        """Xuất báo cáo CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"scan_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Category", "Application", "Type", "Path", "Status"])

                    # Add system information
                    system = self.scan_results['system']
                    writer.writerow([
                        "System",
                        "Computer Name",
                        "System Info",
                        "Environment",
                        system.get('computer_name', 'Unknown')
                    ])
                    writer.writerow([
                        "System",
                        "Username",
                        "System Info",
                        "Environment",
                        system.get('username', 'Unknown')
                    ])
                    writer.writerow([
                        "System",
                        "OS Name",
                        "System Info",
                        "Registry",
                        system.get('os_name', 'Unknown')
                    ])
                    writer.writerow([
                        "System",
                        "OS Version",
                        "System Info",
                        "Registry",
                        system.get('os_version', 'Unknown')
                    ])
                    writer.writerow([
                        "System",
                        "BIOS Version",
                        "System Info",
                        "BIOS",
                        system.get('bios_version', 'Unknown')
                    ])
                    writer.writerow([
                        "System",
                        "System Type",
                        "System Info",
                        "Registry",
                        system.get('system_type', 'Unknown')
                    ])
                    writer.writerow([
                        "System",
                        "Scan Time",
                        "System Info",
                        "Generated",
                        system.get('scan_time', 'Unknown')
                    ])
                    
                    for category in ['vpn', 'chat', 'remote']:
                        for app in self.scan_results[category]:
                            writer.writerow([
                                category.upper(),
                                app['name'],
                                app['type'],
                                app['path'],
                                "Installed"
                            ])
                    
                    writer.writerow([
                        "Security",
                        "Kaspersky",
                        "Antivirus",
                        "System",
                        "Installed" if self.scan_results['kaspersky'] else "Not Installed"
                    ])

                    # Add security configuration information
                    security = self.scan_results['security']
                    writer.writerow([
                        "Security",
                        "File Extensions",
                        "System Setting",
                        "Registry",
                        security.get('file_extensions', 'Unknown')
                    ])
                    writer.writerow([
                        "Security",
                        "Guest Account",
                        "User Account",
                        "System",
                        security.get('guest_account', 'Unknown')
                    ])
                    writer.writerow([
                        "Security",
                        "AutoPlay",
                        "System Setting",
                        "Registry",
                        security.get('autoplay', 'Unknown')
                    ])
                    writer.writerow([
                        "Security",
                        "MAC Address",
                        "Network",
                        "System",
                        security.get('mac_address', 'Unknown')
                    ])

                    # Windows Firewall
                    firewall = security.get('firewall_status', {})
                    writer.writerow([
                        "Security",
                        "Windows Firewall - Overall",
                        "Firewall",
                        "System",
                        firewall.get('overall', 'Unknown')
                    ])
                    writer.writerow([
                        "Security",
                        "Windows Firewall - Domain Profile",
                        "Firewall",
                        "System",
                        firewall.get('domain', 'Unknown')
                    ])
                    writer.writerow([
                        "Security",
                        "Windows Firewall - Private Profile",
                        "Firewall",
                        "System",
                        firewall.get('private', 'Unknown')
                    ])
                    writer.writerow([
                        "Security",
                        "Windows Firewall - Public Profile",
                        "Firewall",
                        "System",
                        firewall.get('public', 'Unknown')
                    ])

                    # Port Blocking
                    port_blocking = security.get('port_blocking', {})
                    for port in [135, 136, 137, 138, 139, 445]:
                        port_info = port_blocking.get(port, {})
                        blocked = port_info.get('blocked', 'Unknown')
                        details = port_info.get('details', '')
                        status = f"{blocked} - {details}" if details else blocked
                        writer.writerow([
                            "Security",
                            f"Port {port}",
                            "Port Blocking",
                            "Firewall/Network",
                            status
                        ])

                    # Network Interfaces
                    network_interfaces = security.get('network_interfaces', {})
                    writer.writerow([
                        "Security",
                        "Network Interfaces - Total",
                        "Network",
                        "System",
                        str(network_interfaces.get('total_count', 0))
                    ])
                    writer.writerow([
                        "Security",
                        "Network Interfaces - Enabled",
                        "Network",
                        "System",
                        str(network_interfaces.get('enabled_count', 0))
                    ])
                    writer.writerow([
                        "Security",
                        "Network Interfaces - Disabled",
                        "Network",
                        "System",
                        str(network_interfaces.get('disabled_count', 0))
                    ])
                    writer.writerow([
                        "Security",
                        "Network Interfaces - Unused but Enabled",
                        "Network",
                        "System",
                        str(network_interfaces.get('unused_enabled_count', 0))
                    ])
                    writer.writerow([
                        "Security",
                        "Network Interfaces - Summary",
                        "Network",
                        "System",
                        network_interfaces.get('summary', 'Unknown')
                    ])

                    # Individual network interfaces
                    for interface in network_interfaces.get('all_interfaces', []):
                        writer.writerow([
                            "Network Interface",
                            interface.get('name', 'Unknown'),
                            "Adapter",
                            interface.get('description', 'Unknown'),
                            interface.get('status', 'Unknown')
                        ])

                messagebox.showinfo("Success", f"Báo cáo CSV đã được xuất ra:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi khi xuất báo cáo CSV:\n{str(e)}")

    def export_pdf(self):
        """Export scan results to PDF report with charts and formatting"""
        print("[DEBUG] export_pdf() called")  # Debug output

        # Check if PDF functionality is available
        if not PDF_AVAILABLE:
            print("[ERROR] PDF_AVAILABLE is False")  # Debug output
            messagebox.showerror("Error",
                "PDF export not available.\n\n"
                "Please install required libraries:\n"
                "pip install reportlab pillow")
            return

        print("[DEBUG] PDF_AVAILABLE is True, proceeding...")  # Debug output

        # Check if scan results exist
        if not hasattr(self, 'scan_results') or not self.scan_results:
            print("[ERROR] No scan results available")  # Debug output
            messagebox.showerror("Error",
                "No scan results available.\n\n"
                "Please perform a system scan first.")
            return

        print(f"[DEBUG] Scan results available: {len(self.scan_results)} keys")  # Debug output

        try:
            # Generate default filename with timestamp
            default_filename = f"SystemScan_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            print(f"[DEBUG] Default filename: {default_filename}")  # Debug output

            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Export PDF Report"
            )

            print(f"[DEBUG] Selected filename: {filename}")  # Debug output

            if filename:
                print("[DEBUG] User selected a file, generating PDF...")  # Debug output

                # Show progress
                self.status_label.config(text="Generating PDF report...", fg=self.colors['primary'])
                self.root.update()

                # Create PDF reporter and generate report
                print("[DEBUG] Creating PDFReporter instance...")  # Debug output
                pdf = PDFReporter(self.scan_results, filename)

                print("[DEBUG] Calling pdf.generate()...")  # Debug output
                pdf.generate()

                print(f"[DEBUG] PDF generated successfully: {filename}")  # Debug output

                # Success message
                self.status_label.config(text="✓ PDF report exported successfully!", fg=self.colors['success'])
                messagebox.showinfo("Success",
                    f"PDF report exported successfully!\n\n"
                    f"Location:\n{filename}")

                # Ask if user wants to open the PDF
                if messagebox.askyesno("Open PDF?",
                    "Would you like to open the PDF report now?"):
                    try:
                        print(f"[DEBUG] Opening PDF with os.startfile: {filename}")  # Debug output
                        os.startfile(filename)
                    except Exception as open_error:
                        print(f"[ERROR] Failed to open PDF: {open_error}")  # Debug output
                        messagebox.showwarning("Warning",
                            f"Could not open PDF automatically:\n{str(open_error)}\n\n"
                            f"Please open manually:\n{filename}")
            else:
                print("[DEBUG] User cancelled file dialog")  # Debug output

        except Exception as e:
            print(f"[ERROR] Exception in export_pdf: {type(e).__name__}: {str(e)}")  # Debug output
            import traceback
            traceback.print_exc()  # Print full traceback to console
            messagebox.showerror("Error", f"Failed to export PDF report:\n\n{str(e)}")
            self.status_label.config(text="✗ PDF export failed", fg=self.colors['danger'])


def main():
    """Hàm main để chạy ứng dụng"""
    try:
        root = tk.Tk()
        
        # Try to set icon if exists
        try:
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                base_path = sys._MEIPASS
            else:
                # Running as script
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, 'scanner.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except:
            pass
        
        app = SystemScannerGUI(root)
        root.mainloop()
        
    except Exception as e:
        # Fallback error handling
        import traceback
        error_msg = f"Lỗi nghiêm trọng:\n{str(e)}\n\nChi tiết:\n{traceback.format_exc()}"
        
        # Try to show error in GUI
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", error_msg)
        except:
            # If GUI fails, print to console
            print(error_msg)
            input("Press Enter to exit...")
        
        sys.exit(1)


if __name__ == "__main__":
    main()