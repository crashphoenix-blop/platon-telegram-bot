#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальная отладка обработки данных ГЛОНАСС
"""

import pandas as pd
import re

def extract_vehicle_number(grouping_text: str) -> str:
    """Функция извлечения номера автомобиля"""
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

def extract_date_from_grouping(grouping_text: str) -> str:
    """Функция извлечения даты"""
    if pd.isna(grouping_text):
        return "None"
        
    # Ищем паттерн даты: DD.MM.YYYY
    date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
    match = re.search(date_pattern, grouping_text)
    
    if match:
        date_str = match.group()
        try:
            from datetime import datetime
            parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    return "None"

def main():
    """Детальная отладка"""
    
    print("=== ДЕТАЛЬНАЯ ОТЛАДКА ОБРАБОТКИ ДАННЫХ ГЛОНАСС ===")
    
    # Загружаем данные
    df = pd.read_excel('топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx', sheet_name='Заправки и зарядки батареи')
    
    print(f"Исходный размер данных: {df.shape}")
    print(f"Колонки: {list(df.columns)}")
    
    # Обрабатываем иерархическую структуру данных
    processed_data = []
    current_vehicle = None
    vehicle_count = 0
    refuel_count = 0
    
    print("\n=== ОБРАБОТКА ДАННЫХ ===")
    
    for i, (_, row) in enumerate(df.iterrows()):
        grouping = str(row['Группировка'])
        
        # Проверяем, является ли это названием автомобиля
        vehicle_number = extract_vehicle_number(grouping)
        if vehicle_number and vehicle_number != "None":
            current_vehicle = vehicle_number
            vehicle_count += 1
            print(f"Найден автомобиль {i+1}: {grouping} -> {vehicle_number}")
            continue
        
        # Проверяем, является ли это датой
        date = extract_date_from_grouping(grouping)
        if date and current_vehicle:
            # Проверяем, что это валидная заправка
            if (str(row['Время']) != '-----' and 
                str(row['Заправлено']) != '-----' and 
                str(row['Пробег']) != '-----'):
                
                refuel_count += 1
                print(f"  Заправка {refuel_count}: {grouping} | {row['Время']} | {row['Заправлено']}л | Пробег: {row['Пробег']}")
                
                # Это заправка для текущего автомобиля
                processed_row = row.copy()
                processed_row['vehicle_number'] = current_vehicle
                processed_row['date'] = date
                
                # Очищаем время от даты, если она там есть
                time_str = str(row['Время'])
                time_cleaned = re.search(r'(\d{2}:\d{2}:\d{2})', time_str)
                if time_cleaned:
                    time_str = time_cleaned.group(1)
                
                processed_row['datetime'] = pd.to_datetime(date + ' ' + time_str)
                processed_data.append(processed_row)
    
    print(f"\n=== РЕЗУЛЬТАТЫ ===")
    print(f"Найдено автомобилей: {vehicle_count}")
    print(f"Найдено заправок: {refuel_count}")
    print(f"Обработано записей: {len(processed_data)}")
    
    if processed_data:
        result_df = pd.DataFrame(processed_data)
        print(f"Размер итогового DataFrame: {result_df.shape}")
        print(f"Колонки: {list(result_df.columns)}")
        
        print("\n=== ПЕРВЫЕ 5 ЗАПРАВОК ===")
        for i, (_, row) in enumerate(result_df.head(5).iterrows()):
            print(f"{i+1}. Автомобиль: {row['vehicle_number']}")
            print(f"   Дата: {row['date']}")
            print(f"   Время: {row['datetime']}")
            print(f"   Заправлено: {row['Заправлено']}л")
            print(f"   Пробег: {row['Пробег']}")
            print()
    else:
        print("❌ Нет обработанных данных!")

if __name__ == "__main__":
    main()
