#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для запуска обработки данных системы Платон
"""

import os
import sys
import glob
from platon_processor import PlatonProcessor

def main():
    """Основная функция для запуска обработки"""
    print("=== Обработка данных системы Платон ===")
    
    # Ищем CSV файлы в текущей директории
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("❌ CSV файлы не найдены в текущей директории")
        print("Поместите CSV файлы в папку с программой и запустите снова")
        return 1
    
    print(f"Найдено CSV файлов: {len(csv_files)}")
    for file in csv_files:
        print(f"  - {file}")
    
    # Создаем процессор
    processor = PlatonProcessor()
    
    # Обрабатываем каждый CSV файл
    for csv_file in csv_files:
        print(f"\n📁 Обрабатываю файл: {csv_file}")
        if not processor.read_csv_file(csv_file):
            print(f"❌ Не удалось прочитать файл {csv_file}")
            continue
    
    if not processor.data:
        print("❌ Не удалось загрузить данные из файлов")
        return 1
    
    # Обрабатываем данные
    print("\n🔄 Обрабатываю данные...")
    processor.process_data()
    
    # Создаем Excel отчет
    output_file = "отчет_платон.xlsx"
    print(f"\n📊 Создаю Excel отчет: {output_file}")
    
    if processor.create_excel_report(output_file):
        print(f"\n✅ Отчет успешно создан: {output_file}")
        print("\n📋 Отчет содержит следующие листы:")
        print("  - Общая сводка")
        print("  - По транспортным средствам")
        print("  - По дорогам")
        print("  - По датам")
        print("  - Детальные данные")
        return 0
    else:
        print("\n❌ Ошибка при создании отчета")
        return 1

if __name__ == "__main__":
    sys.exit(main())

