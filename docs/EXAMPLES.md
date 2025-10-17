# Примеры использования Image Generator

## Пример 1: Простая генерация с одним полем

### Подготовка данных

Создайте Excel файл `products.xlsx`:

| Артикул | Название |
|---------|----------|
| ABC123  | Товар 1  |
| DEF456  | Товар 2  |
| GHI789  | Товар 3  |

### Конфигурация

```json
{
  "template": "template.jpg",
  "output_dir": "output",
  "fields": [
    {
      "name": "Артикул",
      "x": 100,
      "y": 100,
      "font_size": 48,
      "color": "#000000",
      "anchor": "la"
    },
    {
      "name": "Название", 
      "x": 100,
      "y": 150,
      "font_size": 36,
      "color": "#333333",
      "anchor": "la"
    }
  ],
  "filename_pattern": "{article_clean}.jpg"
}
```

### Результат

- `output/abc123.jpg` - изображение с артикулом "ABC123" и названием "Товар 1"
- `output/def456.jpg` - изображение с артикулом "DEF456" и названием "Товар 2"
- `output/ghi789.jpg` - изображение с артикулом "GHI789" и названием "Товар 3"

## Пример 2: Каталог товаров с изображениями

### Подготовка данных

Excel файл `catalog.xlsx`:

| Артикул | Название | Ссылка на фото |
|---------|----------|----------------|
| PH001   | Смартфон | https://example.com/phone1.jpg |
| LT002   | Ноутбук  | https://example.com/laptop1.jpg |

### Конфигурация

```json
{
  "template": "catalog_template.jpg",
  "output_dir": "catalog",
  "fields": [
    {
      "name": "Артикул",
      "x": 0.05,
      "y": 0.85,
      "font_size": 0.04,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#000000",
      "anchor": "la"
    },
    {
      "name": "Название",
      "x": 0.05,
      "y": 0.90,
      "font_size": 0.03,
      "font_ref": "w", 
      "font_units": "rel",
      "color": "#333333",
      "anchor": "la"
    }
  ],
  "image_box": {
    "source_column": "Ссылка на фото",
    "x": 0.05,
    "y": 0.05,
    "width": 0.9,
    "height": 0.75,
    "fit": "contain",
    "remove_bg": true,
    "remove_bg_color": "#FFFFFF",
    "remove_bg_tolerance": 30,
    "auto_crop": true
  },
  "filename_pattern": "{article_clean}.jpg"
}
```

### Результат

- `catalog/ph001.jpg` - товар PH001 с изображением смартфона
- `catalog/lt002.jpg` - товар LT002 с изображением ноутбука

## Пример 3: Многострочные описания

### Подготовка данных

Excel файл `descriptions.xlsx`:

| Артикул | Применимость |
|---------|--------------|
| AUTO01  | Легковые/Грузовые/Мотоциклы/Внедорожники |
| INDUST  | Станки/Оборудование/Инструмент/Запасные части |

### Конфигурация

```json
{
  "template": "template.jpg",
  "output_dir": "output",
  "fields": [
    {
      "name": "Артикул",
      "x": 0.05,
      "y": 0.05,
      "font_size": 0.06,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#000000",
      "anchor": "la"
    }
  ],
  "multiline_fields": [
    {
      "name": "Применимость",
      "x": 0.05,
      "y": 0.15,
      "width": 0.9,
      "height": 0.8,
      "font_size": 0.04,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#000000",
      "anchor": "la",
      "delimiter": "/",
      "max_lines": 8,
      "max_chars": 25,
      "overflow_text": "и др.",
      "show_overflow_text": true,
      "line_spacing": 1.3,
      "title": "Применимость:"
    }
  ],
  "filename_pattern": "{article_clean}.jpg"
}
```

### Результат

Текст будет разбит по символу "/" и размещен в несколько строк:
- Строка 1: "Применимость:"
- Строка 2: "Легковые"
- Строка 3: "Грузовые"  
- Строка 4: "Мотоциклы"
- Строка 5: "Внедорожники"

## Пример 4: Сложная композиция

### Подготовка данных

Excel файл `complex.xlsx`:

| Артикул | Название | Цена | Ссылка на фото | Описание |
|---------|----------|------|----------------|----------|
| PROD001 | Премиум товар | 15000 | https://example.com/prod1.jpg | Высокое качество/Надежность/Гарантия |

### Конфигурация

```json
{
  "template": "premium_template.jpg",
  "output_dir": "premium",
  "fields": [
    {
      "name": "Артикул",
      "x": 0.02,
      "y": 0.02,
      "font_size": 0.03,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#FFFFFF",
      "anchor": "la"
    },
    {
      "name": "Название",
      "x": 0.02,
      "y": 0.85,
      "font_size": 0.04,
      "font_ref": "w",
      "font_units": "rel", 
      "color": "#000000",
      "anchor": "la"
    },
    {
      "name": "Цена",
      "x": 0.02,
      "y": 0.92,
      "font_size": 0.05,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#FF0000",
      "anchor": "la"
    }
  ],
  "multiline_fields": [
    {
      "name": "Описание",
      "x": 0.02,
      "y": 0.95,
      "width": 0.96,
      "height": 0.05,
      "font_size": 0.025,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#666666",
      "anchor": "la",
      "delimiter": "/",
      "max_lines": 3,
      "max_chars": 30,
      "overflow_text": "...",
      "show_overflow_text": true,
      "line_spacing": 1.2
    }
  ],
  "image_box": {
    "source_column": "Ссылка на фото",
    "x": 0.05,
    "y": 0.05,
    "width": 0.9,
    "height": 0.75,
    "fit": "cover",
    "remove_bg": false,
    "auto_crop": false
  },
  "font": {
    "ttf_path": "C:/Windows/Fonts/arialbd.ttf"
  },
  "filename_pattern": "{article_clean}_premium.jpg"
}
```

### Результат

- `premium/prod001_premium.jpg` - премиум карточка товара с:
  - Артикулом в верхнем левом углу (белый текст)
  - Изображением товара (заполняет 90% области)
  - Названием внизу слева
  - Ценой красным цветом под названием
  - Описанием в несколько строк в самом низу

## Пример 5: Использование редактора зон

### Пошаговая настройка

1. **Запустите приложение:**
   ```bash
   python image_generator.py
   ```

2. **Откройте редактор зон:**
   - Нажмите кнопку "Редактор зон"

3. **Настройте зону для артикула:**
   - Выберите режим "Артикул"
   - Укажите имя поля: "Артикул"
   - Установите размер шрифта: 0.05 (относительно ширины)
   - Нарисуйте прямоугольник в нужном месте шаблона
   - Нажмите "Сохранить"

4. **Настройте зону для изображения:**
   - Переключитесь в режим "Картинка"
   - Укажите колонку: "Ссылка на фото"
   - Нарисуйте область для изображения
   - Включите "Убирать белый фон"
   - Нажмите "Сохранить"

5. **Настройте многострочное поле:**
   - Переключитесь в режим "Применимость"
   - Укажите имя поля: "Применимость"
   - Установите размер шрифта: 0.03
   - Нарисуйте область для текста
   - Нажмите "Сохранить"

6. **Экспортируйте конфигурацию:**
   - Нажмите "Сохранить в файл..."
   - Выберите место сохранения

## Пример 6: Автоматизация через скрипт

### Python скрипт для автоматизации

```python
import json
import pandas as pd
from image_generator import ImageGeneratorApp, DEFAULT_CONFIG
import tkinter as tk

# Загрузка конфигурации
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Загрузка данных
df = pd.read_excel('data.xlsx')

# Создание приложения (без GUI)
root = tk.Tk()
root.withdraw()  # Скрыть главное окно

app = ImageGeneratorApp(root)
app.config = config
app.input_path = 'data.xlsx'
app.output_dir = 'output'

# Запуск обработки
app._process()

print("Генерация завершена!")
```

## Пример 7: Обработка больших объемов данных

### Оптимизация для больших файлов

```json
{
  "template": "template.jpg",
  "output_dir": "batch_output",
  "fields": [
    {
      "name": "Артикул",
      "x": 0.05,
      "y": 0.05,
      "font_size": 0.04,
      "font_ref": "w",
      "font_units": "rel",
      "color": "#000000",
      "anchor": "la"
    }
  ],
  "image_box": {
    "source_column": "Фото",
    "x": 0.05,
    "y": 0.15,
    "width": 0.9,
    "height": 0.8,
    "fit": "contain",
    "remove_bg": false,
    "auto_crop": false
  },
  "font": {
    "ttf_path": null
  },
  "filename_pattern": "batch_{row_index:06d}.jpg"
}
```

### Результат для 10000 записей

- `batch_output/batch_000001.jpg`
- `batch_output/batch_000002.jpg`
- ...
- `batch_output/batch_010000.jpg`

## Советы по оптимизации

### Производительность

1. **Отключите удаление фона** для быстрой обработки
2. **Используйте системные шрифты** вместо загрузки TTF
3. **Ограничьте размер изображений** в image_box
4. **Обрабатывайте данные порциями** по 1000 записей

### Качество

1. **Используйте высокое разрешение** шаблона (300 DPI)
2. **Настройте точные координаты** через редактор зон
3. **Проверяйте результат** на нескольких записях
4. **Сохраняйте конфигурации** для разных типов продукции

### Отладка

1. **Включите подробное логирование** в процессе обработки
2. **Проверяйте URL изображений** на доступность
3. **Тестируйте на малых выборках** перед массовой обработкой
4. **Сохраняйте промежуточные результаты** для анализа
