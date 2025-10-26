#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладка извлечения номеров автомобилей
"""

import pandas as pd
import re

def extract_vehicle_number(grouping_text: str) -> str:
    """Тестовая функция извлечения номера автомобиля"""
    if pd.isna(grouping_text):
        return "None"
        
    # Ищем паттерн: буква + цифры + буквы + цифры (например, "т497ес797")
    pattern = r'[а-яё]\d+[а-яё]+\d+'
    match = re.search(pattern, grouping_text.lower())
    
    if match:
        # Извлекаем только цифры после первой буквы
        number_part = match.group()
        numbers = re.findall(r'\d+', number_part)
        if numbers:
            return numbers[0]  # Возвращаем первые цифры (497)
    
    # Если не нашли по старому паттерну, ищем просто цифры
    # Но исключаем даты (4 цифры) и одиночные цифры
    numbers = re.findall(r'\d+', grouping_text)
    if numbers:
        # Исключаем даты (4 цифры) и одиночные цифры
        filtered_numbers = [n for n in numbers if len(n) != 4 and len(n) > 1]
        if filtered_numbers:
            return filtered_numbers[-1]  # Возвращаем последние цифры
    
    return "None"

def main():
    """Тестируем извлечение номеров"""
    
    # Тестовые данные
    test_cases = [
        "Scania т497ес797(406)*",
        "MAN н203ек799*",
        "Mercedes т701ун 797",
        "Scania а258ах797*",
        "Hino А585ТЕ790",
        "Scania в370ау797*",
        "Scania в374ау797*",
        "Scania н089са799*",
        "Scania о646ае799*нп",
        "Scania р378тв777*нп",
        "Scania с093вс797*",
        "Scania с128вс797*нп",
        "Scania с869ар797*нп",
        "Scania с879ах797*нп",
        "Scania у583ем797(977)*",
        "Scania х915ку799*",
        "SITRAK у149оу 797*",
        "SITRAK у210оу 797*",
        "Камаз м436сх799*",
        "Камаз м453сх799*",
        "Камаз с750тр799*нп",
        "МАЗ м756ве797*",
        "МАЗ у048ну797*",
        "FORD о535ус 777",
        "HINO в304ва 250"
    ]
    
    print("=== ТЕСТИРОВАНИЕ ИЗВЛЕЧЕНИЯ НОМЕРОВ АВТОМОБИЛЕЙ ===")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        result = extract_vehicle_number(test_case)
        print(f"{i:2d}. {test_case:<35} -> {result}")
    
    print()
    print("=== ТЕСТИРОВАНИЕ С РЕАЛЬНЫМИ ДАННЫМИ ===")
    print()
    
    # Загружаем реальные данные
    df = pd.read_excel('топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx', sheet_name='Заправки и зарядки батареи')
    
    # Находим уникальные значения группировки с автомобилями
    vehicle_groups = []
    for val in df['Группировка'].unique():
        if any(brand in str(val) for brand in ['Scania', 'MAN', 'Mercedes', 'Hino', 'HINO', 'FORD', 'SITRAK', 'Камаз', 'МАЗ']):
            vehicle_groups.append(val)
    
    print(f"Найдено {len(vehicle_groups)} групп с автомобилями:")
    print()
    
    for i, group in enumerate(vehicle_groups, 1):
        result = extract_vehicle_number(group)
        print(f"{i:2d}. {group:<35} -> {result}")

if __name__ == "__main__":
    main()
