import customtkinter as ctk
import json
from tkinter import messagebox
import os

PROFILE_FILE = "user_profile.json"

class UserProfileTab(ctk.CTkFrame):
    """A tab for managing a user profile with save/load functionality."""
    def __init__(self, master, log_callback):
        super().__init__(master)
        self.log = log_callback
        self.entries = {}

        self.grid_columnconfigure(0, weight=1)

        # --- Personal Information ---
        personal_frame = ctk.CTkFrame(self)
        personal_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        personal_frame.grid_columnconfigure((1, 3), weight=1)
        ctk.CTkLabel(personal_frame, text="Personal Information", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=(5,10), sticky="w", padx=10)
        
        personal_fields = ["First Name", "Last Name", "Email Address", "Phone Number"]
        self._create_form_fields(personal_frame, personal_fields, 1)

        # --- Account Information ---
        account_frame = ctk.CTkFrame(self)
        account_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        account_frame.grid_columnconfigure((1, 3), weight=1)
        ctk.CTkLabel(account_frame, text="Account Information", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=(5,10), sticky="w", padx=10)
        
        account_fields = [("Username", False), ("Password", True), ("Confirm Password", True)]
        self._create_form_fields(account_frame, account_fields, 1, is_password_list=True)

        # --- Address Information ---
        address_frame = ctk.CTkFrame(self)
        address_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        address_frame.grid_columnconfigure((1, 3), weight=1)
        ctk.CTkLabel(address_frame, text="Address Information", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=(5,10), sticky="w", padx=10)
        
        address_fields = ["Address Line 1", "Address Line 2", "City", "State/Province", "Postal Code", "Country"]
        self._create_form_fields(address_frame, address_fields, 1)

        # --- Action Buttons ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=20)
        
        save_button = ctk.CTkButton(button_frame, text="Save Profile", command=self.save_profile)
        save_button.pack(side="left", padx=10)
        
        load_button = ctk.CTkButton(button_frame, text="Load Profile", command=lambda: self.load_profile(silent=False))
        load_button.pack(side="left", padx=10)

        self.load_profile(silent=True) # Load profile on startup without user notifications

    def _create_form_fields(self, parent, fields, start_row, is_password_list=False):
        for i, field_info in enumerate(fields):
            label_text, is_password = (field_info, False) if not is_password_list else field_info
            key = label_text.lower().replace(" ", "_")
            row, col = (i // 2) + start_row, (i % 2) * 2
            
            label = ctk.CTkLabel(parent, text=f"{label_text}:")
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            entry = ctk.CTkEntry(parent, show="*" if is_password else None)
            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky="ew")
            self.entries[key] = entry

    def save_profile(self):
        profile_data = {key: entry.get() for key, entry in self.entries.items()}

        if profile_data.get("password") != profile_data.get("confirm_password"):
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            self.log("[Error] Profile save failed: Passwords do not match.")
            return

        try:
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=4)
            self.log(f"[Info] User profile saved to {PROFILE_FILE}")
            messagebox.showinfo("Success", "Profile saved successfully.", parent=self)
        except IOError as e:
            self.log(f"[Error] Failed to save profile: {e}")
            messagebox.showerror("Error", f"Failed to save profile:\n{e}", parent=self)

    def load_profile(self, silent=False):
        if not os.path.exists(PROFILE_FILE):
            if not silent: self.log("[Info] No existing user profile found to load.")
            return
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
            for key, value in profile_data.items():
                if key in self.entries:
                    self.entries[key].delete(0, "end")
                    self.entries[key].insert(0, value)
            if not silent: self.log(f"[Info] User profile loaded from {PROFILE_FILE}")
        except (json.JSONDecodeError, IOError) as e:
            if not silent:
                self.log(f"[Error] Failed to load profile: {e}")
                messagebox.showerror("Error", f"Failed to load profile:\n{e}", parent=self)