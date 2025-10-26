#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенная программа для обработки данных системы "Платон"
Работает без дополнительных зависимостей
"""

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict
import json

class SimplePlatonProcessor:
    """Упрощенный класс для обработки данных системы Платон"""
    
    def __init__(self):
        self.data = []
        self.summary = {}
        
    def read_csv_file(self, file_path):
        """Читает CSV файл с данными системы Платон"""
        print(f"Читаю файл: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Определяем разделитель
                sample = file.read(1024)
                file.seek(0)
                
                if ';' in sample:
                    delimiter = ';'
                else:
                    delimiter = ','
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    # Очищаем данные от лишних пробелов
                    cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                    self.data.append(cleaned_row)
                    
            print(f"Прочитано {len(self.data)} записей")
            return True
            
        except Exception as e:
            print(f"Ошибка при чтении файла {file_path}: {e}")
            return False
    
    def process_data(self):
        """Обрабатывает данные и создает сводку"""
        print("Обрабатываю данные...")
        
        # Группируем данные по различным критериям
        by_vehicle = defaultdict(list)
        by_road = defaultdict(list)
        by_date = defaultdict(list)
        by_operation_type = defaultdict(list)
        
        total_amount = 0
        total_distance = 0
        
        for record in self.data:
            # Извлекаем основные данные
            vehicle = record.get('ГРЗ ТС', '')
            road = record.get('Наименование дороги', '')
            operation_type = record.get('Тип операции', '')
            distance = self._parse_float(record.get('Путь по фед. дорогам, км', '0'))
            amount = self._parse_float(record.get('Списание с РЗ (руб.)', '0'))
            date_str = record.get('Дата/время операции (мск)', '')
            
            # Группируем данные
            by_vehicle[vehicle].append(record)
            by_road[road].append(record)
            by_operation_type[operation_type].append(record)
            
            # Парсим дату
            try:
                date_obj = datetime.strptime(date_str.split()[0], '%d.%m.%Y')
                by_date[date_obj.strftime('%Y-%m-%d')].append(record)
            except:
                pass
            
            total_amount += amount
            total_distance += distance
        
        # Создаем сводку
        self.summary = {
            'total_records': len(self.data),
            'total_amount': total_amount,
            'total_distance': total_distance,
            'by_vehicle': dict(by_vehicle),
            'by_road': dict(by_road),
            'by_date': dict(by_date),
            'by_operation_type': dict(by_operation_type),
            'vehicles': list(by_vehicle.keys()),
            'roads': list(by_road.keys()),
            'operation_types': list(by_operation_type.keys())
        }
        
        print(f"Обработано {len(self.data)} записей")
        print(f"Общая сумма: {total_amount:.2f} руб.")
        print(f"Общее расстояние: {total_distance:.2f} км")
        print(f"Транспортных средств: {len(by_vehicle)}")
        print(f"Дорог: {len(by_road)}")
        
    def _parse_float(self, value):
        """Парсит строку в число с плавающей точкой"""
        try:
            # Заменяем запятую на точку для корректного парсинга
            return float(value.replace(',', '.'))
        except:
            return 0.0
    
    def create_html_report(self, output_file):
        """Создает HTML отчет"""
        print(f"Создаю HTML отчет: {output_file}")
        
        try:
            html_content = self._generate_html()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"HTML отчет создан: {output_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка при создании HTML отчета: {e}")
            return False
    
    def _generate_html(self):
        """Генерирует HTML содержимое отчета"""
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по начислениям системы Платон</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #e7f3ff; padding: 15px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        h1, h2 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Отчет по начислениям системы Платон</h1>
    
    <div class="summary">
        <h2>Общая сводка</h2>
        <p><strong>Общее количество записей:</strong> {self.summary['total_records']}</p>
        <p><strong>Общая сумма начислений:</strong> {self.summary['total_amount']:.2f} руб.</p>
        <p><strong>Общее расстояние:</strong> {self.summary['total_distance']:.2f} км</p>
        <p><strong>Количество транспортных средств:</strong> {len(self.summary['vehicles'])}</p>
        <p><strong>Количество дорог:</strong> {len(self.summary['roads'])}</p>
    </div>
    
    <div class="section">
        <h2>По транспортным средствам</h2>
        {self._generate_vehicles_table()}
    </div>
    
    <div class="section">
        <h2>По дорогам</h2>
        {self._generate_roads_table()}
    </div>
    
    <div class="section">
        <h2>По датам</h2>
        {self._generate_dates_table()}
    </div>
    
    <div class="section">
        <h2>Детальные данные (первые 100 записей)</h2>
        {self._generate_details_table()}
    </div>
    
</body>
</html>
"""
        return html
    
    def _generate_vehicles_table(self):
        """Генерирует таблицу по транспортным средствам"""
        vehicle_data = []
        
        for vehicle, records in self.summary['by_vehicle'].items():
            total_amount = sum(self._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
            total_distance = sum(self._parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
            trips_count = len(records)
            
            vehicle_data.append({
                'vehicle': vehicle,
                'trips': trips_count,
                'amount': total_amount,
                'distance': total_distance,
                'avg_amount': total_amount/trips_count if trips_count > 0 else 0
            })
        
        # Сортируем по сумме
        vehicle_data.sort(key=lambda x: x['amount'], reverse=True)
        
        html = """
        <table>
            <tr>
                <th>ГРЗ ТС</th>
                <th>Количество поездок</th>
                <th>Общая сумма (руб.)</th>
                <th>Общее расстояние (км)</th>
                <th>Средняя сумма за поездку (руб.)</th>
            </tr>
        """
        
        for data in vehicle_data:
            html += f"""
            <tr>
                <td>{data['vehicle']}</td>
                <td>{data['trips']}</td>
                <td>{data['amount']:.2f}</td>
                <td>{data['distance']:.2f}</td>
                <td>{data['avg_amount']:.2f}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_roads_table(self):
        """Генерирует таблицу по дорогам"""
        road_data = []
        
        for road, records in self.summary['by_road'].items():
            total_amount = sum(self._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
            total_distance = sum(self._parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
            trips_count = len(records)
            
            road_data.append({
                'road': road,
                'trips': trips_count,
                'amount': total_amount,
                'distance': total_distance,
                'avg_per_km': total_amount/total_distance if total_distance > 0 else 0
            })
        
        # Сортируем по сумме
        road_data.sort(key=lambda x: x['amount'], reverse=True)
        
        html = """
        <table>
            <tr>
                <th>Наименование дороги</th>
                <th>Количество поездок</th>
                <th>Общая сумма (руб.)</th>
                <th>Общее расстояние (км)</th>
                <th>Средняя сумма за км (руб.)</th>
            </tr>
        """
        
        for data in road_data:
            html += f"""
            <tr>
                <td>{data['road']}</td>
                <td>{data['trips']}</td>
                <td>{data['amount']:.2f}</td>
                <td>{data['distance']:.2f}</td>
                <td>{data['avg_per_km']:.2f}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_dates_table(self):
        """Генерирует таблицу по датам"""
        date_data = []
        
        for date, records in self.summary['by_date'].items():
            total_amount = sum(self._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
            total_distance = sum(self._parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
            trips_count = len(records)
            
            date_data.append({
                'date': date,
                'trips': trips_count,
                'amount': total_amount,
                'distance': total_distance
            })
        
        # Сортируем по дате
        date_data.sort(key=lambda x: x['date'])
        
        html = """
        <table>
            <tr>
                <th>Дата</th>
                <th>Количество поездок</th>
                <th>Общая сумма (руб.)</th>
                <th>Общее расстояние (км)</th>
            </tr>
        """
        
        for data in date_data:
            html += f"""
            <tr>
                <td>{data['date']}</td>
                <td>{data['trips']}</td>
                <td>{data['amount']:.2f}</td>
                <td>{data['distance']:.2f}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_details_table(self):
        """Генерирует таблицу с детальными данными"""
        html = """
        <table>
            <tr>
                <th>Дата операции</th>
                <th>ГРЗ ТС</th>
                <th>Тип операции</th>
                <th>Дорога</th>
                <th>Расстояние (км)</th>
                <th>Сумма (руб.)</th>
                <th>Номер БУ/МК</th>
            </tr>
        """
        
        # Показываем только первые 100 записей
        for record in self.data[:100]:
            date = record.get('Дата/время операции (мск)', '')
            vehicle = record.get('ГРЗ ТС', '')
            operation_type = record.get('Тип операции', '')
            road = record.get('Наименование дороги', '')
            distance = record.get('Путь по фед. дорогам, км', '0')
            amount = record.get('Списание с РЗ (руб.)', '0')
            bu_number = record.get('Номер БУ/МК', '')
            
            html += f"""
            <tr>
                <td>{date}</td>
                <td>{vehicle}</td>
                <td>{operation_type}</td>
                <td>{road}</td>
                <td>{distance}</td>
                <td>{amount}</td>
                <td>{bu_number}</td>
            </tr>
            """
        
        html += "</table>"
        return html


def main():
    """Основная функция программы"""
    print("=== Упрощенная программа обработки данных системы Платон ===")
    
    # Ищем CSV файлы в текущей директории
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ CSV файлы не найдены в текущей директории")
        print("Поместите CSV файлы в папку с программой и запустите снова")
        return 1
    
    print(f"Найдено CSV файлов: {len(csv_files)}")
    for file in csv_files:
        print(f"  - {file}")
    
    # Создаем процессор
    processor = SimplePlatonProcessor()
    
    # Обрабатываем каждый CSV файл
    for csv_file in csv_files:
        print(f"\n📁 Обрабатываю файл: {csv_file}")
        if not processor.read_csv_file(csv_file):
            print(f"❌ Не удалось прочитать файл {csv_file}")
            continue
    
    if not processor.data:
        print("❌ Не удалось загрузить данные из файлов")
        return 1
    
    # Обрабатываем данные
    print("\n🔄 Обрабатываю данные...")
    processor.process_data()
    
    # Создаем HTML отчет
    output_file = "отчет_платон.html"
    print(f"\n📊 Создаю HTML отчет: {output_file}")
    
    if processor.create_html_report(output_file):
        print(f"\n✅ Отчет успешно создан: {output_file}")
        print("\n📋 Отчет содержит следующие разделы:")
        print("  - Общая сводка")
        print("  - По транспортным средствам")
        print("  - По дорогам")
        print("  - По датам")
        print("  - Детальные данные")
        print(f"\n🌐 Откройте файл {output_file} в браузере для просмотра")
        return 0
    else:
        print("\n❌ Ошибка при создании отчета")
        return 1

if __name__ == "__main__":
    sys.exit(main())
