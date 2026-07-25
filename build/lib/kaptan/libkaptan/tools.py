# Copyright 2016 Metehan Özbek <mthnzbk@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import re, os, struct, json, configparser
from PyQt6.QtCore import QSettings, QSize, Qt, QRectF
from PyQt6.QtGui import QImage, QPixmap, QIcon, QPainter, QColor, QPen
from PyQt6.QtWidgets import QStyleFactory
from PyQt6.QtSvg import QSvgRenderer


class Parser(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def read(self):
        with open(self.file_name) as config_file:
            return config_file.read()

    def sync(self, data):
        with open(self.file_name, "w") as self.config_file:
            self.config_file.write(data)
            self.config_file.flush()

    def getApplets(self):
        regex = r"(\n\[Containments\]\[([1-9]+)\]\[Applets\]\[([1-9]+)\]\nimmutability=1\nplugin=(.*)\n)"

        all_applets = re.findall(regex, self.read())

        if all_applets:
            return all_applets

        return []
    # Example [('[Containments][1][Applets][2]\nimmutability=1\nplugin=org.kde.plasma.kickoff\n', '1', '2', 'org.kde.plasma.kickoff')]

    def setMenuStyleOrCreate(self, menu_style):
        is_there = False
        menu_applet = None
        applets = self.getApplets()

        for applet in applets:
            if ("org.kde.plasma.kickoff" in applet) or ("org.kde.plasma.kicker" in applet) or ("org.kde.plasma.kickerdash" in applet):
                is_there = True
                menu_applet = applet
                break

        if is_there:
            regex = r"\n\[Containments\]\[%s\]\[Applets\]\[%s\]\nimmutability=.\nplugin=.*\n"%(menu_applet[1], menu_applet[2])

            com = re.compile(regex)

            new_data = com.sub(menu_applet[0].replace(menu_applet[3], menu_style), self.read())
            self.sync(new_data)

            # '[Containments][1][Applets][2]\nimmutability=1\nplugin=org.kde.plasma.kicker\n'
        else:
            last_nums = []

            if applets:
                first_applet = applets[0]
                for applet in applets:
                    last_nums.append(int(applet[2]))

                applet_index = str(max(last_nums)+1)
                applet = "\n[Containments][{}][Applets][{}]\nimmutability=1\nplugin={}\n".format(first_applet[1], applet_index, menu_style)

                com = re.compile(r"\n\[Containments\]\[%s\]\[Applets\]\[%s\]\nimmutability=.\nplugin=.*\n"%(first_applet[1], first_applet[2]))

                new_data = com.sub(first_applet[0] + applet, self.read())
                self.sync(new_data)
                self.setAppletOrder(0, applet_index)

    def addWallpaper(self, path):
        applets = self.getApplets()
        if applets:
            first_applet = applets[0][1]
            wp_applet_index = str(int(first_applet)-1)
            applet = "\n\n[Containments][{}][ConfigDialog]\nDialogHeight=480\nDialogWidth=640\n\n[Containments][{}][Wallpaper][org.kde.image][General]\nImage={}\nSlidePaths=/usr/share/wallpapers/\n".format(wp_applet_index, wp_applet_index, path)

            home_dir = os.environ['HOME']
            file_path = "{}/.config/plasma-org.kde.plasma.desktop-appletsrc".format(home_dir)
            # print("file_path :", file_path)
            with open(file_path, 'a') as f:
                f.write(applet)

    def getWallpaper(self):
        regex = r"(\[Containments\]\[[1-9]+\]\[Wallpaper\]\[org.kde.image\]\[General\]\n(.*)=(.*)\n)"
        read = re.search(regex, self.read())

        if read:
            if read.group(2) != "Image":
                regex = r"(\[Containments\]\[[1-9]+\]\[Wallpaper\]\[org.kde.image\]\[General\]\n)((.*)=.*\n.*\n)"
                read = re.search(regex, self.read())
                if read:
                    return read.group(1), read.group(2), read.group(3)
            return read.group(1), read.group(2), read.group(3)

        else:
            return False

    #('[Containments][27][Wallpaper][org.kde.image][General]\nImage=/usr/share/wallpapers/Sprout/contents/images/1920x1440.png\n', 'Image', '/usr/share/wallpapers/Sprout/contents/images/1920x1440.png')

    def setWallpaper(self, path):
        if self.getWallpaper()[1] != "Image":
            regex = r"\[Containments\]\[[1-9]+\]\[Wallpaper\]\[org.kde.image\]\[General\]\n.*\n.*\n"
            compiled = re.compile(regex)
            wp = compiled.sub((self.getWallpaper()[0]+"Image=%s\n"+self.getWallpaper()[1]) % path, self.read())
            self.sync(wp)
            
        elif self.getWallpaper()[1] == "Image":
            regex = r"\[Containments\]\[[1-9]+\]\[Wallpaper\]\[org.kde.image\]\[General\]\n%s=.*\n"%(self.getWallpaper()[1])
            compiled = re.compile(regex)
            wp = compiled.sub(self.getWallpaper()[0].replace(self.getWallpaper()[2], path), self.read())
            self.sync(wp)

    def getDesktopType(self):
        regex = r"(\[Containments\]\[[1-9]*\]\n.*\n.*\nactivityId=.+\n.*\n.*\nlastScreen=.*\n.*\nplugin=(.*)\n)"

        read = re.search(regex, self.read())

        if read:
            return read.group(1), read.group(2)

    def setDesktopType(self, view):
        regex = r"(\[Containments\]\[[1-9]*\]\n.*\n.*\nactivityId=.+\n.*\n.*\nlastScreen=.*\n.*\nplugin=(.*)\n)"

        com = re.compile(regex)

        if view != self.getDesktopType()[1]:
            new_data = com.sub(self.getDesktopType()[0].replace(self.getDesktopType()[1], view), self.read())
            self.sync(new_data)

    def getAppletOrder(self):
        regex = r"(\n\[Containments\]\[([1-9]+)\]\[General\]\nAppletOrder=(.*)\n)"

        applet_order = re.findall(regex, self.read())

        if applet_order:
            return applet_order[0]

    def setAppletOrder(self, index = int, value = str):
        applet_order = self.getAppletOrder()

        order = applet_order[-1].split(";")
        order.insert(index, value)

        values = ";".join(order)

        regex = r"\n\[Containments\]\[%s\]\[General\]\nAppletOrder=.+\n"%applet_order[1]

        com = re.compile(regex)

        new_data = com.sub(applet_order[0].replace(applet_order[2], values), self.read())
        self.sync(new_data)

    def setShowDesktopApplet(self):
        is_there = False
        applets = self.getApplets()

        for applet in applets:
            if "org.kde.plasma.showdesktop" in applet:
                is_there = True
                break

        if not is_there:
            last_nums = []
            first_applet = applets[0]
            for applet in applets:
                last_nums.append(int(applet[2]))

            applet_index = str(max(last_nums)+1)
            applet = "\n[Containments][{}][Applets][{}]\nimmutability=1\nplugin={}\n".format(first_applet[1],
                                                                                             applet_index, "org.kde.plasma.showdesktop")

            com = re.compile(r"\n\[Containments\]\[%s\]\[Applets\]\[%s\]\nimmutability=.\nplugin=.*\n"%(first_applet[1], first_applet[2]))

            new_data = com.sub(first_applet[0] + applet, self.read())
            self.sync(new_data)
            self.setAppletOrder(1, applet_index)


#parser = Parser("/home/metehan/.config/plasma-org.kde.plasma.desktop-appletsrc2")

#print(parser.getApplets())
#print(parser.getAppletOrder())
#parser.setMenuStyleOrCreate("org.kde.plasma.kickerdash")
#print(parser.setAppletOrder(0, "2"))
#parser.setShowDesktopApplet()
#print(parser.getWallpaper())
#parser.setWallpaper("/home/metehan/Dropbox/metehan.png")
#print(parser.getDesktopType())
#parser.setDesktopType("org.kde.plasma.folder")

def listToStr(list):
    str = ""
    for l in list:
        str += l + ","
    return str[:-1]

def iniToCss(file):
    """
    label text color
    button background-border-text
    groupbox background-bordor
    textbrowser background-text-linktext-alinktext
    """

    iniFile = QSettings(file, QSettings.Format.IniFormat)

    cssText = """QLabel#previewLabel {
    color : rgb(%s);
    }

    QPushButton#previewPushButton {
    color : rgb(%s);
    background-color : rgb(%s);
    }

    QGroupBox#previewGroupBox {
    background-color : rgb(%s);
    }

    QTextBrowser#previewTextBrowser {
    background-color : rgb(%s);
    color : rgb(%s);
    }"""%(listToStr(iniFile.value("Colors:Window/ForegroundNormal")),
          listToStr(iniFile.value("Colors:Button/ForegroundNormal")),
          listToStr(iniFile.value("Colors:Button/BackgroundNormal")),
          listToStr(iniFile.value("Colors:Window/BackgroundNormal")),
          listToStr(iniFile.value("Colors:View/BackgroundNormal")),
          listToStr(iniFile.value("Colors:View/ForegroundNormal")))

    textbrowser = listToStr(iniFile.value("Colors:View/ForegroundLink")), listToStr(iniFile.value("Colors:View/ForegroundVisited"))

    return cssText, textbrowser


#print(iniToCss("/usr/share/color-schemes/Breeze.colors"))


def read_xcursor_image(cursor_file, preferred_size=32):
    """Xcursor dosyasından belirli boyutta cursor görselini çıkarır."""
    try:
        with open(cursor_file, 'rb') as f:
            magic = f.read(4)
            if magic != b'Xcur':
                return None
            header_size = struct.unpack('<I', f.read(4))[0]
            version = struct.unpack('<I', f.read(4))[0]
            ntoc = struct.unpack('<I', f.read(4))[0]

            toc = []
            for i in range(ntoc):
                type_ = struct.unpack('<I', f.read(4))[0]
                subtype = struct.unpack('<I', f.read(4))[0]
                position = struct.unpack('<I', f.read(4))[0]
                toc.append((type_, subtype, position))

            # Image type: 0xFFFD0002
            image_entries = [(t, s, p) for t, s, p in toc if t == 0xFFFD0002]
            if not image_entries:
                return None

            # En yakın boyutu seç
            best = min(image_entries, key=lambda x: abs(x[1] - preferred_size))

            f.seek(best[2])
            chunk_header_size = struct.unpack('<I', f.read(4))[0]
            chunk_type = struct.unpack('<I', f.read(4))[0]
            chunk_subtype = struct.unpack('<I', f.read(4))[0]
            chunk_version = struct.unpack('<I', f.read(4))[0]
            width = struct.unpack('<I', f.read(4))[0]
            height = struct.unpack('<I', f.read(4))[0]
            xhot = struct.unpack('<I', f.read(4))[0]
            yhot = struct.unpack('<I', f.read(4))[0]
            delay = struct.unpack('<I', f.read(4))[0]

            pixels = f.read(width * height * 4)

            img = QImage(pixels, width, height, QImage.Format.Format_ARGB32)
            return img.copy()
    except Exception:
        return None


def generate_cursor_preview(theme_dir, size=128):
    """Bir cursor teması için birden fazla cursor görseli birleştirerek önizleme oluşturur."""
    cursor_names = ['default', 'pointer', 'wait', 'text', 'crosshair', 'help']
    cursors_dir = os.path.join(theme_dir, 'cursors')

    images = []
    for name in cursor_names:
        cursor_path = os.path.join(cursors_dir, name)
        # Symlink'leri takip et
        if os.path.exists(cursor_path):
            img = read_xcursor_image(cursor_path, 32)
            if img is not None:
                images.append(img)
        if len(images) >= 6:
            break

    if not images:
        return None

    # Tüm cursor görsellerini yan yana bir preview'da birleştir
    spacing = 4
    cursor_size = 32
    total_width = len(images) * cursor_size + (len(images) - 1) * spacing
    total_height = cursor_size

    preview = QImage(total_width, total_height, QImage.Format.Format_ARGB32)
    preview.fill(QColor(0, 0, 0, 0))

    painter = QPainter(preview)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    x = 0
    for img in images:
        scaled = img.scaled(cursor_size, cursor_size,
                           transformMode=Qt.TransformationMode.SmoothTransformation)
        painter.drawImage(x, 0, scaled)
        x += cursor_size + spacing
    painter.end()

    return QPixmap.fromImage(preview)


def generate_icon_theme_preview(theme_path_or_name, icon_size=32):
    """Bir ikon teması için temsili ikonları birleştirerek önizleme oluşturur."""
    if os.path.isdir(theme_path_or_name):
        theme_dir = theme_path_or_name
        theme_name = os.path.basename(theme_dir)
    else:
        theme_name = theme_path_or_name
        theme_dir = None
        for icons_dir in get_data_dirs('icons'):
            p = os.path.join(icons_dir, theme_name)
            if os.path.isdir(p):
                theme_dir = p
                break
        if not theme_dir:
            return None

    # Temsili ikon isimleri
    icon_names = [
        'system-file-manager', 'utilities-terminal', 'preferences-system',
        'applications-internet', 'accessories-text-editor', 'system-software-install',
        'applications-multimedia', 'user-home'
    ]

    # Ikon dosyalarını bul
    found_icons = []
    search_dirs = []
    for size_dir in ['48x48', '48', '32x32', '32', 'scalable']:
        for category in ['apps', 'places', 'categories']:
            p = os.path.join(theme_dir, size_dir, category)
            if os.path.isdir(p):
                search_dirs.append(p)

    for icon_name in icon_names:
        found = False
        for search_dir in search_dirs:
            for ext in ['.svg', '.svgz', '.png']:
                icon_path = os.path.join(search_dir, icon_name + ext)
                if os.path.exists(icon_path):
                    found_icons.append(icon_path)
                    found = True
                    break
            if found:
                break
        if len(found_icons) >= 6:
            break

    # Eğer ikon bulunamazsa, QIcon.fromTheme dene
    if len(found_icons) < 3:
        # QIcon.fromTheme ile fallback
        pixmaps = []
        for icon_name in icon_names[:6]:
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                pixmaps.append(icon.pixmap(icon_size, icon_size))
        if not pixmaps:
            return None

        spacing = 6
        total_width = len(pixmaps) * icon_size + (len(pixmaps) - 1) * spacing
        preview = QImage(total_width, icon_size, QImage.Format.Format_ARGB32)
        preview.fill(QColor(0, 0, 0, 0))
        painter = QPainter(preview)
        x = 0
        for pix in pixmaps:
            painter.drawPixmap(x, 0, pix)
            x += icon_size + spacing
        painter.end()
        return QPixmap.fromImage(preview)

    # Dosyalardan önizleme oluştur
    spacing = 6
    total_width = len(found_icons) * icon_size + (len(found_icons) - 1) * spacing
    preview = QImage(total_width, icon_size, QImage.Format.Format_ARGB32)
    preview.fill(QColor(0, 0, 0, 0))
    painter = QPainter(preview)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    x = 0
    for icon_path in found_icons:
        if icon_path.endswith('.svg') or icon_path.endswith('.svgz'):
            renderer = QSvgRenderer(icon_path)
            if renderer.isValid():
                renderer.render(painter, QRectF(x, 0, icon_size, icon_size))
        else:
            pix = QPixmap(icon_path)
            if not pix.isNull():
                scaled = pix.scaled(icon_size, icon_size,
                                   transformMode=Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(x, 0, scaled)
        x += icon_size + spacing
    painter.end()
    return QPixmap.fromImage(preview)


def generate_plasma_theme_preview(theme_dir, width=212, height=60):
    """Plasma masaüstü teması için panel-background'dan önizleme oluşturur."""
    widgets_dir = os.path.join(theme_dir, 'widgets')

    # Panel background dosyasını bul
    for fname in ['panel-background.svgz', 'panel-background.svg']:
        panel_path = os.path.join(widgets_dir, fname)
        if os.path.exists(panel_path):
            renderer = QSvgRenderer(panel_path)
            if renderer.isValid():
                img = QImage(width, height, QImage.Format.Format_ARGB32)
                img.fill(QColor(0, 0, 0, 0))
                painter = QPainter(img)
                renderer.render(painter)
                painter.end()
                return QPixmap.fromImage(img)

    # Background dosyasını dene
    for fname in ['background.svgz', 'background.svg']:
        bg_path = os.path.join(widgets_dir, fname) if os.path.isdir(widgets_dir) else os.path.join(theme_dir, fname)
        if os.path.exists(bg_path):
            renderer = QSvgRenderer(bg_path)
            if renderer.isValid():
                img = QImage(width, height, QImage.Format.Format_ARGB32)
                img.fill(QColor(0, 0, 0, 0))
                painter = QPainter(img)
                renderer.render(painter)
                painter.end()
                return QPixmap.fromImage(img)

    return None


def get_data_dirs(subpath):
    """Returns all existing directories for a given subpath under standard XDG paths and home."""
    dirs = []
    home = os.path.expanduser('~')
    
    # User dirs
    p1 = os.path.join(home, '.local', 'share', subpath)
    if os.path.isdir(p1):
        dirs.append(p1)
        
    if subpath == 'icons':
        p2 = os.path.join(home, '.icons')
        if os.path.isdir(p2):
            dirs.append(p2)
    elif subpath == 'themes':
        p2 = os.path.join(home, '.themes')
        if os.path.isdir(p2):
            dirs.append(p2)
    elif subpath == 'color-schemes':
        p2 = os.path.join(home, '.kde', 'share', 'apps', 'color-schemes')
        if os.path.isdir(p2):
            dirs.append(p2)
        p3 = os.path.join(home, '.kde4', 'share', 'apps', 'color-schemes')
        if os.path.isdir(p3):
            dirs.append(p3)

    # System dirs
    xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/share:/usr/local/share').split(':')
    for d in xdg_data_dirs:
        if d:
            p = os.path.join(d, subpath)
            if os.path.isdir(p) and p not in dirs:
                dirs.append(p)
                
    for default in ['/usr/share', '/usr/local/share']:
        p = os.path.join(default, subpath)
        if os.path.isdir(p) and p not in dirs:
            dirs.append(p)
            
    return dirs


def get_cursor_themes():
    """Sistemdeki ve kullanıcının yerelindeki cursor temalarını tespit eder.
    Returns: [(tema_adı, tema_dizini, görüntü_adı), ...]
    """
    themes = []
    seen = set()
    for icons_dir in get_data_dirs('icons'):
        if not os.path.isdir(icons_dir):
            continue
        try:
            entries = os.listdir(icons_dir)
        except Exception:
            continue
        for entry in entries:
            if entry in seen:
                continue
            theme_dir = os.path.join(icons_dir, entry)
            cursors_dir = os.path.join(theme_dir, 'cursors')
            if os.path.isdir(cursors_dir):
                seen.add(entry)
                display_name = entry
                index_path = os.path.join(theme_dir, 'index.theme')
                if os.path.exists(index_path):
                    try:
                         cp = configparser.ConfigParser()
                         cp.read(index_path)
                         if cp.has_option('Icon Theme', 'Name'):
                             display_name = cp.get('Icon Theme', 'Name')
                    except Exception:
                         pass
                themes.append((entry, theme_dir, display_name))
    return sorted(themes, key=lambda x: x[2].lower())


def get_icon_themes():
    """Sistemdeki ve kullanıcının yerelindeki ikon temalarını (cursor teması olmayanlar) tespit eder.
    Returns: [(tema_adı, tema_dizini, görüntü_adı), ...]
    """
    themes = []
    seen = set()
    hidden_themes = {'default', 'hicolor', 'locolor', 'AdwaitaLegacy'}
    for icons_dir in get_data_dirs('icons'):
        if not os.path.isdir(icons_dir):
            continue
        try:
            entries = os.listdir(icons_dir)
        except Exception:
            continue
        for entry in entries:
            if entry in hidden_themes or entry in seen:
                continue
            theme_dir = os.path.join(icons_dir, entry)
            if not os.path.isdir(theme_dir):
                continue
            index_path = os.path.join(theme_dir, 'index.theme')
            if not os.path.exists(index_path):
                continue

            has_icons = False
            try:
                subdirs = os.listdir(theme_dir)
            except Exception:
                continue
            for category in ['apps', 'places', 'devices', 'actions', 'categories', 'mimetypes']:
                for size_dir in subdirs:
                    if os.path.isdir(os.path.join(theme_dir, size_dir, category)):
                        has_icons = True
                        break
                if has_icons:
                    break
            if not has_icons:
                continue

            seen.add(entry)
            try:
                cp = configparser.ConfigParser()
                cp.read(index_path)
                if cp.has_option('Icon Theme', 'Hidden') and cp.get('Icon Theme', 'Hidden').lower() == 'true':
                    continue
                display_name = entry
                if cp.has_option('Icon Theme', 'Name'):
                    display_name = cp.get('Icon Theme', 'Name')
            except Exception:
                display_name = entry

            themes.append((entry, theme_dir, display_name))
    return sorted(themes, key=lambda x: x[2].lower())


def get_plasma_themes():
    """Sistemdeki ve kullanıcının yerelindeki Plasma masaüstü temalarını tespit eder.
    Returns: [(tema_id, tema_dizini, görüntü_adı), ...]
    """
    themes = []
    seen = set()
    for themes_dir in get_data_dirs('plasma/desktoptheme'):
        if not os.path.isdir(themes_dir):
            continue
        try:
            entries = os.listdir(themes_dir)
        except Exception:
            continue
        for entry in entries:
            if entry in seen:
                continue
            theme_dir = os.path.join(themes_dir, entry)
            if not os.path.isdir(theme_dir):
                continue

            seen.add(entry)
            display_name = entry
            meta_json = os.path.join(theme_dir, 'metadata.json')
            meta_desktop = os.path.join(theme_dir, 'metadata.desktop')
            if os.path.exists(meta_json):
                try:
                    with open(meta_json) as f:
                        data = json.load(f)
                        name = data.get('KPlugin', {}).get('Name', '')
                        if name:
                            display_name = name
                except Exception:
                    pass
            elif os.path.exists(meta_desktop):
                try:
                    cp = configparser.ConfigParser()
                    cp.read(meta_desktop)
                    if cp.has_option('Desktop Entry', 'Name'):
                        display_name = cp.get('Desktop Entry', 'Name')
                except Exception:
                    pass
            themes.append((entry, theme_dir, display_name))
    return sorted(themes, key=lambda x: x[2].lower())


def get_window_decorations():
    """Sistemdeki ve kullanıcının yerelindeki KWin pencere dekorasyonlarını tespit eder.
    Returns: [(dekorasyon_id, görüntü_adı, tema_dizini), ...]
    """
    decorations = []
    seen_ids = set()

    for dec_version in ['org.kde.kdecoration3', 'org.kde.kdecoration2']:
        for lib_dir in ['/usr/lib/qt6/plugins', '/usr/lib64/qt6/plugins', '/usr/lib/plugins', '/usr/lib/x86_64-linux-gnu/qt6/plugins']:
            dec_dir = os.path.join(lib_dir, dec_version)
            if os.path.isdir(dec_dir):
                try:
                    files = os.listdir(dec_dir)
                except Exception:
                    continue
                for f in sorted(files):
                    if f.endswith('.so') and not f.endswith('kcm.so'):
                        dec_id = f.rsplit('.so', 1)[0]
                        if 'aurorae' in dec_id:
                            continue
                        if dec_id in seen_ids:
                            continue
                        seen_ids.add(dec_id)
                        display_name = dec_id.split('.')[-1].capitalize()
                        decorations.append((dec_id, display_name, None))

    for aurorae_dir in get_data_dirs('aurorae/themes'):
        if os.path.isdir(aurorae_dir):
            try:
                entries = os.listdir(aurorae_dir)
            except Exception:
                continue
            for entry in sorted(entries):
                theme_dir = os.path.join(aurorae_dir, entry)
                if os.path.isdir(theme_dir):
                    dec_id = 'kwin4_decoration_qml_' + entry
                    if dec_id in seen_ids:
                        continue
                    seen_ids.add(dec_id)
                    decorations.append((dec_id, entry, theme_dir))

    for kwin_dec_dir in get_data_dirs('kwin/decorations'):
        if os.path.isdir(kwin_dec_dir):
            try:
                entries = os.listdir(kwin_dec_dir)
            except Exception:
                continue
            for entry in sorted(entries):
                dec_dir = os.path.join(kwin_dec_dir, entry)
                if not os.path.isdir(dec_dir):
                    continue
                dec_id = entry
                if dec_id in seen_ids:
                    continue
                seen_ids.add(dec_id)
                display_name = entry
                meta_json = os.path.join(dec_dir, 'metadata.json')
                if os.path.exists(meta_json):
                    try:
                        with open(meta_json) as f:
                            data = json.load(f)
                            kplugin = data.get('KPlugin', {})
                            name = kplugin.get('Name', '')
                            if name:
                                display_name = name
                    except Exception:
                        pass
                decorations.append((dec_id, display_name, dec_dir))

    return decorations


def get_widget_styles():
    """Sistemdeki QStyle widget stillerini tespit eder.
    Returns: [stil_adı, ...]
    """
    return QStyleFactory.keys()


def get_color_schemes():
    """Sistemdeki ve kullanıcının yerelindeki renk şemalarını tespit eder.
    Returns: [(şema_adı, dosya_yolu), ...]
    """
    schemes = []
    seen = set()
    for schemes_dir in get_data_dirs('color-schemes'):
        if not os.path.isdir(schemes_dir):
            continue
        try:
            files = os.listdir(schemes_dir)
        except Exception:
            continue
        for entry in files:
            if entry.endswith('.colors'):
                name = entry.split('.colors')[0]
                if name in seen:
                    continue
                seen.add(name)
                schemes.append((name, os.path.join(schemes_dir, entry)))
    return sorted(schemes, key=lambda x: x[0].lower())


def generate_window_decoration_preview(dec_id, theme_dir=None):
    """KWin pencere dekorasyonu için temsili bir pencere önizleme görseli oluşturur."""
    pixmap = QPixmap(340, 105)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    title_bg = QColor(230, 232, 235)
    text_color = QColor(40, 40, 45)
    window_bg = QColor(255, 255, 255)
    border_color = QColor(190, 195, 200)

    is_dark = False
    lower_id = dec_id.lower()
    lower_dir = theme_dir.lower() if theme_dir else ""
    if "dark" in lower_id or "dark" in lower_dir or "black" in lower_id or "black" in lower_dir or "night" in lower_id:
        is_dark = True
        title_bg = QColor(45, 48, 54)
        text_color = QColor(220, 225, 230)
        window_bg = QColor(30, 30, 35)
        border_color = QColor(60, 64, 72)

    is_aurorae = theme_dir and (os.path.exists(os.path.join(theme_dir, 'decoration.svg')) or os.path.exists(os.path.join(theme_dir, 'close.svg')))

    # Pencere gövdesi
    painter.setBrush(window_bg)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(10, 10, 320, 85, 8, 8)

    # Başlık çubuğu arka planı
    if is_aurorae:
        rendered_titlebar = False
        try:
            dec_svg = os.path.join(theme_dir, 'decoration.svg')
            if not os.path.exists(dec_svg):
                dec_svg = os.path.join(theme_dir, 'titlebar-active.svg')
            if os.path.exists(dec_svg):
                renderer = QSvgRenderer(dec_svg)
                if renderer.isValid():
                    renderer.render(painter, Qt.RectF(10, 10, 320, 35))
                    rendered_titlebar = True
        except Exception:
            pass
        if not rendered_titlebar:
            painter.setBrush(title_bg)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(10, 10, 320, 35, 8, 8)
            painter.drawRect(10, 25, 320, 20)
    else:
        painter.setBrush(title_bg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, 320, 35, 8, 8)
        painter.drawRect(10, 25, 320, 20)

    # Separator çizgisi
    painter.setPen(QColor(220, 220, 220) if not is_dark else QColor(55, 55, 60))
    painter.drawLine(10, 45, 330, 45)

    # Pencere kenarlığı
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.setPen(border_color)
    painter.drawRoundedRect(10, 10, 320, 85, 8, 8)

    rendered_buttons = False
    if is_aurorae:
        try:
            btn_y = 18
            btn_size = 18

            close_svg = os.path.join(theme_dir, 'close.svg')
            max_svg = os.path.join(theme_dir, 'maximize.svg')
            min_svg = os.path.join(theme_dir, 'minimize.svg')

            def render_btn(renderer, painter, rect):
                for element_id in ["active-center", "active", "normal"]:
                    if renderer.elementExists(element_id):
                        renderer.render(painter, element_id, rect)
                        return
                renderer.render(painter, rect)

            if os.path.exists(close_svg):
                r_close = QSvgRenderer(close_svg)
                if r_close.isValid():
                    render_btn(r_close, painter, QRectF(300, btn_y, btn_size, btn_size))
            if os.path.exists(max_svg):
                r_max = QSvgRenderer(max_svg)
                if r_max.isValid():
                    render_btn(r_max, painter, QRectF(280, btn_y, btn_size, btn_size))
            if os.path.exists(min_svg):
                r_min = QSvgRenderer(min_svg)
                if r_min.isValid():
                    render_btn(r_min, painter, QRectF(260, btn_y, btn_size, btn_size))
            rendered_buttons = True
        except Exception:
            pass

    if not rendered_buttons:
        btn_color = QColor(100, 105, 115) if not is_dark else QColor(180, 185, 195)
        painter.setPen(QPen(btn_color, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Close button X
        painter.drawLine(304, 21, 316, 33)
        painter.drawLine(316, 21, 304, 33)

        # Maximize button square
        painter.drawRect(284, 21, 12, 12)

        # Minimize button line
        painter.drawLine(264, 27, 276, 27)

    # Başlık Metni
    painter.setPen(text_color)
    font = painter.font()
    font.setBold(True)
    font.setPointSize(10)
    painter.setFont(font)
    title_text = dec_id.split('.')[-1].replace('kwin4_decoration_qml_', '').replace('_', ' ').capitalize()
    painter.drawText(QRectF(20, 10, 200, 35), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, title_text)

    # Temsili pencere içeriği
    painter.setPen(QColor(160, 165, 175) if not is_dark else QColor(90, 95, 105))
    painter.drawRect(25, 55, 290, 30)
    painter.drawText(QRectF(25, 55, 290, 30), Qt.AlignmentFlag.AlignCenter, "Window Content")

    painter.end()
    return pixmap


def generate_color_scheme_preview(file_path):
    """Renk şeması için temsili renk paleti önizleme görseli oluşturur."""
    try:
        iniFile = QSettings(file_path, QSettings.Format.IniFormat)

        def get_color(key, default):
            val = iniFile.value(key)
            if not val:
                return default
            if isinstance(val, list):
                val = ",".join(val)
            parts = [int(x) for x in re.findall(r'\d+', val)]
            if len(parts) >= 3:
                return QColor(parts[0], parts[1], parts[2])
            return default

        win_bg = get_color("Colors:Window/BackgroundNormal", QColor(240, 240, 240))
        win_fg = get_color("Colors:Window/ForegroundNormal", QColor(0, 0, 0))
        btn_bg = get_color("Colors:Button/BackgroundNormal", QColor(220, 220, 220))
        sel_bg = get_color("Colors:Selection/BackgroundNormal", QColor(30, 144, 255))
        view_bg = get_color("Colors:View/BackgroundNormal", QColor(255, 255, 255))
    except Exception:
        win_bg = QColor(240, 240, 240)
        win_fg = QColor(0, 0, 0)
        btn_bg = QColor(220, 220, 220)
        sel_bg = QColor(30, 144, 255)
        view_bg = QColor(255, 255, 255)

    width, height = 64, 40
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(win_bg)
    painter.setPen(QColor(180, 180, 180))
    painter.drawRoundedRect(2, 2, width-4, height-4, 4, 4)

    painter.setBrush(view_bg)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRect(8, 8, 20, 24)

    painter.setBrush(btn_bg)
    painter.drawRect(36, 8, 20, 10)

    painter.setBrush(sel_bg)
    painter.drawRect(36, 22, 20, 10)

    painter.setPen(win_fg)
    painter.drawLine(12, 14, 24, 14)
    painter.drawLine(12, 20, 24, 20)
    painter.drawLine(12, 26, 20, 26)

    painter.end()
    return pixmap
