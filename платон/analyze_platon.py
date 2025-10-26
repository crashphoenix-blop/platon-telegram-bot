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

def main():
    """Основная функция"""
    print("=== Анализ данных системы Платон ===")
    
    # Ищем CSV файлы
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("CSV файлы не найдены в текущей директории")
        return
    
    print(f"Найдено CSV файлов: {len(csv_files)}")
    for file in csv_files:
        print(f"  - {file}")
    
    all_data = []
    
    # Читаем все CSV файлы
    for csv_file in csv_files:
        print(f"\nЧитаю файл: {csv_file}")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Определяем разделитель
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ';' if ';' in sample else ','
                print(f"  Использую разделитель: '{delimiter}'")
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                count = 0
                for row in reader:
                    cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                    all_data.append(cleaned_row)
                    count += 1
                    
                print(f"  Прочитано записей: {count}")
                
        except Exception as e:
            print(f"  Ошибка при чтении файла: {e}")
            continue
    
    if not all_data:
        print("\n❌ Не удалось загрузить данные")
        return
    
    print(f"\n✅ Всего загружено записей: {len(all_data)}")
    
    # Анализируем данные
    print("\n🔄 Анализирую данные...")
    
    by_vehicle = defaultdict(list)
    by_road = defaultdict(list)
    by_date = defaultdict(list)
    by_operation_type = defaultdict(list)
    
    total_amount = 0
    total_distance = 0
    
    for record in all_data:
        vehicle = record.get('ГРЗ ТС', '')
        road = record.get('Наименование дороги', '')
        operation_type = record.get('Тип операции', '')
        distance = parse_float(record.get('Путь по фед. дорогам, км', '0'))
        amount = parse_float(record.get('Списание с РЗ (руб.)', '0'))
        date_str = record.get('Дата/время операции (мск)', '')
        
        by_vehicle[vehicle].append(record)
        by_road[road].append(record)
        by_operation_type[operation_type].append(record)
        
        # Парсим дату
        try:
            date_part = date_str.split()[0]
            by_date[date_part].append(record)
        except:
            pass
        
        total_amount += amount
        total_distance += distance
    
    # Выводим общую сводку
    print(f"\n📊 ОБЩАЯ СВОДКА")
    print(f"Общее количество записей: {len(all_data)}")
    print(f"Общая сумма начислений: {total_amount:.2f} руб.")
    print(f"Общее расстояние: {total_distance:.2f} км")
    print(f"Количество транспортных средств: {len([v for v in by_vehicle.keys() if v])}")
    print(f"Количество дорог: {len([r for r in by_road.keys() if r])}")
    print(f"Количество типов операций: {len([t for t in by_operation_type.keys() if t])}")
    
    # Анализ по транспортным средствам
    print(f"\n🚛 ПО ТРАНСПОРТНЫМ СРЕДСТВАМ")
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
    
    print("Топ-10 транспортных средств по сумме начислений:")
    for i, (vehicle, trips, amount, distance) in enumerate(vehicle_stats[:10], 1):
        avg_amount = amount / trips if trips > 0 else 0
        print(f"{i:2d}. {vehicle}: {trips:3d} поездок, {amount:8.2f} руб., {distance:8.2f} км (ср. {avg_amount:.2f} руб./поездка)")
    
    # Анализ по дорогам
    print(f"\n🛣️  ПО ДОРОГАМ")
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
    
    print("Топ-10 дорог по сумме начислений:")
    for i, (road, trips, amount, distance) in enumerate(road_stats[:10], 1):
        avg_per_km = amount / distance if distance > 0 else 0
        print(f"{i:2d}. {road}: {trips:3d} поездок, {amount:8.2f} руб., {distance:8.2f} км (ср. {avg_per_km:.2f} руб./км)")
    
    # Анализ по датам
    print(f"\n📅 ПО ДАТАМ")
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
    
    print("Статистика по датам (первые 10 дней):")
    for i, (date, trips, amount, distance) in enumerate(date_stats[:10], 1):
        print(f"{i:2d}. {date}: {trips:3d} поездок, {amount:8.2f} руб., {distance:8.2f} км")
    
    # Анализ по типам операций
    print(f"\n⚙️  ПО ТИПАМ ОПЕРАЦИЙ")
    for operation_type, records in by_operation_type.items():
        if not operation_type:
            continue
        total_amount_type = sum(parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
        total_distance_type = sum(parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
        trips_count = len(records)
        
        print(f"{operation_type}: {trips_count:3d} операций, {total_amount_type:8.2f} руб., {total_distance_type:8.2f} км")
    
    # Создаем текстовый отчет
    print(f"\n💾 Создаю текстовый отчет...")
    
    try:
        with open('отчет_платон.txt', 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ ПО НАЧИСЛЕНИЯМ СИСТЕМЫ ПЛАТОН\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("ОБЩАЯ СВОДКА\n")
            f.write(f"Общее количество записей: {len(all_data)}\n")
            f.write(f"Общая сумма начислений: {total_amount:.2f} руб.\n")
            f.write(f"Общее расстояние: {total_distance:.2f} км\n")
            f.write(f"Количество транспортных средств: {len([v for v in by_vehicle.keys() if v])}\n")
            f.write(f"Количество дорог: {len([r for r in by_road.keys() if r])}\n")
            f.write(f"Количество типов операций: {len([t for t in by_operation_type.keys() if t])}\n\n")
            
            f.write("ПО ТРАНСПОРТНЫМ СРЕДСТВАМ\n")
            f.write("-" * 50 + "\n")
            for vehicle, trips, amount, distance in vehicle_stats:
                avg_amount = amount / trips if trips > 0 else 0
                f.write(f"{vehicle}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км (ср. {avg_amount:.2f} руб./поездка)\n")
            
            f.write("\nПО ДОРОГАМ\n")
            f.write("-" * 50 + "\n")
            for road, trips, amount, distance in road_stats:
                avg_per_km = amount / distance if distance > 0 else 0
                f.write(f"{road}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км (ср. {avg_per_km:.2f} руб./км)\n")
            
            f.write("\nПО ДАТАМ\n")
            f.write("-" * 50 + "\n")
            for date, trips, amount, distance in date_stats:
                f.write(f"{date}: {trips} поездок, {amount:.2f} руб., {distance:.2f} км\n")
            
            f.write("\nПО ТИПАМ ОПЕРАЦИЙ\n")
            f.write("-" * 50 + "\n")
            for operation_type, records in by_operation_type.items():
                if not operation_type:
                    continue
                total_amount_type = sum(parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
                total_distance_type = sum(parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
                trips_count = len(records)
                
                f.write(f"{operation_type}: {trips_count} операций, {total_amount_type:.2f} руб., {total_distance_type:.2f} км\n")
        
        print("✅ Текстовый отчет сохранен в файл 'отчет_платон.txt'")
        
    except Exception as e:
        print(f"❌ Ошибка при создании отчета: {e}")
    
    print(f"\n🎉 Анализ завершен!")

if __name__ == "__main__":
    main()
