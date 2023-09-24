import os
from PIL import Image
import importlib
import tkinter as tk
from customtkinter import CTk, CTkImage, CTkFrame, CTkLabel, CTkButton, CTkFont, CTkOptionMenu


class Main_window(CTk):
    def __init__(self):
        super().__init__()

        self.title("Guardian AI - Antivirus")
        self.geometry("1100x580")

        self.grid_rowconfigure(0, weight=1)g
        self.grid_columnconfigure(1, weight=1)

        self.logo_image = CTkImage(
            Image.open("assets/guardian.png"), size=(26, 26))
        self.large_test_image = CTkImage(
            Image.open("assets/large_test_image.png"), size=(500, 150))

        views = [
            {"name": "Home", "icon_path": "assets/home.png"},
            {"name": "Update", "icon_path": "assets/update.png"},
            {"name": "File Scan", "icon_path": "assets/scan.png"},
            {"name": "Settings", "icon_path": "assets/settings.png"},
            {"name": "Support", "icon_path": "assets/support.png"}
        ]

        self.icons = {}
        self.ui_scaling_selector = None
        self.current_view = None

        for view in views:
            icon_path = view["icon_path"]
            icon_image = Image.open(icon_path)
            self.icons[view["name"]] = CTkImage(icon_image)

        self.navigation_frame = CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")

        self.navigation_frame.grid_rowconfigure(0, weight=1)
        for i in range(len(views) + 1):
            self.navigation_frame.grid_rowconfigure(i + 1, weight=1)

        self.navigation_frame_label = CTkLabel(
            self.navigation_frame, text="  Guardian AI", image=self.logo_image,
            compound="left", font=CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=15)

        self.buttons = []

        for i, view in enumerate(views):
            button = CTkButton(
                self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text=view["name"],
                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray70"),
                image=self.icons[view["name"]], anchor="w", command=lambda v=view: self.button_event(v["name"]))
            button.grid(row=i + 1, column=0, sticky="ew")
            self.buttons.append(button)

        self.home_frame = CTkFrame(
            self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = CTkLabel(
            self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(
            row=0, column=0, padx=20, pady=10)

        for i in range(1, 5):
            button = CTkButton(
                self.home_frame, text="", image=self.icons["Home"])
            button.grid(row=i, column=0, padx=20, pady=10)

        self.select_frame_by_name("Home")

    def button_event(self, name):
        self.select_frame_by_name(name)

    def select_frame_by_name(self, name):
        for button in self.buttons:
            if button.cget("text") == name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color="transparent")

        if self.current_view:
            self.current_view.grid_forget()

        if name == "Home":
            try:
                module = importlib.import_module("gui.views.home")
                view_class = getattr(module, "Home")
                self.current_view = view_class(self)
                self.current_view.grid(
                    row=0, column=1, padx=0, pady=0, sticky="nsew")
            except (ImportError, AttributeError):
                self.current_view = None
        elif name == "Update":
            try:
                module = importlib.import_module("gui.views.update")
                view_class = getattr(module, "Update")
                self.current_view = view_class(self)
                self.current_view.grid(
                    row=0, column=1, padx=0, pady=0, sticky="nsew")
            except (ImportError, AttributeError):
                self.current_view = None


if __name__ == "__main__":
    app = Main_window()
    app.geometry("1100x580+100+100")
    app.mainloop()
