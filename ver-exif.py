#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nautilus Script: Visualizador EXIF com GUI Nativa (GTK3)
Compatível: Debian 13 + GNOME
Herda automaticamente: GTK_THEME, GSETTINGS_BACKEND, DBUS_SESSION_BUS_ADDRESS, etc.
"""
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from PIL import Image, ExifTags

# ============================================================
# 📡 Captura arquivo do Nautilus ou argumentos
# ============================================================
def obter_arquivo():
    paths = os.environ.get("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", "").strip()
    if not paths and len(sys.argv) > 1:
        paths = "\n".join(sys.argv[1:])
    if not paths:
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Nenhum arquivo selecionado.")
        dialog.run()
        dialog.destroy()
        sys.exit(1)
    return paths.split("\n")[0]

# ============================================================
# 📊 Leitura e Formatação EXIF
# ============================================================
def formatar_valor(tag, valor):
    if valor is None: return "N/A"
    if isinstance(valor, bytes):
        return valor.decode('utf-8', errors='ignore').strip('\x00')
    
    v = float(valor) if isinstance(valor, (int, float)) else None
    if tag == "ExposureTime" and v is not None:
        return f"{v:.3f} s" if v >= 1 else f"1/{int(1/v)} s"
    if tag == "FNumber" and v is not None:
        return f"f/{v:.1f}"
    if tag == "FocalLength" and v is not None:
        return f"{v:.1f} mm"
    if tag in ("ExposureProgram", "MeteringMode", "WhiteBalance", "Flash"):
        mapas = {
            "ExposureProgram": {0:"Desconhecido", 1:"Manual", 2:"Normal", 3:"Prioridade Abertura", 4:"Prioridade Velocidade", 5:"Criativo", 6:"Ação", 7:"Retrato", 8:"Paisagem"},
            "MeteringMode": {0:"Desconhecido", 1:"Média", 2:"Ponderada ao Centro", 3:"Spot", 5:"Multizona", 6:"Parcial"},
            "WhiteBalance": {0:"Automático", 1:"Manual"},
            "Flash": {0:"Não disparou", 1:"Disparou", 5:"Disparou, s/ retorno", 7:"Disparou, c/ retorno", 9:"Auto, s/ retorno", 13:"Auto, c/ retorno", 16:"Sem função", 24:"Auto, não disparou", 25:"Auto, s/ retorno", 29:"Auto, c/ retorno", 31:"Auto, sem função"},
        }
        return mapas.get(tag, {}).get(valor, str(valor))
    if isinstance(valor, tuple) and len(valor) == 3:
        try:
            dec = lambda t: float(t[0])/float(t[1]) if t[1] != 0 else 0
            return f"{dec(valor[0])}° {dec(valor[1])}' {dec(valor[2])}\""
        except Exception: pass
    return str(valor)

def extrair_exif(caminho):
    try:
        img = Image.open(caminho)
        exif = img.getexif()
    except Exception as e:
        raise RuntimeError(f"❌ Não foi possível ler a imagem:\n{e}")

    categorias = {
        "📷 Câmera / Equipamento": {},
        "⚙️ Configurações de Imagem": {},
        "📅 Data e Hora": {},
        "📍 GPS / Localização": {},
        "🔍 Exposição / Disparo": {},
        "📝 Outros / Metadados": {}
    }
    mapa = {
        "Make":0, "Model":0, "LensModel":0, "LensMake":0, "Software":0, "BodySerialNumber":0,
        "ImageWidth":1, "ImageLength":1, "Orientation":1, "XResolution":1, "YResolution":1, "ResolutionUnit":1, "ColorSpace":1, "BitsPerSample":1,
        "DateTime":2, "DateTimeOriginal":2, "DateTimeDigitized":2,
        "GPSLatitude":3, "GPSLongitude":3, "GPSLatitudeRef":3, "GPSLongitudeRef":3, "GPSAltitude":3, "GPSAltitudeRef":3, "GPSDateStamp":3, "GPSTimeStamp":3, "GPSImgDirection":3, "GPSMapDatum":3,
        "ExposureTime":4, "FNumber":4, "ISOSpeedRatings":4, "FocalLength":4, "Flash":4, "WhiteBalance":4, "MeteringMode":4, "ExposureProgram":4, "ExposureMode":4, "BrightnessValue":4, "ExposureBiasValue":4, "MaxApertureValue":4, "FocalLengthIn35mmFilm":4,
        "Artist":5, "Copyright":5, "UserComment":5
    }
    idx_to_cat = list(categorias.keys())

    for tag_id, valor in exif.items():
        nome = ExifTags.TAGS.get(tag_id, f"Tag_{tag_id}")
        idx = mapa.get(nome, 5)
        categorias[idx_to_cat[idx]][nome] = formatar_valor(nome, valor)

    # GPS em IFD separado
    try:
        gps_ifd = exif.get_ifd(getattr(ExifTags.IFD, 'GPSInfo', 34853))
        for tid, val in gps_ifd.items():
            nome = ExifTags.GPSINFO.get(tid, f"GPS_{tid}")
            if nome not in categorias["📍 GPS / Localização"]:
                categorias["📍 GPS / Localização"][nome] = formatar_valor(nome, val)
    except Exception:
        pass
    return categorias

# ============================================================
# 🖥️ Interface Gráfica GTK3
# ============================================================
class ExifViewerWindow(Gtk.Window):
    def __init__(self, image_path):
        super().__init__(title="Visualizador EXIF")
        self.set_default_size(650, 480)
        self.set_border_width(10)
        self.image_path = image_path

        try:
            self.dados = extrair_exif(image_path)
        except Exception as e:
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, str(e))
            dialog.run()
            dialog.destroy()
            sys.exit(1)

        # Layout principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(vbox)

        # Cabeçalho
        header = Gtk.Label(label=f"📄 {os.path.basename(image_path)}")
        header.set_halign(Gtk.Align.START)
        header.get_style_context().add_class("heading")
        vbox.pack_start(header, False, False, 0)

        # Painel dividido
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(paned, True, True, 0)

        # Lista de Categorias
        self.store_cat = Gtk.ListStore(str)
        self.view_cat = Gtk.TreeView(model=self.store_cat)
        col = Gtk.TreeViewColumn("Categoria", Gtk.CellRendererText(), text=0)
        self.view_cat.append_column(col)
        self.view_cat.set_headers_visible(False)
        self.view_cat.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

        # Lista de Detalhes
        self.store_det = Gtk.ListStore(str, str)
        self.view_det = Gtk.TreeView(model=self.store_det)
        self.view_det.append_column(Gtk.TreeViewColumn("Tag", Gtk.CellRendererText(), text=0))
        self.view_det.append_column(Gtk.TreeViewColumn("Valor", Gtk.CellRendererText(), text=1))
        self.view_det.set_headers_visible(True)

        # Scroll
        sw1 = Gtk.ScrolledWindow()
        sw1.add(self.view_cat)
        paned.pack1(sw1, resize=True, shrink=False)

        sw2 = Gtk.ScrolledWindow()
        sw2.add(self.view_det)
        paned.pack2(sw2, resize=True, shrink=False)

        # Popula categorias
        self.categorias = list(self.dados.keys())
        for cat in self.categorias:
            self.store_cat.append([cat])

        # Eventos
        self.view_cat.get_selection().connect("changed", self.on_cat_selected)
        self.view_cat.get_selection().select_path((0,))

        # Botão Encerrar
        btn_close = Gtk.Button.new_with_label("Encerrar")
        btn_close.set_halign(Gtk.Align.END)
        btn_close.connect("clicked", lambda w: self.destroy())
        vbox.pack_start(btn_close, False, False, 0)

        self.connect("destroy", Gtk.main_quit)

    def on_cat_selected(self, selection):
        model, it = selection.get_selected()
        if it:
            cat = model[it][0]
            self.store_det.clear()
            for tag, val in self.dados[cat].items():
                self.store_det.append([tag, str(val)])

def main():
    # Garante que o GTK leia o ambiente GNOME (tema, fontes, dbus)
    Gtk.init([])
    caminho = obter_arquivo()
    win = ExifViewerWindow(caminho)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
