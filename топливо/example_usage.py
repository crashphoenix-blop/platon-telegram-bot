#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования анализатора расхода топлива
"""

from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import os

def example_usage():
    """Пример использования программы"""
    
    # Создаем анализатор
    analyzer = FuelConsumptionAnalyzer()
    
    # Пути к файлам (замените на реальные пути)
    krassula_file = "топливо/15.10.2025 11_24_18 Отчёт о транзакциях.xlsx"
    glonass_file = "топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx"
    
    # Проверяем существование файлов
    if not os.path.exists(krassula_file):
        print(f"Файл Крассулы не найден: {krassula_file}")
        return
    
    if not os.path.exists(glonass_file):
        print(f"Файл ГЛОНАСС не найден: {glonass_file}")
        return
    
    try:
        # Загружаем данные
        print("Загружаем данные Крассулы...")
        if not analyzer.load_krassula_data(krassula_file):
            print("Ошибка загрузки данных Крассулы!")
            return
        
        print("Загружаем данные ГЛОНАСС...")
        if not analyzer.load_glonass_data(glonass_file):
            print("Ошибка загрузки данных ГЛОНАСС!")
            return
        
        # Настраиваем соответствие карт и автомобилей
        # ВАЖНО: Замените на реальные данные!
        card_mapping = {
            "0249": "497",  # Пример: карта 0249 -> автомобиль 497
            "1234": "203",  # Пример: карта 1234 -> автомобиль 203
            # Добавьте другие соответствия...
        }
        
        analyzer.load_card_mapping(card_mapping)
        
        # Выполняем анализ
        print("Сопоставляем заправки...")
        analyzer.match_refuels()
        
        print("Рассчитываем расход топлива...")
        consumption_results = analyzer.calculate_fuel_consumption()
        
        # Создаем отчет
        output_file = "отчет_расход_топлива_пример.xlsx"
        print(f"Создаем отчет: {output_file}")
        
        if analyzer.generate_excel_report(output_file):
            print("Отчет успешно создан!")
        else:
            print("Ошибка создания отчета!")
            return
        
        # Показываем уведомления
        analyzer.print_notifications()
        
        # Показываем результаты
        print("\n=== РЕЗУЛЬТАТЫ ===")
        for vehicle, refuels in analyzer.results.items():
            print(f"\nАвтомобиль {vehicle}:")
            for refuel in refuels[:3]:  # Показываем первые 3 заправки
                print(f"  {refuel['date']}: {refuel['krassula_liters']}л, статус: {refuel['status']}")
            if len(refuels) > 3:
                print(f"  ... и еще {len(refuels) - 3} заправок")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    example_usage()
