import os
import sys
import threading
import re
import io
from urllib.request import urlopen, Request
import traceback
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


def get_base_dir() -> str:
    """Возвращает базовую директорию для ресурсов в обычном и frozen-режиме.

    - В обычном запуске: директория файла скрипта
    - В PyInstaller (frozen): sys._MEIPASS (временная распаковка) либо директория exe
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass and os.path.isdir(meipass):
        return meipass
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_run_dir() -> str:
    """Директория запуска для файлов вывода (папка с exe или со скриптом)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# GUI-only bootstrap; data processing and Pillow/pandas will be imported lazily




DEFAULT_CONFIG = {
    "template": "template.jpg",
    "output_dir": "output",
    "fields": [
        {"name": "Артикул", "x": 0.58, "y": 0.12, "font_size": 0.070, "font_ref": "w", "font_units": "rel", "color": "#000000", "anchor": "la"},
    ],
    "multiline_fields": [
        {
            "name": "Применимость по КК",
            "x": 0.62,
            "y": 0.42,
            "font_size": 0.050,
            "font_ref": "w",
            "font_units": "rel",
            "color": "#000000",
            "anchor": "la",
            "delimiter": "/",
            "max_lines": 6,
            "overflow_text": "и т.д.",
            "line_spacing": 1.25
        }
    ],
    "image_box": {
        "source_column": "Ссылка на фото",
        "x": 0.05,
        "y": 0.28,
        "width": 0.58,
        "height": 0.52,
        "fit": "contain",
        "remove_bg": True,
        "remove_bg_color": "#FFFFFF",
        "remove_bg_tolerance": 20,
        "auto_crop": True
    },
    "font": {
        "ttf_path": None,
    },
    "filename_pattern": "{article_clean}.jpg",
}


class ImageGeneratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Image Generator")
        self.root.geometry("700x420")

        self.input_path: Optional[str] = None
        self.output_dir: Optional[str] = None
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()

        self._build_ui()

    def _build_ui(self) -> None:
        pad = 8

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=pad, pady=pad)

        tk.Label(frame, text="Файл данных (XLSX/CSV)").grid(row=0, column=0, sticky="w")
        self.input_entry = tk.Entry(frame, width=70)
        self.input_entry.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, pad))
        tk.Button(frame, text="Выбрать...", command=self._choose_input).grid(row=1, column=2, sticky="we")

        tk.Label(frame, text="Папка для изображений").grid(row=2, column=0, sticky="w")
        self.output_entry = tk.Entry(frame, width=70)
        self.output_entry.grid(row=3, column=0, columnspan=2, sticky="we", pady=(0, pad))
        tk.Button(frame, text="Папка...", command=self._choose_output).grid(row=3, column=2, sticky="we")

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=3, sticky="we", pady=(pad, pad))
        tk.Button(btn_frame, text="Загрузить конфиг...", command=self._load_config)
        tk.Button(btn_frame, text="Сохранить конфиг...", command=self._save_config)
        tk.Button(btn_frame, text="Старт", command=self._start)
        tk.Button(btn_frame, text="Редактор зон", command=self._open_zone_editor)
        for idx, child in enumerate(btn_frame.winfo_children()):
            child.pack(side=tk.LEFT, padx=(0 if idx == 0 else pad, 0))

        tk.Label(frame, text="Прогресс").grid(row=5, column=0, sticky="w")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = tk.Scale(
            frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.progress_var
        )
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky="we")

        tk.Label(frame, text="Лог").grid(row=7, column=0, sticky="w", pady=(pad, 0))
        self.log_text = tk.Text(frame, height=10)
        self.log_text.grid(row=8, column=0, columnspan=3, sticky="nsew")

        frame.grid_rowconfigure(8, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=0)

        run_dir = get_run_dir()
        default_output = os.path.join(run_dir, self.config.get("output_dir", "output"))
        self.output_entry.insert(0, default_output)

    def _log(self, msg: str) -> None:
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _choose_input(self) -> None:
        filetypes = [
            ("Табличные файлы", "*.xlsx *.xls *.csv"),
            ("Excel", "*.xlsx *.xls"),
            ("CSV", "*.csv"),
            ("Все файлы", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Выберите файл данных", filetypes=filetypes)
        if path:
            self.input_path = path
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Выберите папку для изображений")
        if path:
            self.output_dir = path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def _load_config(self) -> None:
        import json
        
        def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
            """Рекурсивное слияние словарей: сохраняет вложенные ключи из base,
            если в override нет значений. Значения в override имеют приоритет."""
            result = base.copy()
            for k, v in (override or {}).items():
                if isinstance(v, dict) and isinstance(result.get(k), dict):
                    result[k] = deep_merge(result[k], v)
                else:
                    result[k] = v
            return result

        path = filedialog.askopenfilename(title="Выберите JSON конфиг", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # deep merge with defaults (важно для image_box.remove_bg и др.)
            merged = deep_merge(DEFAULT_CONFIG, data)
            self.config = merged
            self._log(f"Загружен конфиг: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить конфиг: {e}")

    def _save_config(self) -> None:
        import json

        path = filedialog.asksaveasfilename(
            title="Сохранить конфиг как",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self._log(f"Сохранен конфиг: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфиг: {e}")

    def _start(self) -> None:
        self.input_path = self.input_entry.get().strip() or self.input_path
        self.output_dir = self.output_entry.get().strip() or self.output_dir

        if not self.input_path or not os.path.isfile(self.input_path):
            messagebox.showwarning("Внимание", "Укажите корректный файл данных")
            return

        if not self.output_dir:
            run_dir = get_run_dir()
            self.output_dir = os.path.join(run_dir, self.config.get("output_dir", "output"))
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, self.output_dir)

        os.makedirs(self.output_dir, exist_ok=True)

        # Run processing in a background thread to keep UI responsive
        thread = threading.Thread(target=self._process_safe, daemon=True)
        thread.start()

    def _open_zone_editor(self) -> None:
        try:
            columns: Optional[List[str]] = None
            # Пытаемся получить список колонок из выбранного файла
            if self.input_path and os.path.isfile(self.input_path):
                try:
                    import pandas as pd
                    path_lower = self.input_path.lower()
                    if path_lower.endswith(".csv"):
                        dfh = pd.read_csv(self.input_path, nrows=0)
                    else:
                        dfh = pd.read_excel(self.input_path, nrows=0)
                    columns = [str(c) for c in list(dfh.columns)]
                except Exception:
                    columns = None
            ZoneEditor(self.root, self.config, columns)
        except Exception:
            self._log(traceback.format_exc())

    def _process_safe(self) -> None:
        try:
            self._process()
        except Exception:
            self._log(traceback.format_exc())
            messagebox.showerror("Ошибка", "Произошла ошибка, детали в логе.")

    def _process(self) -> None:
        import pandas as pd
        from PIL import Image, ImageDraw, ImageFont

        self._log("Чтение данных...")
        path_lower = self.input_path.lower()
        if path_lower.endswith(".csv"):
            df = pd.read_csv(self.input_path)
        else:
            df = pd.read_excel(self.input_path)

        if df.empty:
            self._log("Файл данных пуст.")
            return

        base_dir = get_base_dir()
        template_path = self.config.get("template", "template.jpg")
        if not os.path.isabs(template_path):
            template_path = os.path.join(base_dir, template_path)

        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Не найден шаблон: {template_path}")

        font_cfg = self.config.get("font", {}) or {}
        ttf_path = font_cfg.get("ttf_path")

        def load_font(size: int):
            from PIL import ImageFont
            if ttf_path and os.path.isfile(ttf_path):
                try:
                    return ImageFont.truetype(ttf_path, size)
                except Exception:
                    pass
            candidates = [
                os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "arial.ttf"),
                os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "segoeui.ttf"),
            ]
            for p in candidates:
                if os.path.isfile(p):
                    try:
                        return ImageFont.truetype(p, size)
                    except Exception:
                        continue
            try:
                return ImageFont.truetype("DejaVuSans.ttf", size)
            except Exception:
                return ImageFont.load_default()
        filename_pattern = self.config.get("filename_pattern", "image_{row_index:04d}.jpg")

        self._log("Начало генерации изображений...")
        total = len(df.index)
        for idx, row in df.iterrows():
            with Image.open(template_path).convert("RGB") as base_img:
                draw = ImageDraw.Draw(base_img)
                W, H = base_img.size

                def resolve_coord(val, total):
                    try:
                        f = float(val)
                        if 0.0 < f <= 1.0:
                            return int(f * total)
                        return int(f)
                    except Exception:
                        return int(val)

                def resolve_font_size(val, ref_dim: str = "w", units: str = "rel"):
                    try:
                        f = float(val)
                        if (units or "rel").lower() == "rel" and 0.0 < f <= 1.0:
                            base = W if (ref_dim or "w").lower() == "w" else H
                            return max(8, int(f * base))
                        return int(f)
                    except Exception:
                        return int(val)

                # вставка изображения по URL
                img_box = (self.config.get("image_box") or {}).copy()
                if img_box:
                    src_col = img_box.get("source_column")
                    url = str(row.get(src_col, "") or "").strip() if src_col else ""
                    if url:
                        try:
                            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                            with urlopen(req, timeout=10) as resp:
                                data = resp.read()
                            from PIL import Image as PILImage
                            with PILImage.open(io.BytesIO(data)) as src_img:
                                remove_bg = bool(img_box.get("remove_bg", True))
                                if remove_bg:
                                    try:
                                        import numpy as np
                                        rgba = src_img.convert("RGBA")
                                        arr = np.array(rgba)
                                        hexcol = (img_box.get("remove_bg_color", "#FFFFFF") or "#FFFFFF").lstrip('#')
                                        rt = int(hexcol[0:2], 16)
                                        gt = int(hexcol[2:4], 16)
                                        bt = int(hexcol[4:6], 16)
                                        tol = int(img_box.get("remove_bg_tolerance", 18))
                                        r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
                                        mask = (np.abs(r-rt) <= tol) & (np.abs(g-gt) <= tol) & (np.abs(b-bt) <= tol)
                                        arr[..., 3] = np.where(mask, 0, a)
                                        src_img = PILImage.fromarray(arr)
                                        if bool(img_box.get("auto_crop", True)):
                                            alpha = src_img.split()[3]
                                            bbox = alpha.getbbox()
                                            if bbox:
                                                src_img = src_img.crop(bbox)
                                    except Exception:
                                        src_img = src_img.convert("RGB")
                                else:
                                    src_img = src_img.convert("RGB")
                                x = resolve_coord(img_box.get("x", 0), W)
                                y = resolve_coord(img_box.get("y", 0), H)
                                bw = max(1, resolve_coord(img_box.get("width", src_img.width), W))
                                bh = max(1, resolve_coord(img_box.get("height", src_img.height), H))
                                fit = (img_box.get("fit", "contain") or "contain").lower()
                                scale_w = bw / src_img.width
                                scale_h = bh / src_img.height
                                scale = max(scale_w, scale_h) if fit == "cover" else min(scale_w, scale_h)
                                new_w = max(1, int(src_img.width * scale))
                                new_h = max(1, int(src_img.height * scale))
                                resized = src_img.resize((new_w, new_h))
                                off_x = x + (bw - new_w) // 2
                                off_y = y + (bh - new_h) // 2
                                if resized.mode == "RGBA":
                                    base_img.paste(resized, (off_x, off_y), mask=resized.split()[3])
                                else:
                                    base_img.paste(resized, (off_x, off_y))

                        except Exception:
                            pass
                for field in self.config.get("fields", []):
                    name = field.get("name")
                    x = resolve_coord(field.get("x", 0), W)
                    y = resolve_coord(field.get("y", 0), H)
                    fx = x
                    fy = y
                    fw = resolve_coord(field.get("width", 0), W)
                    fh = resolve_coord(field.get("height", 0), H)
                    font_ref = (field.get("font_ref") or "w").lower()
                    font_units = (field.get("font_units") or "rel").lower()
                    font_size = resolve_font_size(field.get("font_size", 32), font_ref, font_units)
                    color = field.get("color", "#000000")
                    anchor = field.get("anchor", "la")

                    value = row.get(name, "")
                    text = "" if value is None else str(value)

                    font = load_font(font_size)

                    if fw > 0 and fh > 0:
                        words = text.split()
                        line = ""
                        is_article = (name or "").strip().lower() in ("артикул", "article", "арт", "артикуль")
                        cursor_y = fy
                        try:
                            ascent, descent = font.getmetrics()
                            step = int((ascent + descent) * 1.1)
                        except Exception:
                            step = int(font_size * 1.1)
                        for w in words:
                            test = (line + " " + w).strip()
                            tw, th = font.getbbox(test)[2:4]
                            if tw > fw and line:
                                if is_article:
                                    lw, _ = font.getbbox(line)[2:4]
                                    cx = fx + (fw - lw) // 2
                                    draw.text((cx, cursor_y), line, font=font, fill=color, anchor="la")
                                else:
                                    draw.text((fx, cursor_y), line, font=font, fill=color, anchor="la")
                                cursor_y += step
                                line = w
                                if cursor_y > fy + fh - step:
                                    break
                            else:
                                line = test
                        if cursor_y <= fy + fh - step and line:
                            lw, _ = font.getbbox(line)[2:4]
                            if is_article:
                                cx = fx + (fw - lw) // 2
                                total_height = step
                                if cursor_y == fy:
                                    cursor_y = fy + (fh - total_height) // 2
                                draw.text((cx, cursor_y), line, font=font, fill=color, anchor="la")
                            else:
                                draw.text((fx, cursor_y), line, font=font, fill=color, anchor="la")
                    else:
                        draw.text((x, y), text, font=font, fill=color, anchor=anchor)

                # многострочные поля
                for mfield in self.config.get("multiline_fields", []):
                    name = mfield.get("name")
                    raw = row.get(name, "")
                    text_value = "" if raw is None else str(raw)
                    delimiter = mfield.get("delimiter", "/")
                    
                    parts = [p.strip() for p in str(text_value).split(delimiter) if p.strip()]
                    
                    # очистка от годов выпуска и лишних символов
                    try:
                        import re as _re
                        cleaned_parts = []
                        for p in parts:
                            p = _re.sub(r"\b(19|20)\d{2}\b\s*[-–—]?\s*\b(19|20)\d{2}\b", "", p)
                            p = _re.sub(r"\b(19|20)\d{2}\b", "", p)
                            p = _re.sub(r"[\s\-–—/:]+$", "", p)
                            p = _re.sub(r"\s{2,}", " ", p).strip()
                            if p:
                                cleaned_parts.append(p)
                        parts = cleaned_parts
                    except Exception:
                        pass
                    max_lines = int(mfield.get("max_lines", 6))
                    overflow_text = mfield.get("overflow_text", "и т.д.")
                    show_overflow_text = bool(mfield.get("show_overflow_text", True))
                    x = resolve_coord(mfield.get("x", 0), W)
                    y = resolve_coord(mfield.get("y", 0), H)
                    box_w = resolve_coord(mfield.get("width", 0), W)
                    box_h = resolve_coord(mfield.get("height", 0), H)
                    m_font_ref = (mfield.get("font_ref") or "w").lower()
                    m_font_units = (mfield.get("font_units") or "rel").lower()
                    font_size = resolve_font_size(mfield.get("font_size", 32), m_font_ref, m_font_units)
                    color = mfield.get("color", "#000000")
                    anchor = mfield.get("anchor", "la")
                    line_spacing = float(mfield.get("line_spacing", 1.2))
                    mfont = load_font(font_size)
                    try:
                        ascent, descent = mfont.getmetrics()
                        step = int((ascent + descent) * line_spacing)
                    except Exception:
                        step = int(font_size * line_spacing)
                    # Заголовок "Применимость:" всегда первой строкой
                    title = mfield.get("title", "Применимость:")
                    cursor_y = y
                    def fits(txt: str) -> bool:
                        if box_w <= 0:
                            return True
                        try:
                            width_px = draw.textlength(txt, font=mfont)
                        except Exception:
                            # fallback
                            bx = mfont.getbbox(txt)
                            width_px = bx[2] - bx[0]
                        return width_px <= box_w

                    def emit_line(txt: str) -> bool:
                        nonlocal cursor_y
                        if box_h > 0 and cursor_y + step > y + box_h:
                            return False
                        draw.text((x, cursor_y), txt, font=mfont, fill=color, anchor=anchor)
                        cursor_y += step
                        return True

                    # заголовок
                    if not emit_line(title):
                        continue

                    # построение строк из токенов
                    lines: list[str] = []
                    max_chars = int(mfield.get("max_chars", 20))
                    def clamp_chars(s: str) -> str:
                        if max_chars > 0 and len(s) > max_chars:
                            return s[:max(1, max_chars-3)] + "..."
                        return s
                    
                    lines = []
                    for token in parts:
                        result = clamp_chars(token)
                        lines.append(result)

                    allowed = max_lines
                    to_draw = lines[:allowed] if allowed > 0 else []
                    overflow = len(lines) > allowed

                    for ln in to_draw:
                        ln = clamp_chars(ln)
                        if not emit_line(ln):
                            break

                    if overflow and show_overflow_text:
                        emit_line(str(overflow_text))

                article_value = row.get("Артикул") or row.get("артикул") or row.get("Article") or row.get("article")
                article_clean = ""
                if article_value is not None:
                    article_clean = re.sub(r"[^0-9A-Za-z]+", "", str(article_value)).lower()
                out_name = None
                if "{article_clean}" in filename_pattern and article_clean:
                    out_name = filename_pattern.replace("{article_clean}", article_clean)
                if not out_name:
                    out_name = filename_pattern.format(row_index=idx)
                out_path = os.path.join(self.output_dir, out_name)
                base_img.save(out_path, quality=95)

            progress = (idx + 1) * 100.0 / total
            self.progress_var.set(progress)
            self._log(f"Сохранено: {out_name}")

        self.progress_var.set(100.0)
        self._log("Готово.")


class ZoneEditor(tk.Toplevel):
    """Редактор зон для настройки полей и изображений на шаблоне."""

    def __init__(self, master: tk.Misc, config: Dict[str, Any], columns: Optional[List[str]] = None):
        super().__init__(master)
        self.title("Редактор зон")
        self.geometry("1000x700")
        self.config_ref = config

        self.mode = tk.StringVar(value="image")  # image|field|multiline
        self.field_name = tk.StringVar(value="Артикул")
        self.font_rel = tk.DoubleVar(value=0.04)
        self.line_spacing = tk.DoubleVar(value=1.25)
        self.columns = columns or []

        base_dir = get_base_dir()
        tpath = self.config_ref.get("template", "template.jpg")
        if not os.path.isabs(tpath):
            tpath = os.path.join(base_dir, tpath)

        from PIL import Image, ImageTk
        self.img = Image.open(tpath).convert("RGB")
        self.W, self.H = self.img.size
        self.zoom = 1.0
        self.tk_img = ImageTk.PhotoImage(self.img)

        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Radiobutton(toolbar, text="Картинка", variable=self.mode, value="image").pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(toolbar, text="Артикул", variable=self.mode, value="field").pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(toolbar, text="Применимость", variable=self.mode, value="multiline").pack(side=tk.LEFT, padx=6)
        ttk.Label(toolbar, text="Имя поля:").pack(side=tk.LEFT, padx=6)
        if self.columns:
            self.field_combo = ttk.Combobox(toolbar, width=24, values=self.columns)
            self.field_combo.bind("<<ComboboxSelected>>", lambda e: self.field_name.set(self.field_combo.get()))
            self.field_combo.pack(side=tk.LEFT)
        else:
            ttk.Entry(toolbar, textvariable=self.field_name, width=22).pack(side=tk.LEFT)
        ttk.Label(toolbar, text="Шрифт(0..1) или px:").pack(side=tk.LEFT, padx=6)
        ttk.Entry(toolbar, textvariable=self.font_rel, width=6).pack(side=tk.LEFT)
        self.font_units = tk.StringVar(value="rel")
        ttk.Combobox(toolbar, width=5, values=["rel", "px"], textvariable=self.font_units, state="readonly").pack(side=tk.LEFT, padx=4)
        ttk.Label(toolbar, text="L-Space:").pack(side=tk.LEFT, padx=6)
        ttk.Entry(toolbar, textvariable=self.line_spacing, width=6).pack(side=tk.LEFT)
        self.remove_bg_var = tk.BooleanVar(value=bool(self.config_ref.get("image_box", {}).get("remove_bg", True)))
        ttk.Checkbutton(toolbar, text="Убирать белый фон (Картинка)", variable=self.remove_bg_var, command=self._apply_remove_bg_flag).pack(side=tk.RIGHT, padx=8)
        ttk.Button(toolbar, text="Сохранить", command=self._save_into_config).pack(side=tk.RIGHT, padx=6)
        ttk.Button(toolbar, text="Сохранить в файл...", command=self._export_config).pack(side=tk.RIGHT, padx=6)

        # Scrollable canvas
        body = tk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)
        self.hbar = tk.Scrollbar(body, orient=tk.HORIZONTAL)
        self.vbar = tk.Scrollbar(body, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(body, width=min(self.W, 900), height=min(self.H, 550),
                                 bg="#333", xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.hbar.config(command=self.canvas.xview)
        self.vbar.config(command=self.canvas.yview)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_img = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        self.start_x = self.start_y = None
        self.rect_id = None
        self.point_id = None
        self.current_rect = None  # (x1,y1,x2,y2) in image coords
        self.current_point = None  # (cx,cy) in image coords

        self.canvas.bind("<Button-1>", self.on_down)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_up)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self._update_scrollregion()

    def _update_scrollregion(self):
        zw = int(self.W * self.zoom)
        zh = int(self.H * self.zoom)
        self.canvas.config(scrollregion=(0, 0, zw, zh))
        from PIL import ImageTk
        scaled = self.img.resize((zw, zh))
        self.tk_img = ImageTk.PhotoImage(scaled)
        self.canvas.itemconfigure(self.canvas_img, image=self.tk_img)
        self._redraw_overlays()

    def canvas_to_img(self, x, y):
        return x / self.zoom, y / self.zoom

    def img_to_canvas(self, x, y):
        return x * self.zoom, y * self.zoom

    def _redraw_overlays(self):
        if self.point_id:
            self.canvas.delete(self.point_id)
            self.point_id = None
        if self.current_point:
            cx, cy = self.img_to_canvas(*self.current_point)
            self.point_id = self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, outline="yellow", width=2)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        if self.current_rect:
            x1, y1, x2, y2 = self.current_rect
            c1x, c1y = self.img_to_canvas(x1, y1)
            c2x, c2y = self.img_to_canvas(x2, y2)
            self.rect_id = self.canvas.create_rectangle(c1x, c1y, c2x, c2y, outline="red", width=2)

    def on_down(self, e):
        self.start_x, self.start_y = e.x, e.y
        ix, iy = self.canvas_to_img(e.x, e.y)
        self.current_rect = (ix, iy, ix, iy)
        self._redraw_overlays()

    def on_drag(self, e):
        if self.current_rect and self.start_x is not None:
            x1, y1, _, _ = self.current_rect
            ix, iy = self.canvas_to_img(e.x, e.y)
            self.current_rect = (x1, y1, ix, iy)
            self._redraw_overlays()

    def on_up(self, e):
        pass

    def on_wheel(self, e):
        delta = 1 if e.delta > 0 else -1
        factor = 1.1 if delta > 0 else 1/1.1
        new_zoom = max(0.2, min(5.0, self.zoom * factor))
        if abs(new_zoom - self.zoom) < 1e-6:
            return
        cx = self.canvas.canvasx(e.x)
        cy = self.canvas.canvasy(e.y)
        rx = cx / max(1, int(self.W * self.zoom))
        ry = cy / max(1, int(self.H * self.zoom))
        self.zoom = new_zoom
        self._update_scrollregion()
        self.canvas.xview_moveto(max(0.0, min(1.0, rx)))
        self.canvas.yview_moveto(max(0.0, min(1.0, ry)))

    def _save_into_config(self):
        try:
            mode = self.mode.get()
            if self.rect_id is None and self.current_rect is None:
                messagebox.showwarning("Внимание", "Выделите прямоугольник мышью на шаблоне")
                return
            if self.rect_id:
                x1, y1, x2, y2 = self.canvas.coords(self.rect_id)
                x1, y1 = self.canvas_to_img(x1, y1)
                x2, y2 = self.canvas_to_img(x2, y2)
            else:
                x1, y1, x2, y2 = self.current_rect
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            rel = {
                "x": x1 / self.W,
                "y": y1 / self.H,
                "width": (x2 - x1) / self.W,
                "height": (y2 - y1) / self.H,
            }
            if mode == "image":
                box = self.config_ref.setdefault("image_box", {})
                box.update(rel)
                if not box.get("source_column"):
                    box["source_column"] = "Ссылка на фото"
                if not box.get("fit"):
                    box["fit"] = "contain"
                messagebox.showinfo("OK", "Image Box сохранён в конфиг")
            elif mode == "multiline":
                found = None
                for mf in self.config_ref.setdefault("multiline_fields", []):
                    if mf.get("name") == self.field_name.get():
                        found = mf
                        break
                if not found:
                    found = {"name": self.field_name.get(), "delimiter": "/", "max_lines": 6, "overflow_text": "и т.д.", "anchor": "la", "color": "#000000"}
                    self.config_ref["multiline_fields"].append(found)
                found.update({
                    "x": rel["x"], "y": rel["y"],
                    "font_size": float(self.font_rel.get()),
                    "font_units": self.font_units.get(),
                    "line_spacing": float(self.line_spacing.get())
                })
                messagebox.showinfo("OK", "Многострочное поле сохранено в конфиг")
            else:
                updated = False
                for fld in self.config_ref.setdefault("fields", []):
                    if fld.get("name") == self.field_name.get():
                        fld.update({
                            "x": rel["x"], "y": rel["y"], "width": rel["width"], "height": rel["height"],
                            "font_size": float(self.font_rel.get()), "font_units": self.font_units.get(), "anchor": "la", "color": "#000000"
                        })
                        updated = True
                        break
                if not updated:
                    self.config_ref["fields"].append({
                        "name": self.field_name.get(),
                        "x": rel["x"], "y": rel["y"], "width": rel["width"], "height": rel["height"],
                        "font_size": float(self.font_rel.get()), "font_units": self.font_units.get(), "anchor": "la", "color": "#000000"
                    })
                messagebox.showinfo("OK", "Поле сохранено в конфиг (зона)")
        except Exception as e:
            import traceback
            messagebox.showerror("Ошибка", traceback.format_exc())

    def _export_config(self):
        import json
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(title="Сохранить конфиг как", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.config_ref, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("OK", f"Конфиг сохранён: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфиг: {e}")

    def _apply_remove_bg_flag(self):
        box = self.config_ref.setdefault("image_box", {})
        box["remove_bg"] = bool(self.remove_bg_var.get())


def main() -> None:
    root = tk.Tk()
    app = ImageGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()



