# Конфигурация Image Generator

## Структура конфигурационного файла

Конфигурация хранится в JSON формате и содержит настройки для генерации изображений.

### Основные секции

```json
{
  "template": "template.jpg",
  "output_dir": "output",
  "fields": [...],
  "multiline_fields": [...],
  "image_box": {...},
  "font": {...},
  "filename_pattern": "{article_clean}.jpg"
}
```

## Описание параметров

### Общие настройки

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `template` | string | Путь к файлу шаблона | "template.jpg" |
| `output_dir` | string | Папка для сохранения результатов | "output" |
| `filename_pattern` | string | Шаблон имени файла | "{article_clean}.jpg" |

### Поля текста (fields)

Массив объектов для настройки текстовых полей:

```json
{
  "name": "Артикул",
  "x": 0.58,
  "y": 0.12,
  "width": 0.4,
  "height": 0.07,
  "font_size": 0.070,
  "font_ref": "w",
  "font_units": "rel",
  "color": "#000000",
  "anchor": "la"
}
```

#### Параметры полей

| Параметр | Тип | Описание | Возможные значения |
|----------|-----|----------|-------------------|
| `name` | string | Название колонки в данных | Любое |
| `x` | number | X координата (0-1 или пиксели) | 0-1 или >0 |
| `y` | number | Y координата (0-1 или пиксели) | 0-1 или >0 |
| `width` | number | Ширина поля (0-1 или пиксели) | 0-1 или >0 |
| `height` | number | Высота поля (0-1 или пиксели) | 0-1 или >0 |
| `font_size` | number | Размер шрифта | 0-1 (относительно) или >0 (пиксели) |
| `font_ref` | string | Базовая размерность для шрифта | "w" (ширина), "h" (высота) |
| `font_units` | string | Единицы измерения шрифта | "rel" (относительно), "px" (пиксели) |
| `color` | string | Цвет текста | HEX формат (#000000) |
| `anchor` | string | Якорь текста | "la", "mm", "ra", "lt", "mt", "rt", "lb", "mb", "rb" |

### Многострочные поля (multiline_fields)

Специальные поля для длинного текста с автоматическим переносом:

```json
{
  "name": "Применимость по КК",
  "x": 0.62,
  "y": 0.42,
  "width": 0.32,
  "height": 0.35,
  "font_size": 0.050,
  "font_ref": "w",
  "font_units": "rel",
  "color": "#000000",
  "anchor": "la",
  "delimiter": "/",
  "max_lines": 6,
  "max_chars": 20,
  "overflow_text": "и т.д.",
  "show_overflow_text": true,
  "line_spacing": 1.25,
  "title": "Применимость:"
}
```

#### Дополнительные параметры многострочных полей

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `delimiter` | string | Разделитель для разбивки текста | "/" |
| `max_lines` | number | Максимальное количество строк | 6 |
| `max_chars` | number | Максимальная длина строки | 20 |
| `overflow_text` | string | Текст при переполнении | "и т.д." |
| `show_overflow_text` | boolean | Показывать текст переполнения | true |
| `line_spacing` | number | Межстрочный интервал | 1.25 |
| `title` | string | Заголовок поля | "Применимость:" |

### Блок изображений (image_box)

Настройки для вставки изображений по URL:

```json
{
  "source_column": "Ссылка на фото",
  "x": 0.05,
  "y": 0.28,
  "width": 0.58,
  "height": 0.52,
  "fit": "contain",
  "remove_bg": true,
  "remove_bg_color": "#FFFFFF",
  "remove_bg_tolerance": 20,
  "auto_crop": true
}
```

#### Параметры блока изображений

| Параметр | Тип | Описание | Возможные значения |
|----------|-----|----------|-------------------|
| `source_column` | string | Название колонки с URL | Любое |
| `x` | number | X координата (0-1 или пиксели) | 0-1 или >0 |
| `y` | number | Y координата (0-1 или пиксели) | 0-1 или >0 |
| `width` | number | Ширина блока | 0-1 или >0 |
| `height` | number | Высота блока | 0-1 или >0 |
| `fit` | string | Способ подгонки изображения | "contain", "cover" |
| `remove_bg` | boolean | Удалять белый фон | true/false |
| `remove_bg_color` | string | Цвет фона для удаления | HEX формат |
| `remove_bg_tolerance` | number | Допуск для удаления фона | 0-255 |
| `auto_crop` | boolean | Автообрезка пустых областей | true/false |

### Настройки шрифта (font)

```json
{
  "ttf_path": "C:/Windows/Fonts/arial.ttf"
}
```

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `ttf_path` | string | Путь к TTF файлу шрифта | null (системный) |

## Система координат

### Относительные координаты (0-1)

- `0.0` - левый/верхний край изображения
- `1.0` - правый/нижний край изображения
- `0.5` - центр изображения

Пример: `"x": 0.58, "y": 0.12` означает 58% от ширины и 12% от высоты

### Абсолютные координаты (пиксели)

Любые значения больше 1.0 интерпретируются как пиксели.

Пример: `"x": 100, "y": 50` означает 100 пикселей от левого края и 50 от верхнего

## Якоря текста (anchor)

Определяют точку привязки текста:

- `la` - левый верхний угол
- `ma` - средний верхний угол  
- `ra` - правый верхний угол
- `lm` - левый центр
- `mm` - центр (по умолчанию)
- `rm` - правый центр
- `lb` - левый нижний угол
- `mb` - средний нижний угол
- `rb` - правый нижний угол

## Шаблоны имен файлов

В `filename_pattern` можно использовать:

- `{article_clean}` - артикул, очищенный от спецсимволов
- `{row_index}` - номер строки в данных

Примеры:
- `"{article_clean}.jpg"` → `abc123.jpg`
- `"image_{row_index:04d}.jpg"` → `image_0001.jpg`

## Примеры конфигураций

### Простая конфигурация

```json
{
  "template": "template.jpg",
  "output_dir": "output",
  "fields": [
    {
      "name": "Название",
      "x": 100,
      "y": 100,
      "font_size": 48,
      "color": "#000000",
      "anchor": "la"
    }
  ],
  "filename_pattern": "image_{row_index:04d}.jpg"
}
```

### Продвинутая конфигурация

```json
{
  "template": "template.jpg",
  "output_dir": "output",
  "fields": [
    {
      "name": "Артикул",
      "x": 0.58,
      "y": 0.12,
      "width": 0.4,
      "height": 0.07,
      "font_size": 0.070,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#000000",
      "anchor": "la"
    }
  ],
  "multiline_fields": [
    {
      "name": "Применимость по КК",
      "x": 0.62,
      "y": 0.42,
      "width": 0.32,
      "height": 0.35,
      "font_size": 0.050,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#000000",
      "anchor": "la",
      "delimiter": "/",
      "max_lines": 6,
      "max_chars": 20,
      "overflow_text": "и т.д.",
      "line_spacing": 1.25,
      "title": "Применимость:"
    }
  ],
  "image_box": {
    "source_column": "Ссылка на фото",
    "x": 0.05,
    "y": 0.28,
    "width": 0.58,
    "height": 0.52,
    "fit": "contain",
    "remove_bg": true,
    "remove_bg_color": "#FFFFFF",
    "remove_bg_tolerance": 20,
    "auto_crop": true
  },
  "font": {
    "ttf_path": "C:/Windows/Fonts/arial.ttf"
  },
  "filename_pattern": "{article_clean}.jpg"
}
```
