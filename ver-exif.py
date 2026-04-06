#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nautilus Script: Visualizador EXIF Completo + Sub-categorias + Exportação
Compatível: Debian 13 + GNOME | GTK3 | exiftool
"""
import os
import sys
import json
import csv
import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# ============================================================
# 🔍 Captura do ficheiro
# ============================================================
def obter_ficheiro():
    paths = os.environ.get("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", "").strip()
    if not paths and len(sys.argv) > 1:
        paths = "\n".join(sys.argv[1:])
    if not paths:
        dlg = Gtk.MessageDialog(None, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "Nenhum ficheiro selecionado.")
        dlg.run(); dlg.destroy()
        sys.exit(0)
    return paths.split("\n")[0]

def mostrar_erro(msg):
    dlg = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, msg)
    dlg.run(); dlg.destroy()

# ============================================================
# 🏷️ Mapeamento de Sub-categorias
# ============================================================
def determinar_subcategoria(grupo, tag):
    t = tag.upper()
    if grupo == "EXIF":
        if any(k in t for k in ["MAKE","MODEL","SERIAL","OWNER","FIRMWARE","HOST","CAMERAS"]): return "📷 Corpo & Fabricante"
        if any(k in t for k in ["LENS","FOCALLENGTHIN35","LENSID"]): return "🔭 Objetiva"
        if any(k in t for k in ["EXPOSURE","FNUMBER","APERTURE","ISO","SHUTTER","METERING","FLASH","LIGHTSOURCE","BRIGHTNESS","CONTRAST","SATURATION","SHARPNESS","WHITEBALANCE","SCENECAPTURE","GAIN","SENSING","DIGITALZOOM"]): return "⚡ Exposição & Disparo"
        if any(k in t for k in ["DATE","TIME","OFFSET","SUBSEC"]): return "🕒 Data & Hora"
        if any(k in t for k in ["WIDTH","HEIGHT","RESOLUTION","COLORSPACE","ORIENTATION","BITS","COMPRESS","PLANAR","YCBCR","CFAPATTERN","SCENETYPE","COMPONENT"]): return "🖼️ Imagem & Formato"
        return "🔧 Outros EXIF"
    elif grupo == "MakerNotes":
        if any(k in t for k in ["FOCUS","AF","LENSDATA","DRIVEMODE","PICTURESTYLE","COLORTONE","FLASH","FACE","TRACKING","STABILIZ","VR","D-LIGHTING","CREATIVE"]): return "🎯 Foco & Config. Avançadas"
        return "🏭 Notas do Fabricante (Decodificadas)"
    elif "XMP" in grupo:
        if "dc" in grupo.lower() or any(k in t for k in ["CREATOR","TITLE","SUBJECT","DESCRIPTION","RIGHTS","SOURCE","PUBLISHER","CONTRIBUTOR"]): return "📖 XMP: Dublin Core & Direitos"
        if "lr" in grupo.lower() or any(k in t for k in ["RATING","LABEL","CREATORTOOL","PROCESSED","RAWFILE","CROP","HIERARCHICAL","DEVELOP","CAMERAPROFILE"]): return "💡 XMP: Lightroom & Edição"
        return "🌐 XMP: Metadados Gerais"
    elif grupo == "IPTC":
        if any(k in t for k in ["KEYWORD","CAPTION","CREDIT","SOURCE","LOCATION","CITY","STATE","COUNTRY","HEADLINE","INSTRUCTIONS","ARTIST"]): return "📰 IPTC: Profissional & Notícias"
        return "🏷️ IPTC: Geral"
    elif grupo == "Composite":
        if any(k in t for k in ["LENS","FOCUS","DOF","HYPERFOCAL","CIRCLE","DISTANCE","SCALE","BLUR"]): return "🔍 Cálculos Ópticos"
        return "📐 Valores Compostos & Derivados"
    elif grupo == "File":
        return "💾 Sistema & Ficheiro"
    elif grupo == "GPS":
        return "📍 Geolocalização GPS"
    elif grupo == "ICC_Profile":
        return "🎨 Perfil de Cor (ICC)"
    return "📂 Geral"

# ============================================================
# 🛠️ Execução & Parsing do exiftool
# ============================================================
def executar_exiftool(caminho):
    try:
        cmd = ["exiftool", "-json", "-g", "-struct", "-c", "%.6f", "-charset", "UTF8", "-api", "largefilesupport=1", caminho]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=8)
        data = json.loads(proc.stdout)
        return data[0] if isinstance(data, list) else data
    except FileNotFoundError:
        mostrar_erro("❌ 'exiftool' não encontrado.\nInstale: sudo apt install libimage-exiftool-perl")
        sys.exit(1)
    except Exception as e:
        mostrar_erro(f"❌ Falha ao processar metadados:\n{str(e)}")
        sys.exit(1)

def formatar_valor(val):
    if isinstance(val, (list, dict)):
        txt = json.dumps(val, ensure_ascii=False, indent=2)
        return txt if len(txt) <= 1200 else txt[:1200] + "\n... [truncado]"
    if isinstance(val, str) and len(val) > 1200:
        return val[:1200] + "\n... [truncado]"
    return str(val)

# ============================================================
# 🖥️ Interface GTK3
# ============================================================
class ExifViewer(Gtk.Window):
    def __init__(self, caminho):
        super().__init__(title="📊 Visualizador EXIF Completo")
        self.set_default_size(850, 600)
        self.set_border_width(8)
        self.caminho = caminho
        self.termo_busca = ""
        self.dados_brutos = [] # Lista de (main_cat, sub_cat, tag, value)

        # 1. Processar dados
        bruto = executar_exiftool(caminho)
        for grupo, tags in bruto.items():
            if grupo == "SourceFile" or not isinstance(tags, dict): continue
            main = {"EXIF":"📷 EXIF Padrão", "MakerNotes":"🏭 MakerNotes", "XMP":"🌐 XMP", "IPTC":"📰 IPTC", 
                    "Composite":"🔢 Composite", "File":"📁 Ficheiro", "GPS":"📍 GPS", "ICC_Profile":"🎨 ICC"}.get(grupo, f"📂 {grupo}")
            for tag, val in tags.items():
                self.dados_brutos.append((main, determinar_subcategoria(grupo, tag), tag, formatar_valor(val)))
        
        # Ordenar
        self.dados_brutos.sort(key=lambda x: (x[0], x[1], x[2]))
        self.total = len(self.dados_brutos)

        # 2. Layout Principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Cabeçalho
        lbl = Gtk.Label(label=f"📄 {os.path.basename(caminho)}")
        lbl.set_halign(Gtk.Align.START)
        lbl.get_style_context().add_class("heading")
        vbox.pack_start(lbl, False, False, 0)

        # Barra de ferramentas
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.busca = Gtk.SearchEntry()
        self.busca.set_placeholder_text("🔍 Filtrar tags, valores ou sub-categorias...")
        self.busca.connect("changed", self.on_busca)
        toolbar.pack_start(self.busca, True, True, 0)
        
        btn_expand = Gtk.Button.new_with_label("🔽 Expandir Tudo")
        btn_expand.connect("clicked", lambda w: self.view.expand_all())
        toolbar.pack_start(btn_expand, False, False, 0)
        
        btn_collapse = Gtk.Button.new_with_label("🔼 Recolher")
        btn_collapse.connect("clicked", lambda w: self.view.collapse_all())
        toolbar.pack_start(btn_collapse, False, False, 0)
        vbox.pack_start(toolbar, False, False, 0)

        # Árvore
        self.store = Gtk.TreeStore(str, str, str) # [DISPLAY, FULL_PATH, VALUE]
        self.preencher_arvore()

        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filtro_visivel)
        self.view = Gtk.TreeView(model=self.filter)
        self.view.set_headers_visible(True)
        col = Gtk.TreeViewColumn("Estrutura", Gtk.CellRendererText(), text=0)
        col.set_expand(True)
        self.view.append_column(col)
        col2 = Gtk.TreeViewColumn("Valor", Gtk.CellRendererText(), text=2)
        col2.set_fixed_width(280)
        col2.set_resizable(True)
        self.view.append_column(col2)
        
        sw = Gtk.ScrolledWindow()
        sw.add(self.view)
        vbox.pack_start(sw, True, True, 0)

        # Menu de contexto
        menu = Gtk.Menu()
        item_copy = Gtk.MenuItem(label="📋 Copiar Valor")
        item_copy.connect("activate", self.copiar_valor)
        menu.append(item_copy)
        menu.show_all()
        self.view.connect("button-press-event", lambda w, e: menu.popup_at_pointer(e) if e.button == 3 else None)

        # Rodapé
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.info_lbl = Gtk.Label(label=f"✅ {self.total} metadados extraídos")
        self.info_lbl.set_halign(Gtk.Align.START)
        footer.pack_start(self.info_lbl, True, True, 0)
        
        btn_export = Gtk.Button.new_with_label("💾 Exportar")
        btn_export.connect("clicked", self.exportar)
        footer.pack_start(btn_export, False, False, 0)
        
        btn_close = Gtk.Button.new_with_label("Encerrar")
        btn_close.connect("clicked", lambda w: self.destroy())
        footer.pack_start(btn_close, False, False, 0)
        vbox.pack_start(footer, False, False, 0)

        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.view.expand_all()

    def preencher_arvore(self):
        parents = {}
        for main, sub, tag, val in self.dados_brutos:
            # Main Category
            if main not in parents:
                parents[main] = (self.store.append(None, [f"📁 {main}", main, ""]), {})
            # Sub Category
            sub_dict = parents[main][1]
            if sub not in sub_dict:
                sub_dict[sub] = self.store.append(parents[main][0], [f"📂 {sub}", f"{main} > {sub}", ""])
            # Tag Leaf
            self.store.append(sub_dict[sub], [f"🏷️ {tag}", f"{main} > {sub} > {tag}", val])

    def filtro_visivel(self, model, it, data):
        if not self.termo_busca:
            return True
        txt = self.termo_busca.lower()
        # Verifica Display e Value
        return any(txt in str(model[it][col]).lower() for col in (0, 2))

    def on_busca(self, entry):
        self.termo_busca = entry.get_text()
        self.filter.refilter()
        # Se há filtro, expande para mostrar resultados
        if self.termo_busca:
            self.view.expand_all()

    def copiar_valor(self, widget):
        sel = self.view.get_selection()
        model, it = sel.get_selected()
        # Converter de FilterModel para TreeStore se necessário
        real_model = model.get_model()
        real_it = model.convert_iter_to_child_iter(it)
        val = real_model[real_it][2]
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(val, -1)
        clipboard.store()

    def exportar(self, widget):
        dlg = Gtk.FileChooserDialog("Exportar Metadados", self, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        filtro_json = Gtk.FileFilter(); filtro_json.set_name("JSON"); filtro_json.add_pattern("*.json")
        filtro_csv = Gtk.FileFilter(); filtro_csv.set_name("CSV"); filtro_csv.add_pattern("*.csv")
        dlg.add_filter(filtro_json); dlg.add_filter(filtro_csv)
        dlg.set_current_name(f"{os.path.splitext(os.path.basename(self.caminho))[0]}_EXIF")

        if dlg.run() == Gtk.ResponseType.ACCEPT:
            path = dlg.get_filename()
            ext = os.path.splitext(path)[1].lower()
            try:
                if ext == ".json":
                    self.exportar_json(path)
                else:
                    self.exportar_csv(path)
                dlg.destroy()
                info = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "✅ Exportado com sucesso!")
                info.run(); info.destroy()
            except Exception as e:
                mostrar_erro(f"❌ Erro ao exportar:\n{e}")
        dlg.destroy()

    def exportar_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Categoria", "Sub-categoria", "Tag", "Valor"])
            for main, sub, tag, val in self.dados_brutos:
                writer.writerow([main, sub, tag, val])

    def exportar_json(self, path):
        estrutura = {}
        for main, sub, tag, val in self.dados_brutos:
            estrutura.setdefault(main, {}).setdefault(sub, {})[tag] = val
        with open(path, "w", encoding="utf-8") as f:
            json.dump(estrutura, f, indent=2, ensure_ascii=False)

# ============================================================
# 🚀 Entrada
# ============================================================
def main():
    Gtk.init()
    caminho = obter_ficheiro()
    if not os.path.isfile(caminho):
        mostrar_erro(f"❌ Ficheiro não encontrado:\n{caminho}")
        sys.exit(1)
    win = ExifViewer(caminho)
    Gtk.main()

if __name__ == "__main__":
    main()