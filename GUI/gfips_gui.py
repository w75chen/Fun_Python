import sys
import tkinter as tk
from datetime import date
from tkinter import ttk


def validate_date(year, month, day):
    """Check that year/month/day (strings) form a real calendar date.

    Returns (year, month, day) normalized to "yyyy", "mm", "dd" strings.
    Raises ValueError with a user-friendly message if the date is invalid.
    """
    if not (year.isdigit() and len(year) == 4):
        raise ValueError("Year must be 4 digits (yyyy).")
    if not (month.isdigit() and 1 <= len(month) <= 2):
        raise ValueError("Month must be a number from 1 to 12 (mm).")
    if not (day.isdigit() and 1 <= len(day) <= 2):
        raise ValueError("Day must be a number from 1 to 31 (dd).")

    try:
        valid = date(int(year), int(month), int(day))
    except ValueError:
        raise ValueError(f"{year}-{month}-{day} is not a valid date.") from None

    return f"{valid.year:04d}", f"{valid.month:02d}", f"{valid.day:02d}"


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
        self.geometry("520x620")
        self.minsize(480, 540)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)  # message panel expands

        self._credentials = None  # (username, password) after a successful Save
        self._reports = []  # [(key, info_dict), ...] in dropdown order
        self._server_vars = {}  # server name -> BooleanVar (one check box each)
        self._selected_server = None

        self._build_login_panel()
        self._build_server_panel()
        self._build_report_panel()
        self._build_message_panel()

        # Redirect system messages (print statements, errors) to the message box
        sys.stdout = TextRedirector(self.log)
        sys.stderr = TextRedirector(lambda m: self.log(m, tag="error"))

        # Placeholder list: replace by calling self.set_servers([...]) with real names
        self.set_servers(["Server 1", "Server 2", "Server 3"])

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
    # ----------------------------------------------------------------- Server
    def _build_server_panel(self):
        self.server_frame = ttk.LabelFrame(self, text="Select Server", padding=10)
        self.server_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

    def set_servers(self, servers):
        """Build the vertical list of check boxes from a list of server names.

        Only one can be selected at a time; the first is selected by default.
        """
        for child in self.server_frame.winfo_children():
            child.destroy()
        self._server_vars = {}
        self._selected_server = None

        for name in servers:
            var = tk.BooleanVar(value=False)
            self._server_vars[name] = var
            ttk.Checkbutton(
                self.server_frame,
                text=str(name),
                variable=var,
                command=lambda n=name: self._select_server(n),
            ).pack(anchor="w", pady=1)

        if servers:
            self._select_server(servers[0])

    def _select_server(self, name):
        """Make `name` the only ticked server (clicking the ticked one keeps it)."""
        self._selected_server = name
        for server, var in self._server_vars.items():
            var.set(server == name)

    def get_selected_server(self):
        """Return the selected server name, or None if there are no servers."""
        return self._selected_server

    def _build_report_panel(self):
        frame = ttk.LabelFrame(self, text="Report Download", padding=10)
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        frame.columnconfigure(4, weight=1)  # spare space goes to the right

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

        # Same size as Download, directly to its right; takes the same inputs
        self.find_button = ttk.Button(
            frame, text="Find", command=self.on_find, width=10
        )
        self.find_button.grid(
            row=0, column=3, rowspan=2, sticky="ns", padx=(10, 0), pady=3
        )

    # --------------------------------------------------------------- Messages
    def _build_message_panel(self):
        frame = ttk.LabelFrame(self, text="Messages", padding=5)
        frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5, 10))
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

    def save_login(self, username, password, server):
        """Save logic. Return True on success, False on failure."""
        # TODO: implement login save logic using username, password and server
        return True  # placeholder until real logic is added

    def on_save(self):
        """Save button: uses the Username, Password and selected server."""
        self.saved_var.set(False)
        self._credentials = None
        creds = self._get_credentials()
        if creds is None:
            return
        username, password = creds

        server = self.get_selected_server()
        if server is None:
            self.log("Please select a server.", tag="error")
            return

        if self.save_login(username, password, server):
            # Keep the credentials in memory for Download, then clear the boxes
            self._credentials = creds
            self.username_var.set("")
            self.password_var.set("")
            self.saved_var.set(True)
            self.log(f"Login saved for user '{username}' on {server}.")
        else:
            self.log("Save failed.", tag="error")

    def download_report(
        self, username, password, server, report_id, report, year, month, day
    ):
        """Download logic. Return True on success, False on failure.

        report_id is the key in the dict passed to set_reports(); report is
        that key's inner dict.
        """
        # TODO: implement report download logic
        return True  # placeholder until real logic is added

    def _get_report_inputs(self):
        """Gather and validate the inputs shared by Download and Find.

        Returns (username, password, server, report_id, report, year, month, day),
        or None (with an error logged) if something is missing.
        """
        if self._credentials is None:
            self.log("Please enter your credentials and click Save first.", tag="error")
            return None
        username, password = self._credentials

        server = self.get_selected_server()
        selected = self.get_selected_report()
        year = self.year_entry.get_value().strip()
        month = self.month_entry.get_value().strip()
        day = self.day_entry.get_value().strip()

        if server is None:
            self.log("Please select a server.", tag="error")
            return None
        if selected is None:
            self.log("Please select a report.", tag="error")
            return None
        report_id, report = selected
        if not (year and month and day):
            self.log("Please enter the full date (yyyy-mm-dd).", tag="error")
            return None
        try:
            year, month, day = validate_date(year, month, day)
        except ValueError as err:
            self.log(str(err), tag="error")
            return None

        return username, password, server, report_id, report, year, month, day

    def on_download(self):
        """Download button: uses saved username/password, selected server,
        report dropdown and date."""
        inputs = self._get_report_inputs()
        if inputs is None:
            return
        _user, _pw, server, report_id, _report, year, month, day = inputs

        if self.download_report(*inputs):
            self.log(
                f"Download requested: '{report_id}' for {year}-{month}-{day} "
                f"from {server}."
            )
        else:
            self.log("Download failed.", tag="error")

    def find_report(
        self, username, password, server, report_id, report, year, month, day
    ):
        """Find logic. Return True on success, False on failure."""
        # TODO: implement find logic (same inputs as download_report)
        return True  # placeholder until real logic is added

    def on_find(self):
        """Find button: uses the same inputs as Download."""
        inputs = self._get_report_inputs()
        if inputs is None:
            return
        _user, _pw, server, report_id, _report, year, month, day = inputs

        if self.find_report(*inputs):
            self.log(
                f"Find requested: '{report_id}' for {year}-{month}-{day} "
                f"on {server}."
            )
        else:
            self.log("Find failed.", tag="error")


if __name__ == "__main__":
    App().mainloop()
