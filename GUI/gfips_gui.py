import sys
import tkinter as tk
from tkinter import ttk


class TextRedirector:
    """Sends anything written to stdout/stderr into the message box."""

    def __init__(self, log_func):
        self.log_func = log_func

    def write(self, text):
        if text.strip():
            self.log_func(text.rstrip("\n"))

    def flush(self):
        pass


class PlaceholderEntry(ttk.Entry):
    """Entry that shows gray template text when empty and unfocused.

    The placeholder is never treated as a value: use get_value(), which
    returns "" while the placeholder is showing.
    """

    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self._showing_placeholder = False
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self._show_placeholder()

    def _show_placeholder(self):
        self.delete(0, "end")
        self.insert(0, self.placeholder)
        self.configure(foreground="gray")
        self._showing_placeholder = True

    def _on_focus_in(self, _event):
        if self._showing_placeholder:
            self.delete(0, "end")
            self.configure(foreground="")
            self._showing_placeholder = False

    def _on_focus_out(self, _event):
        if not self.get():
            self._show_placeholder()

    def get_value(self):
        return "" if self._showing_placeholder else self.get()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Report Downloader")
        self.geometry("520x520")
        self.minsize(480, 460)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)  # message panel expands

        self._credentials = None  # (username, password) after a successful Save
        self._reports = []  # [(key, info_dict), ...] in dropdown order

        self._build_login_panel()
        self._build_report_panel()
        self._build_message_panel()

        # Redirect system messages (print statements, errors) to the message box
        sys.stdout = TextRedirector(self.log)
        sys.stderr = TextRedirector(lambda m: self.log(m, tag="error"))

        self.log("Application started.")

    # ------------------------------------------------------------------ Login
    def _build_login_panel(self):
        frame = ttk.LabelFrame(self, text="Login", padding=10)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        frame.columnconfigure(4, weight=1)  # spare space goes to the right

        ttk.Label(frame, text="Username :").grid(row=0, column=0, sticky="w", pady=3)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(frame, textvariable=self.username_var, width=15)
        self.username_entry.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)

        ttk.Label(frame, text="Password :").grid(row=1, column=0, sticky="w", pady=3)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            frame, textvariable=self.password_var, show="*", width=15
        )
        self.password_entry.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)

        # Spans both rows so it sits to the right of the inputs and is taller
        self.save_button = ttk.Button(
            frame, text="Save", command=self.on_save, width=6
        )
        self.save_button.grid(
            row=0, column=2, rowspan=2, sticky="ns", padx=(10, 0), pady=3
        )

        # Indicator: ticked automatically when Save succeeds (not user-clickable)
        self.saved_var = tk.BooleanVar(value=False)
        self.saved_check = ttk.Checkbutton(
            frame,
            text="Credential check successful",
            variable=self.saved_var,
            state="disabled",
        )
        self.saved_check.grid(row=0, column=3, rowspan=2, padx=(30, 0))

    # ---------------------------------------------------------------- Report
    def _build_report_panel(self):
        frame = ttk.LabelFrame(self, text="Report Download", padding=10)
        frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        frame.columnconfigure(3, weight=1)  # spare space goes to the right

        ttk.Label(frame, text="Select Report :").grid(
            row=0, column=0, sticky="w", pady=3
        )
        self.report_var = tk.StringVar()
        # Populate with self.set_reports({...}) once the report list is available
        self.report_combo = ttk.Combobox(
            frame, textvariable=self.report_var, state="readonly", values=[], width=30
        )
        self.report_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)

        ttk.Label(frame, text="Date :").grid(row=1, column=0, sticky="w", pady=3)
        date_frame = ttk.Frame(frame)
        date_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)

        # Gray template text; use .get_value() to read (returns "" if untouched)
        self.year_entry = PlaceholderEntry(date_frame, "yyyy", width=5)
        self.month_entry = PlaceholderEntry(date_frame, "mm", width=3)
        self.day_entry = PlaceholderEntry(date_frame, "dd", width=3)

        self.year_entry.grid(row=0, column=0)
        ttk.Label(date_frame, text="-").grid(row=0, column=1, padx=3)
        self.month_entry.grid(row=0, column=2)
        ttk.Label(date_frame, text="-").grid(row=0, column=3, padx=3)
        self.day_entry.grid(row=0, column=4)

        # Spans both rows so it sits to the right of the inputs and is taller
        self.download_button = ttk.Button(
            frame, text="Download", command=self.on_download, width=10
        )
        self.download_button.grid(
            row=0, column=2, rowspan=2, sticky="ns", padx=(10, 0), pady=3
        )

    # --------------------------------------------------------------- Messages
    def _build_message_panel(self):
        frame = ttk.LabelFrame(self, text="Messages", padding=5)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.message_box = tk.Text(
            frame, height=8, state="disabled", wrap="word", font=("Consolas", 10)
        )
        self.message_box.grid(row=0, column=0, sticky="nsew")
        self.message_box.tag_configure("error", foreground="red")

        scrollbar = ttk.Scrollbar(frame, command=self.message_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.message_box.configure(yscrollcommand=scrollbar.set)

    def log(self, message, tag=None):
        """Append a message to the message box (thread-safe via after())."""
        def _append():
            self.message_box.configure(state="normal")
            self.message_box.insert("end", message + "\n", tag)
            self.message_box.see("end")
            self.message_box.configure(state="disabled")

        self.after(0, _append)

    # ----------------------------------------------------------- Report list
    def set_reports(self, reports):
        """Initialize the dropdown from a dict of dicts, e.g.

            {"r1": {"name": "Sales"}, "r2": {"name": "Inventory", ...}}

        Entries are sorted A-Z by the outer dictionary key (case-insensitive
        for text keys), and the dropdown displays the key itself.
        """
        def sort_key(item):
            key = item[0]
            return key.casefold() if isinstance(key, str) else key

        try:
            self._reports = sorted(reports.items(), key=sort_key)
        except TypeError:  # keys of mixed types can't be compared directly
            self._reports = sorted(
                reports.items(), key=lambda item: str(item[0]).casefold()
            )

        self.report_combo["values"] = [str(key) for key, _info in self._reports]
        self.report_combo.set("")  # nothing selected until the user chooses

    def get_selected_report(self):
        """Return (key, info_dict) for the selected dropdown item, or None."""
        index = self.report_combo.current()
        if index < 0:
            return None
        return self._reports[index]

    # ------------------------------------------------------------ Button logic
    def _get_credentials(self):
        """Return (username, password), or None (with an error logged) if missing."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            self.log("Please enter both Username and Password.", tag="error")
            return None
        return username, password

    def save_login(self, username, password):
        """Save logic. Return True on success, False on failure."""
        # TODO: implement login save logic using username and password
        return True  # placeholder until real logic is added

    def on_save(self):
        """Save button: uses the Username and Password inputs."""
        self.saved_var.set(False)
        self._credentials = None
        creds = self._get_credentials()
        if creds is None:
            return
        username, password = creds

        if self.save_login(username, password):
            # Keep the credentials in memory for Download, then clear the boxes
            self._credentials = creds
            self.username_var.set("")
            self.password_var.set("")
            self.saved_var.set(True)
            self.log(f"Login saved for user '{username}'.")
        else:
            self.log("Save failed.", tag="error")

    def download_report(self, username, password, report_id, report, year, month, day):
        """Download logic. Return True on success, False on failure.

        report_id is the key in the dict passed to set_reports(); report is
        that key's inner dict.
        """
        # TODO: implement report download logic
        return True  # placeholder until real logic is added

    def on_download(self):
        """Download button: uses saved username/password, report dropdown and date."""
        if self._credentials is None:
            self.log("Please enter your credentials and click Save first.", tag="error")
            return
        username, password = self._credentials

        selected = self.get_selected_report()
        year = self.year_entry.get_value().strip()
        month = self.month_entry.get_value().strip()
        day = self.day_entry.get_value().strip()

        if selected is None:
            self.log("Please select a report.", tag="error")
            return
        report_id, report = selected
        if not (year and month and day):
            self.log("Please enter the full date (yyyy-mm-dd).", tag="error")
            return

        if self.download_report(
            username, password, report_id, report, year, month, day
        ):
            self.log(f"Download requested: '{report_id}' for {year}-{month}-{day}.")
        else:
            self.log("Download failed.", tag="error")


if __name__ == "__main__":
    App().mainloop()