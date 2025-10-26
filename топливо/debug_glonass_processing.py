#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладка обработки данных ГЛОНАСС
"""

import pandas as pd
import re
from fuel_consumption_analyzer import FuelConsumptionAnalyzer

def debug_glonass_processing():
    """Отладка обработки данных ГЛОНАСС"""
    
    analyzer = FuelConsumptionAnalyzer()
    
    # Загружаем данные
    print("Загружаем данные ГЛОНАСС...")
    if not analyzer.load_glonass_data("топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx"):
        print("❌ Ошибка загрузки данных ГЛОНАСС!")
        return
    
    print(f"✅ Загружено {len(analyzer.glonass_refuel_data)} заправок")
    
    if analyzer.glonass_refuel_data.empty:
        print("❌ Данные заправок пусты!")
        return
    
    print("\n=== СТРУКТУРА ДАННЫХ ===")
    print(f"Колонки: {list(analyzer.glonass_refuel_data.columns)}")
    print(f"Размер: {analyzer.glonass_refuel_data.shape}")
    
    print("\n=== ПЕРВЫЕ 10 ЗАПИСЕЙ ===")
    for i, (_, row) in enumerate(analyzer.glonass_refuel_data.head(10).iterrows()):
        print(f"{i+1:2d}. {row['Группировка']:<30} | {row['Время']:<20} | {row['Заправлено']}")
    
    print("\n=== УНИКАЛЬНЫЕ АВТОМОБИЛИ ===")
    if 'vehicle_number' in analyzer.glonass_refuel_data.columns:
        vehicles = analyzer.glonass_refuel_data['vehicle_number'].dropna().unique()
        print(f"Найдено {len(vehicles)} автомобилей: {list(vehicles)}")
    else:
        print("Колонка 'vehicle_number' не найдена!")
    
    print("\n=== ПРИМЕРЫ ЗАПРАВОК ===")
    if not analyzer.glonass_refuel_data.empty:
        for i, (_, row) in enumerate(analyzer.glonass_refuel_data.head(5).iterrows()):
            print(f"{i+1}. Автомобиль: {row.get('vehicle_number', 'N/A')}")
            print(f"   Дата: {row.get('date', 'N/A')}")
            print(f"   Время: {row.get('datetime', 'N/A')}")
            print(f"   Заправлено: {row.get('Заправлено', 'N/A')}")
            print(f"   Пробег: {row.get('Пробег', 'N/A')}")
            print()

if __name__ == "__main__":
    debug_glonass_processing()
