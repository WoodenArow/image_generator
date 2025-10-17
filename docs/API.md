# API Documentation - Image Generator

## Основные классы и функции

### ImageGeneratorApp

Главный класс приложения с GUI интерфейсом.

#### Конструктор

```python
def __init__(self, root: tk.Tk) -> None
```

**Параметры:**
- `root` - корневое окно tkinter

**Инициализирует:**
- GUI интерфейс
- Конфигурацию по умолчанию
- Пути к входным и выходным файлам

#### Основные методы

##### _build_ui()

```python
def _build_ui(self) -> None
```

Создает пользовательский интерфейс:
- Поля для выбора входного файла и папки вывода
- Кнопки управления (Загрузить конфиг, Сохранить конфиг, Старт, Редактор зон)
- Прогресс-бар
- Область логов

##### _choose_input()

```python
def _choose_input(self) -> None
```

Открывает диалог выбора файла данных (XLSX/CSV).

##### _choose_output()

```python
def _choose_output(self) -> None
```

Открывает диалог выбора папки для сохранения результатов.

##### _load_config()

```python
def _load_config(self) -> None
```

Загружает конфигурацию из JSON файла с глубоким слиянием с настройками по умолчанию.

##### _save_config()

```python
def _save_config(self) -> None
```

Сохраняет текущую конфигурацию в JSON файл.

##### _start()

```python
def _start(self) -> None
```

Запускает процесс генерации изображений в отдельном потоке.

##### _process()

```python
def _process(self) -> None
```

Основная функция обработки данных и генерации изображений.

**Процесс работы:**
1. Загрузка данных из файла (CSV/Excel)
2. Подготовка конфигурации шрифтов
3. Обработка каждой строки данных:
   - Загрузка шаблона
   - Вставка изображений по URL
   - Добавление текстовых полей
   - Обработка многострочных полей
   - Сохранение результата

##### _open_zone_editor()

```python
def _open_zone_editor(self) -> None
```

Открывает редактор зон для настройки полей на шаблоне.

### ZoneEditor

Класс для визуального редактирования зон на шаблоне.

#### Конструктор

```python
def __init__(self, master: tk.Misc, config: Dict[str, Any], columns: Optional[List[str]] = None)
```

**Параметры:**
- `master` - родительское окно
- `config` - ссылка на конфигурацию
- `columns` - список доступных колонок из данных

#### Основные методы

##### _update_scrollregion()

```python
def _update_scrollregion(self)
```

Обновляет область прокрутки и масштабирование изображения.

##### canvas_to_img()

```python
def canvas_to_img(self, x, y)
```

Конвертирует координаты canvas в координаты изображения.

##### img_to_canvas()

```python
def img_to_canvas(self, x, y)
```

Конвертирует координаты изображения в координаты canvas.

##### _redraw_overlays()

```python
def _redraw_overlays(self)
```

Перерисовывает наложения (точки и прямоугольники).

##### on_down(), on_drag(), on_up()

```python
def on_down(self, e)
def on_drag(self, e)  
def on_up(self, e)
```

Обработчики событий мыши для рисования зон.

##### on_wheel()

```python
def on_wheel(self, e)
```

Обработчик колеса мыши для масштабирования.

##### _save_into_config()

```python
def _save_into_config(self)
```

Сохраняет выделенную зону в конфигурацию.

##### _export_config()

```python
def _export_config(self)
```

Экспортирует конфигурацию в файл.

### Вспомогательные функции

#### get_base_dir()

```python
def get_base_dir() -> str
```

Возвращает базовую директорию для ресурсов.

**Логика:**
- В обычном режиме: директория скрипта
- В PyInstaller: sys._MEIPASS или директория exe

#### get_run_dir()

```python
def get_run_dir() -> str
```

Возвращает директорию запуска для файлов вывода.

**Логика:**
- В обычном режиме: директория скрипта
- В PyInstaller: директория exe

### Конфигурация по умолчанию

#### DEFAULT_CONFIG

Словарь с настройками по умолчанию:

```python
DEFAULT_CONFIG = {
    "template": "template.jpg",
    "output_dir": "output",
    "fields": [...],
    "multiline_fields": [...],
    "image_box": {...},
    "font": {...},
    "filename_pattern": "{article_clean}.jpg"
}
```

## Алгоритмы обработки

### Обработка изображений

1. **Загрузка по URL:**
   ```python
   req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
   with urlopen(req, timeout=10) as resp:
       data = resp.read()
   ```

2. **Удаление фона:**
   ```python
   rgba = src_img.convert("RGBA")
   arr = np.array(rgba)
   # Создание маски по цвету и допуску
   mask = (np.abs(r-rt) <= tol) & (np.abs(g-gt) <= tol) & (np.abs(b-bt) <= tol)
   arr[..., 3] = np.where(mask, 0, a)
   ```

3. **Масштабирование:**
   ```python
   scale = max(scale_w, scale_h) if fit == "cover" else min(scale_w, scale_h)
   new_w = max(1, int(src_img.width * scale))
   new_h = max(1, int(src_img.height * scale))
   ```

### Обработка текста

1. **Загрузка шрифтов:**
   ```python
   def load_font(size: int):
       # 1) Проверка явного пути
       # 2) Поиск системных шрифтов Windows
       # 3) Fallback на DejaVu или системный
   ```

2. **Многострочный текст:**
   ```python
   parts = [p.strip() for p in str(text_value).split(delimiter) if p.strip()]
   # Очистка от годов и лишних символов
   # Ограничение по количеству строк и символов
   ```

3. **Перенос по словам:**
   ```python
   words = text.split()
   for w in words:
       test = (line + " " + w).strip()
       tw, th = font.getbbox(test)[2:4]
       if tw > fw and line:
           # Перенос строки
   ```

### Обработка данных

1. **Загрузка файлов:**
   ```python
   if path_lower.endswith(".csv"):
       df = pd.read_csv(self.input_path)
   else:
       df = pd.read_excel(self.input_path)
   ```

2. **Именование файлов:**
   ```python
   article_clean = re.sub(r"[^0-9A-Za-z]+", "", str(article_value)).lower()
   out_name = filename_pattern.replace("{article_clean}", article_clean)
   ```

## Обработка ошибок

### Исключения

- `FileNotFoundError` - не найден шаблон
- `URLError` - ошибка загрузки изображения по URL
- `Exception` - общие ошибки обработки

### Логирование

Все операции логируются через `_log()` метод:
```python
def _log(self, msg: str) -> None:
    self.log_text.insert(tk.END, msg + "\n")
    self.log_text.see(tk.END)
    self.root.update_idletasks()
```

## Потокобезопасность

- Обработка данных выполняется в отдельном потоке
- GUI остается отзывчивым во время генерации
- Обновление прогресса через tkinter переменные

## Расширяемость

### Добавление новых типов полей

1. Добавить новый тип в `DEFAULT_CONFIG`
2. Реализовать обработку в `_process()`
3. Добавить поддержку в `ZoneEditor`

### Кастомные обработчики изображений

```python
def custom_image_processor(src_img, config):
    # Ваша логика обработки
    return processed_img
```

### Новые форматы данных

```python
def load_custom_format(file_path):
    # Ваша логика загрузки
    return pandas.DataFrame
```
