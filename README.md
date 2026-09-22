# DisplaySwitch

Windows desktop utility to seamlessly toggle secondary TVs or monitors off and on, remember per-display startup refresh rates (Hz), designate your preferred primary monitor, and switch display profiles with customizable global keyboard and mouse shortcuts.

---

## English

### Key Features
- **Clean TV / Monitor Toggling**: Powers off the video signal to secondary displays so Windows completely drops them from the desktop (windows and mouse cursor won't wander off). Powers back on instantly on demand.
- **Refresh Rate Memory**: Automatically detects and restores each monitor's preferred startup refresh rate (Hz) upon re-enabling.
- **Persistent Primary Monitor**: Designate your main gaming/work display to keep Windows from shifting the primary display role when turning other screens on or off.
- **Mouse & Keyboard Hotkeys**: Configure global shortcuts using keyboard combinations or extra mouse buttons (`Middle Click`, `Mouse 4 / XButton1`, `Mouse 5 / XButton2`).
- **Global Modes**: Instant switching between "Monitors Only", "TV Only", and "Extend All".

### How to Run

#### Option 1: Run directly from source (Python)
No external pip packages required (uses Python standard library `tkinter` and `ctypes`):
```powershell
python main.py
```
*(Requires Python 3.10+ on Windows 10/11)*

#### Option 2: Pre-built Binary (`MonitorSwitch.exe`)
Download the standalone executable from the **[Releases](https://github.com/ultratiza/DisplaySwitch/releases)** tab.
> **Note on executable naming**: The standalone binary is named `MonitorSwitch.exe` specifically to avoid filename collisions with Windows' native `C:\Windows\System32\DisplaySwitch.exe` (the built-in Win+P projection utility).

### Default Shortcuts
| Action | Hotkey |
| :--- | :--- |
| **Toggle TV** | `Ctrl + Alt + T` |
| **Monitors Only** | `Ctrl + Alt + M` |
| **TV Only** | `Ctrl + Alt + V` |
| **Extend All** | `Ctrl + Alt + E` |

---

## Español

### Características Principales
- **Corte Limpio de TV / Monitor**: Corta la señal de video del televisor o monitor secundario para que Windows lo desconecte por completo del escritorio (el cursor y las ventanas no quedan atrapados). Se reactiva al instante con un atajo.
- **Memoria de Tasa de Refresco**: Detecta y restaura automáticamente la tasa de refresco (Hz) elegida para cada pantalla al reencenderla.
- **Monitor Principal Persistente**: Permite elegir qué monitor debe mantenerse siempre como Principal de Windows, evitando que se desconfigure al apagar o prender pantallas.
- **Atajos de Teclado y Ratón**: Atajos globales configurables para combinaciones de teclas o botones extra del mouse (`Rueda / Clic Central`, `Botón 4`, `Botón 5`).
- **Modos Globales**: Cambio rápido entre "Solo Monitores", "Solo TV" y "Extender Todo".

### Cómo ejecutar

#### Opción 1: Ejecutar con Python directamente
Sin necesidad de instalar paquetes externos vía pip (utiliza únicamente la librería estándar de Python: `tkinter` y `ctypes`):
```powershell
python main.py
```
*(Requiere Python 3.10+ en Windows 10/11)*

#### Opción 2: Ejecutable precompilado (`MonitorSwitch.exe`)
Descarga el binario portable desde la pestaña **Releases**.
> **Nota sobre el nombre**: El ejecutable se distribuye como `MonitorSwitch.exe` para no entrar en conflicto con la herramienta nativa de Windows `C:\Windows\System32\DisplaySwitch.exe` (el menú Win+P del sistema).

### Atajos por defecto
| Acción | Atajo |
| :--- | :--- |
| **Alternar TV** | `Ctrl + Alt + T` |
| **Solo Monitores** | `Ctrl + Alt + M` |
| **Solo TV** | `Ctrl + Alt + V` |
| **Extender Todo** | `Ctrl + Alt + E` |

---

## Third-Party Attributions
- **MultiMonitorTool**: This software incorporates `MultiMonitorTool` by Nir Sofer ([NirSoft](https://www.nirsoft.net/)), licensed as Freeware. MultiMonitorTool handles low-level CCD display state enabling and disabling.

## Credits / Créditos
- **UltraTiza**: Development & Architecture
- **FedeFadda**: Co-creator & Functional Design
- **FedeNahas**: Testing & Quality Assurance
- **Future-Plastic7826 From Reddit**: Testing, helping with suggestions and being very nice.

## License / Licencia
This project is Free Software released under the terms of the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for the full license text.
