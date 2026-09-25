#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт отбирает из подписки только vless+reality конфиги,
у которых имя начинается на LTE или 5G (любой оператор),
переименовывает их в "🇪🇺 🌍 • Универсальный • N" и сохраняет
в новый файл с нужной шапкой. Всё остальное отбрасывается.

Использование:
    python rename_universal.py <источник> <файл_результата>
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

# Имя должно начинаться (после эмодзи/спецсимволов) на LTE или 5G
NAME_PATTERN = re.compile(r'^[^A-Za-z0-9]*(LTE|5G)', re.IGNORECASE)


def load_source(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    else:
        with open(source, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def is_reality_vless(link: str) -> bool:
    """Проверяет, что ссылка это vless:// и содержит security=reality"""
    if not link.startswith("vless://"):
        return False
    parsed = urllib.parse.urlparse(link)
    query = urllib.parse.parse_qs(parsed.query)
    security = query.get("security", [""])[0].lower()
    return security == "reality"


def process(text: str) -> str:
    lines = text.splitlines()
    result_lines = []
    counter = 1

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # пропускаем строки шапки исходного файла
        if stripped.startswith("#"):
            continue

        if "#" not in stripped or "://" not in stripped:
            continue

        base, _, fragment = stripped.rpartition("#")

        # проверка: это vless + reality?
        if not is_reality_vless(base):
            continue

        decoded_name = urllib.parse.unquote(fragment)

        # проверка: имя начинается на LTE или 5G?
        if not NAME_PATTERN.match(decoded_name):
            continue

        new_name = f"🇪🇺 🌍 • Универсальный • {counter}"
        counter += 1
        new_fragment = urllib.parse.quote(new_name)
        new_line = f"{base}#{new_fragment}"
        result_lines.append(new_line)

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