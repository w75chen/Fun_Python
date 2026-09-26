import tkinter as tk
from tkinter import ttk
from datetime import datetime


class SystemManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Manager")
        self.root.geometry("650x720")
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

        # ---------- FIP Test panel ----------
        fip_frame = ttk.LabelFrame(main_frame, text="FIP Test", padding=10)

        self.fip_vars = {}
        checkbox_frame = ttk.Frame(fip_frame)
        checkbox_frame.pack(side="left")
        for label in ("H3", "H5", "H8"):
            var = tk.BooleanVar(value=False)
            self.fip_vars[label] = var
            chk = ttk.Checkbutton(checkbox_frame, text=label, variable=var)
            chk.pack(side="left", padx=(0, 10))

        self.start_offering_button = ttk.Button(
            fip_frame, text="Start FIP Offering feed", command=self.on_start_offering_feed, width=22
        )
        self.start_offering_button.pack(side="left", padx=(20, 0))

        fip_frame.pack(fill="x", pady=(15, 0))

        # ---------- FIS Prod - Resend Trade panel ----------
        resend_frame = ttk.LabelFrame(main_frame, text="FIS Prod - Resend Trade", padding=10)

        ttk.Label(resend_frame, text="Short form trade ID:").pack(side="left")
        self.trade_id_var = tk.StringVar()
        self.trade_id_entry = ttk.Entry(resend_frame, textvariable=self.trade_id_var, width=12)
        self.trade_id_entry.pack(side="left", padx=(10, 0))

        self.resend_button = ttk.Button(
            resend_frame, text="Resend to Venom", command=self.on_resend_to_venom, width=22
        )
        self.resend_button.pack(side="left", padx=(20, 0))

        resend_frame.pack(fill="x", pady=(15, 0))

        # ---------- FIS Prod - Add BBG Trader Mapping panel ----------
        bbg_frame = ttk.LabelFrame(main_frame, text="FIS Prod - Add BBG Trader Mapping", padding=10)

        ttk.Label(bbg_frame, text="BBG ID:").pack(side="left")
        self.bbg_id_var = tk.StringVar()
        self.bbg_id_entry = ttk.Entry(bbg_frame, textvariable=self.bbg_id_var, width=12)
        self.bbg_id_entry.pack(side="left", padx=(5, 15))

        ttk.Label(bbg_frame, text="FIS ID:").pack(side="left")
        self.fis_id_var = tk.StringVar()
        self.fis_id_entry = ttk.Entry(bbg_frame, textvariable=self.fis_id_var, width=12)
        self.fis_id_entry.pack(side="left", padx=(5, 15))

        ttk.Label(bbg_frame, text="Trader Name:").pack(side="left")
        self.trader_name_var = tk.StringVar()
        self.trader_name_entry = ttk.Entry(bbg_frame, textvariable=self.trader_name_var, width=16)
        self.trader_name_entry.pack(side="left", padx=(5, 15))

        self.bbg_add_button = ttk.Button(bbg_frame, text="Add", command=self.on_add_bbg_mapping)
        self.bbg_add_button.pack(side="left", padx=(10, 0))

        bbg_frame.pack(fill="x", pady=(15, 0))

        # ---------- TIBCO Command Center panel ----------
        tibco_frame = ttk.LabelFrame(main_frame, text="TIBCO Command Center", padding=10)

        ttk.Label(tibco_frame, text="Mailbox:").pack(side="left")
        self.tibco_mailbox_var = tk.StringVar()
        self.tibco_mailbox_entry = ttk.Entry(tibco_frame, textvariable=self.tibco_mailbox_var, width=14)
        self.tibco_mailbox_entry.pack(side="left", padx=(5, 15))

        ttk.Label(tibco_frame, text="From:").pack(side="left")
        self.tibco_from_date_var = tk.StringVar()
        self.tibco_from_date_entry = ttk.Entry(tibco_frame, textvariable=self.tibco_from_date_var, width=13)
        self.tibco_from_date_entry.pack(side="left", padx=(5, 15))
        self._add_placeholder(self.tibco_from_date_entry, "mm/dd/yyyy")

        ttk.Label(tibco_frame, text="To:").pack(side="left")
        self.tibco_to_date_var = tk.StringVar()
        self.tibco_to_date_entry = ttk.Entry(tibco_frame, textvariable=self.tibco_to_date_var, width=13)
        self.tibco_to_date_entry.pack(side="left", padx=(5, 15))
        self._add_placeholder(self.tibco_to_date_entry, "mm/dd/yyyy")

        self.find_audit_log_button = ttk.Button(
            tibco_frame, text="Find Audit Log", command=self.on_find_audit_log, width=24
        )
        self.find_audit_log_button.pack(side="left", padx=(10, 0))

        tibco_frame.pack(fill="x", pady=(15, 0))

        # ---------- Message panel ----------
        ttk.Label(main_frame, text="System Messages:").pack(anchor="w", pady=(15, 0))

        message_frame = ttk.Frame(main_frame)
        message_frame.pack(fill="both", expand=True, pady=(5, 15))

        self.message_text = tk.Text(message_frame, height=6, width=70, state="disabled", wrap="word")
        self.message_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(message_frame, command=self.message_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.message_text.config(yscrollcommand=scrollbar.set)

    def _add_placeholder(self, entry, placeholder, color="grey"):
        """Show grey placeholder text in an Entry box until the user types something."""
        normal_color = "black"

        def on_focus_in(event):
            if entry.get() == placeholder and str(entry.cget("foreground")) == color:
                entry.delete(0, "end")
                entry.config(foreground=normal_color)

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground=color)

        entry.insert(0, placeholder)
        entry.config(foreground=color)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    def get_entry_value(self, entry, placeholder):
        """Return the entry's text, or an empty string if it's still showing the placeholder."""
        value = entry.get()
        return "" if value == placeholder else value

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

    def on_start_offering_feed(self):
        # Placeholder command - replace with real FIP test logic later
        selected = [label for label, var in self.fip_vars.items() if var.get()]
        self.log_message(f'Start FIP Offering feed clicked - Selected: {", ".join(selected) if selected else "none"}')

    def on_resend_to_venom(self):
        # Placeholder command - replace with real resend logic later
        trade_id = self.trade_id_var.get()
        self.log_message(f"Resend to Venom clicked - Trade ID: {trade_id}")

    def on_add_bbg_mapping(self):
        # Placeholder command - replace with real BBG trader mapping logic later
        bbg_id = self.bbg_id_var.get()
        fis_id = self.fis_id_var.get()
        trader_name = self.trader_name_var.get()
        self.log_message(
            f"Add BBG Trader Mapping clicked - BBG ID: {bbg_id}, FIS ID: {fis_id}, Trader Name: {trader_name}"
        )

    def on_find_audit_log(self):
        # Placeholder command - replace with real TIBCO audit log lookup later
        mailbox = self.tibco_mailbox_var.get()
        from_date = self.get_entry_value(self.tibco_from_date_entry, "mm/dd/yyyy")
        to_date = self.get_entry_value(self.tibco_to_date_entry, "mm/dd/yyyy")
        self.log_message(
            f"Find Audit Log clicked - Mailbox: {mailbox}, From: {from_date}, To: {to_date}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemManagerApp(root)
    root.mainloop()