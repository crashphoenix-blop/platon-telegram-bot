#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация работы анализатора расхода топлива
"""

from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import os

def demo():
    """Демонстрация работы программы"""
    
    print("=" * 60)
    print("           ДЕМОНСТРАЦИЯ АНАЛИЗАТОРА РАСХОДА ТОПЛИВА")
    print("=" * 60)
    
    # Создаем анализатор
    analyzer = FuelConsumptionAnalyzer()
    
    # Пути к файлам
    krassula_file = "топливо/15.10.2025 11_24_18 Отчёт о транзакциях.xlsx"
    glonass_file = "топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx"
    mapping_file = "топливо/топливные карты по машинам.xlsx"
    
    print("1. ЗАГРУЗКА ДАННЫХ")
    print("-" * 30)
    
    # Загружаем данные Крассулы
    print("Загружаем данные Крассулы...")
    if not analyzer.load_krassula_data(krassula_file):
        print("❌ Ошибка загрузки данных Крассулы!")
        return
    print(f"✅ Загружено {len(analyzer.krassula_data)} записей")
    
    # Загружаем данные ГЛОНАСС
    print("Загружаем данные ГЛОНАСС...")
    if not analyzer.load_glonass_data(glonass_file):
        print("❌ Ошибка загрузки данных ГЛОНАСС!")
        return
    print(f"✅ Загружено {len(analyzer.glonass_refuel_data)} заправок и {len(analyzer.glonass_drain_data)} сливов")
    
    # Показываем статистику по автомобилям
    if not analyzer.glonass_refuel_data.empty and 'vehicle_number' in analyzer.glonass_refuel_data.columns:
        vehicles = analyzer.glonass_refuel_data['vehicle_number'].dropna().unique()
        print(f"✅ Найдено {len(vehicles)} автомобилей: {list(vehicles)[:10]}")
    else:
        print("❌ Нет данных об автомобилях в ГЛОНАСС")
        vehicles = []
    
    # Загружаем соответствия карт и машин
    print("Загружаем соответствия карт и машин...")
    if not analyzer.load_card_mapping_from_file(mapping_file):
        print("❌ Ошибка загрузки соответствий!")
        return
    print(f"✅ Загружено {len(analyzer.card_to_vehicle_mapping)} соответствий")
    
    # Показываем статистику по картам
    card_numbers = set()
    for card_full in analyzer.krassula_data['Номер карты'].dropna():
        card_num = analyzer._extract_card_number(str(card_full))
        if card_num:
            card_numbers.add(card_num)
    print(f"✅ Найдено {len(card_numbers)} уникальных карт в данных Крассулы")
    
    print("\n2. СООТВЕТСТВИЯ КАРТ И МАШИН")
    print("-" * 30)
    print("   Примеры соответствий:")
    for i, (card, vehicle) in enumerate(list(analyzer.card_to_vehicle_mapping.items())[:10]):
        print(f"     Карта {card} -> Машина {vehicle}")
    if len(analyzer.card_to_vehicle_mapping) > 10:
        print(f"     ... и еще {len(analyzer.card_to_vehicle_mapping) - 10} соответствий")
    
    print("\n3. АНАЛИЗ ДАННЫХ")
    print("-" * 30)
    
    # Сопоставляем заправки
    print("Сопоставляем заправки...")
    results = analyzer.match_refuels()
    
    total_refuels = sum(len(refuels) for refuels in results.values())
    matched_refuels = sum(
        len([r for r in refuels if r['status'] == 'matched'])
        for refuels in results.values()
    )
    
    print(f"✅ Обработано {len(results)} автомобилей")
    print(f"✅ Всего заправок: {total_refuels}")
    print(f"✅ Сопоставлено: {matched_refuels}")
    print(f"✅ Процент сопоставления: {(matched_refuels/total_refuels*100):.1f}%" if total_refuels > 0 else "0%")
    
    # Показываем уведомления
    print(f"\n4. УВЕДОМЛЕНИЯ ({len(analyzer.notifications)})")
    print("-" * 30)
    
    if analyzer.notifications:
        for i, notification in enumerate(analyzer.notifications[:5]):
            print(f"   {i+1}. {notification['type'].upper()}: {notification['message']}")
        if len(analyzer.notifications) > 5:
            print(f"   ... и еще {len(analyzer.notifications) - 5} уведомлений")
    else:
        print("   Уведомлений нет")
    
    # Создаем отчет
    print("\n5. СОЗДАНИЕ ОТЧЕТА")
    print("-" * 30)
    
    output_file = "демо_отчет_расход_топлива.xlsx"
    if analyzer.generate_excel_report(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ Отчет создан: {output_file}")
        print(f"   Размер файла: {file_size:,} байт")
    else:
        print("❌ Ошибка создания отчета!")
        return
    
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)
    print(f"Отчет сохранен в файле: {output_file}")
    print("Откройте файл в Excel для просмотра результатов")

if __name__ == "__main__":
    demo()
