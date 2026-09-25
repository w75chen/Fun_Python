import tkinter as tk
from tkinter import ttk
from datetime import datetime


class SystemManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Manager")
        self.root.geometry("560x430")
        self.root.resizable(False, False)

        # System list shared by the dropdown and the credentials checklist
        self.systems = ["System A", "System B", "System C"]  # placeholder list, update later

        # Main container
        main_frame = ttk.Frame(root, padding=15)
        main_frame.pack(fill="both", expand=True)

        # ---------- Top row: input panel + saved credentials panel ----------
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", side="top")

        # ---------- Left side: inputs ----------
        left_frame = ttk.LabelFrame(top_frame, text="Enter Credentials", padding=10)
        left_frame.pack(side="left", anchor="n")

        ttk.Label(left_frame, text="System:").grid(row=0, column=0, sticky="w", pady=5)
        self.system_var = tk.StringVar()
        self.system_dropdown = ttk.Combobox(
            left_frame,
            textvariable=self.system_var,
            values=self.systems,
            state="readonly",
            width=17,
        )
        self.system_dropdown.grid(row=0, column=1, pady=5, sticky="ew")
        self.system_dropdown.current(0)

        ttk.Label(left_frame, text="User Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(left_frame, textvariable=self.username_var)
        self.username_entry.grid(row=1, column=1, pady=5, sticky="ew")

        ttk.Label(left_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(left_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, sticky="ew")

        left_frame.columnconfigure(1, weight=1)

        # ---------- Buttons (below inputs) ----------
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        self.add_button = ttk.Button(button_frame, text="Add", command=self.on_add)
        self.add_button.grid(row=0, column=0, padx=10)

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.on_delete)
        self.delete_button.grid(row=0, column=1, padx=10)

        # ---------- Right side: credentials checklist panel ----------
        right_frame = ttk.LabelFrame(top_frame, text="Saved Credentials", padding=10)
        right_frame.pack(side="right", anchor="n")

        self.system_check_vars = {}
        for i, system in enumerate(self.systems):
            var = tk.BooleanVar(value=False)
            self.system_check_vars[system] = var
            chk = ttk.Checkbutton(right_frame, text=system, variable=var, state="disabled")
            chk.grid(row=i, column=0, sticky="w", pady=3)

        # ---------- Launch & Login panel ----------
        launch_frame = ttk.LabelFrame(main_frame, text="Launch & Login", padding=10)

        self.launch_system_var = tk.StringVar()
        self.launch_dropdown = ttk.Combobox(
            launch_frame,
            textvariable=self.launch_system_var,
            values=self.systems,
            state="readonly",
            width=17,
        )
        self.launch_dropdown.pack(side="left")
        self.launch_dropdown.current(0)

        self.go_button = ttk.Button(launch_frame, text="Go", command=self.on_go)
        self.go_button.pack(side="left", padx=(10, 0))

        # Lock the panel's width to match Enter Credentials exactly
        self.root.update_idletasks()
        launch_frame.config(width=left_frame.winfo_reqwidth(), height=launch_frame.winfo_reqheight())
        launch_frame.pack_propagate(False)
        launch_frame.pack(anchor="w", pady=(15, 0))

        # ---------- Message panel ----------
        ttk.Label(main_frame, text="System Messages:").pack(anchor="w", pady=(15, 0))

        message_frame = ttk.Frame(main_frame)
        message_frame.pack(fill="both", expand=True, pady=(5, 15))

        self.message_text = tk.Text(message_frame, height=6, width=70, state="disabled", wrap="word")
        self.message_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(message_frame, command=self.message_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.message_text.config(yscrollcommand=scrollbar.set)

    def log_message(self, message):
        """Append a timestamped message to the system messages panel."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_text.config(state="normal")
        self.message_text.insert("end", f"[{timestamp}] {message}\n")
        self.message_text.see("end")
        self.message_text.config(state="disabled")

    def on_add(self):
        # Placeholder command - replace with real logic later
        system = self.system_var.get()
        username = self.username_var.get()
        self.log_message(f"Add clicked - System: {system}, User: {username}")

        # Once credentials are actually saved, mark the system as configured
        if system in self.system_check_vars:
            self.system_check_vars[system].set(True)

    def on_delete(self):
        # Placeholder command - replace with real logic later
        system = self.system_var.get()
        username = self.username_var.get()
        self.log_message(f"Delete clicked - System: {system}, User: {username}")

        # Once credentials are actually removed, uncheck the system
        if system in self.system_check_vars:
            self.system_check_vars[system].set(False)

    def on_go(self):
        # Placeholder command - replace with real launch/login logic later
        system = self.launch_system_var.get()
        self.log_message(f"Go clicked - Launching/logging into: {system}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemManagerApp(root)
    root.mainloop()