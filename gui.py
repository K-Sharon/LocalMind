import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from rag import ask_ollama, process_pdf, ask_from_pdf
import threading

class LocalMindGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LocalMind - Offline AI Assistant")
        self.root.geometry("800x700")
        self.root.configure(bg="#f8f9fa")
        self.root.minsize(700, 600)

        # Modern color scheme
        self.colors = {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f8f9fa",
            "bg_header": "#202123",
            "bg_input": "#ffffff",
            "bg_button_primary": "#10a37f",
            "bg_button_secondary": "#40414f",
            "bg_button_pdf": "#1a56db",
            "bg_button_clear": "#dc2626",
            "text_primary": "#343541",
            "text_secondary": "#6e6e80",
            "text_white": "#ffffff",
            "border_light": "#e5e5e5",
            "user_message": "#10a37f",
            "ai_message": "#1a56db",
            "system_message": "#8b5cf6"
        }

        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Header with modern styling
        header = tk.Frame(
            root, 
            bg=self.colors["bg_header"],
            height=60,
            relief="flat"
        )
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(
            header, 
            text="🧠 LocalMind", 
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg_header"],
            fg=self.colors["text_white"]
        )
        title_label.grid(row=0, column=0, pady=15)

        subtitle_label = tk.Label(
            header,
            text="Offline AI Assistant",
            font=("Segoe UI", 11),
            bg=self.colors["bg_header"],
            fg="#d1d5db"
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 15))

        # Main content area
        main_frame = tk.Frame(root, bg=self.colors["bg_secondary"])
        main_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Chat display with modern styling
        chat_container = tk.Frame(main_frame, bg=self.colors["bg_secondary"])
        chat_container.grid(row=0, column=0, sticky="nsew", padx=16, pady=(16, 8))
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_columnconfigure(0, weight=1)

        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            state='disabled',
            wrap=tk.WORD,
            bg=self.colors["bg_primary"],
            fg=self.colors["text_primary"],
            font=("Segoe UI", 11),
            insertbackground=self.colors["text_primary"],
            relief="flat",
            padx=20,
            pady=20,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors["border_light"],
            highlightcolor=self.colors["border_light"]
        )
        self.chat_display.pack(fill='both', expand=True)

        # Configure tags for modern message styling
        self.chat_display.tag_config("user", 
                                   foreground=self.colors["user_message"], 
                                   font=("Segoe UI", 11, "bold"),
                                   lmargin1=20,
                                   lmargin2=20)
        
        self.chat_display.tag_config("ai", 
                                   foreground=self.colors["ai_message"], 
                                   font=("Segoe UI", 11, "bold"),
                                   lmargin1=20,
                                   lmargin2=20)
        
        self.chat_display.tag_config("system", 
                                   foreground=self.colors["system_message"], 
                                   font=("Segoe UI", 10, "italic"),
                                   lmargin1=20,
                                   lmargin2=20)
        
        self.chat_display.tag_config("error", 
                                   foreground=self.colors["bg_button_clear"], 
                                   font=("Segoe UI", 10, "bold"),
                                   lmargin1=20,
                                   lmargin2=20)

        # Input area with modern styling
        input_container = tk.Frame(main_frame, bg=self.colors["bg_secondary"])
        input_container.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 16))

        # Input frame with border
        input_frame = tk.Frame(
            input_container,
            bg=self.colors["border_light"],
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors["border_light"]
        )
        input_frame.pack(fill='x', pady=0)
        input_frame.grid_columnconfigure(0, weight=1)

        self.user_input = tk.Entry(
            input_frame,
            font=("Segoe UI", 12),
            bg=self.colors["bg_input"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.user_input.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.focus()

        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg=self.colors["bg_button_primary"],
            fg=self.colors["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
            padx=24,
            pady=8,
            cursor="hand2",
            activebackground="#0d8c6d",
            activeforeground=self.colors["text_white"]
        )
        send_btn.grid(row=0, column=1, padx=8, pady=8)

        # Control panel with modern buttons
        control_frame = tk.Frame(main_frame, bg=self.colors["bg_secondary"])
        control_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        # Left side buttons
        left_controls = tk.Frame(control_frame, bg=self.colors["bg_secondary"])
        left_controls.pack(side='left')

        self.pdf_btn = tk.Button(
            left_controls,
            text="📄 Load PDF",
            command=self.load_pdf,
            bg=self.colors["bg_button_pdf"],
            fg=self.colors["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=8,
            cursor="hand2",
            activebackground="#1e40af"
        )
        self.pdf_btn.pack(side='left', padx=(0, 8))

        # Mode indicator
        mode_frame = tk.Frame(control_frame, bg=self.colors["bg_secondary"])
        mode_frame.pack(side='left', padx=20)

        self.mode_label = tk.Label(
            mode_frame,
            text="💬 Chat Mode",
            bg=self.colors["bg_secondary"],
            fg=self.colors["user_message"],
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=6,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.colors["border_light"]
        )
        self.mode_label.pack(side='left')

        # Right side buttons
        right_controls = tk.Frame(control_frame, bg=self.colors["bg_secondary"])
        right_controls.pack(side='right')

        clear_btn = tk.Button(
            right_controls,
            text="Clear Chat",
            command=self.clear_chat,
            bg=self.colors["bg_button_clear"],
            fg=self.colors["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=8,
            cursor="hand2",
            activebackground="#b91c1c"
        )
        clear_btn.pack(side='right', padx=(8, 0))

        # Status bar
        status_frame = tk.Frame(root, bg=self.colors["bg_secondary"], height=24)
        status_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        status_frame.grid_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=self.colors["bg_secondary"],
            fg=self.colors["text_secondary"],
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.status_label.pack(side='left', padx=16, pady=4)

        # State
        self.pdf_loaded = False
        self.mode = "chat"
        self.is_processing = False
        
        # Welcome message
        self.append_message("System", "Welcome to LocalMind! Type your message and press Enter to start chatting.", "system")
        self.append_message("System", "You can load a PDF document to ask questions about its content.", "system")

    def append_message(self, sender, message, tag=""):
        """Append message to chat display with optional tag"""
        self.chat_display.configure(state='normal')
        
        if sender == "You":
            self.chat_display.insert(tk.END, f"{sender}: ", "user")
        elif sender == "AI":
            self.chat_display.insert(tk.END, f"{sender}: ", "ai")
        elif sender == "System":
            self.chat_display.insert(tk.END, f"{sender}: ", "system")
        else:
            self.chat_display.insert(tk.END, f"{sender}: ")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def append_streaming_text(self, text):
        """Append text for streaming output"""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, text)
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)

    def send_message(self, event=None):
        """Send user message and get AI response"""
        if self.is_processing:
            return
        
        msg = self.user_input.get().strip()
        if not msg:
            return
        
        self.append_message("You", msg)
        self.user_input.delete(0, tk.END)
        self.is_processing = True
        self.user_input.config(state='disabled')
        self.update_status("Processing...")
        
        # Start AI response
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, "AI: ", "ai")
        self.chat_display.configure(state='disabled')
        
        # Process in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.process_query, args=(msg,))
        thread.daemon = True
        thread.start()

    def process_query(self, msg):
        """Process query in background thread"""
        def callback(text):
            """Callback for streaming output"""
            self.root.after(0, lambda t=text: self.append_streaming_text(t))
        
        try:
            if self.mode == "chat":
                response = ask_ollama(msg, model="phi3", callback=callback)
            elif self.mode == "pdf":
                if not self.pdf_loaded:
                    self.root.after(0, lambda: self.append_streaming_text("⚠️ No PDF loaded. Please load a PDF first."))
                else:
                    response = ask_from_pdf(msg, callback=callback)
            
            # Add spacing after response
            self.root.after(0, lambda: self.append_streaming_text("\n\n"))
        
        except Exception as e:
            import traceback
            error_msg = f"❌ Error: {str(e)}\n"
            traceback.print_exc()
            self.root.after(0, lambda: self.append_streaming_text(error_msg + "\n"))
        
        finally:
            self.root.after(0, lambda: self.enable_input())

    def enable_input(self):
        """Re-enable input after processing"""
        self.is_processing = False
        self.user_input.config(state='normal')
        self.user_input.focus()
        self.update_status("Ready")

    def load_pdf(self):
        """Load PDF file"""
        if self.is_processing:
            messagebox.showwarning("Processing", "Please wait for current operation to complete.")
            return
        
        pdf_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if pdf_path:
            self.is_processing = True
            self.user_input.config(state='disabled')
            self.pdf_btn.config(state='disabled')
            self.update_status("Loading PDF...")
            self.append_message("System", f"Loading PDF: {pdf_path.split('/')[-1]}", "system")
            
            # Process in background thread
            thread = threading.Thread(target=self.process_pdf_thread, args=(pdf_path,))
            thread.daemon = True
            thread.start()

    def process_pdf_thread(self, pdf_path):
        """Process PDF in background thread"""
        try:
            success = process_pdf(pdf_path)
            
            if success:
                self.pdf_loaded = True
                self.mode = "pdf"
                self.root.after(0, lambda: self.mode_label.config(
                    text="📄 PDF Mode", 
                    fg=self.colors["bg_button_pdf"]
                ))
                self.root.after(0, lambda: self.append_message(
                    "System", 
                    "✅ PDF loaded successfully! You can now ask questions about the document.", 
                    "system"
                ))
            else:
                self.root.after(0, lambda: self.append_message(
                    "System", 
                    "❌ Failed to load PDF. Please try again.", 
                    "error"
                ))
        
        except Exception as e:
            self.root.after(0, lambda: self.append_message(
                "System", 
                f"❌ Error loading PDF: {str(e)}", 
                "error"
            ))
        
        finally:
            self.root.after(0, lambda: self.user_input.config(state='normal'))
            self.root.after(0, lambda: self.pdf_btn.config(state='normal'))
            self.root.after(0, lambda: setattr(self, 'is_processing', False))
            self.root.after(0, lambda: self.user_input.focus())
            self.root.after(0, lambda: self.update_status("Ready"))

    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.configure(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.configure(state='disabled')
        self.append_message("System", "Chat cleared. Start a new conversation.", "system")

    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)

def launch_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    gui = LocalMindGUI(root)
    root.mainloop()