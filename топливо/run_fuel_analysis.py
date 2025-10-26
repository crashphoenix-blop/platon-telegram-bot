#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной интерфейс для запуска анализа расхода топлива
"""

import os
import sys
from pathlib import Path
from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import config

def get_file_path(prompt: str, file_type: str = "Excel") -> str:
    """Получает путь к файлу от пользователя"""
    while True:
        file_path = input(f"{prompt}: ").strip()
        
        if not file_path:
            print("Путь не может быть пустым!")
            continue
            
        if not os.path.exists(file_path):
            print(f"Файл не найден: {file_path}")
            continue
            
        if not file_path.lower().endswith(('.xlsx', '.xls')):
            print(f"Файл должен быть в формате {file_type} (.xlsx или .xls)")
            continue
            
        return file_path

def get_card_mapping() -> dict:
    """Получает соответствие карт и автомобилей от пользователя"""
    print("\n=== НАСТРОЙКА СООТВЕТСТВИЯ КАРТ И АВТОМОБИЛЕЙ ===")
    print("Введите соответствие в формате: номер_карты:номер_автомобиля")
    print("Например: 0249:497")
    print("Для завершения ввода введите пустую строку")
    print()
    
    mapping = {}
    
    while True:
        entry = input("Карта:Автомобиль: ").strip()
        
        if not entry:
            break
            
        if ':' not in entry:
            print("Неверный формат! Используйте: номер_карты:номер_автомобиля")
            continue
            
        try:
            card, vehicle = entry.split(':', 1)
            mapping[card.strip()] = vehicle.strip()
            print(f"Добавлено: карта {card.strip()} -> автомобиль {vehicle.strip()}")
        except ValueError:
            print("Ошибка при разборе ввода!")
            continue
    
    return mapping

def main():
    """Основная функция программы"""
    print("=" * 60)
    print("           АНАЛИЗАТОР РАСХОДА ТОПЛИВА")
    print("=" * 60)
    print("Программа для сопоставления данных Крассулы и ГЛОНАСС")
    print("и автоматического расчета расхода топлива")
    print()
    
    # Создаем анализатор
    analyzer = FuelConsumptionAnalyzer()
    
    try:
        # Получаем пути к файлам
        print("1. ЗАГРУЗКА ДАННЫХ")
        print("-" * 30)
        
        krassula_file = get_file_path(
            "Введите путь к файлу Крассулы (топливные карты)"
        )
        
        glonass_file = get_file_path(
            "Введите путь к файлу ГЛОНАСС (заправки и сливы)"
        )
        
        mapping_file = get_file_path(
            "Введите путь к файлу соответствий карт и машин"
        )
        
        # Загружаем данные
        print("\nЗагружаем данные...")
        
        if not analyzer.load_krassula_data(krassula_file):
            print("ОШИБКА: Не удалось загрузить данные Крассулы!")
            return
        
        if not analyzer.load_glonass_data(glonass_file):
            print("ОШИБКА: Не удалось загрузить данные ГЛОНАСС!")
            return
        
        # Загружаем соответствие карт и автомобилей
        print("\n2. ЗАГРУЗКА СООТВЕТСТВИЙ")
        print("-" * 30)
        
        if not analyzer.load_card_mapping_from_file(mapping_file):
            print("ОШИБКА: Не удалось загрузить соответствия карт и автомобилей!")
            return
        
        print(f"✅ Загружено {len(analyzer.card_to_vehicle_mapping)} соответствий")
        print("   Примеры соответствий:")
        for i, (card, vehicle) in enumerate(list(analyzer.card_to_vehicle_mapping.items())[:5]):
            print(f"     Карта {card} -> Машина {vehicle}")
        if len(analyzer.card_to_vehicle_mapping) > 5:
            print(f"     ... и еще {len(analyzer.card_to_vehicle_mapping) - 5} соответствий")
        
        # Выполняем анализ
        print("\n3. АНАЛИЗ ДАННЫХ")
        print("-" * 30)
        
        print("Сопоставляем заправки...")
        analyzer.match_refuels()
        
        print("Рассчитываем расход топлива...")
        consumption_results = analyzer.calculate_fuel_consumption()
        
        # Генерируем отчет
        print("\n4. СОЗДАНИЕ ОТЧЕТА")
        print("-" * 30)
        
        output_file = "отчет_расход_топлива.xlsx"
        if analyzer.generate_excel_report(output_file):
            print(f"Отчет успешно создан: {output_file}")
        else:
            print("ОШИБКА: Не удалось создать отчет!")
            return
        
        # Показываем уведомления
        print("\n5. УВЕДОМЛЕНИЯ")
        print("-" * 30)
        analyzer.print_notifications()
        
        # Показываем статистику
        print("\n6. СТАТИСТИКА")
        print("-" * 30)
        
        total_vehicles = len(analyzer.results)
        total_refuels = sum(len(refuels) for refuels in analyzer.results.values())
        matched_refuels = sum(
            len([r for r in refuels if r['status'] == 'matched'])
            for refuels in analyzer.results.values()
        )
        
        print(f"Обработано автомобилей: {total_vehicles}")
        print(f"Всего заправок: {total_refuels}")
        print(f"Сопоставлено заправок: {matched_refuels}")
        print(f"Процент сопоставления: {(matched_refuels/total_refuels*100):.1f}%" if total_refuels > 0 else "0%")
        
        print("\n" + "=" * 60)
        print("АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
