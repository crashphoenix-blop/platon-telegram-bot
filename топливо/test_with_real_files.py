#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование программы с реальными файлами
"""

from fuel_consumption_analyzer import FuelConsumptionAnalyzer
import os
import pandas as pd

def test_with_real_files():
    """Тестирование с реальными файлами из папки топливо"""
    
    print("=== ТЕСТИРОВАНИЕ С РЕАЛЬНЫМИ ФАЙЛАМИ ===")
    
    # Пути к реальным файлам
    krassula_file = "топливо/15.10.2025 11_24_18 Отчёт о транзакциях.xlsx"
    glonass_file = "топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx"
    
    # Проверяем существование файлов
    if not os.path.exists(krassula_file):
        print(f"❌ Файл Крассулы не найден: {krassula_file}")
        return False
    
    if not os.path.exists(glonass_file):
        print(f"❌ Файл ГЛОНАСС не найден: {glonass_file}")
        return False
    
    print(f"✅ Файл Крассулы найден: {krassula_file}")
    print(f"✅ Файл ГЛОНАСС найден: {glonass_file}")
    
    # Создаем анализатор
    analyzer = FuelConsumptionAnalyzer()
    
    try:
        # Тестируем загрузку данных Крассулы
        print("\n1. Тестируем загрузку данных Крассулы...")
        if analyzer.load_krassula_data(krassula_file):
            print("✅ Данные Крассулы загружены успешно")
            print(f"   Количество записей: {len(analyzer.krassula_data)}")
            
            # Показываем первые несколько записей
            print("   Первые 3 записи:")
            for i, (_, row) in enumerate(analyzer.krassula_data.head(3).iterrows()):
                print(f"     {i+1}. {row['Дата и время']} - {row['Кол-во литров']}л - {row['Комментарий']}")
        else:
            print("❌ Ошибка загрузки данных Крассулы")
            return False
        
        # Тестируем загрузку данных ГЛОНАСС
        print("\n2. Тестируем загрузку данных ГЛОНАСС...")
        if analyzer.load_glonass_data(glonass_file):
            print("✅ Данные ГЛОНАСС загружены успешно")
            print(f"   Заправки: {len(analyzer.glonass_refuel_data)}")
            print(f"   Сливы: {len(analyzer.glonass_drain_data)}")
            
            # Показываем уникальные номера автомобилей
            if not analyzer.glonass_refuel_data.empty:
                vehicles = analyzer.glonass_refuel_data['vehicle_number'].dropna().unique()
                print(f"   Найдено автомобилей: {len(vehicles)}")
                print(f"   Номера: {list(vehicles)[:5]}...")  # Показываем первые 5
        else:
            print("❌ Ошибка загрузки данных ГЛОНАСС")
            return False
        
        # Тестируем извлечение номеров карт
        print("\n3. Тестируем извлечение номеров карт...")
        card_numbers = set()
        for card_full in analyzer.krassula_data['Номер карты'].dropna():
            card_num = analyzer._extract_card_number(str(card_full))
            if card_num:
                card_numbers.add(card_num)
        
        print(f"   Найдено уникальных карт: {len(card_numbers)}")
        print(f"   Номера карт: {list(card_numbers)[:10]}...")  # Показываем первые 10
        
        # Создаем тестовое соответствие карт и автомобилей
        print("\n4. Создаем тестовое соответствие...")
        test_mapping = {}
        
        # Берем первые несколько карт и автомобилей для тестирования
        cards = list(card_numbers)[:5]
        vehicles = analyzer.glonass_refuel_data['vehicle_number'].dropna().unique()[:5]
        
        for i, card in enumerate(cards):
            if i < len(vehicles):
                test_mapping[card] = vehicles[i]
        
        print(f"   Создано соответствий: {len(test_mapping)}")
        for card, vehicle in test_mapping.items():
            print(f"     Карта {card} -> Автомобиль {vehicle}")
        
        analyzer.load_card_mapping(test_mapping)
        
        # Тестируем сопоставление
        print("\n5. Тестируем сопоставление заправок...")
        results = analyzer.match_refuels()
        
        print(f"   Обработано автомобилей: {len(results)}")
        total_refuels = sum(len(refuels) for refuels in results.values())
        matched_refuels = sum(
            len([r for r in refuels if r['status'] == 'matched'])
            for refuels in results.values()
        )
        
        print(f"   Всего заправок: {total_refuels}")
        print(f"   Сопоставлено: {matched_refuels}")
        print(f"   Процент сопоставления: {(matched_refuels/total_refuels*100):.1f}%" if total_refuels > 0 else "0%")
        
        # Показываем уведомления
        print(f"\n6. Уведомления: {len(analyzer.notifications)}")
        for i, notification in enumerate(analyzer.notifications[:5]):  # Показываем первые 5
            print(f"   {i+1}. {notification['type']}: {notification['message']}")
        
        if len(analyzer.notifications) > 5:
            print(f"   ... и еще {len(analyzer.notifications) - 5} уведомлений")
        
        # Тестируем создание отчета
        print("\n7. Тестируем создание отчета...")
        test_output = "test_report.xlsx"
        if analyzer.generate_excel_report(test_output):
            print(f"✅ Отчет создан: {test_output}")
            
            # Проверяем размер файла
            file_size = os.path.getsize(test_output)
            print(f"   Размер файла: {file_size} байт")
        else:
            print("❌ Ошибка создания отчета")
            return False
        
        print("\n" + "="*50)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ВО ВРЕМЯ ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_file_structure():
    """Анализирует структуру файлов для понимания данных"""
    
    print("\n=== АНАЛИЗ СТРУКТУРЫ ФАЙЛОВ ===")
    
    # Анализируем файл Крассулы
    krassula_file = "топливо/15.10.2025 11_24_18 Отчёт о транзакциях.xlsx"
    
    if os.path.exists(krassula_file):
        print(f"\n📊 Анализ файла Крассулы: {krassula_file}")
        try:
            df = pd.read_excel(krassula_file)
            print(f"   Размер: {df.shape[0]} строк, {df.shape[1]} колонок")
            print("   Колонки:")
            for i, col in enumerate(df.columns):
                print(f"     {i+1}. {col}")
            
            print("\n   Первые 3 строки:")
            for i, (_, row) in enumerate(df.head(3).iterrows()):
                print(f"     Строка {i+1}:")
                for col in df.columns:
                    value = str(row[col])[:50] + "..." if len(str(row[col])) > 50 else str(row[col])
                    print(f"       {col}: {value}")
                print()
                
        except Exception as e:
            print(f"   ❌ Ошибка чтения файла: {e}")
    
    # Анализируем файл ГЛОНАСС
    glonass_file = "топливо/Все_ТС-ИП_Серкин_9)_Групповой_отчет_по_заправкам_и_сливам_15.10.2025_12-26-52.xlsx"
    
    if os.path.exists(glonass_file):
        print(f"\n📊 Анализ файла ГЛОНАСС: {glonass_file}")
        try:
            # Читаем листы
            excel_file = pd.ExcelFile(glonass_file)
            print(f"   Листы: {excel_file.sheet_names}")
            
            for sheet_name in excel_file.sheet_names:
                print(f"\n   Лист '{sheet_name}':")
                df = pd.read_excel(glonass_file, sheet_name=sheet_name)
                print(f"     Размер: {df.shape[0]} строк, {df.shape[1]} колонок")
                print("     Колонки:")
                for i, col in enumerate(df.columns):
                    print(f"       {i+1}. {col}")
                
                if not df.empty:
                    print("     Первая строка:")
                    for col in df.columns:
                        value = str(df.iloc[0][col])[:50] + "..." if len(str(df.iloc[0][col])) > 50 else str(df.iloc[0][col])
                        print(f"       {col}: {value}")
                
        except Exception as e:
            print(f"   ❌ Ошибка чтения файла: {e}")

if __name__ == "__main__":
    # Сначала анализируем структуру файлов
    analyze_file_structure()
    
    # Затем тестируем программу
    test_with_real_files()
