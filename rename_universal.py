#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный скрипт для обработки подписки с vless/reality конфигами.

Использование:
    python rename_universal.py <источник> <файл_результата>

<источник> может быть:
    - путь к локальному файлу (например txt.txt)
    - URL (например https://sub.vlessfo.ru/vlessforu/working_configs.txt)

Пример:
    python rename_universal.py txt.txt result.txt
    python rename_universal.py https://sub.vlessfo.ru/vlessforu/working_configs.txt result.txt
"""

import sys
import re
import urllib.request
import urllib.parse

HEADER = """#profile-title: КуклаVPN
#announce: Вся информация по кнопке «Поддержка»
#subscription-userinfo: expire=151400523600
#support-url: https://t.me/kyklavpn
"""

# Регулярка для поиска "LTE" или "5G" в начале имени (после отсечения эмодзи/спецсимволов)
NAME_PATTERN = re.compile(r'^[^A-Za-z0-9]*(LTE|5G)', re.IGNORECASE)


def load_source(source: str) -> str:
    """Загружает содержимое из URL или локального файла."""
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    else:
        with open(source, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def process(text: str) -> str:
    lines = text.splitlines()
    result_lines = []
    counter = 1

    for line in lines:
        stripped = line.strip()

        # пропускаем пустые строки и старые строки шапки (начинаются с #profile-title и т.п.)
        if not stripped:
            continue
        if stripped.startswith("#profile-title") or \
           stripped.startswith("#announce") or \
           stripped.startswith("#subscription-userinfo") or \
           stripped.startswith("#support-url"):
            continue

        # Проверяем, есть ли в строке протокол-ссылка с фрагментом (#имя) в конце
        if "#" in stripped and "://" in stripped:
            base, _, fragment = stripped.rpartition("#")
            decoded_name = urllib.parse.unquote(fragment)

            if NAME_PATTERN.match(decoded_name):
                new_name = f"🌍 • Универсальный • {counter}"
                counter += 1
                new_fragment = urllib.parse.quote(new_name)
                new_line = f"{base}#{new_fragment}"
                result_lines.append(new_line)
                continue

        # если не подошло под условие — оставляем строку как есть
        result_lines.append(stripped)

    body = "\n".join(result_lines)
    return HEADER + "\n" + body + "\n"


def main():
    if len(sys.argv) != 3:
        print("Использование: python rename_universal.py <источник> <файл_результата>")
        sys.exit(1)

    source = sys.argv[1]
    output_path = sys.argv[2]

    text = load_source(source)
    result = process(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Готово! Результат сохранён в {output_path}")


if __name__ == "__main__":
    main()