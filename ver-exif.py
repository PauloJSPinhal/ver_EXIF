#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nautilus Script: Visualizador EXIF Completo + Dicionário JSON + Favoritos
Compatível: Debian 13 + GNOME | GTK3 | exiftool
"""
import os
import sys
import json
import csv
import subprocess
import pathlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# ============================================================
# ⚙️ Configuração & Paths
# ============================================================
CONFIG_DIR = pathlib.Path.home() / ".config" / "ver-exif"
DICT_FILE = CONFIG_DIR / "tag-dictionary.json"
FAV_FILE = CONFIG_DIR / "favorites.json"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 📖 Dicionário Padrão (priority 1 = visível, 2 = técnico/oculto)
# ============================================================
DEFAULT_DICT = {
  "Make": {"desc": "Fabricante da câmara ou dispositivo.", "category": "📷 Corpo & Fabricante", "priority": 1},
  "Model": {"desc": "Modelo exato da câmara.", "category": "📷 Corpo & Fabricante", "priority": 1},
  "SerialNumber": {"desc": "Número de série único do corpo.", "category": "📷 Corpo & Fabricante", "priority": 1},
  "FirmwareVersion": {"desc": "Versão do firmware instalada.", "category": "📷 Corpo & Fabricante", "priority": 1},
  "CameraOwnerName": {"desc": "Nome do proprietário registado.", "category": "📷 Corpo & Fabricante", "priority": 1},
  "LensMake": {"desc": "Fabricante da objetiva.", "category": "🔭 Objetiva", "priority": 1},
  "LensModel": {"desc": "Nome ou modelo comercial da lente.", "category": "🔭 Objetiva", "priority": 1},
  "LensSerialNumber": {"desc": "Número de série da objetiva.", "category": "🔭 Objetiva", "priority": 1},
  "FocalLength": {"desc": "Distância focal real em milímetros.", "category": "🔭 Objetiva", "priority": 1},
  "FocalLengthIn35mmFilm": {"desc": "Distância focal equivalente a full-frame (35mm).", "category": "🔭 Objetiva", "priority": 1},
  "MaxApertureValue": {"desc": "Abertura máxima possível da lente.", "category": "🔭 Objetiva", "priority": 1},
  "ExposureTime": {"desc": "Tempo real do obturador (segundos).", "category": "⚡ Exposição & Disparo", "priority": 1},
  "ShutterSpeedValue": {"desc": "Velocidade em escala APEX (logarítmica).", "category": "⚡ Exposição & Disparo", "priority": 2},
  "TargetExposureTime": {"desc": "Velocidade alvo calculada antes do disparo.", "category": "⚡ Exposição & Disparo", "priority": 2},
  "ShutterSpeed": {"desc": "Velocidade do obturador (formato texto alternativo).", "category": "⚡ Exposição & Disparo", "priority": 2},
  "FNumber": {"desc": "Abertura real do diafragma (número f).", "category": "⚡ Exposição & Disparo", "priority": 1},
  "ApertureValue": {"desc": "Abertura em escala APEX.", "category": "⚡ Exposição & Disparo", "priority": 2},
  "TargetAperture": {"desc": "Abertura alvo calculada antes do disparo.", "category": "⚡ Exposição & Disparo", "priority": 2},
  "ISOSpeedRatings": {"desc": "Sensibilidade ISO efetiva usada na foto.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "BaseISO": {"desc": "Sensibilidade nativa do sensor (antes de amplificação).", "category": "⚡ Exposição & Disparo", "priority": 2},
  "AutoISO": {"desc": "Valor ISO selecionado pelo algoritmo automático.", "category": "⚡ Exposição & Disparo", "priority": 2},
  "ISO": {"desc": "Valor ISO alternativo (geralmente duplicado).", "category": "⚡ Exposição & Disparo", "priority": 2},
  "ExposureProgram": {"desc": "Modo de exposição: Manual, Prioridade, Automático, etc.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "MeteringMode": {"desc": "Método de medição de luz.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "Flash": {"desc": "Estado do flash no momento do disparo.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "LightSource": {"desc": "Tipo de iluminação ambiente detectada.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "WhiteBalance": {"desc": "Modo de balanço de brancos.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "ExposureBias": {"desc": "Compensação de exposição aplicada (EV).", "category": "⚡ Exposição & Disparo", "priority": 1},
  "ExposureCompensation": {"desc": "Compensação de exposição (alias de ExposureBias).", "category": "⚡ Exposição & Disparo", "priority": 2},
  "BrightnessValue": {"desc": "Brilho da cena medido pela câmara (APEX).", "category": "⚡ Exposição & Disparo", "priority": 1},
  "Contrast": {"desc": "Ajuste de contraste interno.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "Saturation": {"desc": "Ajuste de saturação interno.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "Sharpness": {"desc": "Ajuste de nitidez interno.", "category": "⚡ Exposição & Disparo", "priority": 1},
  "DateTimeOriginal": {"desc": "Data e hora exata do disparo.", "category": "🕒 Data & Hora", "priority": 1},
  "DateTimeDigitized": {"desc": "Data e hora de criação do ficheiro.", "category": "🕒 Data & Hora", "priority": 1},
  "OffsetTimeOriginal": {"desc": "Desvio do fuso horário no disparo (ex: +01:00).", "category": "🕒 Data & Hora", "priority": 1},
  "SubSecTimeOriginal": {"desc": "Frações de segundo do disparo original.", "category": "🕒 Data & Hora", "priority": 1},
  "ImageWidth": {"desc": "Largura da imagem em píxeis.", "category": "🖼️ Imagem & Formato", "priority": 1},
  "ImageHeight": {"desc": "Altura da imagem em píxeis.", "category": "🖼️ Imagem & Formato", "priority": 1},
  "ColorSpace": {"desc": "Espaço de cor embutido (sRGB, AdobeRGB).", "category": "🖼️ Imagem & Formato", "priority": 1},
  "Orientation": {"desc": "Rotação/espelhamento aplicado pelo leitor.", "category": "🖼️ Imagem & Formato", "priority": 1},
  "XResolution": {"desc": "Resolução horizontal em DPI.", "category": "🖼️ Imagem & Formato", "priority": 1},
  "YResolution": {"desc": "Resolução vertical em DPI.", "category": "🖼️ Imagem & Formato", "priority": 1},
  "GPSLatitude": {"desc": "Coordenada de latitude do local.", "category": "📍 GPS & Geolocalização", "priority": 1},
  "GPSLongitude": {"desc": "Coordenada de longitude do local.", "category": "📍 GPS & Geolocalização", "priority": 1},
  "GPSAltitude": {"desc": "Altitude em relação ao nível do mar.", "category": "📍 GPS & Geolocalização", "priority": 1},
  "GPSMapDatum": {"desc": "Sistema de referência geodésica (ex: WGS-84).", "category": "📍 GPS & Geolocalização", "priority": 1},
  "GPSSpeed": {"desc": "Velocidade de movimento do dispositivo.", "category": "📍 GPS & Geolocalização", "priority": 1},
  "GPSImgDirection": {"desc": "Direção para onde a câmara apontava.", "category": "📍 GPS & Geolocalização", "priority": 1},
  "XMP:Rating": {"desc": "Classificação de 0 a 5 estrelas.", "category": "💡 XMP: Edição & Organização", "priority": 1},
  "XMP:Label": {"desc": "Etiqueta de cor atribuída.", "category": "💡 XMP: Edição & Organização", "priority": 1},
  "XMP:CreatorTool": {"desc": "Software utilizado para editar o ficheiro.", "category": "💡 XMP: Edição & Organização", "priority": 1},
  "XMP:CameraProfile": {"desc": "Perfil de processamento RAW aplicado.", "category": "💡 XMP: Edição & Organização", "priority": 1},
  "Keywords": {"desc": "Palavras-chave associadas.", "category": "📰 IPTC: Profissional", "priority": 1},
  "Caption": {"desc": "Descrição ou legenda da imagem.", "category": "📰 IPTC: Profissional", "priority": 1},
  "Credit": {"desc": "Agência ou entidade responsável.", "category": "📰 IPTC: Profissional", "priority": 1},
  "Source": {"desc": "Fonte original ou copyright.", "category": "📰 IPTC: Profissional", "priority": 1},
  "ICC_Profile:ProfileName": {"desc": "Nome do perfil de cor embutido.", "category": "🎨 Perfil de Cor (ICC)", "priority": 1},
  "FileSize": {"desc": "Tamanho do ficheiro em disco.", "category": "💾 Sistema & Ficheiro", "priority": 1},
  "FileType": {"desc": "Extensão/formato do ficheiro.", "category": "💾 Sistema & Ficheiro", "priority": 1},
  "MIMEType": {"desc": "Tipo MIME oficial.", "category": "💾 Sistema & Ficheiro", "priority": 1},
  "ImageSize": {"desc": "Dimensões totais (Largura x Altura).", "category": "🔢 Cálculos & Derivados", "priority": 1},
  "Megapixels": {"desc": "Resolução em megapíxeis.", "category": "🔢 Cálculos & Derivados", "priority": 1},
  "CircleOfConfusion": {"desc": "Círculo de confusão calculado.", "category": "🔢 Cálculos & Derivados", "priority": 1},
  "HyperfocalDistance": {"desc": "Distância hiperfocal calculada.", "category": "🔢 Cálculos & Derivados", "priority": 1},
  "DOF": {"desc": "Profundidade de campo estimada.", "category": "🔢 Cálculos & Derivados", "priority": 1},
  "FocusMode": {"desc": "Modo de focagem utilizado.", "category": "🏭 MakerNotes & Avançados", "priority": 1},
  "AFPointsUsed": {"desc": "Pontos de focagem activos.", "category": "🏭 MakerNotes & Avançados", "priority": 1},
  "DriveMode": {"desc": "Modo de disparo: Único, Contínuo, etc.", "category": "🏭 MakerNotes & Avançados", "priority": 1},
  "PictureStyle": {"desc": "Perfil de imagem: Standard, Retrato, etc.", "category": "🏭 MakerNotes & Avançados", "priority": 1},
  "VibrationReduction": {"desc": "Estado do estabilizador de imagem.", "category": "🏭 MakerNotes & Avançados", "priority": 1}
}

# ============================================================
# 📖 Carregamento & Gestão do Dicionário
# ============================================================
def load_dictionary():
    if DICT_FILE.exists():
        try:
            with open(DICT_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict): return d
        except Exception: pass
    with open(DICT_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_DICT, f, indent=2, ensure_ascii=False)
    return DEFAULT_DICT

def get_info(tag):
    info = TAG_DICT.get(tag, {})
    return {
        "desc": info.get("desc", f"Parâmetro técnico: {tag}"),
        "category": info.get("category", "🔧 Outros / Não Mapeados"),
        "priority": info.get("priority", 1)
    }

# ============================================================
# 🔍 Captura & Execução
# ============================================================
def obter_ficheiro():
    paths = os.environ.get("NAUTILUS_SCRIPT_SELECTED_FILE_PATHS", "").strip()
    if not paths and len(sys.argv) > 1:
        paths = "\n".join(sys.argv[1:])
    if not paths:
        Gtk.MessageDialog(None, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, "Nenhum ficheiro selecionado.").run()
        sys.exit(0)
    return paths.split("\n")[0]

def executar_exiftool(caminho):
    try:
        cmd = ["exiftool", "-json", "-g", "-struct", "-c", "%.6f", "-charset", "UTF8", "-api", "largefilesupport=1", caminho]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=8)
        data = json.loads(proc.stdout)
        return data[0] if isinstance(data, list) else data
    except FileNotFoundError:
        dlg = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "❌ 'exiftool' não encontrado.\nInstale: sudo apt install libimage-exiftool-perl")
        dlg.run(); sys.exit(1)
    except Exception as e:
        dlg = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, f"❌ Falha ao processar:\n{str(e)}")
        dlg.run(); sys.exit(1)

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
        self.set_default_size(940, 700)
        self.set_border_width(8)
        self.caminho = caminho
        self.termo_busca = ""
        self.fav_set = set()
        self.dados = []  # (categoria, tag, val, tag_id)
        self._carregar_favoritos()

        # ✅ EXTRAÇÃO COM DEDUPLICAÇÃO POR NOME DE TAG
        bruto = executar_exiftool(caminho)
        seen_tags = set()
        for grupo, tags in bruto.items():
            if grupo == "SourceFile" or not isinstance(tags, dict): continue
            for tag, val in tags.items():
                tag_key = tag.lower()
                if tag_key in seen_tags:
                    continue
                seen_tags.add(tag_key)

                tid = f"{grupo}:{tag}"
                info = get_info(tag)
                if info["priority"] == 1:
                    self.dados.append((info["category"], tag, formatar_valor(val), tid))
        
        self.dados.sort(key=lambda x: (x[0], x[1]))
        self.total = len(self.dados)

        # UI
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        lbl = Gtk.Label(label=f"📄 {os.path.basename(caminho)}")
        lbl.set_halign(Gtk.Align.START)
        lbl.get_style_context().add_class("heading")
        vbox.pack_start(lbl, False, False, 0)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.busca = Gtk.SearchEntry()
        self.busca.set_placeholder_text("🔍 Filtrar tags, valores ou categorias...")
        self.busca.connect("changed", self.on_busca)
        toolbar.pack_start(self.busca, True, True, 0)
        for txt, func in [("🔽 Expandir", lambda w: self.view.expand_all()), ("🔼 Recolher", lambda w: self.view.collapse_all())]:
            btn = Gtk.Button.new_with_label(txt)
            btn.connect("clicked", func)
            toolbar.pack_start(btn, False, False, 0)
        vbox.pack_start(toolbar, False, False, 0)

        self.store = Gtk.TreeStore(str, str, str) # Display, TagID, Value
        self.build_tree()
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filtro_visivel)
        
        self.view = Gtk.TreeView(model=self.filter)
        self.view.set_headers_visible(True)
        self.view.set_has_tooltip(True)
        self.view.connect("query-tooltip", self.on_tooltip)
        self.view.connect("button-press-event", self.on_right_click)

        col0 = Gtk.TreeViewColumn("Estrutura", Gtk.CellRendererText(), text=0)
        col0.set_expand(True)
        self.view.append_column(col0)
        col2 = Gtk.TreeViewColumn("Valor", Gtk.CellRendererText(), text=2)
        col2.set_fixed_width(320)
        col2.set_resizable(True)
        self.view.append_column(col2)
        
        sw = Gtk.ScrolledWindow()
        sw.add(self.view)
        vbox.pack_start(sw, True, True, 0)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.info_lbl = Gtk.Label(label=f"✅ {self.total} parâmetros visíveis | {len(self.fav_set)} favoritos")
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

    def build_tree(self):
        cats = {}
        fav_node = self.store.append(None, ["⭐ Favoritos", "FAV_ROOT", ""])
        for cat, tag, val, tid in self.dados:
            if cat not in cats:
                cats[cat] = self.store.append(None, [f"📁 {cat}", cat, ""])
            self.store.append(cats[cat], [f"🏷️ {tag}", tid, val])
            if tid in self.fav_set:
                self.store.append(fav_node, [f"⭐ {tag}", tid, val])

    # ✅ CORREÇÃO EXATA DE COORDENADAS PARA TOOLTIP
    def on_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        try:
            bx, by = widget.convert_widget_to_bin_window_coords(x, y)
            path_info = widget.get_path_at_pos(bx, by)
            if path_info:
                tree_path = path_info[0]
                model = self.filter
                it = model.get_iter(tree_path)
                if it:
                    tid = model[it][1]
                    if tid and tid != "FAV_ROOT":
                        tag_name = tid.split(":", 1)[-1] if ":" in tid else tid
                        desc = get_info(tag_name)["desc"]
                        tooltip.set_text(desc)
                        return True
        except Exception:
            pass
        return False

    def on_right_click(self, widget, event):
        if event.button != 3: return
        path = widget.get_path_at_pos(int(event.x), int(event.y))
        if not path: return
        model, tree_path = self.filter, path[0]
        if not tree_path: return
        
        tid = model[model.get_iter(tree_path)][1]
        if not tid or tid == "FAV_ROOT": return

        menu = Gtk.Menu()
        label = "🗑️ Remover dos Favoritos" if tid in self.fav_set else "➕ Adicionar aos Favoritos"
        item = Gtk.MenuItem(label=label)
        item.connect("activate", lambda w: self.toggle_fav(tid))
        menu.append(item)
        menu.show_all()
        menu.popup_at_pointer(event)

    def toggle_fav(self, tid):
        if tid in self.fav_set:
            self.fav_set.discard(tid)
            for row in self.store:
                if row[1] == tid and row[0].startswith("⭐ "):
                    self.store.remove(row.iter)
                    break
        else:
            self.fav_set.add(tid)
            val = next((v for c, t, v, id_ in self.dados if id_ == tid), "")
            tag_name = tid.split(":", 1)[-1] if ":" in tid else tid
            fav_iter = self.store.get_iter_first()
            self.store.append(fav_iter, [f"⭐ {tag_name}", tid, val])
        self._salvar_favoritos()
        self.info_lbl.set_text(f"✅ {self.total} parâmetros visíveis | {len(self.fav_set)} favoritos")

    def _carregar_favoritos(self):
        try:
            if FAV_FILE.exists():
                self.fav_set = set(json.loads(FAV_FILE.read_text(encoding="utf-8")))
        except: self.fav_set = set()

    def _salvar_favoritos(self):
        FAV_FILE.write_text(json.dumps(list(self.fav_set), indent=2), encoding="utf-8")

    def filtro_visivel(self, model, it, data):
        if not self.termo_busca: return True
        txt = self.termo_busca.lower()
        return any(txt in str(model[it][col]).lower() for col in (0, 2))

    def on_busca(self, entry):
        self.termo_busca = entry.get_text()
        self.filter.refilter()
        if self.termo_busca: self.view.expand_all()

    def exportar(self, widget):
        dlg = Gtk.FileChooserDialog("Exportar Metadados", self, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
        f1, f2 = Gtk.FileFilter(), Gtk.FileFilter()
        f1.set_name("JSON"); f1.add_pattern("*.json")
        f2.set_name("CSV"); f2.add_pattern("*.csv")
        dlg.add_filter(f1); dlg.add_filter(f2)
        dlg.set_current_name(f"{os.path.splitext(os.path.basename(self.caminho))[0]}_EXIF")

        if dlg.run() == Gtk.ResponseType.ACCEPT:
            path = dlg.get_filename()
            try:
                if path.lower().endswith(".json"): self.exportar_json(path)
                else: self.exportar_csv(path)
                dlg.destroy()
                Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "✅ Exportado com sucesso!").run()
            except Exception as e:
                Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, f"❌ Erro:\n{e}").run()
        dlg.destroy()

    def exportar_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Categoria", "Tag", "Valor", "Favorito"])
            for c, t, v, tid in self.dados:
                w.writerow([c, t, v, "Sim" if tid in self.fav_set else "Não"])

    def exportar_json(self, path):
        out = {}
        for c, t, v, tid in self.dados:
            out.setdefault(c, {})[t] = {"valor": v, "favorito": tid in self.fav_set}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

# ============================================================
# 🚀 Entrada
# ============================================================
def main():
    global TAG_DICT
    TAG_DICT = load_dictionary()
    Gtk.init()
    caminho = obter_ficheiro()
    if not os.path.isfile(caminho):
        Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, f"❌ Ficheiro não encontrado:\n{caminho}").run()
        sys.exit(1)
    win = ExifViewer(caminho)
    Gtk.main()

if __name__ == "__main__":
    main()