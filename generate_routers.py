"""
Генератор роутеров для всех 11 специализаций.
Создает файлы на основе шаблона oupds.py.
"""

# Конфигурация специализаций
SPECIALIZATIONS = [
    ("oupds", "ООУПДС", "🚨"),
    ("ispolniteli", "Исполнительное производство", "📊"),
    ("aliment", "Алименты", "🧑‍🧑‍🧒"),
    ("doznanie", "Дознание", "🎯"),
    ("rozyisk", "Розыск", "⏳"),
    ("prof", "Профподготовка", "📈"),
    ("oko", "ОКО", "📡"),
    ("informatika", "Информатизация", "💻"),
    ("kadry", "Кадры", "👥"),
    ("bezopasnost", "Безопасность", "🔒"),
    ("upravlenie", "Управление", "💼"),
]

# Читаем шаблон
with open("specializations/oupds.py", "r", encoding="utf-8") as f:
    template = f.read()

# Генерируем файлы для остальных специализаций
for spec_id, spec_name, emoji in SPECIALIZATIONS[1:]:  # Пропускаем oupds
    # Заменяем все вхождения
    content = template.replace("oupds", spec_id)
    content = content.replace("OUPDS", spec_id.upper())
    content = content.replace("ООУПДС", spec_name)
    content = content.replace("🚨", emoji)
    content = content.replace("oupds_router", f"{spec_id}_router")
    content = content.replace('"spec_oupds"', f'"spec_{spec_id}"')
    content = content.replace("Выбор специализации OOУПДС", f"Выбор специализации {spec_name}")
    
    # Исправляем комментарий в первой строке
    first_line = f'specializations/{spec_id}.py: Хэндлеры для {spec_name} теста.'
    lines = content.split('\n')
    lines[1] = f'"{first_line}"'
    content = '\n'.join(lines)
    
    # Записываем файл
    with open(f"specializations/{spec_id}.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Создан роутер: {spec_id}.py")

print("\n🎉 Все роутеры созданы успешно!")
