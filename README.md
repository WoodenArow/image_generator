Запуск

1. Установите Python 3.10+.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Поместите файл шаблона `template.jpg` рядом со скриптом (либо укажите путь в конфиге).
4. Запустите GUI:

```bash
python image_generator.py
```

Сборка .exe (Windows)

Вариант A (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./build_exe.ps1
```

Вариант B (cmd):

```bat
build_exe.bat
```

После сборки появится `image_generator.exe` в корне проекта. Рядом должен лежать `template.jpg` (он также упаковывается в exe, но вы можете заменить файл рядом с exe, если нужно обновить шаблон без пересборки).

Использование

- Выберите файл данных (XLSX/CSV).
- Укажите папку вывода (по умолчанию создастся `output` рядом со скриптом).
- При необходимости загрузите/сохраните JSON-конфиг с полями и координатами.
- Нажмите «Старт» для генерации изображений по шаблону.

Конфиг (пример)

```json
{
  "template": "template.jpg",
  "output_dir": "output",
  "fields": [
    {"name": "Name", "x": 100, "y": 100, "font_size": 48, "color": "#000000", "anchor": "la"}
  ],
  "font": {"ttf_path": "C:/Windows/Fonts/arial.ttf"},
  "filename_pattern": "image_{row_index:04d}.jpg"
}
```

Примечания

- Для XLSX используется `openpyxl`, для XLS — `xlrd`, для CSV — `pandas`.
- Параметр `anchor` повторяет логику Pillow (`ImageDraw.text`, docs Pillow).


