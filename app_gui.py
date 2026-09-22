"""
DisplaySwitch - Modern GUI for Windows (Windows 11 Fluent Dark Design)
Copyright (C) 2026 UltraTiza, FedeFadda
Testing & Quality Assurance: FedeNahas
Licencia: Software Libre (GPLv3)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys
import ctypes
from ctypes import wintypes
from i18n import t, format_hotkey_display

class ModernButton(tk.Canvas):
    """Botón con esquinas redondeadas, animaciones hover, auto-escalado responsive y soporte de iconos"""
    def __init__(self, parent, text, command, bg_color="#6366f1", hover_color="#4f46e5", 
                 text_color="#ffffff", font=("Segoe UI Semibold", 10), width=180, height=38, radius=8):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.width = width
        self.height = height
        self.radius = radius
        self.text = text
        self.is_hover = False
        self.enabled = True

        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        changed = False
        if event.width > 1 and event.width != self.width:
            self.width = event.width
            changed = True
        if event.height > 1 and event.height != self.height:
            self.height = event.height
            changed = True
        if changed:
            self._draw()

    def _draw(self):
        self.delete("all")
        color = self.hover_color if self.is_hover else self.bg_color
        if not self.enabled:
            color = "#272b38"
        
        w = self.winfo_width() if self.winfo_width() > 1 else self.width
        h = self.winfo_height() if self.winfo_height() > 1 else self.height
        r = min(self.radius, max(1, h // 2), max(1, w // 2))

        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=color, outline="")
        self.create_arc((w - r*2, 0, w, r*2), start=0, extent=90, fill=color, outline="")
        self.create_arc((0, h - r*2, r*2, h), start=180, extent=90, fill=color, outline="")
        self.create_arc((w - r*2, h - r*2, w, h), start=270, extent=90, fill=color, outline="")
        self.create_rectangle((r, 0, w - r, h), fill=color, outline="")
        self.create_rectangle((0, r, w, h - r), fill=color, outline="")

        txt_col = self.text_color if self.enabled else "#64748b"
        self.create_text(w//2, h//2, text=self.text, fill=txt_col, font=self.font)

    def set_text(self, text, bg_color=None, hover_color=None):
        self.text = text
        if bg_color:
            self.bg_color = bg_color
        if hover_color:
            self.hover_color = hover_color
        self._draw()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self._draw()

    def _on_enter(self, event):
        if self.enabled:
            self.is_hover = True
            self.config(cursor="hand2")
            self._draw()

    def _on_leave(self, event):
        self.is_hover = False
        self.config(cursor="")
        self._draw()

    def _on_click(self, event):
        if self.enabled and self.command:
            self.command()


class AboutModal(tk.Toplevel):
    """Ventana modal con información legal, créditos y derechos de autor de Software Libre"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        lang = self.controller.get_language()
        self.title(t("about_title", lang))
        self.geometry("540x440")
        self.resizable(False, False)
        self.configure(bg="#0f1117")
        self.transient(parent)
        self.grab_set()

        try:
            self.update_idletasks()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            w, h = 540, 440
            x = px + (pw // 2) - (w // 2)
            y = py + (ph // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        box = tk.Frame(self, bg="#141721", padx=24, pady=20)
        box.pack(fill="both", expand=True, padx=16, pady=16)

        t_lbl = tk.Label(box, text="⚡ DisplaySwitch", font=("Segoe UI Bold", 17), bg="#141721", fg="#ffffff")
        t_lbl.pack(pady=(0, 2))

        sub = tk.Label(box, text=t("about_subtitle", lang), font=("Segoe UI", 9), bg="#141721", fg="#38bdf8")
        sub.pack(pady=(0, 14))

        sep = tk.Frame(box, bg="#262b3b", height=1)
        sep.pack(fill="x", pady=(0, 14))

        credits_title = tk.Label(box, text=t("about_credits_title", lang), font=("Segoe UI Bold", 9), bg="#141721", fg="#94a3b8")
        credits_title.pack(anchor="w", pady=(0, 6))

        authors = [
            (t("about_role_dev", lang), "UltraTiza"),
            (t("about_role_fede", lang), "FedeFadda"),
            (t("about_role_qa", lang), "FedeNahas"),
        ]
        for role, name in authors:
            row = tk.Frame(box, bg="#141721")
            row.pack(fill="x", pady=2)
            r_lbl = tk.Label(row, text=role, font=("Segoe UI", 9), bg="#141721", fg="#cbd5e1", width=24, anchor="w")
            r_lbl.pack(side="left")
            n_lbl = tk.Label(row, text=name, font=("Segoe UI Bold", 9), bg="#141721", fg="#f8fafc", anchor="w")
            n_lbl.pack(side="left")

        sep2 = tk.Frame(box, bg="#262b3b", height=1)
        sep2.pack(fill="x", pady=(14, 12))

        lic_title = tk.Label(box, text=t("about_license_title", lang), font=("Segoe UI Bold", 9), bg="#141721", fg="#94a3b8")
        lic_title.pack(anchor="w", pady=(0, 4))

        lic_text = t("about_license_body", lang)
        lic_lbl = tk.Label(box, text=lic_text, font=("Segoe UI", 8), bg="#141721", fg="#94a3b8", justify="left")
        lic_lbl.pack(anchor="w", pady=(0, 14))

        btn_close = ModernButton(
            box, text=t("about_btn_close", lang), command=self.destroy,
            bg_color="#1e2230", hover_color="#2c3345", text_color="#f8fafc",
            font=("Segoe UI Semibold", 9), width=90, height=30, radius=6
        )
        btn_close.pack(anchor="e")


class SettingsModal(tk.Toplevel):
    """Ventana modal unificada para configurar preferencias generales, notificaciones y atajos globales"""
    def __init__(self, parent, controller, tray_manager, app=None, on_saved_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.tray = tray_manager
        self.app = app
        self.on_saved = on_saved_callback

        app_title = self.controller.get_app_title()
        lang = self.controller.get_language()
        self.title(t("settings_title", lang, title=app_title))
        self.geometry("750x700")
        self.minsize(700, 650)
        self.configure(bg="#0f1117")
        self.transient(parent)
        self.grab_set()

        # Centrar con respecto a la ventana principal
        try:
            self.update_idletasks()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_x()
            py = parent.winfo_y()
            w = 750
            h = 700
            x = px + (pw // 2) - (w // 2)
            y = py + (ph // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

        self.current_hotkeys = dict(self.controller.get_hotkeys())
        self.notif_var = tk.BooleanVar(value=self.controller.get_show_notifications())
        self._recording_action = None
        self._value_labels = {}
        self._record_buttons = {}
        self._pressed_keys = set()

        self._build_ui()

    def _format_display(self, hk_str):
        return format_hotkey_display(hk_str, lang=self.controller.get_language(), for_tray=False)

    def _on_language_changed(self, event=None):
        val = self.lang_var.get()
        new_lang = "es" if val == "Español" else "en"
        self.controller.set_language(new_lang)
        if self.app:
            self.app.retranslate_ui()
        self._rebuild_ui()

    def _rebuild_ui(self):
        self._cancel_recording()
        for w in self.winfo_children():
            w.destroy()
        self._value_labels.clear()
        self._record_buttons.clear()
        app_title = self.controller.get_app_title()
        lang = self.controller.get_language()
        self.title(t("settings_title", lang, title=app_title))
        self._build_ui()

    def _on_toggle_notif(self):
        val = self.notif_var.get()
        self.controller.set_show_notifications(val)

    def _on_toggle_legacy(self):
        if self.app:
            self.app._on_toggle_legacy_mode()
            app_title = self.controller.get_app_title()
            lang = self.controller.get_language()
            self.title(t("settings_title", lang, title=app_title))

    def _build_ui(self):
        lang = self.controller.get_language()

        # Header
        header = tk.Frame(self, bg="#141721", height=64)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        htitle_box = tk.Frame(header, bg="#141721")
        htitle_box.pack(side="left", padx=20, pady=10)

        t_lbl = tk.Label(
            htitle_box, text=t("settings_header", lang),
            font=("Segoe UI Bold", 13), bg="#141721", fg="#f8fafc"
        )
        t_lbl.pack(anchor="w")

        s_lbl = tk.Label(
            htitle_box, text=t("settings_subtitle", lang),
            font=("Segoe UI", 8), bg="#141721", fg="#94a3b8"
        )
        s_lbl.pack(anchor="w")

        sep = tk.Frame(self, bg="#262b3b", height=1)
        sep.pack(fill="x")

        # Contenido Principal
        body = tk.Frame(self, bg="#0f1117")
        body.pack(fill="both", expand=True, padx=20, pady=14)

        # 1. SECCIÓN: PREFERENCIAS GENERALES
        pref_box = tk.Frame(body, bg="#141721", highlightbackground="#262b3b", highlightthickness=1)
        pref_box.pack(fill="x", pady=(0, 14), ipady=6)

        pref_header = tk.Frame(pref_box, bg="#141721")
        pref_header.pack(fill="x", padx=14, pady=(6, 4))
        tk.Label(pref_header, text=t("sec_general_prefs", lang), font=("Segoe UI Bold", 9), bg="#141721", fg="#94a3b8").pack(anchor="w")

        # Fila 0: Idioma / Language (Rótulo fijo universal)
        row_lang = tk.Frame(pref_box, bg="#141721")
        row_lang.pack(fill="x", padx=14, pady=3)

        lbl_lang = tk.Label(
            row_lang, text=t("pref_language_label", lang),
            font=("Segoe UI Semibold", 9), bg="#141721", fg="#ffffff"
        )
        lbl_lang.pack(side="left")

        current_lang = self.controller.get_language()
        lang_text = "English" if current_lang == "en" else "Español"
        self.lang_var = tk.StringVar(value=lang_text)

        cb_lang = ttk.Combobox(
            row_lang, textvariable=self.lang_var, values=["English", "Español"],
            state="readonly", width=10, font=("Segoe UI Semibold", 9)
        )
        cb_lang.pack(side="left", padx=(8, 8))
        cb_lang.bind("<<ComboboxSelected>>", self._on_language_changed)

        tk.Label(
            row_lang, text=t("pref_language_desc", lang),
            font=("Segoe UI", 8), bg="#141721", fg="#64748b"
        ).pack(side="left")

        # Fila 0.5: Monitor Principal por defecto
        row_prim = tk.Frame(pref_box, bg="#141721")
        row_prim.pack(fill="x", padx=14, pady=3)

        lbl_prim = tk.Label(
            row_prim, text=t("pref_primary_label", lang),
            font=("Segoe UI Semibold", 9), bg="#141721", fg="#ffffff"
        )
        lbl_prim.pack(side="left")

        monitors = self.controller.get_connected_monitors()
        eligible_monitors = [m for m in monitors if not m.is_designated_tv]
        mon_map = {}
        for m in eligible_monitors:
            label = f"{m.friendly_name} ({m.short_id})" if m.short_id else m.friendly_name
            mon_map[label] = m

        des_primary = self.controller.get_designated_primary()
        initial_label = ""
        if des_primary:
            k = f"{des_primary.friendly_name} ({des_primary.short_id})" if des_primary.short_id else des_primary.friendly_name
            if k in mon_map:
                initial_label = k
        if not initial_label and eligible_monitors:
            first_m = eligible_monitors[0]
            initial_label = f"{first_m.friendly_name} ({first_m.short_id})" if first_m.short_id else first_m.friendly_name

        self.prim_var = tk.StringVar(value=initial_label)
        cb_prim = ttk.Combobox(
            row_prim, textvariable=self.prim_var, values=list(mon_map.keys()),
            state="readonly", width=22, font=("Segoe UI Semibold", 9)
        )
        cb_prim.pack(side="left", padx=(8, 8))

        def _on_primary_selected(event=None):
            sel = self.prim_var.get()
            if sel in mon_map:
                target_m = mon_map[sel]
                if self.app:
                    self.app._set_as_primary(target_m)
                else:
                    threading.Thread(target=lambda: self.controller.set_designated_primary(target_m), daemon=True).start()

        cb_prim.bind("<<ComboboxSelected>>", _on_primary_selected)

        tk.Label(
            row_prim, text=t("pref_primary_desc", lang),
            font=("Segoe UI", 8), bg="#141721", fg="#64748b"
        ).pack(side="left")

        # Fila 1: Iniciar con Windows
        row1 = tk.Frame(pref_box, bg="#141721")
        row1.pack(fill="x", padx=14, pady=3)
        startup_var = self.app.startup_var if self.app else tk.BooleanVar(value=False)
        cb_startup = tk.Checkbutton(
            row1, text=t("pref_startup_label", lang), variable=startup_var,
            command=self.app._on_toggle_startup if self.app else None,
            bg="#141721", fg="#ffffff", selectcolor="#1e2230", activebackground="#141721", activeforeground="#ffffff",
            font=("Segoe UI Semibold", 9)
        )
        cb_startup.pack(side="left")
        tk.Label(row1, text=t("pref_startup_desc", lang), font=("Segoe UI", 8), bg="#141721", fg="#64748b").pack(side="left", padx=8)

        # Fila 2: Notificaciones de Windows
        row2 = tk.Frame(pref_box, bg="#141721")
        row2.pack(fill="x", padx=14, pady=3)
        cb_notif = tk.Checkbutton(
            row2, text=t("pref_notif_label", lang), variable=self.notif_var,
            command=self._on_toggle_notif,
            bg="#141721", fg="#ffffff", selectcolor="#1e2230", activebackground="#141721", activeforeground="#ffffff",
            font=("Segoe UI Semibold", 9)
        )
        cb_notif.pack(side="left")
        tk.Label(row2, text=t("pref_notif_desc", lang), font=("Segoe UI", 8), bg="#141721", fg="#64748b").pack(side="left", padx=8)

        # Fila 3: Legacy Mode
        row3 = tk.Frame(pref_box, bg="#141721")
        row3.pack(fill="x", padx=14, pady=3)
        legacy_var = self.app.legacy_var if self.app else tk.BooleanVar(value=False)
        cb_legacy = tk.Checkbutton(
            row3, text=t("pref_legacy_label", lang), variable=legacy_var,
            command=self._on_toggle_legacy,
            bg="#141721", fg="#ffffff", selectcolor="#1e2230", activebackground="#141721", activeforeground="#ffffff",
            font=("Segoe UI Semibold", 9)
        )
        cb_legacy.pack(side="left")
        tk.Label(row3, text=t("pref_legacy_desc", lang), font=("Segoe UI", 8), bg="#141721", fg="#64748b").pack(side="left", padx=8)

        # 2. SECCIÓN: GESTOR DE ATAJOS GLOBALES
        hk_box = tk.Frame(body, bg="#141721", highlightbackground="#262b3b", highlightthickness=1)
        hk_box.pack(fill="both", expand=True, pady=(0, 4), ipady=4)

        hk_header = tk.Frame(hk_box, bg="#141721")
        hk_header.pack(fill="x", padx=14, pady=(8, 2))
        tk.Label(hk_header, text=t("sec_hotkeys", lang), font=("Segoe UI Bold", 9), bg="#141721", fg="#94a3b8").pack(anchor="w")
        tk.Label(hk_header, text=t("hotkeys_sub", lang), font=("Segoe UI", 8), bg="#141721", fg="#64748b").pack(anchor="w", pady=(1, 6))

        actions = [
            ("toggle_tv", t("hk_action_toggle", lang), t("hk_desc_toggle", lang)),
            ("monitors_only", t("hk_action_monitors", lang), t("hk_desc_monitors", lang)),
            ("tv_only", t("hk_action_tv_only", lang), t("hk_desc_tv_only", lang)),
            ("extend_all", t("hk_action_extend", lang), t("hk_desc_extend", lang))
        ]

        for act_key, title, desc in actions:
            row = tk.Frame(hk_box, bg="#161922", highlightbackground="#262b3b", highlightthickness=1)
            row.pack(fill="x", padx=12, pady=4, ipady=3)

            inner = tk.Frame(row, bg="#161922")
            inner.pack(fill="x", padx=10, pady=4)

            info_col = tk.Frame(inner, bg="#161922")
            info_col.pack(side="left", fill="both", expand=True)

            lbl_title = tk.Label(info_col, text=title, font=("Segoe UI Bold", 10), bg="#161922", fg="#ffffff")
            lbl_title.pack(anchor="w")

            lbl_desc = tk.Label(info_col, text=desc, font=("Segoe UI", 8), bg="#161922", fg="#64748b")
            lbl_desc.pack(anchor="w")

            ctrl_col = tk.Frame(inner, bg="#161922")
            ctrl_col.pack(side="right")

            hk_val = self.current_hotkeys.get(act_key, "")
            disp_text = self._format_display(hk_val)
            disp_fg = "#38bdf8" if hk_val else "#64748b"

            val_lbl = tk.Label(
                ctrl_col, text=disp_text, font=("Segoe UI Bold", 9),
                bg="#222634", fg=disp_fg, padx=10, pady=4, width=18
            )
            val_lbl.pack(side="left", padx=(0, 6))
            self._value_labels[act_key] = val_lbl

            btn_rec = ModernButton(
                ctrl_col, text=t("btn_record", lang),
                command=lambda k=act_key: self._start_recording(k),
                bg_color="#1e2230", hover_color="#2c3345", text_color="#cbd5e1",
                font=("Segoe UI Semibold", 8), width=82, height=28, radius=6
            )
            btn_rec.pack(side="left", padx=2)
            self._record_buttons[act_key] = btn_rec

            btn_mouse = ModernButton(
                ctrl_col, text=t("btn_mouse", lang),
                command=None,
                bg_color="#1e2230", hover_color="#2c3345", text_color="#38bdf8",
                font=("Segoe UI Semibold", 8), width=82, height=28, radius=6
            )
            btn_mouse.command = lambda k=act_key, b=btn_mouse: self._open_mouse_menu(k, b)
            btn_mouse.pack(side="left", padx=2)

            btn_del = ModernButton(
                ctrl_col, text=t("btn_clear", lang),
                command=lambda k=act_key: self._clear_hotkey(k),
                bg_color="#1e2230", hover_color="#7f1d1d", text_color="#f87171",
                font=("Segoe UI Semibold", 8), width=74, height=28, radius=6
            )
            btn_del.pack(side="left", padx=2)

        # Footer con botones de acción
        footer = tk.Frame(self, bg="#141721", height=54)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        f_inner = tk.Frame(footer, bg="#141721")
        f_inner.pack(fill="both", expand=True, padx=20, pady=10)

        btn_default = ModernButton(
            f_inner, text=t("btn_reset_defaults", lang),
            command=self._reset_defaults,
            bg_color="#1e2230", hover_color="#2c3345", text_color="#94a3b8",
            font=("Segoe UI Semibold", 8), width=140, height=32, radius=6
        )
        btn_default.pack(side="left")

        btn_save = ModernButton(
            f_inner, text=t("btn_save_close", lang),
            command=self._save_and_close,
            bg_color="#2563eb", hover_color="#1d4ed8", text_color="#ffffff",
            font=("Segoe UI Bold", 9), width=140, height=32, radius=6
        )
        btn_save.pack(side="right", padx=(8, 0))

        btn_cancel = ModernButton(
            f_inner, text=t("btn_cancel", lang),
            command=self.destroy,
            bg_color="#1e2230", hover_color="#2c3345", text_color="#94a3b8",
            font=("Segoe UI Semibold", 9), width=85, height=32, radius=6
        )
        btn_cancel.pack(side="right")

    def _open_mouse_menu(self, act_key, btn_widget):
        lang = self.controller.get_language()
        self._cancel_recording()
        menu = tk.Menu(
            self, tearoff=0, bg="#161922", fg="#f8fafc",
            activebackground="#2563eb", activeforeground="#ffffff", font=("Segoe UI", 9)
        )
        options = [
            (t("mouse_mbutton", lang), "MButton"),
            (t("mouse_xbutton1", lang), "XButton1"),
            (t("mouse_xbutton2", lang), "XButton2"),
            (None, None),
            (t("mouse_ctrl_mbutton", lang), "Ctrl+MButton"),
            (t("mouse_ctrl_xbutton1", lang), "Ctrl+XButton1"),
            (t("mouse_ctrl_xbutton2", lang), "Ctrl+XButton2"),
            (None, None),
            (t("mouse_alt_mbutton", lang), "Alt+MButton"),
            (t("mouse_alt_xbutton1", lang), "Alt+XButton1"),
            (t("mouse_alt_xbutton2", lang), "Alt+XButton2"),
            (None, None),
            (t("mouse_ctrl_alt_mbutton", lang), "Ctrl+Alt+MButton"),
            (t("mouse_ctrl_alt_xbutton1", lang), "Ctrl+Alt+XButton1"),
            (t("mouse_ctrl_alt_xbutton2", lang), "Ctrl+Alt+XButton2"),
        ]
        for label, val in options:
            if label is None:
                menu.add_separator()
            else:
                menu.add_command(label=label, command=lambda v=val: self._apply_hotkey(act_key, v))

        try:
            btn_widget.update_idletasks()
            x = btn_widget.winfo_rootx()
            y = btn_widget.winfo_rooty() + btn_widget.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _apply_hotkey(self, act, combo):
        lang = self.controller.get_language()
        self.current_hotkeys[act] = combo
        lbl = self._value_labels.get(act)
        if lbl:
            lbl.config(text=self._format_display(combo), fg="#f8fafc" if combo else "#64748b")

        btn = self._record_buttons.get(act)
        if btn:
            btn.set_text(t("btn_record", lang), bg_color="#1e2230", hover_color="#2c3345")

        self.unbind("<KeyPress>")
        self.unbind("<KeyRelease>")
        self.unbind("<Button-2>")
        self._recording_action = None
        self._pressed_keys.clear()

    def _start_recording(self, action_key):
        lang = self.controller.get_language()
        self._cancel_recording()
        self._recording_action = action_key
        self._pressed_keys.clear()

        btn = self._record_buttons.get(action_key)
        lbl = self._value_labels.get(action_key)

        if btn:
            btn.set_text(t("rec_recording", lang), bg_color="#0284c7", hover_color="#0369a1")
        if lbl:
            lbl.config(text=f"[ {t('rec_prompt', lang)} ]", fg="#38bdf8")

        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Button-2>", lambda e: self._on_mouse_click_record("MButton"))
        self.focus_force()

        # Iniciar sondeo de botones físicos del ratón
        self.after(50, self._poll_mouse_recording)

    def _cancel_recording(self):
        if self._recording_action:
            lang = self.controller.get_language()
            act = self._recording_action
            btn = self._record_buttons.get(act)
            lbl = self._value_labels.get(act)
            val = self.current_hotkeys.get(act, "")

            if btn:
                btn.set_text(t("btn_record", lang), bg_color="#1e2230", hover_color="#2c3345")
            if lbl:
                lbl.config(text=self._format_display(val), fg="#38bdf8" if val else "#64748b")

            self.unbind("<KeyPress>")
            self.unbind("<KeyRelease>")
            self.unbind("<Button-2>")
            self._recording_action = None
            self._pressed_keys.clear()

    def _poll_mouse_recording(self):
        if not self._recording_action:
            return

        user32 = ctypes.windll.user32
        m_btn = None
        if user32.GetAsyncKeyState(0x04) & 0x8000:
            m_btn = "MButton"
        elif user32.GetAsyncKeyState(0x05) & 0x8000:
            m_btn = "XButton1"
        elif user32.GetAsyncKeyState(0x06) & 0x8000:
            m_btn = "XButton2"

        if m_btn:
            self._on_mouse_click_record(m_btn)
            return

        self.after(35, self._poll_mouse_recording)

    def _on_mouse_click_record(self, m_btn):
        if not self._recording_action:
            return
        user32 = ctypes.windll.user32
        mods = []
        if (user32.GetAsyncKeyState(0x11) & 0x8000) or any('Control' in k for k in self._pressed_keys):
            mods.append("Ctrl")
        if (user32.GetAsyncKeyState(0x12) & 0x8000) or any('Alt' in k for k in self._pressed_keys):
            mods.append("Alt")
        if (user32.GetAsyncKeyState(0x10) & 0x8000) or any('Shift' in k for k in self._pressed_keys):
            mods.append("Shift")
        if (user32.GetAsyncKeyState(0x5B) & 0x8000) or (user32.GetAsyncKeyState(0x5C) & 0x8000) or any('Win' in k for k in self._pressed_keys):
            mods.append("Win")

        final_combo = "+".join(mods + [m_btn])
        self._apply_hotkey(self._recording_action, final_combo)

    def _on_key_press(self, event):
        if not self._recording_action:
            return

        ks = event.keysym
        self._pressed_keys.add(ks)

        # Si es solo una tecla modificadora, mostrar en progreso
        mod_syms = ('Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Shift_L', 'Shift_R', 'Win_L', 'Win_R')
        if ks in mod_syms:
            active_mods = []
            if any('Control' in k for k in self._pressed_keys): active_mods.append("Ctrl")
            if any('Alt' in k for k in self._pressed_keys): active_mods.append("Alt")
            if any('Shift' in k for k in self._pressed_keys): active_mods.append("Shift")
            if any('Win' in k for k in self._pressed_keys): active_mods.append("Win")
            self._value_labels[self._recording_action].config(
                text=f"{' + '.join(active_mods)} + ...", fg="#38bdf8"
            )
            return

        # Si presiona Escape solo, cancelar la grabación
        if ks == "Escape" and not (event.state & 0x0004 or event.state & 0x20000 or event.state & 0x0001):
            self._cancel_recording()
            return

        # Tecla final presionada: construir la combinación completa
        mods = []
        if (event.state & 0x0004) or any('Control' in k for k in self._pressed_keys):
            mods.append("Ctrl")
        if (event.state & 0x20000) or (event.state & 0x0008) or any('Alt' in k for k in self._pressed_keys):
            mods.append("Alt")
        if (event.state & 0x0001) or any('Shift' in k for k in self._pressed_keys):
            mods.append("Shift")
        if any('Win' in k for k in self._pressed_keys):
            mods.append("Win")

        key_name = ks.upper()
        special_names = {
            'RETURN': 'Enter', 'SPACE': 'Space', 'ESCAPE': 'Esc',
            'PRIOR': 'PageUp', 'NEXT': 'PageDown',
            'UP': 'Up', 'DOWN': 'Down', 'LEFT': 'Left', 'RIGHT': 'Right'
        }
        key_name = special_names.get(key_name, key_name)

        final_combo = "+".join(mods + [key_name])
        self._apply_hotkey(self._recording_action, final_combo)

    def _on_key_release(self, event):
        if event.keysym in self._pressed_keys:
            self._pressed_keys.discard(event.keysym)

    def _clear_hotkey(self, action_key):
        self._cancel_recording()
        self.current_hotkeys[action_key] = ""
        lbl = self._value_labels.get(action_key)
        if lbl:
            lbl.config(text=self._format_display(""), fg="#64748b")

    def _reset_defaults(self):
        self._cancel_recording()
        self.current_hotkeys = {
            "toggle_tv": "Ctrl+Alt+T",
            "monitors_only": "Ctrl+Alt+M",
            "tv_only": "Ctrl+Alt+V",
            "extend_all": "Ctrl+Alt+E"
        }
        for k, v in self.current_hotkeys.items():
            lbl = self._value_labels.get(k)
            if lbl:
                lbl.config(text=self._format_display(v), fg="#38bdf8" if v else "#64748b")

    def _save_and_close(self):
        self._cancel_recording()
        self.controller.set_hotkeys(self.current_hotkeys)
        if self.tray:
            self.tray.reload_hotkeys()
            app_t = self.controller.get_app_title()
            lang = self.controller.get_language()
            msg = "Settings and hotkeys updated." if lang == "en" else "Configuración y atajos actualizados."
            self.tray.show_notification(app_t, msg)
        if self.on_saved:
            self.on_saved()
        self.destroy()


HotkeySettingsModal = SettingsModal


class ModernTrayMenu(tk.Toplevel):
    """
    Menú contextual flotante moderno para el System Tray.
    Diseñado específicamente para verse 100% nítido en Windows 11 con fondo oscuro,
    texto blanco brillante, soporte completo de iconos/emojis y atajos de teclado.
    Se auto-cierra al hacer clic fuera o presionar Escape.
    """
    def __init__(self, app, x=None, y=None):
        super().__init__(app.root)
        self.app = app
        self.controller = app.controller
        self.tray = app.tray

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#2b3040")

        if x is None or y is None:
            pt = wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            x, y = pt.x, pt.y

        self.cursor_x = x
        self.cursor_y = y

        self._build_items()
        self._position_menu()

        self.bind("<Escape>", lambda e: self.close())
        self.after(150, self._monitor_outside_clicks)

    def _build_items(self):
        container = tk.Frame(self, bg="#161922", padx=4, pady=4)
        container.pack(fill="both", expand=True, padx=1, pady=1)

        lang = self.controller.get_language()
        hotkeys = self.controller.get_hotkeys()
        hk_toggle = format_hotkey_display(hotkeys.get("toggle_tv", ""), lang=lang, for_tray=True)
        hk_monitors = format_hotkey_display(hotkeys.get("monitors_only", ""), lang=lang, for_tray=True)
        hk_tv_only = format_hotkey_display(hotkeys.get("tv_only", ""), lang=lang, for_tray=True)
        hk_extend = format_hotkey_display(hotkeys.get("extend_all", ""), lang=lang, for_tray=True)

        tv = self.controller.get_designated_tv()
        if tv:
            if tv.is_active:
                toggle_label = t("tray_toggle_off", lang, name=tv.friendly_name[:14])
            else:
                toggle_label = t("tray_toggle_on", lang, name=tv.friendly_name[:14])
        else:
            toggle_label = t("tray_toggle_default", lang)

        menu_def = [
            (toggle_label, hk_toggle, self._cmd_toggle),
            (None, None, None),
            (t("tray_monitors_only", lang), hk_monitors, self._cmd_monitors_only),
            (t("tray_tv_only", lang), hk_tv_only, self._cmd_tv_only),
            (t("tray_extend_all", lang), hk_extend, self._cmd_extend_all),
            (None, None, None),
            (t("tray_settings", lang), "", self._cmd_settings),
            (t("tray_open_app", lang, title=self.controller.get_app_title()), "", self._cmd_open_app),
            (None, None, None),
            (t("tray_exit", lang), "", self._cmd_exit),
        ]

        for label, hk, cmd in menu_def:
            if label is None:
                sep = tk.Frame(container, bg="#262b3b", height=1)
                sep.pack(fill="x", padx=6, pady=4)
                continue

            row = tk.Frame(container, bg="#161922", cursor="hand2")
            row.pack(fill="x", pady=1)

            lbl_left = tk.Label(
                row, text=f"  {label}", bg="#161922", fg="#f8fafc",
                font=("Segoe UI", 9), anchor="w"
            )
            lbl_left.pack(side="left", fill="x", expand=True, pady=5)

            lbl_right = None
            if hk:
                lbl_right = tk.Label(
                    row, text=f"{hk}  ", bg="#161922", fg="#94a3b8",
                    font=("Segoe UI Semibold", 8), anchor="e"
                )
                lbl_right.pack(side="right", pady=5)

            def make_hover(r=row, l1=lbl_left, l2=lbl_right):
                def on_enter(e):
                    r.configure(bg="#2563eb")
                    l1.configure(bg="#2563eb", fg="#ffffff")
                    if l2:
                        l2.configure(bg="#2563eb", fg="#e0e7ff")
                def on_leave(e):
                    r.configure(bg="#161922")
                    l1.configure(bg="#161922", fg="#f8fafc")
                    if l2:
                        l2.configure(bg="#161922", fg="#94a3b8")
                return on_enter, on_leave

            enter_fn, leave_fn = make_hover()

            def make_click(command=cmd):
                def on_click(e):
                    self.close()
                    if command:
                        command()
                return on_click

            click_fn = make_click()

            for w in [row, lbl_left] + ([lbl_right] if lbl_right else []):
                w.bind("<Enter>", enter_fn)
                w.bind("<Leave>", leave_fn)
                w.bind("<Button-1>", click_fn)

    def _position_menu(self):
        self.update_idletasks()
        w = max(260, self.winfo_reqwidth())
        h = self.winfo_reqheight()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        if self.cursor_x + w > screen_w:
            pos_x = max(8, self.cursor_x - w)
        else:
            pos_x = self.cursor_x

        if self.cursor_y + h > screen_h:
            pos_y = max(8, self.cursor_y - h - 8)
        else:
            pos_y = self.cursor_y + 8

        pos_x = max(8, min(pos_x, screen_w - w - 8))
        pos_y = max(8, min(pos_y, screen_h - h - 8))

        self.geometry(f"{w}x{h}+{pos_x}+{pos_y}")
        self.focus_force()

    def _monitor_outside_clicks(self):
        if not self.winfo_exists():
            return
        user32 = ctypes.windll.user32
        l_down = user32.GetAsyncKeyState(0x01) & 0x8000
        r_down = user32.GetAsyncKeyState(0x02) & 0x8000
        if l_down or r_down:
            pt = wintypes.POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            try:
                wx = self.winfo_rootx()
                wy = self.winfo_rooty()
                ww = self.winfo_width()
                wh = self.winfo_height()
                if not (wx <= pt.x <= wx + ww and wy <= pt.y <= wy + wh):
                    self.close()
                    return
            except Exception:
                self.close()
                return

        self.after(35, self._monitor_outside_clicks)

    def close(self):
        try:
            self.destroy()
        except Exception:
            pass

    def _cmd_toggle(self):
        self.app.toggle_tv()

    def _cmd_monitors_only(self):
        self.app.set_mode("monitors_only")

    def _cmd_tv_only(self):
        self.app.set_mode("tv_only")

    def _cmd_extend_all(self):
        self.app.set_mode("extend")

    def _cmd_settings(self):
        self.app.show_from_tray()
        self.app.open_settings_modal()

    def _cmd_hotkey_settings(self):
        self._cmd_settings()

    def _cmd_open_app(self):
        self.app.show_from_tray()

    def _cmd_exit(self):
        self.app._on_exit()


class DisplayFlowApp:
    def __init__(self, root, controller, tray_manager):
        self.root = root
        self.controller = controller
        self.tray = tray_manager
        self._active_tray_menu = None

        self.root.title(self.controller.get_app_title())
        self.root.geometry("780x780")
        self.root.minsize(760, 760)
        self.root.configure(bg="#0f1117")

        # Configurar icono propio en la ventana y barra de tareas
        self._setup_window_icon()

        self.is_busy = False
        self._last_state_signature = None
        self.startup_var = tk.BooleanVar(value=self._check_startup_enabled())
        self.legacy_var = tk.BooleanVar(value=self.controller.get_legacy_mode())

        self._setup_styles()
        self._build_ui()
        self._refresh_monitors_ui(force=True)

        # Sondeo de estado suave cada 3.5s (solo redibuja si la firma del estado cambió)
        self.root.after(3500, self._auto_poll_state)

        # Minimizar a bandeja al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def _setup_window_icon(self):
        """Aplica el icono personalizado de Fede en la ventana y barra de tareas"""
        app_dir = os.path.dirname(os.path.abspath(__file__))
        self._ico_path = os.path.join(app_dir, "app_icon.ico")

        # Establecer AppUserModelID consistente con main.py para la barra de tareas
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Fede.DisplaySwitch.App.2.0")
        except Exception:
            pass

        if os.path.exists(self._ico_path):
            try:
                self.root.iconbitmap(default=self._ico_path)
                self.root.iconbitmap(self._ico_path)
            except Exception:
                pass

        # Forzar iconos nativos de Win32 para asegurar que la barra de tareas muestre el icono de Fede
        self._apply_native_win32_icon()
        self.root.bind("<Map>", lambda e: self._apply_native_win32_icon())

    def _apply_native_win32_icon(self):
        """Aplica los iconos nativos de Win32 en la ventana y clase de ventana"""
        if not hasattr(self, "_ico_path") or not os.path.exists(self._ico_path):
            return
        try:
            self.root.update_idletasks()
            user32 = ctypes.windll.user32
            hwnd = user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()

            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1
            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x00000010
            GCLP_HICON = -14
            GCLP_HICONSM = -34

            hicon_big = user32.LoadImageW(None, self._ico_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
            hicon_sm = user32.LoadImageW(None, self._ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
            hicon_32 = user32.LoadImageW(None, self._ico_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)

            h_main = hicon_big or hicon_32
            if h_main:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_main)
                user32.SetClassLongPtrW(hwnd, GCLP_HICON, h_main)
            if hicon_sm:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_sm)
                user32.SetClassLongPtrW(hwnd, GCLP_HICONSM, hicon_sm)
        except Exception:
            pass

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#0f1117")
        style.configure("TLabel", background="#0f1117", foreground="#f8fafc", font=("Segoe UI", 9))
        style.configure("Vertical.TScrollbar", background="#1e2230", bordercolor="#0f1117", arrowcolor="#94a3b8")
        style.map('TCombobox', fieldbackground=[('readonly', '#1e2230')])
        style.map('TCombobox', selectbackground=[('readonly', '#2563eb')])
        style.map('TCombobox', selectforeground=[('readonly', '#ffffff')])
        style.configure('TCombobox', background='#1e2230', foreground='#f8fafc', arrowcolor='#38bdf8', borderwidth=0)
        try:
            self.root.option_add('*TCombobox*Listbox.background', '#161922')
            self.root.option_add('*TCombobox*Listbox.foreground', '#f8fafc')
            self.root.option_add('*TCombobox*Listbox.selectBackground', '#2563eb')
            self.root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')
            self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI Semibold', 8))
        except Exception:
            pass

    def _get_toggle_hotkey_text(self):
        hotkeys = self.controller.get_hotkeys()
        val = hotkeys.get("toggle_tv", "Ctrl+Alt+T")
        lang = self.controller.get_language()
        if not val:
            return t("hk_none", lang)
        return format_hotkey_display(val, lang=lang, for_tray=True)

    def retranslate_ui(self):
        """Actualiza todos los textos de la interfaz principal al cambiar de idioma"""
        lang = self.controller.get_language()
        app_t = self.controller.get_app_title()
        self.root.title(app_t)
        self.app_title_lbl.config(text=f"⚡ {app_t}")
        if hasattr(self, "subtitle_lbl"):
            self.subtitle_lbl.config(text=t("app_subtitle", lang))
        if hasattr(self, "btn_detect"):
            self.btn_detect.set_text(t("detect_displays", lang))
        if hasattr(self, "sec_label"):
            self.sec_label.config(text=t("section_displays", lang))
        if hasattr(self, "tv_tip_label"):
            self.tv_tip_label.config(text=t("tip_displays", lang))
        if hasattr(self, "modes_header"):
            self.modes_header.config(text=t("section_modes", lang))
        if hasattr(self, "btn_solo_monitores"):
            self.btn_solo_monitores.set_text(t("btn_monitors_only", lang))
        if hasattr(self, "btn_solo_tv"):
            self.btn_solo_tv.set_text(t("btn_tv_only", lang))
        if hasattr(self, "btn_extender"):
            self.btn_extender.set_text(t("btn_extend_all", lang))
        if hasattr(self, "btn_settings"):
            self.btn_settings.set_text(t("btn_settings", lang))
        if hasattr(self, "btn_about"):
            self.btn_about.config(text=t("footer_copyright", lang))
        if hasattr(self, "tray_btn"):
            self.tray_btn.set_text(t("btn_hide_tray", lang))
        if self.tray:
            self.tray.update_tooltip(t("tray_tip_running", lang, title=app_t))
        self._refresh_monitors_ui(force=True)

    def _build_ui(self):
        lang = self.controller.get_language()

        # 1. HEADER BAR
        header_frame = tk.Frame(self.root, bg="#141721", height=72)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_box = tk.Frame(header_frame, bg="#141721")
        title_box.pack(side="left", padx=24, pady=12)

        self.app_title_lbl = tk.Label(
            title_box, text=f"⚡ {self.controller.get_app_title()}", font=("Segoe UI Bold", 15),
            bg="#141721", fg="#f8fafc"
        )
        self.app_title_lbl.pack(anchor="w")

        self.subtitle_lbl = tk.Label(
            title_box, text=t("app_subtitle", lang),
            font=("Segoe UI", 9), bg="#141721", fg="#94a3b8"
        )
        self.subtitle_lbl.pack(anchor="w")

        # Indicador de estado y botón buscar pantallas
        right_header = tk.Frame(header_frame, bg="#141721")
        right_header.pack(side="right", padx=24)

        self.status_pill = tk.Label(
            right_header, text=t("status_ready", lang), font=("Segoe UI Semibold", 8),
            bg="#1e293b", fg="#10b981", padx=10, pady=5
        )
        self.status_pill.pack(side="right", padx=(8, 0))

        self.btn_detect = ModernButton(
            right_header, text=t("detect_displays", lang),
            command=self._detect_new_displays,
            bg_color="#1e2230", hover_color="#2c3345", text_color="#38bdf8",
            font=("Segoe UI Semibold", 8), width=130, height=28, radius=6
        )
        self.btn_detect.pack(side="right")

        # Separador
        sep = tk.Frame(self.root, bg="#262b3b", height=1)
        sep.pack(fill="x")

        # 2. CONTENIDO PRINCIPAL (Responsivo centrado en pantalla completa)
        self.content_outer = tk.Frame(self.root, bg="#0f1117")
        self.content_outer.pack(fill="both", expand=True)

        self.content = tk.Frame(self.content_outer, bg="#0f1117")
        self.content.pack(expand=True, fill="both", padx=20, pady=12)

        self.root.bind("<Configure>", self._on_window_configure)

        # Hero Action Toggle (Botón principal para la TV asignada)
        hero_box = tk.Frame(self.content, bg="#0f1117")
        hero_box.pack(fill="x", pady=(0, 14))

        self.hero_btn = ModernButton(
            hero_box,
            text="",
            command=self.toggle_tv,
            bg_color="#dc2626",
            hover_color="#b91c1c",
            font=("Segoe UI Bold", 12),
            width=680,
            height=48,
            radius=10
        )
        self.hero_btn.pack(fill="x")

        self.hero_subtext = tk.Label(
            hero_box, text="",
            font=("Segoe UI", 8), bg="#0f1117", fg="#64748b"
        )
        self.hero_subtext.pack(pady=(4, 0))

        # Sección: Lista Dinámica de Pantallas
        list_header_row = tk.Frame(self.content, bg="#0f1117")
        list_header_row.pack(fill="x", pady=(0, 6))

        self.sec_label = tk.Label(
            list_header_row, text=t("section_displays", lang),
            font=("Segoe UI Bold", 9), bg="#0f1117", fg="#64748b"
        )
        self.sec_label.pack(side="left")

        self.tv_tip_label = tk.Label(
            list_header_row, text=t("tip_displays", lang),
            font=("Segoe UI", 8), bg="#0f1117", fg="#94a3b8"
        )
        self.tv_tip_label.pack(side="right")

        # Canvas con scrollbar inteligente auto-ocultable
        cards_scroll_frame = tk.Frame(self.content, bg="#0f1117")
        cards_scroll_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.canvas = tk.Canvas(cards_scroll_frame, bg="#0f1117", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(cards_scroll_frame, orient="vertical", command=self.canvas.yview)
        self.cards_inner = tk.Frame(self.canvas, bg="#0f1117")

        self.cards_inner.bind("<Configure>", self._on_cards_configure)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_inner, anchor="nw")
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 3. MODOS RÁPIDOS GLOBALES
        self.modes_header = tk.Label(
            self.content, text=t("section_modes", lang), font=("Segoe UI Bold", 9),
            bg="#0f1117", fg="#64748b"
        )
        self.modes_header.pack(anchor="w", pady=(2, 6))

        modes_row = tk.Frame(self.content, bg="#0f1117")
        modes_row.pack(fill="x", pady=(0, 8))

        self.btn_solo_monitores = ModernButton(
            modes_row, text=t("btn_monitors_only", lang),
            command=lambda: self.set_mode("monitors_only"),
            bg_color="#1a1d26", hover_color="#2a3040",
            font=("Segoe UI Semibold", 9), width=220, height=38, radius=8
        )
        self.btn_solo_monitores.pack(side="left", padx=(0, 4), expand=True, fill="x")

        self.btn_solo_tv = ModernButton(
            modes_row, text=t("btn_tv_only", lang),
            command=lambda: self.set_mode("tv_only"),
            bg_color="#1a1d26", hover_color="#2a3040",
            font=("Segoe UI Semibold", 9), width=220, height=38, radius=8
        )
        self.btn_solo_tv.pack(side="left", padx=(4, 4), expand=True, fill="x")

        self.btn_extender = ModernButton(
            modes_row, text=t("btn_extend_all", lang),
            command=lambda: self.set_mode("extend"),
            bg_color="#1a1d26", hover_color="#2a3040",
            font=("Segoe UI Semibold", 9), width=220, height=38, radius=8
        )
        self.btn_extender.pack(side="left", padx=(4, 0), expand=True, fill="x")

        # 4. FOOTER Y AJUSTES
        footer = tk.Frame(self.root, bg="#141721", height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ft_inner = tk.Frame(footer, bg="#141721")
        ft_inner.pack(fill="both", expand=True, padx=20, pady=8)

        left_box = tk.Frame(ft_inner, bg="#141721")
        left_box.pack(side="left")

        self.btn_settings = ModernButton(
            left_box, text=t("btn_settings", lang),
            command=self.open_settings_modal,
            bg_color="#1e2230", hover_color="#2c3345", text_color="#38bdf8",
            font=("Segoe UI Semibold", 9), width=145, height=30, radius=6
        )
        self.btn_settings.pack(side="left")

        self.btn_about = tk.Label(
            left_box, text=t("footer_copyright", lang),
            font=("Segoe UI", 8, "underline"), bg="#141721", fg="#64748b",
            cursor="hand2"
        )
        self.btn_about.pack(side="left", padx=(14, 0))
        self.btn_about.bind("<Button-1>", lambda e: self.open_about_dialog())

        self.tray_btn = ModernButton(
            ft_inner, text=t("btn_hide_tray", lang),
            command=self.hide_to_tray,
            bg_color="#1e2230", hover_color="#2c3345", text_color="#94a3b8",
            font=("Segoe UI", 8), width=155, height=30, radius=6
        )
        self.tray_btn.pack(side="right")

    def _on_window_configure(self, event):
        """Adapta el contenedor central según el ancho de la ventana para una estética perfecta"""
        if event.widget == self.root:
            win_w = self.root.winfo_width()
            if win_w > 1150:
                side_pad = max(20, (win_w - 1040) // 2)
                self.content.pack_configure(padx=side_pad, fill="both")
            else:
                self.content.pack_configure(padx=18, fill="both")

    def _on_cards_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.root.after_idle(self._check_scrollbar_visibility)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.root.after_idle(self._check_scrollbar_visibility)

    def _check_scrollbar_visibility(self):
        """Oculta la barra de scroll si el contenido cabe completamente en el lienzo"""
        try:
            bbox = self.canvas.bbox("all")
            if not bbox:
                return
            content_h = bbox[3] - bbox[1]
            canvas_h = self.canvas.winfo_height()
            if content_h > (canvas_h + 10) and canvas_h > 80:
                if not self.scrollbar.winfo_ismapped():
                    self.scrollbar.pack(side="right", fill="y")
            else:
                if self.scrollbar.winfo_ismapped():
                    self.scrollbar.pack_forget()
        except Exception:
            pass

    def open_about_dialog(self):
        """Abre el diálogo modal con información legal y créditos de Software Libre"""
        AboutModal(self.root, self.controller)

    def _on_toggle_legacy_mode(self):
        """Alterna el modo Legacy y actualiza los títulos en caliente"""
        val = self.legacy_var.get()
        self.controller.set_legacy_mode(val)
        app_t = self.controller.get_app_title()
        self.root.title(app_t)
        self.app_title_lbl.config(text=f"⚡ {app_t}")
        if self.tray:
            self.tray.update_tooltip(f"{app_t}: Activo")

    def open_settings_modal(self):
        """Abre la ventana modal unificada de Configuración"""
        SettingsModal(self.root, self.controller, self.tray, app=self, on_saved_callback=self._on_settings_updated)

    def open_hotkey_settings(self):
        """Redirige al gestor unificado de Configuración"""
        self.open_settings_modal()

    def _on_settings_updated(self):
        """Actualiza la interfaz tras guardar configuraciones"""
        app_t = self.controller.get_app_title()
        self.root.title(app_t)
        self.app_title_lbl.config(text=f"⚡ {app_t}")
        hk_toggle = self._get_toggle_hotkey_text()
        self.hero_subtext.config(text=f"Alterna la pantalla designada como televisor (Atajo: {hk_toggle})")
        self._refresh_monitors_ui(force=True)

    def _on_hotkeys_updated(self):
        self._on_settings_updated()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _refresh_monitors_ui(self, force=False):
        """
        Reconstruye dinámicamente las tarjetas de monitores solo si el estado real cambió,
        evitando por completo el parpadeo (flickering).
        """
        signature = self.controller.get_state_signature()
        lang = self.controller.get_language()
        app_t = self.controller.get_app_title()

        if not force and signature == self._last_state_signature:
            return

        self._last_state_signature = signature

        monitors = self.controller.get_connected_monitors()
        tv = self.controller.get_designated_tv()
        is_tv_on = self.controller.is_tv_active()
        hk_toggle = self._get_toggle_hotkey_text()

        # Limpiar tarjetas existentes
        for widget in self.cards_inner.winfo_children():
            widget.destroy()

        # Actualizar botón principal Hero según el televisor designado
        if tv:
            tv_name = tv.friendly_name
            if is_tv_on:
                self.hero_btn.set_text(t("hero_turn_off", lang, tv=tv_name), bg_color="#dc2626", hover_color="#b91c1c")
                self.hero_subtext.config(text=t("hero_sub_off", lang, tv=tv_name, hk=hk_toggle))
                active_count = len([m for m in monitors if m.is_active])
                self.status_pill.config(text=t("status_active", lang, count=active_count), fg="#10b981")
                if self.tray:
                    self.tray.update_tooltip(t("tray_tip_active", lang, title=app_t, tv=tv_name))
            else:
                self.hero_btn.set_text(t("hero_turn_on", lang, tv=tv_name), bg_color="#059669", hover_color="#047857")
                self.hero_subtext.config(text=t("hero_sub_on", lang, tv=tv_name, hk=hk_toggle))
                self.status_pill.config(text=t("status_tv_off", lang, tv=tv_name), fg="#38bdf8")
                if self.tray:
                    self.tray.update_tooltip(t("tray_tip_off", lang, title=app_t, tv=tv_name))
        else:
            self.hero_btn.set_text(t("hero_select_tv", lang), bg_color="#3b82f6", hover_color="#2563eb")
            self.hero_subtext.config(text=t("hero_sub_select", lang))
            active_count = len([m for m in monitors if m.is_active])
            self.status_pill.config(text=t("status_no_tv", lang, count=active_count), fg="#94a3b8")
            if self.tray:
                self.tray.update_tooltip(t("tray_tip_no_tv", lang, title=app_t))

        # Generar una tarjeta para cada monitor
        for m in monitors:
            self._create_monitor_card(m)

    def _create_monitor_card(self, m):
        """Crea una tarjeta estilizada para un monitor específico"""
        lang = self.controller.get_language()
        is_tv = m.is_designated_tv
        border_color = "#10b981" if (is_tv and m.is_active) else ("#6366f1" if is_tv else "#262b3b")
        card_bg = "#161922" if is_tv else "#141721"

        card = tk.Frame(self.cards_inner, bg=card_bg, highlightbackground=border_color, highlightthickness=1)
        card.pack(fill="x", pady=5, ipady=6)

        inner = tk.Frame(card, bg=card_bg)
        inner.pack(fill="x", padx=14, pady=6)

        # Icono
        icon_str = "📺" if is_tv else "🖥️"
        icon_lbl = tk.Label(inner, text=icon_str, font=("Segoe UI", 22), bg=card_bg)
        icon_lbl.pack(side="left", padx=(0, 12))

        # Acciones a la derecha (se empaquetan primero para garantizar espacio intacto de controles y Hz)
        actions_box = tk.Frame(inner, bg=card_bg)
        actions_box.pack(side="right", padx=(8, 0))

        # Información central (ocupa todo el espacio restante disponible)
        info_box = tk.Frame(inner, bg=card_bg)
        info_box.pack(side="left", fill="both", expand=True)

        title_row = tk.Frame(info_box, bg=card_bg)
        title_row.pack(fill="x")

        # Nombre del monitor
        name_lbl = tk.Label(
            title_row, text=m.friendly_name, font=("Segoe UI Bold", 11),
            bg=card_bg, fg="#ffffff"
        )
        name_lbl.pack(side="left")

        # Etiquetas (Principal / Televisor Designado / Monitor)
        if getattr(m, 'is_designated_primary', False):
            des_badge = tk.Label(
                title_row, text=t("badge_designated_primary", lang), font=("Segoe UI Bold", 7),
                bg="#854d0e", fg="#fef08a", padx=6, pady=2
            )
            des_badge.pack(side="left", padx=6)
        elif m.is_primary:
            prim_badge = tk.Label(
                title_row, text=t("badge_primary", lang), font=("Segoe UI Bold", 7),
                bg="#1e293b", fg="#94a3b8", padx=6, pady=2
            )
            prim_badge.pack(side="left", padx=6)

        if is_tv:
            tv_tag = tk.Label(
                title_row, text=t("badge_designated_tv", lang), font=("Segoe UI Bold", 7),
                bg="#312e81", fg="#a5b4fc", padx=6, pady=2
            )
            tv_tag.pack(side="left", padx=4)
        else:
            mon_tag = tk.Label(
                title_row, text=t("badge_monitor", lang), font=("Segoe UI Bold", 7),
                bg="#0e2a3f", fg="#38bdf8", padx=6, pady=2
            )
            mon_tag.pack(side="left", padx=4)

        # Especificaciones
        specs_str = f"{m.width}x{m.height} @ {m.hz}Hz" if m.width and m.hz else t("res_native", lang)
        details_list = [specs_str]
        if m.gdi_name:
            details_list.append(f"{t('card_port', lang)}: {m.gdi_name}")
        if m.short_id:
            details_list.append(f"{t('card_id', lang)}: {m.short_id}")

        specs_lbl = tk.Label(
            info_box, text="  •  ".join(details_list),
            font=("Segoe UI", 8), bg=card_bg, fg="#94a3b8"
        )
        specs_lbl.pack(anchor="w", pady=(2, 0))

        # 1. Badge de estado activo/inactivo
        if m.is_active:
            status_lbl = tk.Label(
                actions_box, text=t("badge_active", lang), font=("Segoe UI Bold", 8),
                bg="#064e3b", fg="#34d399", padx=8, pady=4
            )
        else:
            status_lbl = tk.Label(
                actions_box, text=t("badge_off", lang), font=("Segoe UI Bold", 8),
                bg="#262b3b", fg="#94a3b8", padx=8, pady=4
            )
        status_lbl.pack(side="right", padx=(4, 0))

        # 2. Botón individual para activar/desactivar (si no es el primario)
        if not m.is_primary:
            if m.is_active:
                btn_toggle = ModernButton(
                    actions_box, text=t("btn_card_turn_off", lang),
                    command=lambda mon=m: self._toggle_specific_monitor(mon),
                    bg_color="#7f1d1d", hover_color="#991b1b",
                    font=("Segoe UI Semibold", 8), width=85, height=28, radius=6
                )
            else:
                btn_toggle = ModernButton(
                    actions_box, text=t("btn_card_turn_on", lang),
                    command=lambda mon=m: self._toggle_specific_monitor(mon),
                    bg_color="#065f46", hover_color="#047857",
                    font=("Segoe UI Semibold", 8), width=85, height=28, radius=6
                )
            btn_toggle.pack(side="right", padx=4)

        # 3. Botón para setear o quitar como Televisor
        if is_tv:
            btn_unset_tv = ModernButton(
                actions_box, text=t("btn_unset_tv", lang),
                command=lambda mon=m: self._unset_as_tv(mon),
                bg_color="#262b3b", hover_color="#374151", text_color="#cbd5e1",
                font=("Segoe UI Semibold", 8), width=90, height=28, radius=6
            )
            btn_unset_tv.pack(side="right", padx=4)
        else:
            btn_set_tv = ModernButton(
                actions_box, text=t("btn_set_tv", lang),
                command=lambda mon=m: self._set_as_tv(mon),
                bg_color="#1e2230", hover_color="#3730a3", text_color="#cbd5e1",
                font=("Segoe UI Semibold", 8), width=115, height=28, radius=6
            )
            btn_set_tv.pack(side="right", padx=4)

            # 3.5 Botón para designar como Monitor Principal por defecto
            if not getattr(m, 'is_designated_primary', False):
                btn_set_primary = ModernButton(
                    actions_box, text=t("btn_set_primary", lang),
                    command=lambda mon=m: self._set_as_primary(mon),
                    bg_color="#1e2230", hover_color="#854d0e", text_color="#fef08a",
                    font=("Segoe UI Semibold", 8), width=110, height=28, radius=6
                )
                btn_set_primary.pack(side="right", padx=4)

        # 4. Selector de Tasa de Refresco de Inicio (Hz)
        if m.available_refresh_rates:
            hz_box = tk.Frame(actions_box, bg=card_bg)
            hz_box.pack(side="right", padx=(0, 6))

            hz_lbl = tk.Label(hz_box, text=t("card_startup_hz", lang), font=("Segoe UI", 8), bg=card_bg, fg="#94a3b8")
            hz_lbl.pack(side="left", padx=(0, 3))

            current_hz_val = f"{m.startup_hz or m.hz} Hz"
            hz_var = tk.StringVar(value=current_hz_val)
            hz_options = [f"{x} Hz" for x in m.available_refresh_rates]

            cb_hz = ttk.Combobox(
                hz_box, textvariable=hz_var, values=hz_options,
                state="readonly", width=7, font=("Segoe UI Semibold", 8)
            )
            cb_hz.pack(side="left")

            def on_hz_selected(event, mon=m, var=hz_var):
                sel = var.get().replace("Hz", "").strip()
                if sel.isdigit():
                    self._on_change_refresh_rate(mon, int(sel))

            cb_hz.bind("<<ComboboxSelected>>", on_hz_selected)

    def _on_change_refresh_rate(self, monitor, new_hz):
        """Aplica y guarda la tasa de refresco para el monitor de forma asíncrona para no congelar la UI"""
        ident = monitor.short_id or monitor.friendly_name
        lang = self.controller.get_language()
        self.status_pill.config(text=t("status_applying_hz", lang, hz=new_hz), fg="#38bdf8")
        
        def worker():
            ok, msg = self.controller.set_refresh_rate(ident, new_hz)
            def done():
                self._refresh_monitors_ui(force=True)
                if self.tray:
                    app_t = self.controller.get_app_title()
                    self.tray.show_notification(app_t, t("notif_hz_applied", lang, name=monitor.friendly_name, hz=new_hz))
            self.root.after(0, done)

        import threading
        threading.Thread(target=worker, daemon=True).start()

    def _set_as_tv(self, monitor):
        """Setea el monitor elegido como el televisor y los otros como monitores"""
        ok, msg = self.controller.set_designated_tv(monitor)
        self._refresh_monitors_ui(force=True)
        if self.tray:
            self.tray.show_notification(self.controller.get_app_title(), msg)

    def _unset_as_tv(self, monitor):
        """Desmarca el monitor como televisor para que todas las pantallas sean monitores"""
        ok, msg = self.controller.unset_designated_tv()
        self._refresh_monitors_ui(force=True)
        if self.tray:
            self.tray.show_notification(self.controller.get_app_title(), msg)

    def _set_as_primary(self, monitor):
        """Designa un monitor como el Monitor Principal por defecto y lo aplica en Windows"""
        if self.is_busy:
            return
        lang = self.controller.get_language()
        name = monitor.friendly_name if hasattr(monitor, 'friendly_name') else str(monitor)
        self._run_async(
            lambda: self.controller.set_designated_primary(monitor),
            f"⭐ {name}"
        )

    def _toggle_specific_monitor(self, monitor):
        """Alterna el estado de un monitor específico"""
        if self.is_busy:
            return
        lang = self.controller.get_language()
        status_msg = t("action_turning_off", lang, name=monitor.friendly_name) if monitor.is_active else t("action_turning_on", lang, name=monitor.friendly_name)
        self._run_async(
            lambda: self.controller.toggle_monitor(monitor),
            status_msg
        )

    def _detect_new_displays(self):
        """Fuerza un escaneo profundo de nuevas pantallas conectadas"""
        lang = self.controller.get_language()
        self.status_pill.config(text=t("status_scanning", lang), fg="#fbbf24")
        self.root.update_idletasks()
        monitors = self.controller.get_connected_monitors(force_refresh=True)
        self._refresh_monitors_ui(force=True)
        self.status_pill.config(text=t("status_detected", lang, count=len(monitors)), fg="#10b981")
        if self.tray:
            self.tray.show_notification(self.controller.get_app_title(), t("notif_displays_detected", lang, count=len(monitors)))

    def _auto_poll_state(self):
        """Sondeo suave periódico (solo actualiza si el estado cambió)"""
        if not self.is_busy:
            self._refresh_monitors_ui(force=False)
        self.root.after(3500, self._auto_poll_state)

    def toggle_tv(self):
        """Alternar el televisor designado"""
        if self.is_busy:
            return
        lang = self.controller.get_language()
        tv = self.controller.get_designated_tv()
        if not tv:
            messagebox.showinfo(t("dialog_no_tv_title", lang), t("dialog_no_tv_msg", lang))
            return
        tv_name = tv.friendly_name
        self._run_async(self.controller.toggle_tv, t("action_toggling", lang, name=tv_name))

    def set_mode(self, mode):
        """Establecer modo global de pantallas"""
        if self.is_busy:
            return
        lang = self.controller.get_language()
        if mode in ("monitors_only", "internal"):
            desc = t("btn_monitors_only", lang)
        elif mode in ("tv_only", "solotv", "solo_tv"):
            desc = t("btn_tv_only", lang)
        else:
            desc = t("btn_extend_all", lang)
        self._run_async(lambda: self.controller.set_mode(mode), t("action_applying_mode", lang, mode=desc))

    def _run_async(self, func, status_text):
        self.is_busy = True
        self.hero_btn.set_enabled(False)
        self.status_pill.config(text=f"⏳ {status_text}", fg="#fbbf24")

        def worker():
            ok, msg = func()
            self.root.after(0, lambda: self._on_async_done(ok, msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_async_done(self, ok, msg):
        self.is_busy = False
        self.hero_btn.set_enabled(True)
        self._refresh_monitors_ui(force=True)

        if self.tray:
            self.tray.show_notification(self.controller.get_app_title(), msg)

    def hide_to_tray(self):
        self.root.withdraw()
        lang = self.controller.get_language()
        hk = self._get_toggle_hotkey_text()
        msg = t("notif_hidden_tray", lang, hk=hk) if hk != t("hk_none", lang) else t("notif_hidden_tray_no_hk", lang)
        if self.tray:
            self.tray.show_notification(self.controller.get_app_title(), msg)

    def show_from_tray(self):
        try:
            self.root.deiconify()
            self.root.state('normal')
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(lambda: self.root.attributes('-topmost', False))
            self.root.focus_force()

            # Forzar primer plano a nivel Win32 si está en segundo plano o minimizada
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
                ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
        except Exception:
            pass
        self._refresh_monitors_ui(force=True)

    def _check_startup_enabled(self):
        startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
        vbs_path = os.path.join(startup_dir, "DisplaySwitch.vbs")
        return os.path.exists(vbs_path)

    def _on_toggle_startup(self):
        enabled = self.startup_var.get()
        startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
        vbs_target = os.path.join(startup_dir, "DisplaySwitch.vbs")
        
        app_dir = os.path.dirname(os.path.abspath(__file__))
        source_vbs = os.path.join(app_dir, "DisplaySwitch.vbs")

        try:
            old_vbs_target = os.path.join(startup_dir, "DisplayFlow.vbs")
            if os.path.exists(old_vbs_target):
                try: os.remove(old_vbs_target)
                except Exception: pass
            if enabled:
                if os.path.exists(source_vbs):
                    import shutil
                    shutil.copy2(source_vbs, vbs_target)
                else:
                    with open(vbs_target, "w", encoding="utf-8") as f:
                        f.write(f'CreateObject("Wscript.Shell").Run "pyw ""{os.path.join(app_dir, "main.py")}""", 0, False\n')
            else:
                if os.path.exists(vbs_target):
                    os.remove(vbs_target)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el inicio con Windows: {e}")

    def show_tray_menu(self, x=None, y=None):
        """Muestra el menú contextual flotante moderno en el System Tray"""
        if hasattr(self, "_active_tray_menu") and self._active_tray_menu:
            try:
                self._active_tray_menu.destroy()
            except Exception:
                pass
            self._active_tray_menu = None

        self._active_tray_menu = ModernTrayMenu(self, x, y)

    def _on_exit(self):
        """Cierre seguro y completo de la aplicación"""
        if self.tray:
            self.tray.stop()
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)
