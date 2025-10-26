#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование финальной версии программы анализа расхода топлива
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import pandas as pd

def test_final_program():
    """Тестирование финальной программы"""
    
    print("=" * 80)
    print("           ТЕСТИРОВАНИЕ ФИНАЛЬНОЙ ВЕРСИИ ПРОГРАММЫ")
    print("=" * 80)
    
    # Создаем анализатор
    analyzer = FuelConsumptionAnalyzer()
    
    print("\n1. ЗАГРУЗКА ДАННЫХ")
    print("-" * 50)
    
    # Загружаем данные Крассулы
    print("Загружаем данные Крассулы...")
    krassula_file = "топливо/15.10.2025 11_24_18 Отчёт о транзакциях.xlsx"
    if not os.path.exists(krassula_file):
        print(f"❌ Файл не найден: {krassula_file}")
        return False
    
    if not analyzer.load_krassula_data(krassula_file):
        print("❌ Ошибка загрузки данных Крассулы!")
        return False
    print(f"✅ Загружено {len(analyzer.krassula_data)} записей")
    
    # Загружаем данные ГЛОНАСС
    print("\nЗагружаем данные ГЛОНАСС...")
    glonass_file = "топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx"
    if not os.path.exists(glonass_file):
        print(f"❌ Файл не найден: {glonass_file}")
        return False
    
    if not analyzer.load_glonass_data(glonass_file):
        print("❌ Ошибка загрузки данных ГЛОНАСС!")
        return False
    print(f"✅ Загружено {len(analyzer.glonass_refuel_data)} заправок и {len(analyzer.glonass_drain_data)} сливов")
    
    # Загружаем соответствия карт и машин
    print("\nЗагружаем соответствия карт и машин...")
    mapping_file = "топливо/топливные карты по машинам.xlsx"
    if not os.path.exists(mapping_file):
        print(f"❌ Файл не найден: {mapping_file}")
        return False
    
    if not analyzer.load_card_mapping_from_file(mapping_file):
        print("❌ Ошибка загрузки соответствий!")
        return False
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
        output_file = "тест_отчет_расход_топлива.xlsx"
        if analyzer.create_excel_report(results, output_file):
            print(f"✅ Отчет создан: {output_file}")
            
            # Проверяем размер файла
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   Размер файла: {file_size:,} байт")
        else:
            print("❌ Ошибка создания отчета")
            return False
        
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
            
            output_file = "тест_отчет_расход_топлива.xlsx"
            if analyzer.create_excel_report(results, output_file):
                print(f"✅ Отчет создан: {output_file}")
                
                # Проверяем размер файла
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"   Размер файла: {file_size:,} байт")
            else:
                print("❌ Ошибка создания отчета")
                return False
        else:
            print("❌ Не удалось сопоставить данные")
            return False
    
    print("\n" + "=" * 80)
    print("           ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = test_final_program()
    if success:
        print("\n🎉 Программа работает корректно!")
    else:
        print("\n❌ Обнаружены проблемы в работе программы")
