import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AntivirusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Guardian AI - Antivirus")
        self.geometry("1100x580")

        self.create_ui()

    def create_ui(self):
        self.configure_grid()
        self.create_main_frame()
        self.create_sidebar()
        self.create_quarantined_items()
        self.center_main_frame()

    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

    def create_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self.main_frame, width=140)
        sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(sidebar_frame, text="Guardian AI - Antivirus",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        scan_button = ctk.CTkButton(
            sidebar_frame, text="Scan", command=self.scan)
        scan_button.grid(row=1, column=0, padx=20, pady=10)
        update_button = ctk.CTkButton(
            sidebar_frame, text="Update Definitions", command=self.update_definitions)
        update_button.grid(row=2, column=0, padx=20, pady=10)

        appearance_label = ctk.CTkLabel(
            sidebar_frame, text="Appearance Mode:", anchor="w")
        appearance_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        appearance_optionmenu = ctk.CTkOptionMenu(sidebar_frame, values=["Light", "Dark", "System"],
                                                  command=self.change_appearance_mode_event)
        appearance_optionmenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        scaling_label = ctk.CTkLabel(
            sidebar_frame, text="UI Scaling:", anchor="w")
        scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))

        scaling_optionmenu = ctk.CTkOptionMenu(sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                               command=self.change_scaling_event)
        scaling_optionmenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.scan_button = scan_button
        self.scan_progress = None

    def create_quarantined_items(self):
        items_frame = ctk.CTkScrollableFrame(
            self.main_frame, label_text="Quarantined Items")
        items_frame.grid(row=0, column=1, padx=(
            20, 0), pady=(20, 0), sticky="nsew")

        items_frame.grid_rowconfigure(0, weight=1)
        items_frame.grid_columnconfigure(0, weight=1)

        # Simulate adding quarantined items (Replacing after project structure changes)
        for i in range(10):
            ctk.CTkSwitch(master=items_frame, text=f"Item {i}").grid(
                row=i, column=0, padx=10, pady=(0, 20))

    def center_main_frame(self):
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def scan(self):
        self.scan_button.configure(state="disabled", text="Scanning...")
        self.scan_progress = ctk.CTkProgressBar(self.main_frame)
        self.scan_progress.grid(row=1, column=0, padx=20,
                                pady=(20, 0), sticky="nsew")
        self.scan_progress.start()
        self.after(3000, self.stop_scan)  # Add Scanning callback func here!

    def stop_scan(self):
        if self.scan_progress:
            self.scan_progress.stop()
            self.scan_progress.destroy()
            self.scan_progress = None

        self.scan_button.configure(state="normal", text="Scan")

    def update_definitions(self):
        pass  # Updating this later :)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()
