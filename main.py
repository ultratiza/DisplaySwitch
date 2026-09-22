"""
DisplaySwitch - Main Application Entrypoint
Copyright (C) 2026 UltraTiza, FedeFadda
Testing & Quality Assurance: FedeNahas
Licencia: Software Libre (GPLv3)
"""

import tkinter as tk
import sys
import os
import ctypes

# Asegurar que el directorio de la aplicación esté en el path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Configurar AppUserModelID para que Windows agrupe y muestre el icono en la barra de tareas
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Fede.DisplaySwitch.App.2.0")
except Exception:
    pass

from monitor_controller import MonitorController
from tray_and_hotkey import TrayAndHotkeyManager
from app_gui import DisplayFlowApp
from i18n import t, format_hotkey_display

_single_instance_mutex = None

def check_single_instance():
    """
    Garantiza que solo se ejecute una instancia del programa a la vez.
    Si ya existe un proceso en ejecución:
    - Despierta y restaura la ventana de la instancia existente al primer plano.
    - Cierra de inmediato el nuevo proceso sin generar duplicados ni conflictos.
    """
    global _single_instance_mutex
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    
    ERROR_ALREADY_EXISTS = 183
    mutex_name = "Local\\DisplaySwitch_SingleInstance_Mutex_UltraTizaFede"
    
    _single_instance_mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    
    if last_error == ERROR_ALREADY_EXISTS:
        # Hay otra instancia en ejecución
        start_minimized = "--minimized" in sys.argv or "--tray" in sys.argv
        if not start_minimized:
            # 1. Enviar mensaje registrado broadcast para despertar a la ventana principal
            try:
                wm_wakeup = user32.RegisterWindowMessageW("DisplaySwitch_WakeUp_UltraTizaFede")
                if wm_wakeup:
                    user32.PostMessageW(0xFFFF, wm_wakeup, 0, 0)
            except Exception:
                pass
            
            # 2. Enviar mensaje directo a la ventana oculta del gestor de bandeja
            try:
                hwnd = user32.FindWindowW("DisplaySwitchHiddenWndClass", "DisplaySwitchHiddenWindow")
                if not hwnd:
                    hwnd = user32.FindWindowW("DisplayFlowHiddenWndClass", "DisplayFlowHiddenWindow")
                if hwnd:
                    WM_APP = 0x8000
                    WM_SHOW_EXISTING_APP = WM_APP + 10
                    user32.PostMessageW(hwnd, WM_SHOW_EXISTING_APP, 0, 0)
            except Exception:
                pass
                
        # Finalizar este nuevo proceso de inmediato
        sys.exit(0)

def main():
    check_single_instance()

    start_minimized = "--minimized" in sys.argv or "--tray" in sys.argv

    # 1. Crear el controlador de monitores
    controller = MonitorController()

    # 2. Variable global para la instancia de la UI
    app_holder = {"app": None, "root": None}

    def handle_toggle():
        if app_holder["app"]:
            app_holder["root"].after(0, app_holder["app"].toggle_tv)
        else:
            ok, msg = controller.toggle_tv()
            if tray_mgr:
                tray_mgr.show_notification(controller.get_app_title(), msg)

    def handle_mode(mode):
        if app_holder["app"]:
            app_holder["root"].after(0, lambda: app_holder["app"].set_mode(mode))
        else:
            ok, msg = controller.set_mode(mode)
            if tray_mgr:
                tray_mgr.show_notification(controller.get_app_title(), msg)

    def handle_show_ui():
        if app_holder["app"]:
            app_holder["root"].after(0, app_holder["app"].show_from_tray)

    def handle_display_change():
        if app_holder["app"] and app_holder["root"]:
            app_holder["root"].after(400, lambda: app_holder["app"]._refresh_monitors_ui(force=True))

    def handle_context_menu(x, y):
        if app_holder["app"] and app_holder["root"]:
            app_holder["root"].after(0, lambda: app_holder["app"].show_tray_menu(x, y))

    def handle_exit():
        if tray_mgr:
            tray_mgr.stop()
        if app_holder["root"]:
            app_holder["root"].after(0, app_holder["root"].destroy)
        sys.exit(0)

    # 3. Inicializar el Administrador de Bandeja y Atajos Globales
    tray_mgr = TrayAndHotkeyManager(
        on_toggle=handle_toggle,
        on_mode=handle_mode,
        on_show_ui=handle_show_ui,
        on_exit=handle_exit,
        on_display_change=handle_display_change,
        get_hotkeys_func=controller.get_hotkeys,
        on_context_menu=handle_context_menu,
        get_app_title_func=controller.get_app_title,
        get_show_notifications_func=controller.get_show_notifications,
        get_language_func=controller.get_language
    )
    tray_mgr.start()

    # 4. Inicializar la Interfaz Gráfica (Tkinter)
    root = tk.Tk()
    app = DisplayFlowApp(root, controller, tray_mgr)
    
    app_holder["root"] = root
    app_holder["app"] = app

    # Centrar ventana en la pantalla principal
    try:
        root.update_idletasks()
        w = 780
        h = 780
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        root.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass

    if start_minimized:
        root.withdraw()
        lang = controller.get_language()
        app_t = controller.get_app_title()
        hk = format_hotkey_display(controller.get_hotkeys().get("toggle_tv", "Ctrl+Alt+T"), lang=lang, for_tray=True)
        msg = t("notif_hidden_tray", lang, hk=hk) if hk else t("notif_hidden_tray_no_hk", lang)
        tray_mgr.show_notification(app_t, msg)

    # 5. Iniciar loop de eventos
    try:
        root.mainloop()
    finally:
        tray_mgr.stop()
        if _single_instance_mutex:
            try:
                ctypes.windll.kernel32.CloseHandle(_single_instance_mutex)
            except Exception:
                pass

if __name__ == "__main__":
    main()
