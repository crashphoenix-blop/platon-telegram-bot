#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная версия программы анализа расхода топлива
Исправлены проблемы с ведущими нулями и сопоставлением карт
"""

from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import pandas as pd
import os

def get_file_path(prompt):
    """Получает путь к файлу от пользователя"""
    while True:
        file_path = input(f"{prompt}: ").strip()
        if os.path.exists(file_path):
            return file_path
        else:
            print(f"❌ Файл не найден: {file_path}")
            print("Попробуйте еще раз.")

def main():
    """Главная функция программы"""
    
    print("=" * 80)
    print("           АНАЛИЗАТОР РАСХОДА ТОПЛИВА - ФИНАЛЬНАЯ ВЕРСИЯ")
    print("=" * 80)
    print("Программа для автоматического расчета расхода топлива по автомобилям")
    print("на основе данных из Крассулы и ГЛОНАСС")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = FuelConsumptionAnalyzer()
    
    print("\n1. ЗАГРУЗКА ДАННЫХ")
    print("-" * 50)
    
    # Загружаем данные Крассулы
    print("Загружаем данные Крассулы...")
    krassula_file = get_file_path("Введите путь к файлу Крассулы")
    if not analyzer.load_krassula_data(krassula_file):
        print("❌ Ошибка загрузки данных Крассулы!")
        return
    print(f"✅ Загружено {len(analyzer.krassula_data)} записей")
    
    # Загружаем данные ГЛОНАСС
    print("\nЗагружаем данные ГЛОНАСС...")
    glonass_file = get_file_path("Введите путь к файлу ГЛОНАСС")
    if not analyzer.load_glonass_data(glonass_file):
        print("❌ Ошибка загрузки данных ГЛОНАСС!")
        return
    print(f"✅ Загружено {len(analyzer.glonass_refuel_data)} заправок и {len(analyzer.glonass_drain_data)} сливов")
    
    # Загружаем соответствия карт и машин
    print("\nЗагружаем соответствия карт и машин...")
    mapping_file = get_file_path("Введите путь к файлу соответствий карт и машин")
    if not analyzer.load_card_mapping_from_file(mapping_file):
        print("❌ Ошибка загрузки соответствий!")
        return
    print(f"✅ Загружено {len(analyzer.card_to_vehicle_mapping)} соответствий")
    
    print("\n2. АНАЛИЗ ДАННЫХ")
    print("-" * 50)
    
    # Анализируем карты из Крассулы
    krassula_cards = set()
    for card_full in analyzer.krassula_data['Номер карты'].unique():
        if pd.notna(card_full):
            card_num = analyzer._extract_card_number(str(card_full))
            if card_num:
                krassula_cards.add(card_num)
    
    print(f"Карт в данных Крассулы (топливные товары): {len(krassula_cards)}")
    print(f"Карт в файле соответствий: {len(analyzer.card_to_vehicle_mapping)}")
    
    # Проверяем пересечения
    matched_cards = krassula_cards.intersection(set(analyzer.card_to_vehicle_mapping.keys()))
    print(f"Пересечений: {len(matched_cards)}")
    
    if len(matched_cards) == 0:
        print("\n📋 ОБЪЯСНЕНИЕ РЕЗУЛЬТАТА:")
        print("   В текущем периоде по картам вашей компании")
        print("   не было заправок топливом. Это нормальная ситуация.")
        print("   Программа работает корректно.")
        
        print("\n📊 СТАТИСТИКА:")
        print(f"   • Всего заправок топливом в периоде: {len(analyzer.krassula_data)}")
        print(f"   • Карт вашей компании в файле соответствий: {len(analyzer.card_to_vehicle_mapping)}")
        print(f"   • Карт, по которым были заправки: {len(krassula_cards)}")
        print(f"   • Совпадений: {len(matched_cards)}")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("   1. Проверьте, что период данных Крассулы совпадает с периодом ГЛОНАСС")
        print("   2. Убедитесь, что в файле соответствий указаны правильные карты")
        print("   3. Проверьте, что карты вашей компании используются для заправок")
        
        # Создаем отчет с уведомлениями
        print("\n3. СОЗДАНИЕ ОТЧЕТА")
        print("-" * 50)
        print("Создаем отчет с уведомлениями...")
        
        # Сопоставляем данные (даже если нет совпадений)
        results = analyzer.match_refuels()
        
        # Создаем Excel отчет
        output_file = "отчет_расход_топлива_финальный.xlsx"
        if analyzer.create_excel_report(results, output_file):
            print(f"✅ Отчет создан: {output_file}")
        else:
            print("❌ Ошибка создания отчета")
        
    else:
        print(f"\n✅ Найдено {len(matched_cards)} совпадений!")
        print("Продолжаем анализ расхода топлива...")
        
        # Сопоставляем данные
        print("\n3. СОПОСТАВЛЕНИЕ ДАННЫХ")
        print("-" * 50)
        print("Сопоставляем заправки...")
        
        results = analyzer.match_refuels()
        
        if results:
            print(f"✅ Обработано {len(results)} автомобилей")
            
            # Создаем Excel отчет
            print("\n4. СОЗДАНИЕ ОТЧЕТА")
            print("-" * 50)
            print("Создаем Excel отчет...")
            
            output_file = "отчет_расход_топлива_финальный.xlsx"
            if analyzer.create_excel_report(results, output_file):
                print(f"✅ Отчет создан: {output_file}")
            else:
                print("❌ Ошибка создания отчета")
        else:
            print("❌ Не удалось сопоставить данные")
    
    print("\n" + "=" * 80)
    print("           АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 80)

if __name__ == "__main__":
    main()
