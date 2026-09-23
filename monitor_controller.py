"""
DisplaySwitch - Multi-Display Control Engine
Copyright (C) 2026 UltraTiza, FedeFadda
Testing & Quality Assurance: FedeNahas
Licencia: Software Libre (GPLv3)

Soporta:
- Detección dinámica de monitores y televisores en Windows mediante Windows CCD y MultiMonitorTool.
- Selección interactiva y persistente de la tasa de refresco (Hz) de inicio para cada pantalla.
- Modos globales: "Solo Monitores", "Extender Todo", "Duplicar Pantalla" (Principal -> TV).
- Soporte para alternar modo Legacy ("Los Monitores pingueros del Fede") y Moderno ("MonitorSwitch" / "DisplaySwitch").
"""

import ctypes
from ctypes import wintypes
import subprocess
import time
import threading
import winreg
import os
import json
from i18n import t

user32 = ctypes.windll.user32

# Constantes CCD
QDC_ALL_PATHS = 1
QDC_ONLY_ACTIVE_PATHS = 2
DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME = 2
DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME = 1

SDC_APPLY = 0x00000080
SDC_TOPOLOGY_INTERNAL = 0x00000001
SDC_TOPOLOGY_CLONE = 0x00000002
SDC_TOPOLOGY_EXTEND = 0x00000004
SDC_TOPOLOGY_EXTERNAL = 0x00000008

class LUID(ctypes.Structure):
    _fields_ = [('LowPart', wintypes.DWORD), ('HighPart', wintypes.LONG)]

class DISPLAYCONFIG_PATH_SOURCE_INFO(ctypes.Structure):
    _fields_ = [
        ('adapterId', LUID),
        ('id', wintypes.UINT),
        ('modeInfoIdx', wintypes.UINT),
        ('statusFlags', wintypes.UINT),
    ]

class DISPLAYCONFIG_RATIONAL(ctypes.Structure):
    _fields_ = [('Numerator', wintypes.UINT), ('Denominator', wintypes.UINT)]

class DISPLAYCONFIG_PATH_TARGET_INFO(ctypes.Structure):
    _fields_ = [
        ('adapterId', LUID),
        ('id', wintypes.UINT),
        ('modeInfoIdx', wintypes.UINT),
        ('outputTechnology', wintypes.UINT),
        ('rotation', wintypes.UINT),
        ('scaling', wintypes.UINT),
        ('refreshRate', DISPLAYCONFIG_RATIONAL),
        ('scanLineOrdering', wintypes.UINT),
        ('targetAvailable', wintypes.BOOL),
        ('statusFlags', wintypes.UINT),
    ]

class DISPLAYCONFIG_PATH_INFO(ctypes.Structure):
    _fields_ = [
        ('sourceInfo', DISPLAYCONFIG_PATH_SOURCE_INFO),
        ('targetInfo', DISPLAYCONFIG_PATH_TARGET_INFO),
        ('flags', wintypes.UINT),
    ]

class DISPLAYCONFIG_DEVICE_INFO_HEADER(ctypes.Structure):
    _fields_ = [
        ('type', wintypes.UINT),
        ('size', wintypes.UINT),
        ('adapterId', LUID),
        ('id', wintypes.UINT),
    ]

class DISPLAYCONFIG_TARGET_DEVICE_NAME_FLAGS(ctypes.Structure):
    _fields_ = [('value', wintypes.UINT)]

class DISPLAYCONFIG_TARGET_DEVICE_NAME(ctypes.Structure):
    _fields_ = [
        ('header', DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ('flags', DISPLAYCONFIG_TARGET_DEVICE_NAME_FLAGS),
        ('outputTechnology', wintypes.UINT),
        ('edidManufactureId', wintypes.USHORT),
        ('edidProductCodeId', wintypes.USHORT),
        ('connectorInstance', wintypes.UINT),
        ('monitorFriendlyDeviceName', wintypes.WCHAR * 64),
        ('monitorDevicePath', wintypes.WCHAR * 128),
    ]

class DISPLAYCONFIG_SOURCE_DEVICE_NAME(ctypes.Structure):
    _fields_ = [
        ('header', DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ('viewGdiDeviceName', wintypes.WCHAR * 32),
    ]

class POINTL(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

class RECT(ctypes.Structure):
    _fields_ = [
        ('left', wintypes.LONG),
        ('top', wintypes.LONG),
        ('right', wintypes.LONG),
        ('bottom', wintypes.LONG)
    ]

class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ('dmDeviceName', wintypes.WCHAR * 32),
        ('dmSpecVersion', wintypes.WORD),
        ('dmDriverVersion', wintypes.WORD),
        ('dmSize', wintypes.WORD),
        ('dmDriverExtra', wintypes.WORD),
        ('dmFields', wintypes.DWORD),
        ('dmPosition', POINTL),
        ('dmDisplayOrientation', wintypes.DWORD),
        ('dmDisplayFixedOutput', wintypes.DWORD),
        ('dmColor', wintypes.SHORT),
        ('dmDuplex', wintypes.SHORT),
        ('dmYResolution', wintypes.SHORT),
        ('dmTTOption', wintypes.SHORT),
        ('dmCollate', wintypes.SHORT),
        ('dmFormName', wintypes.WCHAR * 32),
        ('dmLogPixels', wintypes.WORD),
        ('dmBitsPerPel', wintypes.DWORD),
        ('dmPelsWidth', wintypes.DWORD),
        ('dmPelsHeight', wintypes.DWORD),
        ('dmDisplayFlags', wintypes.DWORD),
        ('dmDisplayFrequency', wintypes.DWORD),
        ('dmICMMethod', wintypes.DWORD),
        ('dmICMIntent', wintypes.DWORD),
        ('dmMediaType', wintypes.DWORD),
        ('dmDitherType', wintypes.DWORD),
        ('dmReserved1', wintypes.DWORD),
        ('dmReserved2', wintypes.DWORD),
        ('dmPanningWidth', wintypes.DWORD),
        ('dmPanningHeight', wintypes.DWORD),
    ]


class MonitorInfo:
    def __init__(self, target_id, friendly_name, gdi_name, pnp_id="", short_id="", 
                 device_path="", is_primary=False, is_active=False, width=0, height=0, 
                 hz=0, is_designated_tv=False, is_designated_primary=False,
                 available_refresh_rates=None, startup_hz=0):
        self.target_id = target_id
        self.friendly_name = friendly_name
        self.gdi_name = gdi_name
        self.pnp_id = pnp_id
        self.short_id = short_id or pnp_id
        self.device_path = device_path
        self.is_primary = is_primary
        self.is_active = is_active
        self.width = width
        self.height = height
        self.hz = hz
        self.is_designated_tv = is_designated_tv
        self.is_designated_primary = is_designated_primary
        self.available_refresh_rates = available_refresh_rates or []
        self.startup_hz = startup_hz or hz

    def __repr__(self):
        role = " [TELEVISOR]" if self.is_designated_tv else " [MONITOR]"
        prim = " (Principal)" if self.is_primary else ""
        des = " [MAIN]" if self.is_designated_primary else ""
        return f"<Monitor {self.friendly_name}{role}{prim}{des} ID={self.short_id} Active={self.is_active} {self.width}x{self.height}@{self.hz}Hz AvailableHz={self.available_refresh_rates}>"


class MonitorController:
    def __init__(self):
        self._lock = threading.RLock()
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.app_dir, "config.json")
        self.tools_exe = os.path.join(self.app_dir, "tools", "MultiMonitorTool.exe")
        
        self.config = self._load_config()
        self._cached_monitors = []
        self._last_state_check = 0
        self._saved_tv_windows = []

    def _load_config(self):
        """Carga la configuración de la aplicación"""
        default_config = {
            "designated_tv_id": "",
            "designated_tv_gdi": "",
            "designated_tv_name": "",
            "designated_primary_id": "",
            "designated_primary_name": "",
            "hotkey": "Ctrl+Alt+T",
            "hotkeys": {
                "toggle_tv": "Ctrl+Alt+T",
                "monitors_only": "Ctrl+Alt+M",
                "tv_only": "Ctrl+Alt+V",
                "extend_all": "Ctrl+Alt+E"
            },
            "startup_refresh_rates": {},
            "cached_refresh_rates": {},
            "language": "en",
            "legacy_mode": False,
            "show_notifications": True,
            "minimize_to_tray_on_close": True,
            "start_with_windows": False,
            "restore_window_layout": False
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_config.update(data)
                    # Migración retrocompatible si solo existía "hotkey"
                    if "hotkeys" not in data and "hotkey" in data:
                        default_config["hotkeys"]["toggle_tv"] = data["hotkey"]
            except Exception:
                pass
        return default_config

    def _save_config(self, config_data=None):
        """Guarda la configuración en disco"""
        if config_data is None:
            config_data = self.config
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar config: {e}")

    def get_language(self):
        """Retorna el idioma activo ('en' o 'es', por defecto 'en')"""
        lang = self.config.get("language", "en")
        if lang not in ("en", "es"):
            return "en"
        return lang

    def set_language(self, lang_code: str):
        """Establece y guarda el idioma preferido ('en' o 'es')"""
        if lang_code not in ("en", "es"):
            lang_code = "en"
        with self._lock:
            self.config["language"] = lang_code
            self._save_config()
            return True

    def get_show_notifications(self):
        """Retorna si las notificaciones flotantes de Windows están activadas (True por defecto)"""
        return self.config.get("show_notifications", True)

    def set_show_notifications(self, enabled: bool):
        """Activa o desactiva las notificaciones de Windows y guarda la preferencia"""
        with self._lock:
            self.config["show_notifications"] = bool(enabled)
            self._save_config()
            return True

    def get_legacy_mode(self):
        """Retorna si el modo 'Legacy' está activo (False por defecto)"""
        return self.config.get("legacy_mode", False)

    def set_legacy_mode(self, enabled: bool):
        """Alterna el modo Legacy y guarda la preferencia"""
        with self._lock:
            self.config["legacy_mode"] = bool(enabled)
            self._save_config()
            return True

    def get_restore_window_layout(self):
        """Retorna si la restauración de ventanas en TV está activa (False por defecto)"""
        return self.config.get("restore_window_layout", False)

    def set_restore_window_layout(self, enabled: bool):
        """Activa o desactiva la restauración de ventanas en TV"""
        with self._lock:
            self.config["restore_window_layout"] = bool(enabled)
            self._save_config()
            return True

    def is_startup_enabled(self):
        """Comprueba si la aplicación está configurada para iniciar con Windows en el Registro"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "DisplaySwitch")
            winreg.CloseKey(key)
            return bool(val)
        except Exception:
            return False

    def set_startup_enabled(self, enabled: bool):
        """Activa o desactiva el inicio automático con Windows a través del Registro de usuario"""
        # Limpieza de archivos .vbs huérfanos del método anterior en la carpeta Startup
        try:
            startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
            for dead_file in ("DisplaySwitch.vbs", "DisplayFlow.vbs"):
                p = os.path.join(startup_dir, dead_file)
                if os.path.exists(p):
                    try: os.remove(p)
                    except Exception: pass
        except Exception:
            pass

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                exe_path = os.path.join(self.app_dir, "MonitorSwitch.exe")
                if os.path.exists(exe_path):
                    cmd = f'"{exe_path}" --minimized'
                else:
                    main_py = os.path.join(self.app_dir, "main.py")
                    cmd = f'pythonw.exe "{main_py}" --minimized'
                winreg.SetValueEx(key, "DisplaySwitch", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, "DisplaySwitch")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            with self._lock:
                self.config["start_with_windows"] = bool(enabled)
                self._save_config()
            return True, "Configuración de inicio con Windows actualizada."
        except Exception as e:
            return False, f"Error al modificar el inicio en el Registro: {e}"

    def get_app_title(self):
        """Retorna el título dinámico según el modo Legacy e idioma"""
        lang = self.get_language()
        if self.get_legacy_mode():
            return t("app_title_legacy", lang)
        return t("app_title_modern", lang)

    def get_project_name(self):
        """Retorna el nombre formal del proyecto"""
        return "DisplaySwitch"

    def get_startup_refresh_rates(self):
        """Retorna el diccionario de tasas de refresco configuradas para inicio {id: hz}"""
        return self.config.get("startup_refresh_rates", {})

    def set_refresh_rate(self, monitor_id, hz):
        """
        Aplica la tasa de refresco a un monitor inmediatamente y la guarda como
        frecuencia de inicio preferida para ese monitor.
        """
        with self._lock:
            hz = int(hz)
            m_id = str(monitor_id)
            if "startup_refresh_rates" not in self.config:
                self.config["startup_refresh_rates"] = {}
            self.config["startup_refresh_rates"][m_id] = hz
            self._save_config()

        # Si el monitor está inactivo/apagado, queda registrado como frecuencia de inicio
        # sin necesidad de intentar cambiar la frecuencia de una pantalla desconectada
        monitors = self.get_connected_monitors()
        target = next((m for m in monitors if m.short_id == m_id or m.friendly_name == m_id or m.gdi_name == m_id), None)
        if target and not target.is_active:
            return True, t("notif_hz_applied", self.get_language(), name=target.friendly_name or m_id, hz=hz)

        # Aplicar con MultiMonitorTool fuera del lock para no bloquear otros hilos
        if os.path.exists(self.tools_exe):
            try:
                cmd = [self.tools_exe, "/SetMonitors", f"Name={m_id} DisplayFrequency={hz}"]
                subprocess.run(cmd, check=False, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
                time.sleep(0.4)
                self.get_connected_monitors(force_refresh=True)
                return True, t("notif_hz_applied", self.get_language(), name=m_id, hz=hz)
            except subprocess.TimeoutExpired:
                return True, t("notif_hz_applied", self.get_language(), name=m_id, hz=hz)
            except Exception as e:
                return False, f"Error: {e}"
        return True, t("notif_hz_applied", self.get_language(), name=m_id, hz=hz)

    def apply_startup_refresh_rates(self, only_ids=None, exclude_ids=None):
        """Aplica todas las frecuencias de inicio configuradas a las pantallas correspondientes"""
        rates = self.get_startup_refresh_rates()
        if not rates or not os.path.exists(self.tools_exe):
            return
        args = []
        for mon_id, hz in rates.items():
            if not mon_id or not hz:
                continue
            if exclude_ids and mon_id in exclude_ids:
                continue
            if only_ids is not None and mon_id not in only_ids:
                continue
            args.append(f"Name={mon_id} DisplayFrequency={int(hz)}")
        if args:
            try:
                subprocess.run([self.tools_exe, "/SetMonitors"] + args,
                               check=False, creationflags=subprocess.CREATE_NO_WINDOW, timeout=8)
            except Exception:
                pass

    def get_hotkeys(self):
        """Retorna el diccionario de atajos de teclado configurados"""
        return self.config.get("hotkeys", {
            "toggle_tv": "Ctrl+Alt+T",
            "monitors_only": "Ctrl+Alt+M",
            "tv_only": "Ctrl+Alt+V",
            "extend_all": "Ctrl+Alt+E"
        })

    def set_hotkeys(self, hotkeys_dict):
        """Actualiza y persiste los atajos de teclado"""
        with self._lock:
            self.config["hotkeys"] = hotkeys_dict
            if "toggle_tv" in hotkeys_dict:
                self.config["hotkey"] = hotkeys_dict["toggle_tv"]
            self._save_config()
            return True, "Atajos de teclado guardados exitosamente."

    def set_designated_tv(self, monitor_or_id):
        """
        Establece un monitor específico como el 'Televisor'.
        Todas las demás pantallas pasarán a actuar automáticamente como 'Monitores'.
        Acepta una instancia de MonitorInfo o un string (pnp_id, short_id, friendly_name o target_id).
        """
        with self._lock:
            target_pnp = ""
            target_gdi = ""
            target_name = ""

            if isinstance(monitor_or_id, MonitorInfo):
                target_pnp = monitor_or_id.short_id or monitor_or_id.pnp_id
                target_gdi = monitor_or_id.gdi_name
                target_name = monitor_or_id.friendly_name
            else:
                s = str(monitor_or_id).strip()
                for m in self._cached_monitors:
                    if s in (m.short_id, m.pnp_id, m.gdi_name, m.friendly_name, str(m.target_id)):
                        target_pnp = m.short_id or m.pnp_id
                        target_gdi = m.gdi_name
                        target_name = m.friendly_name
                        break
                if not target_pnp:
                    target_pnp = s
                    target_name = s

            if self.config.get("designated_primary_id") == target_pnp:
                self.config["designated_primary_id"] = ""
                self.config["designated_primary_name"] = ""

            self.config["designated_tv_id"] = target_pnp
            self.config["designated_tv_gdi"] = target_gdi
            self.config["designated_tv_name"] = target_name
            self._save_config()

            # Actualizar marcas en la lista en memoria
            for m in self._cached_monitors:
                m.is_designated_tv = self._matches_designated_tv(m)
                m.is_designated_primary = self._matches_designated_primary(m)

            return True, t("msg_tv_set", self.get_language(), name=target_name)

    def unset_designated_tv(self):
        """
        Desmarca el televisor designado, dejando todas las pantallas como Monitores normales.
        """
        with self._lock:
            self.config["designated_tv_id"] = ""
            self.config["designated_tv_gdi"] = ""
            self.config["designated_tv_name"] = ""
            self._save_config()

            for m in self._cached_monitors:
                m.is_designated_tv = False

            return True, t("msg_tv_unset", self.get_language())

    def _matches_designated_tv(self, m):
        """Comprueba si un monitor coincide con el televisor asignado en config"""
        tv_id = self.config.get("designated_tv_id", "").strip()
        tv_name = self.config.get("designated_tv_name", "").strip()

        if not tv_id and not tv_name:
            return False

        if tv_id:
            if m.short_id and m.short_id.upper() == tv_id.upper():
                return True
            if m.pnp_id and m.pnp_id.upper() == tv_id.upper():
                return True
            if str(m.target_id) == tv_id:
                return True

        if tv_name and m.friendly_name:
            if m.friendly_name.strip().lower() == tv_name.lower():
                return True

        return False

    def get_designated_tv(self):
        """Retorna el objeto MonitorInfo del monitor configurado como TV, o None si no hay ninguno"""
        monitors = self.get_connected_monitors()
        for m in monitors:
            if m.is_designated_tv:
                return m
        return None

    def set_designated_primary(self, monitor_or_id):
        """
        Establece un monitor específico como el 'Monitor Principal' preferido del sistema.
        Persiste entre reinicios y cambios de modo ("Solo Monitores", "Extender Todo").
        """
        with self._lock:
            target_pnp = ""
            target_gdi = ""
            target_name = ""

            if isinstance(monitor_or_id, MonitorInfo):
                target_pnp = monitor_or_id.short_id or monitor_or_id.pnp_id
                target_gdi = monitor_or_id.gdi_name
                target_name = monitor_or_id.friendly_name
            else:
                s = str(monitor_or_id).strip()
                for m in self._cached_monitors:
                    if s in (m.short_id, m.pnp_id, m.gdi_name, m.friendly_name, str(m.target_id)):
                        target_pnp = m.short_id or m.pnp_id
                        target_gdi = m.gdi_name
                        target_name = m.friendly_name
                        break
                if not target_pnp:
                    target_pnp = s
                    target_name = s

            # Si este monitor estaba designado como TV, quitarle la marca de TV
            if self.config.get("designated_tv_id") == target_pnp:
                self.config["designated_tv_id"] = ""
                self.config["designated_tv_gdi"] = ""
                self.config["designated_tv_name"] = ""

            self.config["designated_primary_id"] = target_pnp
            self.config["designated_primary_name"] = target_name
            self._save_config()

            # Aplicar inmediatamente en Windows si el monitor está activo
            target_m = self._resolve_monitor(target_pnp)
            if target_m and target_m.is_active and os.path.exists(self.tools_exe) and target_pnp:
                try:
                    subprocess.run(
                        [self.tools_exe, "/SetPrimary", target_pnp],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.4)
                except Exception:
                    pass

            for m in self._cached_monitors:
                m.is_designated_primary = self._matches_designated_primary(m)
                m.is_designated_tv = self._matches_designated_tv(m)

            return True, t("msg_primary_set", self.get_language(), name=target_name)

    def unset_designated_primary(self):
        """Desmarca el monitor principal preferido"""
        with self._lock:
            self.config["designated_primary_id"] = ""
            self.config["designated_primary_name"] = ""
            self._save_config()

            for m in self._cached_monitors:
                m.is_designated_primary = False

            return True, "Monitor principal desmarcado."

    def _matches_designated_primary(self, m):
        """Comprueba si un monitor coincide con el monitor principal asignado en config"""
        prim_id = self.config.get("designated_primary_id", "").strip()
        prim_name = self.config.get("designated_primary_name", "").strip()

        if not prim_id and not prim_name:
            return False

        if prim_id:
            if m.short_id and m.short_id.upper() == prim_id.upper():
                return True
            if m.pnp_id and m.pnp_id.upper() == prim_id.upper():
                return True
            if str(m.target_id) == prim_id:
                return True

        if prim_name and m.friendly_name:
            if m.friendly_name.strip().lower() == prim_name.lower():
                return True

        return False

    def get_designated_primary(self):
        """Retorna el objeto MonitorInfo del monitor configurado como Principal, o None si no hay ninguno"""
        monitors = self.get_connected_monitors()
        for m in monitors:
            if m.is_designated_primary:
                return m
        return None

    def get_connected_monitors(self, force_refresh=False):
        """
        Detecta dinámicamente todos los monitores disponibles en Windows usando Windows CCD.
        Extrae identificadores de hardware persistentes (Short Monitor ID / PNP ID)
        para permitir activaciones y desactivaciones confiables en todo momento.
        """
        with self._lock:
            now = time.time()
            if not force_refresh and (now - self._last_state_check < 1.0) and self._cached_monitors:
                return self._cached_monitors

            monitors = []

            # 1. Obtener todas las rutas configuradas en Windows CCD
            path_count = wintypes.UINT()
            mode_count = wintypes.UINT()
            res = user32.GetDisplayConfigBufferSizes(QDC_ALL_PATHS, ctypes.byref(path_count), ctypes.byref(mode_count))
            if res != 0 or path_count.value == 0:
                return self._fallback_enum_monitors()

            paths = (DISPLAYCONFIG_PATH_INFO * path_count.value)()
            modes = (ctypes.c_byte * (mode_count.value * 64))()
            res = user32.QueryDisplayConfig(QDC_ALL_PATHS, ctypes.byref(path_count), paths, ctypes.byref(mode_count), modes, None)
            if res != 0:
                return self._fallback_enum_monitors()

            # Rutas actualmente activas
            act_path_count = wintypes.UINT()
            act_mode_count = wintypes.UINT()
            active_target_ids = set()
            if user32.GetDisplayConfigBufferSizes(QDC_ONLY_ACTIVE_PATHS, ctypes.byref(act_path_count), ctypes.byref(act_mode_count)) == 0 and act_path_count.value > 0:
                act_paths = (DISPLAYCONFIG_PATH_INFO * act_path_count.value)()
                act_modes = (ctypes.c_byte * (act_mode_count.value * 64))()
                if user32.QueryDisplayConfig(QDC_ONLY_ACTIVE_PATHS, ctypes.byref(act_path_count), act_paths, ctypes.byref(act_mode_count), act_modes, None) == 0:
                    for i in range(act_path_count.value):
                        active_target_ids.add(act_paths[i].targetInfo.id)

            seen_targets = set()
            for i in range(path_count.value):
                p = paths[i]
                tid = p.targetInfo.id
                if tid in seen_targets:
                    continue

                target_name = DISPLAYCONFIG_TARGET_DEVICE_NAME()
                target_name.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME
                target_name.header.size = ctypes.sizeof(DISPLAYCONFIG_TARGET_DEVICE_NAME)
                target_name.header.adapterId = p.targetInfo.adapterId
                target_name.header.id = tid

                source_name = DISPLAYCONFIG_SOURCE_DEVICE_NAME()
                source_name.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME
                source_name.header.size = ctypes.sizeof(DISPLAYCONFIG_SOURCE_DEVICE_NAME)
                source_name.header.adapterId = p.sourceInfo.adapterId
                source_name.header.id = p.sourceInfo.id

                user32.DisplayConfigGetDeviceInfo(ctypes.byref(target_name))
                user32.DisplayConfigGetDeviceInfo(ctypes.byref(source_name))

                friendly = target_name.monitorFriendlyDeviceName
                if not friendly:
                    continue

                seen_targets.add(tid)
                is_active = (tid in active_target_ids)

                # Extraer Short Monitor ID / PNP ID directamente de monitorDevicePath
                # Formato típico: \\?\DISPLAY#GSM5C8A#5&2c98c06d&0&UID176387#{...}
                device_path = target_name.monitorDevicePath
                short_id = ""
                if device_path and "#" in device_path:
                    parts = device_path.split("#")
                    if len(parts) > 1:
                        short_id = parts[1]

                # Si está activo usamos el GDI actual; si está inactivo Windows puede haber
                # reasignado temporalmente el nombre de GDI, por lo que nos apoyamos en short_id
                gdi = source_name.viewGdiDeviceName if is_active else ""

                width, height, hz = 0, 0, 0
                is_primary = False

                if is_active and gdi:
                    dm = DEVMODEW()
                    dm.dmSize = ctypes.sizeof(DEVMODEW)
                    if user32.EnumDisplaySettingsW(gdi, -1, ctypes.byref(dm)):
                        width = dm.dmPelsWidth
                        height = dm.dmPelsHeight
                        hz = dm.dmDisplayFrequency
                        if dm.dmPosition.x == 0 and dm.dmPosition.y == 0:
                            is_primary = True
                else:
                    # Intento de obtener resolución nativa desde el registro
                    dm = DEVMODEW()
                    dm.dmSize = ctypes.sizeof(DEVMODEW)
                    if gdi and user32.EnumDisplaySettingsW(gdi, -2, ctypes.byref(dm)):
                        width = dm.dmPelsWidth
                        height = dm.dmPelsHeight
                        hz = dm.dmDisplayFrequency

                available_hz = []
                if gdi and width > 0 and height > 0:
                    seen_hz = set()
                    idx = 0
                    dm_enum = DEVMODEW()
                    dm_enum.dmSize = ctypes.sizeof(DEVMODEW)
                    while user32.EnumDisplaySettingsW(gdi, idx, ctypes.byref(dm_enum)):
                        if dm_enum.dmPelsWidth == width and dm_enum.dmPelsHeight == height:
                            if dm_enum.dmDisplayFrequency > 0:
                                seen_hz.add(dm_enum.dmDisplayFrequency)
                        idx += 1
                    if hz > 0:
                        seen_hz.add(hz)
                    available_hz = sorted(list(seen_hz), reverse=True)
                elif hz > 0:
                    available_hz = [hz]

                # Si tenemos tasas disponibles y un short_id, actualizamos el caché
                if available_hz and short_id:
                    cached_dict = self.config.setdefault("cached_refresh_rates", {})
                    if cached_dict.get(short_id) != available_hz:
                        cached_dict[short_id] = available_hz
                        self._save_config()
                elif not available_hz and short_id:
                    # Si la pantalla está inactiva o apagada, recuperamos sus frecuencias conocidas
                    cached = self.config.get("cached_refresh_rates", {}).get(short_id)
                    if cached:
                        available_hz = list(cached)

                startup_rates = self.get_startup_refresh_rates()
                startup_hz = startup_rates.get(short_id, hz)

                # Si aún no hay frecuencias disponibles, asegurar al menos startup_hz o 60 Hz
                if not available_hz:
                    if startup_hz > 0:
                        available_hz = [startup_hz]
                    elif hz > 0:
                        available_hz = [hz]
                    else:
                        available_hz = [60]

                m_obj = MonitorInfo(
                    target_id=tid,
                    friendly_name=friendly,
                    gdi_name=gdi,
                    pnp_id=short_id,
                    short_id=short_id,
                    device_path=device_path,
                    is_primary=is_primary,
                    is_active=is_active,
                    width=width,
                    height=height,
                    hz=hz,
                    is_designated_tv=False,
                    is_designated_primary=False,
                    available_refresh_rates=available_hz,
                    startup_hz=startup_hz
                )
                m_obj.is_designated_tv = self._matches_designated_tv(m_obj)
                m_obj.is_designated_primary = self._matches_designated_primary(m_obj)
                monitors.append(m_obj)

            # Si no hay monitor principal configurado aún, auto-asignar el monitor principal actual que no sea TV
            if not self.config.get("designated_primary_id"):
                current_prim = next((m for m in monitors if m.is_primary and not m.is_designated_tv), None)
                if current_prim and current_prim.short_id:
                    self.config["designated_primary_id"] = current_prim.short_id
                    self.config["designated_primary_name"] = current_prim.friendly_name
                    self._save_config()
                    current_prim.is_designated_primary = True

            # Ordenar: primero el monitor principal designado (o principal de Windows), luego los demás monitores y al final el televisor
            monitors.sort(key=lambda m: (0 if m.is_designated_primary else (1 if m.is_primary else (3 if m.is_designated_tv else 2))))

            self._cached_monitors = monitors
            self._last_state_check = now
            return monitors

    def _fallback_enum_monitors(self):
        return []

    def is_tv_active(self):
        """Retorna True si el monitor designado como Televisor está activo en Windows"""
        target = self.get_designated_tv()
        if target:
            return target.is_active
        return False

    def toggle_tv(self):
        """Alterna el estado del televisor asignado"""
        tv = self.get_designated_tv()
        if not tv:
            return False, "No hay ningún monitor designado como Televisor."
        if tv.is_active:
            return self.turn_off_monitor(tv)
        else:
            return self.turn_on_monitor(tv)

    def turn_off_tv(self):
        tv = self.get_designated_tv()
        if not tv:
            return False, "No se encontró ningún televisor configurado."
        return self.turn_off_monitor(tv)

    def turn_on_tv(self):
        tv = self.get_designated_tv()
        if not tv:
            return False, "No se encontró ningún televisor configurado."
        return self.turn_on_monitor(tv)

    def _get_monitor_rect(self, monitor):
        """Retorna el rectángulo (left, top, right, bottom) del monitor en coordenadas virtuales"""
        if not monitor:
            return None
        gdi = monitor.gdi_name
        if not gdi:
            for m in self.get_connected_monitors():
                if m.short_id == monitor.short_id and m.gdi_name:
                    gdi = m.gdi_name
                    break
        if not gdi:
            return None
        dm = DEVMODEW()
        dm.dmSize = ctypes.sizeof(DEVMODEW)
        if user32.EnumDisplaySettingsW(gdi, -1, ctypes.byref(dm)):
            return (dm.dmPosition.x, dm.dmPosition.y, dm.dmPosition.x + dm.dmPelsWidth, dm.dmPosition.y + dm.dmPelsHeight)
        return None

    def _snapshot_tv_windows(self):
        """Guarda la posición de las ventanas abiertas en el televisor antes de apagarlo"""
        if not self.get_restore_window_layout():
            self._saved_tv_windows = []
            return

        tv = self.get_designated_tv()
        if not tv or not tv.is_active:
            return

        tv_rect = self._get_monitor_rect(tv)
        if not tv_rect:
            return

        saved = []
        DESKTOPENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def enum_proc(hwnd, lparam):
            try:
                if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                    return True
                length = user32.GetWindowTextLengthW(hwnd)
                if length == 0:
                    return True
                ex_style = user32.GetWindowLongW(hwnd, -20)
                if ex_style & 0x00000080:  # WS_EX_TOOLWINDOW
                    return True

                class_buf = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_buf, 256)
                c_name = class_buf.value
                if c_name in ("Progman", "Shell_TrayWnd", "Windows.UI.Core.CoreWindow", "WorkerW"):
                    return True

                rect = RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                w = rect.right - rect.left
                h = rect.bottom - rect.top
                if w <= 10 or h <= 10:
                    return True

                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2

                if tv_rect[0] <= cx < tv_rect[2] and tv_rect[1] <= cy < tv_rect[3]:
                    is_zoomed = bool(user32.IsZoomed(hwnd))
                    saved.append({
                        "hwnd": hwnd,
                        "is_zoomed": is_zoomed,
                        "rel_x": rect.left - tv_rect[0],
                        "rel_y": rect.top - tv_rect[1],
                        "width": w,
                        "height": h
                    })
            except Exception:
                pass
            return True

        cb = DESKTOPENUMPROC(enum_proc)
        try:
            hdesk = user32.OpenDesktopW("Default", 0, False, 0x0100 | 0x0040 | 0x0001)
            if hdesk:
                user32.EnumDesktopWindows(hdesk, cb, 0)
                user32.CloseDesktop(hdesk)
            else:
                user32.EnumWindows(cb, 0)
        except Exception:
            user32.EnumWindows(cb, 0)

        self._saved_tv_windows = saved

    def _restore_tv_windows(self):
        """Restaura las ventanas en el televisor luego de encenderlo"""
        if not self.get_restore_window_layout() or not self._saved_tv_windows:
            return

        time.sleep(1.0)
        tv = self.get_designated_tv()
        if not tv:
            return

        tv_rect = self._get_monitor_rect(tv)
        if not tv_rect:
            self.get_connected_monitors(force_refresh=True)
            tv = self.get_designated_tv()
            if tv:
                tv_rect = self._get_monitor_rect(tv)
            if not tv_rect:
                return

        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010
        SW_RESTORE = 9
        SW_MAXIMIZE = 3

        for win in self._saved_tv_windows:
            hwnd = win["hwnd"]
            try:
                if user32.IsWindow(hwnd):
                    new_x = tv_rect[0] + win["rel_x"]
                    new_y = tv_rect[1] + win["rel_y"]
                    w = win["width"]
                    h = win["height"]

                    if win["is_zoomed"]:
                        user32.ShowWindow(hwnd, SW_RESTORE)
                        user32.SetWindowPos(hwnd, 0, new_x, new_y, w, h, SWP_NOZORDER | SWP_NOACTIVATE)
                        user32.ShowWindow(hwnd, SW_MAXIMIZE)
                    else:
                        user32.SetWindowPos(hwnd, 0, new_x, new_y, w, h, SWP_NOZORDER | SWP_NOACTIVATE)
            except Exception:
                pass

        self._saved_tv_windows = []

    def turn_off_monitor(self, monitor_or_id):
        """Desactiva un monitor o televisor específico usando su identificador persistente"""
        target_m = self._resolve_monitor(monitor_or_id)
        if not target_m:
            return False, "Monitor no encontrado."

        if not target_m.is_active:
            return True, t("msg_tv_off", self.get_language(), tv=target_m.friendly_name)

        if target_m.is_designated_tv:
            self._snapshot_tv_windows()

        monitors = self.get_connected_monitors(force_refresh=True)
        active_monitors = [m for m in monitors if m.is_active]

        # Si es la única pantalla activa, Windows no permite apagarla
        if len(active_monitors) <= 1:
            return False, "No se puede apagar la única pantalla activa."

        # Si el monitor a apagar es el principal, debemos transferir el rol principal a otro monitor activo
        if target_m.is_primary:
            other_active = [m for m in active_monitors if m.short_id != target_m.short_id]
            if other_active and os.path.exists(self.tools_exe):
                # Priorizar el monitor principal designado si está activo entre los restantes
                des_primary = self.get_designated_primary()
                if des_primary and any(m.short_id == des_primary.short_id for m in other_active):
                    preferred = next(m for m in other_active if m.short_id == des_primary.short_id)
                else:
                    preferred = next((m for m in other_active if not m.is_designated_tv), other_active[0])

                if preferred.short_id:
                    try:
                        subprocess.run(
                            [self.tools_exe, "/SetPrimary", preferred.short_id],
                            check=False, creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        time.sleep(0.4)
                    except Exception:
                        pass

        # Desactivar usando SOLO short_id o gdi_name (sin friendly_name para no romper argumentos)
        if os.path.exists(self.tools_exe):
            try:
                ident = target_m.short_id or (target_m.gdi_name if target_m.is_active else None)
                if ident:
                    subprocess.run(
                        [self.tools_exe, "/disable", ident],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                time.sleep(0.5)
                self.get_connected_monitors(force_refresh=True)
                return True, t("msg_tv_off", self.get_language(), tv=target_m.friendly_name)
            except Exception as e:
                return False, f"Error: {e}"

        return False, "MultiMonitorTool error"

    def turn_on_monitor(self, monitor_or_id):
        """Activa un monitor o televisor específico usando su identificador de hardware persistente"""
        target_m = self._resolve_monitor(monitor_or_id)
        if not target_m:
            return False, "Monitor no encontrado"

        if target_m.is_active:
            return True, t("msg_tv_on", self.get_language(), tv=target_m.friendly_name)

        if os.path.exists(self.tools_exe):
            try:
                # 1. Despertar la salida de video usando DisplaySwitch /extend de Windows
                try:
                    subprocess.run(
                        ["C:\\Windows\\System32\\DisplaySwitch.exe", "/extend"],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except Exception:
                    pass

                # 2. Habilitar explícitamente en MultiMonitorTool usando SOLO short_id
                if target_m.short_id:
                    subprocess.run(
                        [self.tools_exe, "/enable", target_m.short_id],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )

                time.sleep(0.6)
                if target_m.short_id:
                    self.apply_startup_refresh_rates(only_ids=[target_m.short_id])

                # Si el monitor principal designado está activo o se acaba de encender, restaurarlo como Windows Primary
                des_primary = self.get_designated_primary()
                if des_primary and des_primary.short_id:
                    if target_m.short_id == des_primary.short_id or (des_primary.is_active and not target_m.is_designated_tv):
                        try:
                            subprocess.run(
                                [self.tools_exe, "/SetPrimary", des_primary.short_id],
                                check=False, creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            time.sleep(0.3)
                        except Exception:
                            pass

                if target_m.is_designated_tv:
                    threading.Thread(target=self._restore_tv_windows, daemon=True).start()

                self.get_connected_monitors(force_refresh=True)
                return True, t("msg_tv_on", self.get_language(), tv=target_m.friendly_name)
            except Exception as e:
                return False, f"Error: {e}"

        return False, "Herramienta MultiMonitorTool no disponible."

    def toggle_monitor(self, monitor_or_id):
        """Alterna el estado de cualquier monitor"""
        target_m = self._resolve_monitor(monitor_or_id)
        if not target_m:
            return False, "Monitor no encontrado."
        if target_m.is_active:
            return self.turn_off_monitor(target_m)
        else:
            return self.turn_on_monitor(target_m)

    def _resolve_monitor(self, monitor_or_id):
        if isinstance(monitor_or_id, MonitorInfo):
            # Refrescar desde la caché para tener el estado actualizado
            for m in self._cached_monitors:
                if (m.short_id and m.short_id == monitor_or_id.short_id) or m.target_id == monitor_or_id.target_id:
                    return m
            return monitor_or_id
        s = str(monitor_or_id).strip()
        for m in self._cached_monitors:
            if s.upper() in (m.short_id.upper(), m.pnp_id.upper(), m.gdi_name.upper(), m.friendly_name.upper(), str(m.target_id)):
                return m
        monitors = self.get_connected_monitors()
        for m in monitors:
            if s.upper() in (m.short_id.upper(), m.pnp_id.upper(), m.gdi_name.upper(), m.friendly_name.upper(), str(m.target_id)):
                return m
        return None

    def set_monitors_only_mode(self):
        """
        Modo 'Solo Monitores':
        Enciende todos los monitores normales de escritorio y apaga los televisores designados.
        """
        monitors = self.get_connected_monitors(force_refresh=True)
        tvs = [m for m in monitors if m.is_designated_tv]
        non_tvs = [m for m in monitors if not m.is_designated_tv]

        if not tvs:
            # Si no hay ningún televisor designado, encender y extender todos los monitores
            return self.set_extend_all_mode()

        self._snapshot_tv_windows()

        if os.path.exists(self.tools_exe):
            try:
                # 1. Asegurar que los monitores de PC estén despiertos y encendidos PRIMERO
                try:
                    subprocess.run(
                        ["C:\\Windows\\System32\\DisplaySwitch.exe", "/extend"],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except Exception:
                    pass

                non_tv_clean_ids = [m.short_id for m in non_tvs if m.short_id]
                if non_tv_clean_ids:
                    subprocess.run(
                        [self.tools_exe, "/enable"] + non_tv_clean_ids,
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )

                time.sleep(0.6)

                # 2. Ahora que los monitores de PC están activos, asegurar que el monitor de PC sea el Principal
                # Priorizar el monitor principal designado si existe y no es TV
                des_primary = self.get_designated_primary()
                if des_primary and not des_primary.is_designated_tv and any(m.short_id == des_primary.short_id for m in non_tvs):
                    primary_pc = next(m for m in non_tvs if m.short_id == des_primary.short_id)
                else:
                    primary_pc = next((m for m in non_tvs if m.is_primary), None) or (non_tvs[0] if non_tvs else None)

                if primary_pc and primary_pc.short_id:
                    subprocess.run(
                        [self.tools_exe, "/SetPrimary", primary_pc.short_id],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.4)

                # 3. Ahora que el monitor de PC es el Principal, deshabilitar los televisores
                tv_clean_ids = [tv.short_id for tv in tvs if tv.short_id]
                if tv_clean_ids:
                    subprocess.run(
                        [self.tools_exe, "/disable"] + tv_clean_ids,
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )

                time.sleep(0.5)
                # 4. Aplicar tasas de refresco SOLO a los monitores que quedan encendidos (excluyendo TV)
                self.apply_startup_refresh_rates(exclude_ids=tv_clean_ids)
                self.get_connected_monitors(force_refresh=True)
                return True, t("msg_monitors_only_applied", self.get_language())
            except Exception as e:
                return False, f"Error: {e}"

        return False, "MultiMonitorTool error"

    def set_tv_only_mode(self):
        """
        Modo 'Solo TV':
        Enciende las pantallas asignadas como Televisor y apaga todos los demás monitores de PC.
        """
        monitors = self.get_connected_monitors(force_refresh=True)
        tvs = [m for m in monitors if m.is_designated_tv]
        non_tvs = [m for m in monitors if not m.is_designated_tv]

        if not tvs:
            return False, t("dialog_no_tv_msg", self.get_language())

        if os.path.exists(self.tools_exe):
            try:
                # 1. Habilitar todos los televisores (usando SOLO short_id limpio)
                tv_clean_ids = [tv.short_id for tv in tvs if tv.short_id]
                if tv_clean_ids:
                    subprocess.run(
                        [self.tools_exe, "/enable"] + tv_clean_ids,
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.5)

                # 2. Establecer el televisor como monitor Principal de Windows
                main_tv = tvs[0]
                if main_tv.short_id:
                    subprocess.run(
                        [self.tools_exe, "/SetPrimary", main_tv.short_id],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.4)

                # 3. Deshabilitar los monitores de PC (usando SOLO short_id limpio)
                non_tv_clean_ids = [m.short_id for m in non_tvs if m.short_id]
                if non_tv_clean_ids:
                    subprocess.run(
                        [self.tools_exe, "/disable"] + non_tv_clean_ids,
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )

                time.sleep(0.5)
                # 4. Aplicar tasas de refresco SOLO a las TVs activas
                self.apply_startup_refresh_rates(only_ids=tv_clean_ids)
                threading.Thread(target=self._restore_tv_windows, daemon=True).start()
                self.get_connected_monitors(force_refresh=True)
                return True, t("msg_tv_only_applied", self.get_language())
            except Exception as e:
                return False, f"Error: {e}"

        return False, "MultiMonitorTool error"

    def set_extend_all_mode(self):
        """
        Modo 'Extender Todo':
        Enciende todas las pantallas del sistema (monitores y televisor).
        """
        monitors = self.get_connected_monitors(force_refresh=True)
        non_tvs = [m for m in monitors if not m.is_designated_tv]

        # 1. Despertar y extender todas las pantallas usando DisplaySwitch de Windows
        try:
            subprocess.run(
                ["C:\\Windows\\System32\\DisplaySwitch.exe", "/extend"],
                check=False, creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception:
            pass

        # 2. Habilitar explícitamente usando MultiMonitorTool con SOLO short_id válidos
        if os.path.exists(self.tools_exe):
            clean_ids = [m.short_id for m in monitors if m.short_id]
            if clean_ids:
                try:
                    subprocess.run(
                        [self.tools_exe, "/enable"] + clean_ids,
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except Exception:
                    pass

        time.sleep(0.7)

        # 3. Si la TV era la principal, restaurar el monitor principal de PC (priorizando el designado)
        if os.path.exists(self.tools_exe) and non_tvs:
            des_primary = self.get_designated_primary()
            if des_primary and not des_primary.is_designated_tv and any(m.short_id == des_primary.short_id for m in non_tvs):
                primary_pc = next(m for m in non_tvs if m.short_id == des_primary.short_id)
            else:
                primary_pc = next((m for m in non_tvs if m.is_primary), None) or non_tvs[0]

            if primary_pc and primary_pc.short_id:
                try:
                    subprocess.run(
                        [self.tools_exe, "/SetPrimary", primary_pc.short_id],
                        check=False, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.4)
                except Exception:
                    pass

        # 4. Aplicar tasas de refresco configuradas a todas las pantallas
        self.apply_startup_refresh_rates()
        threading.Thread(target=self._restore_tv_windows, daemon=True).start()
        time.sleep(0.4)
        self.get_connected_monitors(force_refresh=True)
        return True, t("msg_extend_applied", self.get_language())

    def set_duplicate_mode(self):
        """
        Modo 'Duplicar Pantalla':
        Clona/duplica el monitor principal específicamente en el televisor designado.
        Asegura que el televisor esté encendido y desactiva pantallas secundarias extras
        para forzar a Windows a duplicar exactamente Principal -> TV.
        """
        monitors = self.get_connected_monitors(force_refresh=True)
        tv = self.get_designated_tv()
        if not tv:
            return False, "No hay ningún televisor designado para duplicar. Por favor designa uno con 'Designar TV'."

        # Encontrar monitor principal y secundarios que no sean la TV
        primary_m = None
        other_monitors = []
        for m in monitors:
            if m.is_primary:
                primary_m = m
            elif not m.is_designated_tv:
                other_monitors.append(m)

        # Si no detectó explícitamente primary, tomar el primer no-TV
        if not primary_m:
            for m in monitors:
                if not m.is_designated_tv:
                    primary_m = m
                    break

        # Identificadores para MultiMonitorTool (usar solo short_id o gdi_name, NUNCA friendly_name)
        tv_id = tv.short_id or (tv.gdi_name if tv.is_active else None)
        primary_id = (primary_m.short_id or (primary_m.gdi_name if primary_m.is_active else None)) if primary_m else None
        other_ids = [m.short_id or (m.gdi_name if m.is_active else None) for m in other_monitors if (m.short_id or m.gdi_name)]

        if os.path.exists(self.tools_exe):
            try:
                # 1. Asegurar que TV y Primary estén habilitados
                enable_targets = [x for x in [primary_id, tv_id] if x]
                if enable_targets:
                    subprocess.run(
                        [self.tools_exe, "/enable"] + enable_targets,
                        check=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                # 2. Deshabilitar otros monitores de escritorio secundarios para que Windows no duplique en ellos
                if other_ids:
                    subprocess.run(
                        [self.tools_exe, "/disable"] + other_ids,
                        check=True, creationflags=subprocess.CREATE_NO_WINDOW
                    )
                time.sleep(0.6)
            except Exception as e:
                print(f"Advertencia preparando monitores para duplicar: {e}")

        # 3. Aplicar topología de clonación (Primary -> TV)
        try:
            res = user32.SetDisplayConfig(0, None, 0, None, SDC_APPLY | SDC_TOPOLOGY_CLONE)
            if res == 0:
                time.sleep(0.6)
                self.get_connected_monitors(force_refresh=True)
                p_name = primary_m.friendly_name if primary_m else "Monitor Principal"
                return True, f"Modo Duplicar activado: '{p_name}' duplicado en '{tv.friendly_name}'."
        except Exception:
            pass

        # Fallback a DisplaySwitch
        try:
            subprocess.run(
                ["C:\\Windows\\System32\\DisplaySwitch.exe", "/clone"],
                check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(0.6)
            self.get_connected_monitors(force_refresh=True)
            p_name = primary_m.friendly_name if primary_m else "Monitor Principal"
            return True, f"Modo Duplicar activado: '{p_name}' duplicado en '{tv.friendly_name}'."
        except Exception as e:
            return False, f"Error al duplicar pantalla: {e}"

    def set_mode(self, mode):
        """Aplica un modo de pantalla unificado"""
        m = mode.lower()
        if m in ("internal", "monitors_only", "solomonitores", "solo_monitores"):
            return self.set_monitors_only_mode()
        elif m in ("tv_only", "solotv", "solo_tv"):
            return self.set_tv_only_mode()
        elif m in ("extend", "extender", "extend_all"):
            return self.set_extend_all_mode()
        elif m in ("clone", "duplicar"):
            return self.set_duplicate_mode()
        else:
            return False, f"Modo desconocido: {mode}"

    def get_state_signature(self):
        """Genera una firma hashable del estado actual de las pantallas para evitar redibujados innecesarios"""
        monitors = self.get_connected_monitors()
        tv = self.get_designated_tv()
        tv_id = (tv.short_id or tv.friendly_name) if tv else ""
        prim_id = self.config.get("designated_primary_id", "")
        return (
            tv_id,
            prim_id,
            tuple(
                (m.target_id, m.short_id, m.friendly_name, m.is_active, m.is_primary, m.is_designated_primary, m.is_designated_tv, m.width, m.height, m.hz)
                for m in monitors
            )
        )


if __name__ == "__main__":
    ctrl = MonitorController()
    print("Monitores detectados:")
    for m in ctrl.get_connected_monitors(force_refresh=True):
        print(" ", m)
    tv = ctrl.get_designated_tv()
    print("Televisor actual asignado:", tv)
