#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from collections import defaultdict

def parse_float(value):
    """Парсит строку в число с плавающей точкой"""
    try:
        return float(value.replace(',', '.'))
    except:
        return 0.0

def process_platon_data():
    """Обрабатывает данные системы Платон"""
    
    # Ищем CSV файлы
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("CSV файлы не найдены")
        return
    
    print(f"Найдено файлов: {len(csv_files)}")
    
    all_data = []
    
    # Читаем все CSV файлы
    for csv_file in csv_files:
        print(f"Читаю {csv_file}...")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Определяем разделитель
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ';' if ';' in sample else ','
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                    all_data.append(cleaned_row)
                    
            print(f"  Прочитано {len([r for r in all_data if r.get('ГРЗ ТС')])} записей")
            
        except Exception as e:
            print(f"  Ошибка: {e}")
    
    if not all_data:
        print("Данные не найдены")
        return
    
    # Обрабатываем данные
    print("\nОбрабатываю данные...")
    
    by_vehicle = defaultdict(list)
    by_road = defaultdict(list)
    by_date = defaultdict(list)
    
    total_amount = 0
    total_distance = 0
    
    for record in all_data:
        vehicle = record.get('ГРЗ ТС', '')
        road = record.get('Наименование дороги', '')
        distance = parse_float(record.get('Путь по фед. дорогам, км', '0'))
        amount = parse_float(record.get('Списание с РЗ (руб.)', '0'))
        date_str = record.get('Дата/время операции (мск)', '')
        
        by_vehicle[vehicle].append(record)
        by_road[road].append(record)
        
        # Парсим дату
        try:
            date_part = date_str.split()[0]
            by_date[date_part].append(record)
        except:
            pass
        
        total_amount += amount
        total_distance += distance
    
    # Выводим результаты
    print(f"\n=== ОБЩАЯ СВОДКА ===")
    print(f"Общее количество записей: {len(all_data)}")
    print(f"Общая сумма: {total_amount:.2f} руб.")
    print(f"Общее расстояние: {total_distance:.2f} км")
    print(f"Транспортных средств: {len(by_vehicle)}")
    print(f"Дорог: {len(by_road)}")
    
    print(f"\n=== ПО ТРАНСПОРТНЫМ СРЕДСТВАМ ===")
    vehicle_stats = []
    for vehicle, records in by_vehicle.items():
        if not vehicle:
            continue
        total_amount_vehicle = sum(parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
        total_distance_vehicle = sum(parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
        trips_count = len(records)
        
        vehicle_stats.append((vehicle, trips_count, total_amount_vehicle, total_distance_vehicle))
    
    # Сортируем по сумме
    vehicle_stats.sort(key=lambda x: x[2], reverse=True)
    
    for vehicle, trips, amount, distance in vehicle_stats[:10]:  # Топ 10
        print(f"{vehicle}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км")
    
    print(f"\n=== ПО ДОРОГАМ ===")
    road_stats = []
    for road, records in by_road.items():
        if not road:
            continue
        total_amount_road = sum(parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
        total_distance_road = sum(parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
        trips_count = len(records)
        
        road_stats.append((road, trips_count, total_amount_road, total_distance_road))
    
    # Сортируем по сумме
    road_stats.sort(key=lambda x: x[2], reverse=True)
    
    for road, trips, amount, distance in road_stats[:10]:  # Топ 10
        print(f"{road}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км")
    
    print(f"\n=== ПО ДАТАМ ===")
    date_stats = []
    for date, records in by_date.items():
        if not date:
            continue
        total_amount_date = sum(parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
        total_distance_date = sum(parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
        trips_count = len(records)
        
        date_stats.append((date, trips_count, total_amount_date, total_distance_date))
    
    # Сортируем по дате
    date_stats.sort(key=lambda x: x[0])
    
    for date, trips, amount, distance in date_stats[:10]:  # Первые 10 дат
        print(f"{date}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км")
    
    # Создаем простой текстовый отчет
    with open('отчет_платон.txt', 'w', encoding='utf-8') as f:
        f.write("ОТЧЕТ ПО НАЧИСЛЕНИЯМ СИСТЕМЫ ПЛАТОН\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("ОБЩАЯ СВОДКА\n")
        f.write(f"Общее количество записей: {len(all_data)}\n")
        f.write(f"Общая сумма: {total_amount:.2f} руб.\n")
        f.write(f"Общее расстояние: {total_distance:.2f} км\n")
        f.write(f"Транспортных средств: {len(by_vehicle)}\n")
        f.write(f"Дорог: {len(by_road)}\n\n")
        
        f.write("ПО ТРАНСПОРТНЫМ СРЕДСТВАМ\n")
        f.write("-" * 30 + "\n")
        for vehicle, trips, amount, distance in vehicle_stats:
            f.write(f"{vehicle}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км\n")
        
        f.write("\nПО ДОРОГАМ\n")
        f.write("-" * 30 + "\n")
        for road, trips, amount, distance in road_stats:
            f.write(f"{road}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км\n")
        
        f.write("\nПО ДАТАМ\n")
        f.write("-" * 30 + "\n")
        for date, trips, amount, distance in date_stats:
            f.write(f"{date}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км\n")
    
    print(f"\n✅ Текстовый отчет сохранен в файл 'отчет_платон.txt'")

if __name__ == "__main__":
    process_platon_data()
