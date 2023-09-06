import customtkinter


class Home(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create and configure widgets for the Home view

        self.home_label = customtkinter.CTkLabel(
            self, text="Welcome to Guardian AI Antivirus!", font=customtkinter.CTkFont(size=20, weight="bold")
        )
        self.home_label.pack(pady=(20, 10))

        self.home_description = customtkinter.CTkLabel(
            self, text="Guardian AI is your trusted antivirus solution."
        )
        self.home_description.pack(pady=10)

        self.home_button = customtkinter.CTkButton(
            self, text="Scan for Viruses", corner_radius=5, height=40, border_spacing=10,
            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "green"),
            command=self.scan_for_viruses
        )
        self.home_button.pack(pady=25)

    def scan_for_viruses(self):
        # Implement scan logic here
        pass
