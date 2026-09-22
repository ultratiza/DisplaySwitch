"""
DisplaySwitch - System Tray and Global Hotkey Manager
Copyright (C) 2026 UltraTiza, FedeFadda
Testing & Quality Assurance: FedeNahas
Licencia: Software Libre (GPLv3)

Implementación en 64 bits con ctypes, menú contextual emergente y soporte de ratón
"""

import ctypes
from ctypes import wintypes
import threading
import time
import os
from i18n import t, format_hotkey_display

# Windows User32, Kernel32, Shell32
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

# Mensajes de Windows
WM_APP = 0x8000
WM_TRAYICON = WM_APP + 1
WM_UPDATE_HOTKEYS = WM_APP + 2
WM_SHOW_EXISTING_APP = WM_APP + 10
WM_WAKEUP_STRING = "DisplaySwitch_WakeUp_UltraTizaFede"
try:
    WM_WAKEUP_MSG = user32.RegisterWindowMessageW(WM_WAKEUP_STRING)
except Exception:
    WM_WAKEUP_MSG = 0

WM_COMMAND = 0x0111
WM_RBUTTONUP = 0x0205
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_HOTKEY = 0x0312
WM_DESTROY = 0x0002
WM_DISPLAYCHANGE = 0x007E

# Modificadores de teclas
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# Shell_NotifyIcon
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
NIF_INFO = 0x00000010
NIIF_INFO = 0x00000001

TPM_BOTTOMALIGN = 0x0020
TPM_RIGHTALIGN = 0x0008
MF_STRING = 0x00000000
MF_SEPARATOR = 0x00000800

IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040

# Configurar tipos Win32 para 64 bits de forma exacta
LRESULT = ctypes.c_int64
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

user32.CreateWindowExW.argtypes = [
    wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
]
user32.CreateWindowExW.restype = wintypes.HWND

user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_uint64, wintypes.LPCWSTR]
user32.AppendMenuW.restype = wintypes.BOOL
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.TrackPopupMenuEx.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.HWND, ctypes.c_void_p]
user32.TrackPopupMenuEx.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = [ctypes.c_void_p]
user32.GetCursorPos.restype = wintypes.BOOL

# Hotkey IDs
ID_HOTKEY_TOGGLE = 101
ID_HOTKEY_MONITORS = 102
ID_HOTKEY_TV_ONLY = 103
ID_HOTKEY_EXTEND = 104
ID_HOTKEY_CLONE = 105

# Menú IDs
ID_TRAY_TOGGLE = 1001
ID_TRAY_SOLO_PC = 1002
ID_TRAY_SOLO_TV = 1003
ID_TRAY_EXTENDER = 1004
ID_TRAY_DUPLICAR = 1005
ID_TRAY_SHOW_UI = 1006
ID_TRAY_EXIT = 1007

# Mapeo de teclas virtuales
VK_MAP = {
    'SPACE': 0x20, 'TAB': 0x09, 'ENTER': 0x0D, 'RETURN': 0x0D, 'ESC': 0x1B, 'ESCAPE': 0x1B,
    'INSERT': 0x2D, 'DELETE': 0x2E, 'HOME': 0x24, 'END': 0x23,
    'PAGEUP': 0x21, 'PAGEDOWN': 0x22, 'UP': 0x26, 'DOWN': 0x28, 'LEFT': 0x25, 'RIGHT': 0x27,
    'BACKSPACE': 0x08, 'CAPSLOCK': 0x14, 'NUMLOCK': 0x90, 'SCROLLLOCK': 0x91,
    'PRINTSCREEN': 0x2C, 'PAUSE': 0x13
}
for i in range(1, 25):
    VK_MAP[f'F{i}'] = 0x70 + (i - 1)

# Constantes y Tipos de Hook del Ratón
WH_MOUSE_LL = 14
WM_MBUTTONDOWN = 0x0207
WM_XBUTTONDOWN = 0x020B

HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = LRESULT

class POINT(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('pt', POINT),
        ('mouseData', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_uint64),
    ]

# Mapeo de botones de ratón
MOUSE_BUTTON_MAP = {
    'MBUTTON': 'MBUTTON',
    'MIDDLECLICK': 'MBUTTON',
    'BOTONCENTRAL': 'MBUTTON',
    'MOUSE3': 'MBUTTON',
    'XBUTTON1': 'XBUTTON1',
    'MOUSE4': 'XBUTTON1',
    'BOTONLATERAL1': 'XBUTTON1',
    'XBUTTON2': 'XBUTTON2',
    'MOUSE5': 'XBUTTON2',
    'BOTONLATERAL2': 'XBUTTON2',
}

def parse_hotkey(hk_str):
    """
    Convierte una cadena como 'Ctrl+Alt+T' o 'Ctrl+XButton1' en:
    (is_mouse, modifiers, key_or_mouse_code)
    """
    if not hk_str:
        return False, 0, 0
    parts = [p.strip().upper() for p in hk_str.split('+') if p.strip()]
    mods = 0
    mouse_btn = None
    vk = 0
    for p in parts:
        if p in ('CTRL', 'CONTROL'):
            mods |= MOD_CONTROL
        elif p == 'ALT':
            mods |= MOD_ALT
        elif p == 'SHIFT':
            mods |= MOD_SHIFT
        elif p in ('WIN', 'WINDOWS'):
            mods |= MOD_WIN
        elif p in MOUSE_BUTTON_MAP:
            mouse_btn = MOUSE_BUTTON_MAP[p]
        elif p in VK_MAP:
            vk = VK_MAP[p]
        elif len(p) == 1:
            vk = ord(p)

    if mouse_btn:
        return True, mods, mouse_btn
    elif vk != 0:
        return False, mods | MOD_NOREPEAT, vk
    return False, 0, 0


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('hWnd', wintypes.HWND),
        ('uID', wintypes.UINT),
        ('uFlags', wintypes.UINT),
        ('uCallbackMessage', wintypes.UINT),
        ('hIcon', wintypes.HICON),
        ('szTip', wintypes.WCHAR * 128),
        ('dwState', wintypes.DWORD),
        ('dwStateMask', wintypes.DWORD),
        ('szInfo', wintypes.WCHAR * 256),
        ('uTimeoutOrVersion', wintypes.UINT),
        ('szInfoTitle', wintypes.WCHAR * 64),
        ('dwInfoFlags', wintypes.DWORD),
    ]

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.UINT),
        ('style', wintypes.UINT),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', ctypes.c_int),
        ('cbWndExtra', ctypes.c_int),
        ('hInstance', wintypes.HINSTANCE),
        ('hIcon', wintypes.HICON),
        ('hCursor', wintypes.HANDLE),
        ('hbrBackground', wintypes.HBRUSH),
        ('lpszMenuName', wintypes.LPCWSTR),
        ('lpszClassName', wintypes.LPCWSTR),
        ('hIconSm', wintypes.HICON),
    ]


class TrayAndHotkeyManager:
    def __init__(self, on_toggle, on_mode, on_show_ui, on_exit, on_display_change=None, get_hotkeys_func=None, on_context_menu=None, get_app_title_func=None, get_show_notifications_func=None, get_language_func=None):
        self.on_toggle = on_toggle
        self.on_mode = on_mode
        self.on_show_ui = on_show_ui
        self.on_exit = on_exit
        self.on_display_change = on_display_change
        self.get_hotkeys_func = get_hotkeys_func
        self.on_context_menu = on_context_menu
        self.get_app_title_func = get_app_title_func
        self.get_show_notifications_func = get_show_notifications_func
        self.get_language_func = get_language_func
        
        self.hwnd = None
        self.h_icon = None
        self._thread = None
        self._running = False
        self._wndproc = None
        self._registered_hotkeys = set()
        self._mouse_hook = None
        self._mouse_hotkeys = []
        self._mouse_hook_proc = None

    def get_language(self):
        if self.get_language_func:
            return self.get_language_func()
        return "en"

    def get_title(self):
        """Retorna el título dinámico según el modo configurado"""
        if self.get_app_title_func:
            return self.get_app_title_func()
        return "DisplaySwitch"

    def start(self):
        """Inicia el bucle de mensajes en segundo plano para el atajo y el icono de la bandeja"""
        self._running = True
        self._thread = threading.Thread(target=self._run_message_loop, daemon=True)
        self._thread.start()

    def reload_hotkeys(self):
        """Solicita al hilo Win32 re-registrar los atajos de teclado y mouse en caliente"""
        if self.hwnd:
            user32.PostMessageW(self.hwnd, WM_UPDATE_HOTKEYS, 0, 0)

    def _run_message_loop(self):
        hInstance = kernel32.GetModuleHandleW(None)
        class_name = "DisplaySwitchHiddenWndClass"

        def mouse_hook_callback(nCode, wParam, lParam):
            if nCode >= 0:
                btn_name = None
                if wParam == WM_MBUTTONDOWN:
                    btn_name = 'MBUTTON'
                elif wParam == WM_XBUTTONDOWN:
                    try:
                        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                        x_btn = (info.mouseData >> 16) & 0xFFFF
                        if x_btn == 1:
                            btn_name = 'XBUTTON1'
                        elif x_btn == 2:
                            btn_name = 'XBUTTON2'
                    except Exception:
                        pass

                if btn_name and self._mouse_hotkeys:
                    ctrl = bool(user32.GetAsyncKeyState(0x11) & 0x8000)
                    alt = bool(user32.GetAsyncKeyState(0x12) & 0x8000)
                    shift = bool(user32.GetAsyncKeyState(0x10) & 0x8000)
                    win = bool((user32.GetAsyncKeyState(0x5B) & 0x8000) or (user32.GetAsyncKeyState(0x5C) & 0x8000))

                    current_mods = 0
                    if ctrl: current_mods |= MOD_CONTROL
                    if alt: current_mods |= MOD_ALT
                    if shift: current_mods |= MOD_SHIFT
                    if win: current_mods |= MOD_WIN

                    for action_id, target_mods, target_btn in self._mouse_hotkeys:
                        if target_btn == btn_name and target_mods == current_mods:
                            if action_id == ID_HOTKEY_TOGGLE and self.on_toggle:
                                self.on_toggle()
                            elif action_id == ID_HOTKEY_MONITORS and self.on_mode:
                                self.on_mode("monitors_only")
                            elif action_id == ID_HOTKEY_TV_ONLY and self.on_mode:
                                self.on_mode("tv_only")
                            elif action_id == ID_HOTKEY_EXTEND and self.on_mode:
                                self.on_mode("extend")
                            elif action_id == ID_HOTKEY_CLONE and self.on_mode:
                                self.on_mode("clone")
                            break

            return user32.CallNextHookEx(self._mouse_hook, nCode, wParam, lParam)

        self._mouse_hook_proc = HOOKPROC(mouse_hook_callback)

        def _register_hotkeys_internal(hWnd):
            # 1. Desregistrar atajos de teclado previos
            for hk_id in list(self._registered_hotkeys):
                user32.UnregisterHotKey(hWnd, hk_id)
            self._registered_hotkeys.clear()

            # 2. Desregistrar hook de ratón previo
            if self._mouse_hook:
                try:
                    user32.UnhookWindowsHookEx(self._mouse_hook)
                except Exception:
                    pass
                self._mouse_hook = None
            self._mouse_hotkeys.clear()

            hotkeys = self.get_hotkeys_func() if self.get_hotkeys_func else {}
            hotkey_mapping = [
                (ID_HOTKEY_TOGGLE, hotkeys.get("toggle_tv", "Ctrl+Alt+T")),
                (ID_HOTKEY_MONITORS, hotkeys.get("monitors_only", "")),
                (ID_HOTKEY_TV_ONLY, hotkeys.get("tv_only", "Ctrl+Alt+V")),
                (ID_HOTKEY_EXTEND, hotkeys.get("extend_all", ""))
            ]

            for hk_id, hk_str in hotkey_mapping:
                if hk_str:
                    is_mouse, mods, code = parse_hotkey(hk_str)
                    if is_mouse:
                        self._mouse_hotkeys.append((hk_id, mods, code))
                    elif code != 0:
                        reg_ok = user32.RegisterHotKey(hWnd, hk_id, mods, code)
                        if not reg_ok:
                            reg_ok = user32.RegisterHotKey(hWnd, hk_id, mods & ~MOD_NOREPEAT, code)
                        if reg_ok:
                            self._registered_hotkeys.add(hk_id)

            # Instalar hook del ratón si se configuró al menos un atajo con mouse
            if self._mouse_hotkeys:
                self._mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self._mouse_hook_proc, 0, 0)

        def py_wndproc(hWnd, msg, wParam, lParam):
            if msg == WM_HOTKEY:
                if wParam == ID_HOTKEY_TOGGLE:
                    if self.on_toggle:
                        self.on_toggle()
                elif wParam == ID_HOTKEY_MONITORS:
                    if self.on_mode:
                        self.on_mode("monitors_only")
                elif wParam == ID_HOTKEY_TV_ONLY:
                    if self.on_mode:
                        self.on_mode("tv_only")
                elif wParam == ID_HOTKEY_EXTEND:
                    if self.on_mode:
                        self.on_mode("extend")
                elif wParam == ID_HOTKEY_CLONE:
                    if self.on_mode:
                        self.on_mode("clone")
                return 0

            elif msg == WM_UPDATE_HOTKEYS:
                _register_hotkeys_internal(hWnd)
                return 0

            elif (msg == WM_SHOW_EXISTING_APP) or (WM_WAKEUP_MSG != 0 and msg == WM_WAKEUP_MSG):
                if self.on_show_ui:
                    self.on_show_ui()
                return 0

            elif msg == WM_TRAYICON:
                if lParam == WM_RBUTTONUP:
                    pt = POINT()
                    user32.GetCursorPos(ctypes.byref(pt))
                    if self.on_context_menu:
                        self.on_context_menu(pt.x, pt.y)
                    else:
                        self._show_context_menu(hWnd, pt.x, pt.y)
                elif lParam in (WM_LBUTTONUP, WM_LBUTTONDBLCLK):
                    if self.on_show_ui:
                        self.on_show_ui()
                return 0

            elif msg == WM_COMMAND:
                cmd_id = wParam & 0xFFFF
                if cmd_id == ID_TRAY_TOGGLE:
                    if self.on_toggle:
                        self.on_toggle()
                elif cmd_id == ID_TRAY_SOLO_PC:
                    if self.on_mode:
                        self.on_mode("monitors_only")
                elif cmd_id == ID_TRAY_SOLO_TV:
                    if self.on_mode:
                        self.on_mode("tv_only")
                elif cmd_id == ID_TRAY_EXTENDER:
                    if self.on_mode:
                        self.on_mode("extend")
                elif cmd_id == ID_TRAY_DUPLICAR:
                    if self.on_mode:
                        self.on_mode("clone")
                elif cmd_id == ID_TRAY_SHOW_UI:
                    if self.on_show_ui:
                        self.on_show_ui()
                elif cmd_id == ID_TRAY_EXIT:
                    if self.on_exit:
                        self.on_exit()
                return 0

            elif msg == WM_DISPLAYCHANGE:
                if self.on_display_change:
                    self.on_display_change()
                return 0

            elif msg == WM_DESTROY:
                self._remove_tray_icon()
                if self._mouse_hook:
                    try:
                        user32.UnhookWindowsHookEx(self._mouse_hook)
                    except Exception:
                        pass
                    self._mouse_hook = None
                self._mouse_hotkeys.clear()
                for hk_id in list(self._registered_hotkeys):
                    user32.UnregisterHotKey(hWnd, hk_id)
                self._registered_hotkeys.clear()
                user32.PostQuitMessage(0)
                return 0

            return user32.DefWindowProcW(hWnd, msg, wParam, lParam)

        self._wndproc = WNDPROC(py_wndproc)

        wcex = WNDCLASSEXW()
        wcex.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wcex.lpfnWndProc = self._wndproc
        wcex.hInstance = hInstance
        wcex.lpszClassName = class_name

        user32.RegisterClassExW(ctypes.byref(wcex))

        self.hwnd = user32.CreateWindowExW(
            0, class_name, "DisplaySwitchHiddenWindow", 0, 0, 0, 0, 0, None, None, hInstance, None
        )

        # Cargar icono personalizado ("Fede")
        app_dir = os.path.dirname(os.path.abspath(__file__))
        ico_path = os.path.join(app_dir, "app_icon.ico")
        self.h_icon = None
        if os.path.exists(ico_path):
            try:
                self.h_icon = user32.LoadImageW(
                    None, ico_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE
                )
            except Exception:
                pass

        if not self.h_icon:
            self.h_icon = user32.LoadIconW(None, ctypes.c_wchar_p(32512))

        # Registrar icono en el System Tray
        self._add_tray_icon()

        # Registrar atajos de teclado iniciales
        _register_hotkeys_internal(self.hwnd)

        # Bucle de mensajes estándar Win32
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0 and self._running:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def _add_tray_icon(self):
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        nid.uCallbackMessage = WM_TRAYICON
        nid.hIcon = self.h_icon
        nid.szTip = f"{self.get_title()} - Activo"[:127]
        shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))

    def update_tooltip(self, text):
        if not self.hwnd:
            return
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_TIP
        app_t = self.get_title()
        nid.szTip = f"{app_t}: {text}"[:127]
        shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid))

    def show_notification(self, title=None, message=""):
        """Muestra una notificación flotante (balloon/toast) en Windows si están activadas"""
        if not self.hwnd:
            return
        if self.get_show_notifications_func and not self.get_show_notifications_func():
            return
        eff_title = title if title else self.get_title()
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.hwnd
        nid.uID = 1
        nid.uFlags = NIF_INFO
        nid.szInfo = message[:255]
        nid.szInfoTitle = eff_title[:63]
        nid.dwInfoFlags = NIIF_INFO
        shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid))

    def _show_context_menu(self, hWnd, x, y):
        lang = self.get_language()
        hotkeys = self.get_hotkeys_func() if self.get_hotkeys_func else {}
        hk_toggle = format_hotkey_display(hotkeys.get("toggle_tv", ""), lang=lang, for_tray=True)
        hk_monitors = format_hotkey_display(hotkeys.get("monitors_only", ""), lang=lang, for_tray=True)
        hk_tv_only = format_hotkey_display(hotkeys.get("tv_only", ""), lang=lang, for_tray=True)
        hk_extend = format_hotkey_display(hotkeys.get("extend_all", ""), lang=lang, for_tray=True)

        hMenu = user32.CreatePopupMenu()
        lbl_toggle = f"{t('tray_toggle_default', lang)} [{hk_toggle}]" if hk_toggle else t('tray_toggle_default', lang)
        lbl_monitors = f"{t('tray_monitors_only', lang)} [{hk_monitors}]" if hk_monitors else t('tray_monitors_only', lang)
        lbl_tv_only = f"{t('tray_tv_only', lang)} [{hk_tv_only}]" if hk_tv_only else t('tray_tv_only', lang)
        lbl_extend = f"{t('tray_extend_all', lang)} [{hk_extend}]" if hk_extend else t('tray_extend_all', lang)

        user32.AppendMenuW(hMenu, MF_STRING, ID_TRAY_TOGGLE, f"⚡ {lbl_toggle}")
        user32.AppendMenuW(hMenu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(hMenu, MF_STRING, ID_TRAY_SOLO_PC, f"🖥️ {lbl_monitors}")
        user32.AppendMenuW(hMenu, MF_STRING, ID_TRAY_SOLO_TV, f"📺 {lbl_tv_only}")
        user32.AppendMenuW(hMenu, MF_STRING, ID_TRAY_EXTENDER, f"🪟 {lbl_extend}")
        user32.AppendMenuW(hMenu, MF_SEPARATOR, 0, None)
        user32.AppendMenuW(hMenu, MF_STRING, ID_TRAY_SHOW_UI, t('tray_open_app', lang, title=self.get_title()))
        user32.AppendMenuW(hMenu, MF_STRING, ID_TRAY_EXIT, t('tray_exit', lang))

        user32.SetForegroundWindow(hWnd)
        user32.TrackPopupMenuEx(hMenu, TPM_BOTTOMALIGN | TPM_RIGHTALIGN, x, y, hWnd, None)
        user32.DestroyMenu(hMenu)

    def _remove_tray_icon(self):
        if self.hwnd:
            nid = NOTIFYICONDATAW()
            nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
            nid.hWnd = self.hwnd
            nid.uID = 1
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))

    def stop(self):
        self._running = False
        if self._mouse_hook:
            try:
                user32.UnhookWindowsHookEx(self._mouse_hook)
            except Exception:
                pass
            self._mouse_hook = None
        if self.hwnd:
            user32.PostMessageW(self.hwnd, WM_DESTROY, 0, 0)
