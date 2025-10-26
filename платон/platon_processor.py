#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для обработки данных системы "Платон"
Обрабатывает CSV файлы и создает Excel отчет по начислениям
"""

import csv
import pandas as pd
from datetime import datetime
import os
import sys
from collections import defaultdict
import argparse
import glob
import traceback


class PlatonProcessor:
    """Класс для обработки данных системы Платон"""
    
    def __init__(self):
        self.data = []
        self.summary = {}
        # Желаемый порядок машин по трём цифрам после первой буквы ГРЗ
        self.desired_vehicle_codes_order = [
            '646','378','093','149','210','048','497','583','128','203','758','453','436','756','750','879','869','370','374','258','089','915','701','708'
        ]
        
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
    
    def create_excel_report(self, output_file):
        """Создает Excel отчет по образцу"""
        print(f"Создаю Excel отчет: {output_file}")
        
        try:
            # Создаем Excel writer
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 0. Матрица начислений: ТС × дни
                self._create_daily_vehicle_matrix_sheet(writer)
                
                # 1. Общая сводка
                self._create_summary_sheet(writer)
                
                # 2. Данные по транспортным средствам
                self._create_vehicles_sheet(writer)
                
                # 3. Данные по дорогам
                self._create_roads_sheet(writer)
                
                # 4. Данные по датам
                self._create_dates_sheet(writer)
                
                # 5. Детальные данные
                self._create_details_sheet(writer)
                
            print(f"Excel отчет создан: {output_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка при создании Excel отчета: {e}")
            print(traceback.format_exc())
            return False
    
    def _create_summary_sheet(self, writer):
        """Создает лист с общей сводкой"""
        summary_data = {
            'Показатель': [
                'Общее количество записей',
                'Общая сумма начислений (руб.)',
                'Общее расстояние (км)',
                'Количество транспортных средств',
                'Количество дорог',
                'Количество типов операций'
            ],
            'Значение': [
                self.summary['total_records'],
                f"{self.summary['total_amount']:.2f}",
                f"{self.summary['total_distance']:.2f}",
                len(self.summary['vehicles']),
                len(self.summary['roads']),
                len(self.summary['operation_types'])
            ]
        }
        
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Общая сводка', index=False)
    
    def _create_vehicles_sheet(self, writer):
        """Создает лист с данными по транспортным средствам"""
        vehicle_data = []
        
        for vehicle, records in self.summary['by_vehicle'].items():
            total_amount = sum(self._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
            total_distance = sum(self._parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
            trips_count = len(records)
            avg_amount = (total_amount / trips_count) if trips_count > 0 else 0.0
            
            vehicle_data.append({
                'ГРЗ ТС': vehicle,
                'Количество поездок': trips_count,
                'Общая сумма (руб.)': round(total_amount, 2),
                'Общее расстояние (км)': round(total_distance, 2),
                'Средняя сумма за поездку (руб.)': round(avg_amount, 2)
            })
        
        df = pd.DataFrame(vehicle_data)

        # Сортировка по желаемому порядку кодов ТС; остальные в конце по алфавиту
        def extract_code(grz: str) -> str:
            # Ожидается формат: <буква><три цифры><две буквы><регион>
            # Берём три цифры после первой буквы
            import re
            m = re.match(r'^[A-Za-zА-Яа-я](\d{3})', grz or '')
            return m.group(1) if m else ''

        order_index = {code: i for i, code in enumerate(self.desired_vehicle_codes_order)}
        df['__code'] = df['ГРЗ ТС'].apply(extract_code)
        df['__ord'] = df['__code'].apply(lambda c: order_index.get(c, 10**6))
        df = df.sort_values(['__ord','ГРЗ ТС']).drop(columns=['__code','__ord'])
        df.to_excel(writer, sheet_name='По транспортным средствам', index=False)
    
    def _create_roads_sheet(self, writer):
        """Создает лист с данными по дорогам"""
        road_data = []
        
        for road, records in self.summary['by_road'].items():
            total_amount = sum(self._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
            total_distance = sum(self._parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
            trips_count = len(records)
            
            road_data.append({
                'Наименование дороги': road,
                'Количество поездок': trips_count,
                'Общая сумма (руб.)': f"{total_amount:.2f}",
                'Общее расстояние (км)': f"{total_distance:.2f}",
                'Средняя сумма за км (руб.)': f"{total_amount/total_distance:.2f}" if total_distance > 0 else "0.00"
            })
        
        df = pd.DataFrame(road_data)
        df = df.sort_values('Общая сумма (руб.)', ascending=False)
        df.to_excel(writer, sheet_name='По дорогам', index=False)
    
    def _create_dates_sheet(self, writer):
        """Создает лист с данными по датам"""
        date_data = []
        
        for date, records in self.summary['by_date'].items():
            total_amount = sum(self._parse_float(r.get('Списание с РЗ (руб.)', '0')) for r in records)
            total_distance = sum(self._parse_float(r.get('Путь по фед. дорогам, км', '0')) for r in records)
            trips_count = len(records)
            
            date_data.append({
                'Дата': date,
                'Количество поездок': trips_count,
                'Общая сумма (руб.)': round(total_amount, 2),
                'Общее расстояние (км)': round(total_distance, 2)
            })
        
        if not date_data:
            df = pd.DataFrame(columns=['Дата', 'Количество поездок', 'Общая сумма (руб.)', 'Общее расстояние (км)'])
        else:
            df = pd.DataFrame(date_data)
            if 'Дата' in df.columns:
                df = df.sort_values('Дата')
        
        df.to_excel(writer, sheet_name='По датам', index=False)
    
    def _create_daily_vehicle_matrix_sheet(self, writer):
        """Создает лист-матрицу: строки — ТС, столбцы — дни (дд.мм), значения — сумма начислений за день"""
        # Суммируем по (ТС, день)
        vehicle_to_date_sum = defaultdict(lambda: defaultdict(float))
        all_dates = set()
        
        print("Создаю матрицу начислений по дням...")
        
        for record in self.data:
            vehicle = record.get('ГРЗ ТС', '')
            if not vehicle:
                continue
            # Обрабатываем BOM в названии колонки
            date_str = record.get('Дата/время операции (мск)', '') or record.get('\ufeffДата/время операции (мск)', '')
            amount = self._parse_float(record.get('Списание с РЗ (руб.)', '0'))
            
            if amount == 0:
                continue
                
            try:
                # Парсим дату в формате "01.10.2025 00:06:52"
                if not date_str or not date_str.strip():
                    continue
                date_part = date_str.split()[0]  # "01.10.2025"
                day_key = datetime.strptime(date_part, '%d.%m.%Y').strftime('%d.%m')
            except Exception as e:
                # Убираем отладочный вывод для пустых дат
                if date_str and date_str.strip():
                    print(f"Ошибка парсинга даты '{date_str}': {e}")
                continue
            
            vehicle_to_date_sum[vehicle][day_key] += amount
            all_dates.add(day_key)
        
        print(f"Найдено уникальных дат: {len(all_dates)}")
        print(f"Найдено уникальных ТС: {len(vehicle_to_date_sum)}")
        
        if not all_dates:
            print("Нет данных для создания матрицы")
            df = pd.DataFrame(columns=['ГРЗ ТС'])
        else:
            # Отсортированные оси: даты по месяцу/дню, ТС по заданному порядку
            sorted_dates = sorted(all_dates, key=lambda d: (int(d.split('.')[1]), int(d.split('.')[0])))  # по месяцу, затем дню

            def extract_code_from_grz(grz: str) -> str:
                import re
                m = re.match(r'^[A-Za-zА-Яа-я](\d{3})', grz or '')
                return m.group(1) if m else ''

            order_index = {code: i for i, code in enumerate(self.desired_vehicle_codes_order)}
            sorted_vehicles = sorted(
                vehicle_to_date_sum.keys(),
                key=lambda v: (order_index.get(extract_code_from_grz(v), 10**6), v)
            )
            
            print(f"Создаю таблицу {len(sorted_vehicles)}x{len(sorted_dates)}")
            
            # Формируем таблицу
            table_rows = []
            for vehicle in sorted_vehicles:
                row = {'ГРЗ ТС': vehicle}
                for d in sorted_dates:
                    value = round(vehicle_to_date_sum[vehicle].get(d, 0.0), 2)
                    row[d] = value if value != 0 else ''
                table_rows.append(row)
            
            df = pd.DataFrame(table_rows, columns=['ГРЗ ТС'] + list(sorted_dates))
        
        df.to_excel(writer, sheet_name='Начисления по дням', index=False)
        print("Матрица начислений по дням создана")

    def _create_details_sheet(self, writer):
        """Создает лист с детальными данными"""
        # Преобразуем данные в DataFrame
        df = pd.DataFrame(self.data)
        
        # Переименовываем колонки для лучшей читаемости
        column_mapping = {
            'Дата/время операции (мск)': 'Дата операции',
            'Уникальный номер операции': 'Номер операции',
            'Тип операции': 'Тип операции',
            'ГРЗ ТС': 'ГРЗ ТС',
            'Путь по фед. дорогам, км': 'Расстояние (км)',
            'Наименование дороги': 'Дорога',
            'Списание с РЗ (руб.)': 'Сумма (руб.)',
            'Номер БУ/МК': 'Номер БУ/МК',
            'Дата и время начала движения (мск)': 'Начало движения',
            'Дата и время окончания движения (мск)': 'Окончание движения'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Удаляем колонку "Зачисление на РЗ" если она пустая
        if 'Зачисление на РЗ (руб.)' in df.columns:
            df = df.drop(columns=['Зачисление на РЗ (руб.)'])
        
        df.to_excel(writer, sheet_name='Детальные данные', index=False)


def main():
    """Основная функция программы"""
    parser = argparse.ArgumentParser(description='Обработка данных системы Платон')
    parser.add_argument('csv_files', nargs='*', help='Пути к CSV файлам для обработки')
    parser.add_argument('-o', '--output', default='отчет_платон.xlsx', help='Имя выходного Excel файла')
    
    args = parser.parse_args()
    
    print("=== Программа обработки данных системы Платон ===")
    # Если файлы не переданы, ищем все CSV в текущей директории
    input_files = list(args.csv_files)
    if not input_files:
        input_files = glob.glob("*.csv")
        if not input_files:
            print("Ошибка: CSV файлы не найдены. Укажите файлы или положите их в текущую папку.")
            return 1
        print(f"CSV файлы не были переданы как аргументы. Найдены в папке: {input_files}")

    print(f"Входные файлы: {input_files}")
    print(f"Выходной файл: {args.output}")
    print()
    
    # Создаем процессор
    processor = PlatonProcessor()
    
    # Обрабатываем каждый CSV файл
    for csv_file in input_files:
        if not os.path.exists(csv_file):
            print(f"Ошибка: файл {csv_file} не найден")
            continue
            
        if not processor.read_csv_file(csv_file):
            print(f"Не удалось прочитать файл {csv_file}")
            continue
    
    if not processor.data:
        print("Ошибка: не удалось загрузить данные из файлов")
        return 1
    
    # Обрабатываем данные
    processor.process_data()
    
    # Создаем Excel отчет
    if processor.create_excel_report(args.output):
        print(f"\n✅ Отчет успешно создан: {args.output}")
        return 0
    else:
        print("\n❌ Ошибка при создании отчета")
        return 1


if __name__ == "__main__":
    sys.exit(main())
