#!/usr/bin/env python3
"""Interfaz gráfica GTK 4 para el analizador léxico generado con FLEX."""
import os
import subprocess
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk


class AnalyzerWindow(Adw.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Analizador Léxico — C simplificado")
        self.set_default_size(1240, 800)
        self.set_size_request(920, 620)
        self._analysis_timeout = None
        self._suppress_auto_analysis = False
        self._build_ui()

    @staticmethod
    def _icon_button(label, icon_name, callback, css_class=None):
        button = Gtk.Button(icon_name=icon_name, tooltip_text=label)
        if css_class:
            button.add_css_class(css_class)
        button.connect("clicked", callback)
        return button

    @staticmethod
    def _section_header(title, note):
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_label = Gtk.Label(label=title, xalign=0)
        title_label.add_css_class("heading")
        note_label = Gtk.Label(label=note, xalign=0)
        note_label.add_css_class("dim-label")
        header.append(title_label)
        header.append(note_label)
        return header

    def _build_ui(self):
        toolbar = Adw.ToolbarView()
        self.set_content(toolbar)
        headerbar = Adw.HeaderBar()
        headerbar.set_title_widget(Adw.WindowTitle(title="Analizador Léxico", subtitle="C simplificado"))
        headerbar.pack_start(self._icon_button("Abrir archivo", "document-open-symbolic", self.open_file))
        headerbar.pack_start(self._icon_button("Limpiar editor", "edit-clear-symbolic", self.clear))
        toolbar.add_top_bar(headerbar)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12,
                       margin_top=12, margin_bottom=12, margin_start=12, margin_end=12)
        toolbar.set_content(root)
        self.banner = Adw.Banner(title="El análisis se ejecuta localmente mediante FLEX.", revealed=True)
        root.append(self.banner)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL, vexpand=True)
        paned.set_position(575)
        root.append(paned)
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=13)
        left.append(self._section_header("Código fuente", "Escribe, pega o abre un archivo .c"))
        self.editor = Gtk.TextView(monospace=True, wrap_mode=Gtk.WrapMode.NONE, vexpand=True)
        self.editor.set_top_margin(12); self.editor.set_bottom_margin(12)
        self.editor.set_left_margin(12); self.editor.set_right_margin(12)
        self.editor.get_buffer().connect("changed", self._source_changed)
        editor_scroll = Gtk.ScrolledWindow(vexpand=True, child=self.editor)
        editor_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        left.append(editor_scroll)
        tip = Gtk.Label(label="Consejo: los comentarios y espacios se ignoran; los errores conservan línea y columna.", xalign=0, wrap=True)
        tip.add_css_class("dim-label"); left.append(tip)
        paned.set_start_child(left)

        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=13)
        results_header = Gtk.Box(spacing=8)
        results_header.append(self._section_header("Resultado del análisis", "Tokens detectados por el autómata generado con FLEX"))
        self.summary = Gtk.Label(label="Listo para analizar", xalign=1, hexpand=True)
        self.summary.add_css_class("dim-label")
        results_header.append(self.summary)
        right.append(results_header)
        self.result_stack = Gtk.Stack(vexpand=True)
        empty = Adw.StatusPage(icon_name="system-search-symbolic", title="Aún no hay resultados",
                               description="Abre o escribe código C y selecciona Analizar.")
        self.result_stack.add_named(empty, "empty")
        self.table = Gtk.Grid(column_spacing=8, row_spacing=0)
        self.table.set_halign(Gtk.Align.START)
        table_scroll = Gtk.ScrolledWindow(vexpand=True, child=self.table)
        self.result_stack.add_named(table_scroll, "table")
        self.result_stack.set_visible_child_name("empty")
        right.append(self.result_stack)
        right.append(self._section_header("Diagnóstico", "Errores léxicos y ubicación exacta"))
        self.errors = Gtk.TextView(editable=False, cursor_visible=False, monospace=True,
                                   wrap_mode=Gtk.WrapMode.WORD_CHAR)
        error_scroll = Gtk.ScrolledWindow(height_request=112, child=self.errors)
        right.append(error_scroll)
        paned.set_end_child(right)

    @staticmethod
    def _engine_path():
        configured = os.environ.get("LEXER_ENGINE")
        if configured: return Path(configured)
        local = Path(__file__).resolve().parent / "analizador_lexico_engine"
        return local if local.exists() else Path(__file__).resolve().parent / "build" / "lexer_engine"

    def _source_changed(self, _buffer):
        """Espera una pausa breve al escribir antes de ejecutar FLEX."""
        if self._suppress_auto_analysis:
            return
        if self._analysis_timeout is not None:
            GLib.source_remove(self._analysis_timeout)
        self._analysis_timeout = GLib.timeout_add(250, self._analyze_after_typing)

    def _analyze_after_typing(self):
        self._analysis_timeout = None
        self.analyze(None, show_dialog=False)
        return GLib.SOURCE_REMOVE

    def analyze(self, _button=None, show_dialog=True):
        buffer = self.editor.get_buffer()
        source = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        engine = self._engine_path()
        if not engine.exists():
            if show_dialog:
                self._show_error("No se encontró el motor FLEX. Ejecute «make» antes de abrir la aplicación.")
            return
        result = subprocess.run([str(engine)], input=source, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            if show_dialog:
                self._show_error("El motor FLEX no pudo analizar el código:\n" + result.stderr)
            return
        tokens, errors = [], []
        for record in result.stdout.splitlines():
            fields = record.split("\t", 2)
            if len(fields) != 3: continue
            category, kind, lexeme = fields
            item = (kind, lexeme)
            (tokens if category == "T" else errors).append(item)
        self._render(tokens, errors)

    def _render(self, tokens, errors):
        child = self.table.get_first_child()
        while child:
            following = child.get_next_sibling()
            self.table.remove(child)
            child = following
        for column, heading in enumerate(("#", "Lexema", "Token")):
            self._cell(heading, column, 0, True)
        for row, (kind, lexeme) in enumerate(tokens, start=1):
            for col, value in enumerate((str(row), repr(lexeme), kind)):
                self._cell(value, col, row, False)
        self.summary.set_text(f"{len(tokens)} tokens · {len(errors)} errores")
        self.result_stack.set_visible_child_name("table")
        self.banner.set_revealed(bool(errors))
        if errors:
            self.banner.set_title("Se encontraron errores léxicos. Revisa el diagnóstico.")
        else:
            self.banner.set_title("Análisis completado sin errores léxicos.")
        message = "No se encontraron errores léxicos." if not errors else "\n".join(
            f"{kind}: {lexeme!r}" for kind, lexeme in errors)
        self.errors.get_buffer().set_text(message)

    def _cell(self, text, column, row, heading):
        widths = (4, 16, 18)
        label = Gtk.Label(label=text, xalign=0, ellipsize=3, hexpand=False,
                          margin_start=5, margin_end=5, margin_top=3, margin_bottom=3)
        label.set_width_chars(widths[column])
        label.set_max_width_chars(widths[column])
        if heading:
            label.add_css_class("heading")
        self.table.attach(label, column, row, 1, 1)

    def clear(self, _button):
        if self._analysis_timeout is not None:
            GLib.source_remove(self._analysis_timeout)
            self._analysis_timeout = None
        self._suppress_auto_analysis = True
        self.editor.get_buffer().set_text("")
        self._suppress_auto_analysis = False
        self.errors.get_buffer().set_text("")
        self.summary.set_text("Listo para analizar")
        self.result_stack.set_visible_child_name("empty")
        self.banner.set_title("El análisis se ejecuta localmente mediante FLEX.")
        self.banner.set_revealed(True)

    def open_file(self, _button):
        chooser = Gtk.FileChooserNative(title="Abrir código fuente", transient_for=self,
                                        action=Gtk.FileChooserAction.OPEN, accept_label="Abrir")
        file_filter = Gtk.FileFilter(name="Código C o texto")
        for pattern in ("*.c", "*.h", "*.txt"): file_filter.add_pattern(pattern)
        chooser.add_filter(file_filter)
        chooser.connect("response", self._file_selected)
        chooser.show()

    def _file_selected(self, chooser, response):
        if response == Gtk.ResponseType.ACCEPT:
            try:
                content = chooser.get_file().load_contents(None)[1].decode("utf-8")
                self.editor.get_buffer().set_text(content)
            except Exception as error:
                self._show_error(f"No se pudo abrir el archivo:\n{error}")
        chooser.destroy()

    def _show_error(self, message):
        dialog = Gtk.MessageDialog(transient_for=self, modal=True,
                                   buttons=Gtk.ButtonsType.CLOSE, text=message)
        dialog.connect("response", lambda widget, _response: widget.destroy())
        dialog.show()


class AnalyzerApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="edu.lexico.flex")

    def do_activate(self):
        window = self.props.active_window
        if window is None: window = AnalyzerWindow(self)
        window.present()


if __name__ == "__main__":
    raise SystemExit(AnalyzerApplication().run(None))
