"""
DisplaySwitch - Internationalization (i18n) Engine
Copyright (C) 2026 UltraTiza, FedeFadda
Testing & Quality Assurance: FedeNahas
Licencia: Software Libre (GPLv3)
"""

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "es"]

STRINGS = {
    "en": {
        # General & Header
        "app_title_modern": "MonitorSwitch",
        "app_title_legacy": "Los Monitores pingueros del Fede",
        "app_subtitle": "Smart Multi-Display & TV Manager",
        "detect_displays": "🔄 Detect Displays",
        "status_ready": "● System Ready",
        "status_scanning": "🔍 Scanning...",
        "status_detected": "● {count} Displays Detected",
        "status_active": "● {count} Active Displays",
        "status_tv_off": "● TV '{tv}' Disabled",
        "status_no_tv": "● {count} Displays (No TV designated)",
        "status_applying_hz": "⚡ Applying {hz}Hz...",
        "status_busy": "⏳ {status}",

        # Hero Toggle Button
        "hero_turn_off": "⚡ TURN OFF TV ({tv})",
        "hero_turn_on": "📺 TURN ON TV ({tv})",
        "hero_select_tv": "📺 SELECT A TV BELOW",
        "hero_sub_off": "Turns off video signal to '{tv}' (Hotkey: {hk})",
        "hero_sub_on": "Turns on video signal to '{tv}' and restores desktop (Hotkey: {hk})",
        "hero_sub_select": "Click 'Assign TV' on any display below to assign it",
        "hero_sub_toggle": "Toggles designated TV display (Hotkey: {hk})",

        # Displays List
        "section_displays": "AVAILABLE DISPLAYS IN WINDOWS",
        "tip_displays": "💡 Choose startup refresh rate (Hz) and designated TV",
        "badge_primary": "PRIMARY",
        "badge_designated_tv": "★ DESIGNATED TV",
        "badge_monitor": "MONITOR",
        "badge_active": "● ACTIVE",
        "badge_off": "○ DISABLED",
        "res_native": "Native Resolution",
        "card_port": "Port",
        "card_id": "ID",
        "btn_card_turn_off": "⚡ Turn Off",
        "btn_card_turn_on": "📺 Turn On",
        "btn_set_primary": "⭐ Set Main",
        "btn_set_tv": "📺 Assign TV",
        "btn_unset_tv": "🖥️ Remove TV",
        "card_startup_hz": "⚡ Startup:",
        "badge_designated_primary": "⭐ MAIN",

        # Global Modes
        "section_modes": "GLOBAL DISPLAY MODES",
        "btn_monitors_only": "🖥️ Monitors Only",
        "btn_tv_only": "📺 TV Only",
        "btn_extend_all": "📺 Extend All",

        # Footer
        "btn_settings": "⚙️ Settings",
        "footer_copyright": "© 2026 DisplaySwitch (Free Software)",
        "btn_hide_tray": "📌 Hide to Tray",

        # Settings Modal
        "settings_title": "Settings - {title}",
        "settings_header": "⚙️ System Settings",
        "settings_subtitle": "General preferences, notifications, and global keyboard/mouse hotkeys",
        "sec_general_prefs": "GENERAL PREFERENCES",
        "pref_primary_label": "Default Main Display:",
        "pref_primary_desc": "— Preferred monitor to stay as Windows Primary.",
        "pref_language_label": "Idioma / Language:",
        "pref_language_desc": "— Interface and notification language.",
        "pref_startup_label": "Start with Windows",
        "pref_startup_desc": "— Starts DisplaySwitch in background on PC boot.",
        "pref_restore_windows_label": "Restore TV Windows Layout",
        "pref_restore_windows_desc": "— Automatically restores window positions and maximize state to the TV when it turns back on.",
        "pref_notif_label": "Windows Notifications",
        "pref_notif_desc": "— Shows balloon alerts when switching displays or changing refresh rates.",
        "pref_legacy_label": "Legacy Mode",
        "pref_legacy_desc": "— Restores classic title «Los Monitores pingueros del Fede».",

        "sec_hotkeys": "GLOBAL KEYBOARD & MOUSE HOTKEYS",
        "hotkeys_sub": "Press '⏺️ Record' (supports keyboard or mouse clicks), or use '🖱️ Mouse' for quick presets",
        "hk_action_toggle": "Toggle TV",
        "hk_desc_toggle": "Turns on or off the display configured as TV",
        "hk_action_monitors": "Monitors Only",
        "hk_desc_monitors": "Turns off TV and keeps PC monitors active",
        "hk_action_tv_only": "TV Only",
        "hk_desc_tv_only": "Turns off PC monitors and keeps designated TV active",
        "hk_action_extend": "Extend All",
        "hk_desc_extend": "Turns on and extends all available displays",
        "hk_none": "[ No hotkey ]",
        "btn_record": "⏺️ Record",
        "btn_mouse": "🖱️ Mouse",
        "btn_clear": "❌ Clear",
        "rec_recording": "Recording... press keys or mouse",
        "rec_prompt": "Press any keys or mouse buttons...",
        "btn_reset_defaults": "🔄 Reset Hotkeys",
        "btn_save_close": "✓ Save & Close",
        "btn_cancel": "Cancel",

        # Mouse Menu Options
        "mouse_mbutton": "🖱️ Middle Button (MButton)",
        "mouse_xbutton1": "🖱️ Mouse 4 / Back (XButton1)",
        "mouse_xbutton2": "🖱️ Mouse 5 / Forward (XButton2)",
        "mouse_ctrl_mbutton": "🖱️ Ctrl + Middle Button",
        "mouse_ctrl_xbutton1": "🖱️ Ctrl + Mouse 4",
        "mouse_ctrl_xbutton2": "🖱️ Ctrl + Mouse 5",
        "mouse_alt_mbutton": "🖱️ Alt + Middle Button",
        "mouse_alt_xbutton1": "🖱️ Alt + Mouse 4",
        "mouse_alt_xbutton2": "🖱️ Alt + Mouse 5",
        "mouse_ctrl_alt_mbutton": "🖱️ Ctrl + Alt + Middle Button",
        "mouse_ctrl_alt_xbutton1": "🖱️ Ctrl + Alt + Mouse 4",
        "mouse_ctrl_alt_xbutton2": "🖱️ Ctrl + Alt + Mouse 5",

        # Tray Menu
        "tray_toggle_off": "⚡ Turn Off {name}",
        "tray_toggle_on": "⚡ Turn On {name}",
        "tray_toggle_default": "⚡ Toggle TV",
        "tray_monitors_only": "🖥️ Monitors Only",
        "tray_tv_only": "📺 TV Only",
        "tray_extend_all": "📺 Extend All",
        "tray_settings": "⚙️ Settings...",
        "tray_open_app": "⚙️ Open {title}",
        "tray_exit": "❌ Exit",
        "tray_tip_active": "{title}: '{tv}' Active",
        "tray_tip_off": "{title}: '{tv}' Off",
        "tray_tip_no_tv": "{title}: No designated TV",
        "tray_tip_running": "{title}: Active",

        # Notifications & Dialogs
        "notif_hidden_tray": "Application is running in system tray. Use {hk} to toggle TV.",
        "notif_hidden_tray_no_hk": "Application is running in system tray.",
        "dialog_no_tv_title": "No TV Assigned",
        "dialog_no_tv_msg": "Please click 'Assign TV' on the display you wish to control as TV.",
        "notif_hz_applied": "'{name}' set to {hz}Hz.",
        "notif_displays_detected": "{count} connected displays detected in Windows.",
        "action_turning_off": "Turning off '{name}'...",
        "action_turning_on": "Turning on '{name}'..." ,
        "action_toggling": "Toggling '{name}'...",
        "action_applying_mode": "Applying {mode}...",
        "msg_tv_off": "TV '{tv}' disabled.",
        "msg_tv_on": "TV '{tv}' enabled.",
        "msg_monitors_only_applied": "Monitors Only mode applied successfully.",
        "msg_tv_only_applied": "TV Only mode applied successfully.",
        "msg_extend_applied": "Extend All mode applied successfully.",
        "msg_tv_set": "Designated TV: '{name}'.",
        "msg_tv_unset": "TV designation removed. All screens are now monitors.",
        "msg_primary_set": "Monitor '{name}' is now your default Primary monitor.",

        # About Modal
        "about_title": "About DisplaySwitch",
        "about_app_name": "⚡ DisplaySwitch",
        "about_subtitle": "Smart Multi-Display & TV Manager for Windows",
        "about_credits_title": "DEVELOPMENT TEAM & CREDITS",
        "about_role_dev": "Development & Creation:",
        "about_role_fede": "Co-creator (Fede):",
        "about_role_qa": "Testing & QA:",
        "about_license_title": "LICENSE & COPYRIGHT",
        "about_license_body": (
            "Free Software (GPLv3 / Open Source).\n"
            "Copyright © 2026 UltraTiza, FedeFadda.\n"
            "Testing & Quality Assurance: FedeNahas.\n"
            "Permission is granted to use, study, modify, and redistribute this\n"
            "software freely under the terms of the GNU General Public License v3."
        ),
        "about_btn_close": "Close",
    },

    "es": {
        # General & Encabezado
        "app_title_modern": "MonitorSwitch",
        "app_title_legacy": "Los Monitores pingueros del Fede",
        "app_subtitle": "Gestor Inteligente de Pantallas y Televisor",
        "detect_displays": "🔄 Detectar Pantallas",
        "status_ready": "● Sistema Listo",
        "status_scanning": "🔍 Escaneando...",
        "status_detected": "● {count} Pantallas Detectadas",
        "status_active": "● {count} Pantallas Activas",
        "status_tv_off": "● Televisor '{tv}' Desactivado",
        "status_no_tv": "● {count} Pantallas (Sin TV designado)",
        "status_applying_hz": "⚡ Aplicando {hz}Hz...",
        "status_busy": "⏳ {status}",

        # Botón Principal Hero
        "hero_turn_off": "⚡ DESACTIVAR TELEVISOR ({tv})",
        "hero_turn_on": "📺 ACTIVAR TELEVISOR ({tv})",
        "hero_select_tv": "📺 SELECCIONA UN TELEVISOR ABAJO",
        "hero_sub_off": "Apaga la señal hacia '{tv}' (Atajo: {hk})",
        "hero_sub_on": "Enciende la señal hacia '{tv}' y restaura el escritorio (Atajo: {hk})",
        "hero_sub_select": "Haz clic en 'Designar TV' en cualquiera de las pantallas para controlarla",
        "hero_sub_toggle": "Alterna la pantalla designada como televisor (Atajo: {hk})",

        # Lista de Pantallas
        "section_displays": "PANTALLAS DISPONIBLES EN WINDOWS",
        "tip_displays": "💡 Elige la tasa de refresco (Hz) de inicio y el televisor designado",
        "badge_primary": "PRINCIPAL",
        "badge_designated_tv": "★ TELEVISOR DESIGNADO",
        "badge_monitor": "MONITOR",
        "badge_active": "● ACTIVO",
        "badge_off": "○ APAGADO",
        "res_native": "Resolución Nativa",
        "card_port": "Puerto",
        "card_id": "ID",
        "btn_card_turn_off": "⚡ Desactivar",
        "btn_card_turn_on": "📺 Activar",
        "btn_set_primary": "⭐ Principal",
        "btn_set_tv": "📺 Designar TV",
        "btn_unset_tv": "🖥️ Quitar TV",
        "card_startup_hz": "⚡ Inicio:",
        "badge_designated_primary": "⭐ PRINCIPAL",

        # Modos Globales
        "section_modes": "MODOS GLOBALES DE PANTALLAS",
        "btn_monitors_only": "🖥️ Solo Monitores",
        "btn_tv_only": "📺 Solo TV",
        "btn_extend_all": "📺 Extender Todo",

        # Pie de página
        "btn_settings": "⚙️ Configuración",
        "footer_copyright": "© 2026 DisplaySwitch (Software Libre)",
        "btn_hide_tray": "📌 Ocultar en la bandeja",

        # Ventana de Configuración
        "settings_title": "Configuración - {title}",
        "settings_header": "⚙️ Configuración del Sistema",
        "settings_subtitle": "Preferencias generales, notificaciones y gestor de atajos de teclado y ratón",
        "sec_general_prefs": "PREFERENCIAS GENERALES",
        "pref_primary_label": "Monitor Principal por defecto:",
        "pref_primary_desc": "— Monitor preferido para mantenerse como Principal de Windows.",
        "pref_language_label": "Idioma / Language:",
        "pref_language_desc": "— Idioma de la interfaz y notificaciones.",
        "pref_startup_label": "Iniciar con Windows",
        "pref_startup_desc": "— Inicia DisplaySwitch en segundo plano al arrancar la PC.",
        "pref_restore_windows_label": "Recordar ventanas en TV",
        "pref_restore_windows_desc": "— Restaura automáticamente la posición y tamaño de las ventanas en la TV al volver a encenderla.",
        "pref_notif_label": "Notificaciones de Windows",
        "pref_notif_desc": "— Muestra alertas flotantes al conmutar pantallas o cambiar tasas de refresco.",
        "pref_legacy_label": "Legacy Mode",
        "pref_legacy_desc": "— Restaura el título clásico «Los Monitores pingueros del Fede».",

        "sec_hotkeys": "ATAJOS GLOBALES DE TECLADO Y RATÓN",
        "hotkeys_sub": "Presiona '⏺️ Grabar' (acepta teclado o clics del ratón), o usa '🖱️ Mouse' para combinaciones directas",
        "hk_action_toggle": "Alternar Televisor",
        "hk_desc_toggle": "Enciende o apaga la pantalla configurada como TV",
        "hk_action_monitors": "Solo Monitores",
        "hk_desc_monitors": "Apaga el televisor y mantiene encendidos los monitores de PC",
        "hk_action_tv_only": "Solo TV",
        "hk_desc_tv_only": "Apaga los monitores de PC y mantiene encendidas solo las pantallas asignadas como TV",
        "hk_action_extend": "Extender Todo",
        "hk_desc_extend": "Enciende y extiende todas las pantallas disponibles",
        "hk_none": "[ Sin atajo ]",
        "btn_record": "⏺️ Grabar",
        "btn_mouse": "🖱️ Mouse",
        "btn_clear": "❌ Borrar",
        "rec_recording": "Grabando... presiona teclas o mouse",
        "rec_prompt": "Presiona teclas o clic del ratón...",
        "btn_reset_defaults": "🔄 Restablecer Atajos",
        "btn_save_close": "✓ Guardar y Cerrar",
        "btn_cancel": "Cancelar",

        # Opciones Menú Mouse
        "mouse_mbutton": "🖱️ Botón Central (MButton)",
        "mouse_xbutton1": "🖱️ Mouse 4 / Atrás (XButton1)",
        "mouse_xbutton2": "🖱️ Mouse 5 / Adelante (XButton2)",
        "mouse_ctrl_mbutton": "🖱️ Ctrl + Botón Central",
        "mouse_ctrl_xbutton1": "🖱️ Ctrl + Mouse 4",
        "mouse_ctrl_xbutton2": "🖱️ Ctrl + Mouse 5",
        "mouse_alt_mbutton": "🖱️ Alt + Botón Central",
        "mouse_alt_xbutton1": "🖱️ Alt + Mouse 4",
        "mouse_alt_xbutton2": "🖱️ Alt + Mouse 5",
        "mouse_ctrl_alt_mbutton": "🖱️ Ctrl + Alt + Botón Central",
        "mouse_ctrl_alt_xbutton1": "🖱️ Ctrl + Alt + Mouse 4",
        "mouse_ctrl_alt_xbutton2": "🖱️ Ctrl + Alt + Mouse 5",

        # Menú de la Bandeja (Tray)
        "tray_toggle_off": "⚡ Apagar {name}",
        "tray_toggle_on": "⚡ Encender {name}",
        "tray_toggle_default": "⚡ Alternar Televisor",
        "tray_monitors_only": "🖥️ Solo Monitores",
        "tray_tv_only": "📺 Solo TV",
        "tray_extend_all": "📺 Extender Todo",
        "tray_settings": "⚙️ Configuración...",
        "tray_open_app": "⚙️ Abrir {title}",
        "tray_exit": "❌ Salir",
        "tray_tip_active": "{title}: '{tv}' Activo",
        "tray_tip_off": "{title}: '{tv}' Apagado",
        "tray_tip_no_tv": "{title}: Sin televisor designado",
        "tray_tip_running": "{title}: Activo",

        # Notificaciones y Diálogos
        "notif_hidden_tray": "La aplicación sigue activa en la bandeja del reloj. Usa {hk} para alternar la TV.",
        "notif_hidden_tray_no_hk": "La aplicación sigue activa en la bandeja del reloj.",
        "dialog_no_tv_title": "Televisor no asignado",
        "dialog_no_tv_msg": "Por favor haz clic en 'Designar TV' en la pantalla que deseas usar como televisor.",
        "notif_hz_applied": "'{name}' configurado a {hz}Hz.",
        "notif_displays_detected": "Se han detectado {count} pantallas conectadas en Windows.",
        "action_turning_off": "Desactivando '{name}'...",
        "action_turning_on": "Activando '{name}'...",
        "action_toggling": "Alternando '{name}'...",
        "action_applying_mode": "Aplicando {mode}...",
        "msg_tv_off": "Televisor '{tv}' desactivado.",
        "msg_tv_on": "Televisor '{tv}' activado.",
        "msg_monitors_only_applied": "Modo Solo Monitores aplicado con éxito.",
        "msg_tv_only_applied": "Modo Solo TV aplicado con éxito.",
        "msg_extend_applied": "Modo Extender Todo aplicado con éxito.",
        "msg_tv_set": "Televisor asignado: '{name}'.",
        "msg_tv_unset": "Televisor desasignado. Ahora todas las pantallas son monitores.",
        "msg_primary_set": "Monitor '{name}' establecido como Monitor Principal por defecto.",

        # Diálogo Acerca de
        "about_title": "Acerca de DisplaySwitch",
        "about_app_name": "⚡ DisplaySwitch",
        "about_subtitle": "Gestor Inteligente de Pantallas y Televisor para Windows",
        "about_credits_title": "EQUIPO DE DESARROLLO Y CRÉDITOS",
        "about_role_dev": "Desarrollo y Creación:",
        "about_role_fede": "Co-creator (Fede):",
        "about_role_qa": "Testing & QA:",
        "about_license_title": "LICENCIA Y DERECHOS DE AUTOR",
        "about_license_body": (
            "Software Libre (GPLv3 / Open Source).\n"
            "Copyright © 2026 UltraTiza, FedeFadda.\n"
            "Testing y Control de Calidad: FedeNahas.\n"
            "Se concede permiso para usar, estudiar, modificar y redistribuir este\n"
            "software libremente bajo los términos de la Licencia Pública General GNU v3."
        ),
        "about_btn_close": "Cerrar",
    }
}


def t(key, lang="en", **kwargs):
    """Retorna la cadena traducida según el idioma activo con reemplazo de formato"""
    l_dict = STRINGS.get(lang, STRINGS[DEFAULT_LANGUAGE])
    template = l_dict.get(key) or STRINGS[DEFAULT_LANGUAGE].get(key, key)
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


def format_hotkey_display(hk_str, lang="en", for_tray=False):
    """
    Convierte identificadores internos (XButton1, MButton) a texto amigable
    según el idioma configurado ('en' o 'es').
    """
    if not hk_str:
        return "" if for_tray else t("hk_none", lang)

    s = str(hk_str)
    prefix = "" if for_tray else "🖱️ "

    if lang == "es":
        s = s.replace("MBUTTON", f"{prefix}Botón Central").replace("MButton", f"{prefix}Botón Central")
        s = s.replace("XBUTTON1", f"{prefix}Mouse 4").replace("XButton1", f"{prefix}Mouse 4")
        s = s.replace("XBUTTON2", f"{prefix}Mouse 5").replace("XButton2", f"{prefix}Mouse 5")
    else:
        s = s.replace("MBUTTON", f"{prefix}Middle Button").replace("MButton", f"{prefix}Middle Button")
        s = s.replace("XBUTTON1", f"{prefix}Mouse 4").replace("XButton1", f"{prefix}Mouse 4")
        s = s.replace("XBUTTON2", f"{prefix}Mouse 5").replace("XButton2", f"{prefix}Mouse 5")
    return s
