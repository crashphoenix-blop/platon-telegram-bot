#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная демонстрация анализатора расхода топлива
"""

from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import os

def final_demo():
    """Финальная демонстрация работы программы"""
    
    print("=" * 60)
    print("           ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ АНАЛИЗАТОРА РАСХОДА ТОПЛИВА")
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
    
    # Показываем все карты для отладки
    print(f"Все карты: {sorted(card_numbers)}")
    
    print("\n2. АНАЛИЗ СООТВЕТСТВИЙ")
    print("-" * 30)
    
    # Анализируем соответствия
    matched_cards = 0
    matched_vehicles = 0
    
    print("Карты из Крассулы:")
    for card in sorted(card_numbers):
        if card in analyzer.card_to_vehicle_mapping:
            vehicle = analyzer.card_to_vehicle_mapping[card]
            print(f"  ✅ Карта {card} -> Машина {vehicle}")
            matched_cards += 1
            if vehicle in vehicles:
                matched_vehicles += 1
        else:
            print(f"  ❌ Карта {card} -> НЕ НАЙДЕНА в соответствиях")
    
    print(f"\nНайдено соответствий: {matched_cards}/{len(card_numbers)}")
    
    print(f"\nСоответствия:")
    print(f"  Карт найдено в соответствиях: {matched_cards}/{len(card_numbers)}")
    print(f"  Машин найдено в ГЛОНАСС: {matched_vehicles}/{matched_cards}")
    
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
        for i, notification in enumerate(analyzer.notifications[:10]):
            print(f"   {i+1}. {notification['type'].upper()}: {notification['message']}")
        if len(analyzer.notifications) > 10:
            print(f"   ... и еще {len(analyzer.notifications) - 10} уведомлений")
    else:
        print("   Уведомлений нет")
    
    # Создаем отчет
    print("\n5. СОЗДАНИЕ ОТЧЕТА")
    print("-" * 30)
    
    output_file = "финальный_отчет_расход_топлива.xlsx"
    if analyzer.generate_excel_report(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ Отчет создан: {output_file}")
        print(f"   Размер файла: {file_size:,} байт")
    else:
        print("❌ Ошибка создания отчета!")
        return
    
    print("\n" + "=" * 60)
    print("ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)
    print(f"Отчет сохранен в файле: {output_file}")
    print("Откройте файл в Excel для просмотра результатов")
    
    # Показываем рекомендации
    print("\n6. РЕКОМЕНДАЦИИ")
    print("-" * 30)
    
    if matched_cards == 0:
        print("❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: Ни одна карта из Крассулы не найдена в соответствиях!")
        print("   Проверьте файл соответствий карт и машин")
    elif matched_vehicles == 0:
        print("❌ ПРОБЛЕМА: Карты найдены в соответствиях, но машины не найдены в ГЛОНАСС!")
        print("   Проверьте номера машин в файле соответствий")
    elif matched_refuels == 0:
        print("❌ ПРОБЛЕМА: Машины найдены, но заправки не сопоставлены!")
        print("   Проверьте даты и время заправок")
    else:
        print("✅ Программа работает корректно!")
        print(f"   Успешно сопоставлено {matched_refuels} заправок")

if __name__ == "__main__":
    final_demo()
