# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import tkinter as tk

import customtkinter
from PIL import Image

import src.gui.frames as frames
import src.gui.pages as pages
from src.config_manager import ConfigManager
from src.controllers import MouseController

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("assets/themes/google_theme.json")

logger = logging.getLogger("MainGUi")


class MainGui():

    def __init__(self, tk_root):
        logger.info("Init MainGui")
        super().__init__()
        self.tk_root = tk_root

        self.tk_root.geometry("1280x720")
        self.tk_root.title(f"playAbility 0.2.3")
        self.tk_root.iconbitmap("assets/images/icon.ico")
        self.tk_root.resizable(width=True, height=True)

        self.tk_root.grid_rowconfigure(1, weight=1)
        self.tk_root.grid_columnconfigure(1, weight=1)

        # Create menu frame and assign callbacks
        self.frame_menu = frames.FrameMenu(self.tk_root,
                                           self.change_frame_callback,
                                           height=360,
                                           width=260,
                                           logger_name="frame_menu")
        self.frame_menu.grid(row=0,
                             column=0,
                             padx=0,
                             pady=0,
                             sticky="nsew",
                             columnspan=1,
                             rowspan=3)

        # Create Preview frame
        self.frame_preview = frames.FrameCamPreview(self.tk_root,
                                                    self.cam_preview_callback,
                                                    logger_name="frame_preview")
        self.frame_preview.grid(row=1,
                                column=0,
                                padx=0,
                                pady=0,
                                sticky="sew",
                                columnspan=1)
        self.frame_preview.enter()

        # Create all wizard pages and grid them.
        self.pages = {
            "page_home":
                pages.PageHome(master=self.tk_root,
                               logger_name="page_home",
                               master_callback=self.change_frame_callback),
            "page_camera":
                pages.PageSelectCamera(
                    master=self.tk_root,
                    logger_name="page_camera",
                ),
            "page_cursor":
                pages.PageCursor(
                    master=self.tk_root,
                    logger_name="page_cursor",
                ),
            "page_gestures":
                pages.PageSelectGestures(
                    master=self.tk_root,
                    logger_name="page_gestures",
                ),
            "page_keyboard":
                pages.PageKeyboard(
                    master=self.tk_root,
                    logger_name="page_keyboard",
                )
        }

        self.page_names = list(self.pages.keys())
        self.curr_page_name = None
        for name, page in self.pages.items():
            # Page home extended full window
            if name == "page_home":
                page.grid(row=0,
                          column=0,
                          padx=5,
                          pady=5,
                          sticky="nsew",
                          rowspan=2,
                          columnspan=2)
            else:
                page.grid(row=0,
                          column=1,
                          padx=5,
                          pady=5,
                          sticky="nsew",
                          rowspan=2,
                          columnspan=1)

        self.change_page("page_home")

        self.frame_profile = frames.FrameProfile(
            self.tk_root, refresh_master_fn=self.refresh_profile)

        # Profile button      
        profile_btn = customtkinter.CTkButton(
            master=self.tk_root,
            textvariable=ConfigManager().curr_profile_name,
            border_width=1,
            corner_radius=4,        
            compound="right",
            border_color="gray70",
            anchor="e",
            command=self.frame_profile.show_window)
        # profile_btn.grid(row=0,
        #                  column=0,
        #                  padx=10,
        #                  pady=10,
        #                  sticky="ne",
        #                  columnspan=10,
        #                  rowspan=10)

    def refresh_profile(self):
        logger.info("refresh_profile")
        self.pages["page_gestures"].refresh_profile()
        self.pages["page_camera"].refresh_profile()
        self.pages["page_cursor"].refresh_profile()
        self.pages["page_keyboard"].refresh_profile()

    def change_frame_callback(self, command, args: dict):
        logger.info(f"change_frame_callback {command} with {args}")
        if command == "change_page":
            self.change_page(args["target"])

        self.frame_menu.set_tab_active(tab_name=args["target"])

    def cam_preview_callback(self, command, args: dict):
        logger.info(f"cam_preview_callback {command} with {args}")

        if command == "toggle_switch":
            self.set_mediapipe_mouse_enable(new_state=args["switch_status"])

    def set_mediapipe_mouse_enable(self, new_state: bool):
        if new_state:
            MouseController().set_active(True)
        else:
            MouseController().set_active(False)

    def change_page(self, target_page_name: str):

        if self.curr_page_name == target_page_name:
            return

        for name, page in self.pages.items():
            if name == target_page_name:
                page.grid()
                self.pages[target_page_name].enter()
                self.curr_page_name = target_page_name

            else:
                page.grid_remove()
                page.leave()

    def del_main_gui(self):
        logger.info("Deleting MainGui instance")
        # try:
        self.frame_preview.leave()
        self.frame_preview.destroy()
        self.frame_menu.leave()
        self.frame_menu.destroy()
        for page in self.pages.values():
            page.leave()
            page.destroy()

        self.tk_root.quit()
        self.tk_root.destroy()
