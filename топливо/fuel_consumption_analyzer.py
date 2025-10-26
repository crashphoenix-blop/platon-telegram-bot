#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для автоматического подсчета расхода топлива по автомобилям
Анализирует данные из системы Крассула (топливные карты) и ГЛОНАСС
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fuel_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FuelConsumptionAnalyzer:
    """Основной класс для анализа расхода топлива"""
    
    def __init__(self):
        self.krassula_data = None
        self.glonass_refuel_data = None
        self.glonass_drain_data = None
        self.card_to_vehicle_mapping = {}
        self.notifications = []
        self.results = {}
        
    def load_krassula_data(self, file_path: str) -> bool:
        """
        Загружает данные из файла Крассулы
        
        Args:
            file_path: Путь к Excel файлу с данными топливных карт
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            logger.info(f"Загружаем данные Крассулы из файла: {file_path}")
            self.krassula_data = pd.read_excel(file_path)
            
            # Проверяем наличие необходимых колонок
            required_columns = [
                'Дата и время', 'Номер карты', 'Комментарий', 'АЗС', 'Товар', 
                'Кол-во литров', 'Цена со скидкой', 'Сумма со скидкой'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.krassula_data.columns]
            if missing_columns:
                logger.error(f"Отсутствуют необходимые колонки: {missing_columns}")
                return False
                
            # Преобразуем дату
            self.krassula_data['Дата и время'] = pd.to_datetime(self.krassula_data['Дата и время'])
            
            # Фильтруем только заправки топливом
            self.krassula_data = self.krassula_data[
                self.krassula_data['Товар'].str.contains('дизель|бензин|топливо', case=False, na=False)
            ]
            
            logger.info(f"Загружено {len(self.krassula_data)} записей из Крассулы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных Крассулы: {e}")
            return False
    
    def load_glonass_data(self, file_path: str) -> bool:
        """
        Загружает данные из файла ГЛОНАСС
        
        Args:
            file_path: Путь к Excel файлу с данными ГЛОНАСС
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            logger.info(f"Загружаем данные ГЛОНАСС из файла: {file_path}")
            
            # Загружаем лист с заправками
            self.glonass_refuel_data = pd.read_excel(file_path, sheet_name='Заправки и зарядки батареи')
            
            # Загружаем лист со сливами
            self.glonass_drain_data = pd.read_excel(file_path, sheet_name='Сливы')
            
            # Обрабатываем данные заправок
            if not self.glonass_refuel_data.empty:
                # Обрабатываем иерархическую структуру данных
                processed_data = []
                current_vehicle = None
                
                for _, row in self.glonass_refuel_data.iterrows():
                    grouping = str(row['Группировка'])
                    
                    # Сначала проверяем, является ли это датой
                    date = self._extract_date_from_grouping(grouping)
                    if date and current_vehicle:
                        # Проверяем, что это валидная заправка
                        if (str(row['Время']) != '-----' and 
                            str(row['Заправлено']) != '-----' and 
                            str(row['Пробег']) != '-----'):
                            
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
                        continue
                    
                    # Проверяем, является ли это названием автомобиля
                    vehicle_number = self._extract_vehicle_number(grouping)
                    if vehicle_number and vehicle_number != "None":
                        current_vehicle = vehicle_number
                        continue
                
                # Создаем новый DataFrame с обработанными данными
                if processed_data:
                    self.glonass_refuel_data = pd.DataFrame(processed_data)
                else:
                    self.glonass_refuel_data = pd.DataFrame()
                
                logger.info(f"Загружено {len(self.glonass_refuel_data)} записей заправок из ГЛОНАСС")
            
            # Обрабатываем данные сливов
            if not self.glonass_drain_data.empty:
                # Фильтруем строки с некорректными данными
                self.glonass_drain_data = self.glonass_drain_data[
                    (self.glonass_drain_data['Время'] != '-----') &
                    (self.glonass_drain_data['Слито'] != '-----')
                ].copy()
                
                self.glonass_drain_data['vehicle_number'] = self.glonass_drain_data['Группировка'].apply(
                    self._extract_vehicle_number
                )
                logger.info(f"Загружено {len(self.glonass_drain_data)} записей сливов из ГЛОНАСС")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных ГЛОНАСС: {e}")
            return False
    
    def _extract_vehicle_number(self, grouping_text: str) -> Optional[str]:
        """
        Извлекает номер автомобиля из текста группировки
        
        Args:
            grouping_text: Текст группировки вида "Scania т497ес797"
            
        Returns:
            str: Извлеченный номер (например, "497")
        """
        if pd.isna(grouping_text):
            return None
            
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
        
        return None
    
    def _extract_date_from_grouping(self, grouping_text: str) -> Optional[str]:
        """
        Извлекает дату из текста группировки
        
        Args:
            grouping_text: Текст группировки
            
        Returns:
            str: Дата в формате YYYY-MM-DD или None
        """
        if pd.isna(grouping_text):
            return None
            
        # Ищем паттерн даты: DD.MM.YYYY
        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{4}'
        match = re.search(date_pattern, grouping_text)
        
        if match:
            date_str = match.group()
            try:
                parsed_date = datetime.strptime(date_str, '%d.%m.%Y')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return None
    
    def load_card_mapping(self, mapping_data: Dict[str, str]) -> None:
        """
        Загружает соответствие топливных карт и автомобилей
        
        Args:
            mapping_data: Словарь {номер_карты: номер_автомобиля}
        """
        self.card_to_vehicle_mapping = mapping_data
        logger.info(f"Загружено {len(mapping_data)} соответствий карт и автомобилей")
    
    def load_card_mapping_from_file(self, file_path: str) -> bool:
        """
        Загружает соответствие топливных карт и автомобилей из Excel файла
        
        Args:
            file_path: Путь к Excel файлу с соответствиями
            
        Returns:
            bool: True если загрузка успешна
        """
        try:
            logger.info(f"Загружаем соответствия карт и машин из файла: {file_path}")
            
            # Читаем файл с сохранением ведущих нулей
            df = pd.read_excel(file_path, dtype=str)
            
            # Проверяем наличие необходимых колонок
            if 'номер машины' not in df.columns:
                logger.error("Отсутствует колонка 'номер машины'")
                return False
            
            # Создаем словарь соответствий
            mapping = {}
            
            for _, row in df.iterrows():
                vehicle_number = str(row['номер машины']).strip()
                
                # Обрабатываем все колонки с картами
                for col in df.columns:
                    if col.startswith('топливна карта') and pd.notna(row[col]) and str(row[col]).strip() != '':
                        card_number = str(row[col]).strip()
                        mapping[card_number] = vehicle_number
                        logger.debug(f"Карта {card_number} -> Машина {vehicle_number}")
            
            self.card_to_vehicle_mapping = mapping
            logger.info(f"Загружено {len(mapping)} соответствий карт и автомобилей")
            
            # Показываем статистику
            vehicles_count = len(set(mapping.values()))
            logger.info(f"Обработано {vehicles_count} уникальных машин")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке соответствий: {e}")
            return False
    
    def match_refuels(self) -> Dict[str, List[Dict]]:
        """
        Сопоставляет заправки между системами Крассула и ГЛОНАСС
        
        Returns:
            Dict: Результаты сопоставления по автомобилям
        """
        logger.info("Начинаем сопоставление заправок...")
        
        results = {}
        
        # Группируем данные Крассулы по автомобилям
        krassula_by_vehicle = {}
        
        for _, row in self.krassula_data.iterrows():
            # Извлекаем номер карты из колонки "Номер карты" (последние 4 цифры)
            card_full = str(row['Номер карты'])
            card_number = self._extract_card_number(card_full)
            
            if card_number and card_number in self.card_to_vehicle_mapping:
                vehicle_number = self.card_to_vehicle_mapping[card_number]
                
                if vehicle_number not in krassula_by_vehicle:
                    krassula_by_vehicle[vehicle_number] = []
                
                krassula_by_vehicle[vehicle_number].append({
                    'datetime': row['Дата и время'],
                    'liters': row['Кол-во литров'],
                    'price': row['Цена со скидкой'],
                    'amount': row['Сумма со скидкой'],
                    'azs': row['АЗС'],
                    'card_number': card_number
                })
            else:
                # Карта не найдена в соответствиях - это нормально для карт других компаний
                logger.debug(f"Карта {card_number} не найдена в соответствиях (возможно, карта другой компании)")
        
        # Сопоставляем с данными ГЛОНАСС
        for vehicle_number, krassula_refuels in krassula_by_vehicle.items():
            if vehicle_number not in results:
                results[vehicle_number] = []
            
            # Получаем данные ГЛОНАСС для этого автомобиля
            glonass_refuels = self.glonass_refuel_data[
                self.glonass_refuel_data['vehicle_number'] == vehicle_number
            ].copy()
            
            # Сопоставляем каждую заправку
            for krassula_refuel in krassula_refuels:
                matched_refuel = self._find_matching_refuel(
                    krassula_refuel, glonass_refuels
                )
                
                if matched_refuel:
                    # Заправка найдена в обеих системах
                    result = {
                        'date': krassula_refuel['datetime'],
                        'krassula_liters': krassula_refuel['liters'],
                        'glonass_liters': matched_refuel['Заправлено'],
                        'difference': krassula_refuel['liters'] - matched_refuel['Заправлено'],
                        'odometer': matched_refuel['Пробег'],
                        'status': 'matched',
                        'azs': krassula_refuel['azs']
                    }
                else:
                    # Заправка только в Крассуле
                    result = {
                        'date': krassula_refuel['datetime'],
                        'krassula_liters': krassula_refuel['liters'],
                        'glonass_liters': None,
                        'difference': None,
                        'odometer': None,
                        'status': 'krassula_only',
                        'azs': krassula_refuel['azs']
                    }
                    
                    self.notifications.append({
                        'type': 'missing_glonass',
                        'vehicle': vehicle_number,
                        'date': krassula_refuel['datetime'],
                        'message': f"Заправка {krassula_refuel['liters']}л найдена только в Крассуле"
                    })
                
                results[vehicle_number].append(result)
        
        # Проверяем заправки только в ГЛОНАСС
        glonass_refuels = self.glonass_refuel_data
        for vehicle_number in glonass_refuels['vehicle_number'].unique():
            if pd.isna(vehicle_number):
                continue
                
            vehicle_glonass = glonass_refuels[
                glonass_refuels['vehicle_number'] == vehicle_number
            ]
            
            for _, glonass_refuel in vehicle_glonass.iterrows():
                # Проверяем, есть ли соответствующая заправка в Крассуле
                found_in_krassula = any(
                    abs((glonass_refuel['datetime'] - krassula_refuel['datetime']).total_seconds()) < 3600
                    for krassula_refuel in krassula_by_vehicle.get(vehicle_number, [])
                )
                
                if not found_in_krassula:
                    self.notifications.append({
                        'type': 'missing_krassula',
                        'vehicle': vehicle_number,
                        'date': glonass_refuel['datetime'],
                        'message': f"Заправка {glonass_refuel['Заправлено']}л найдена только в ГЛОНАСС"
                    })
        
        self.results = results
        logger.info(f"Сопоставление завершено для {len(results)} автомобилей")
        return results
    
    def _extract_card_number(self, comment: str) -> Optional[str]:
        """Извлекает номер карты из комментария"""
        if pd.isna(comment):
            return None
        
        # Ищем последние 4 цифры в комментарии
        numbers = re.findall(r'\d{4}', comment)
        return numbers[-1] if numbers else None
    
    def _find_matching_refuel(self, krassula_refuel: Dict, glonass_refuels: pd.DataFrame) -> Optional[Dict]:
        """
        Находит соответствующую заправку в данных ГЛОНАСС
        
        Args:
            krassula_refuel: Данные заправки из Крассулы
            glonass_refuels: DataFrame с заправками из ГЛОНАСС
            
        Returns:
            Dict: Найденная заправка или None
        """
        if glonass_refuels.empty:
            return None
        
        # Ищем заправку в пределах 2 часов
        time_diff = abs(glonass_refuels['datetime'] - krassula_refuel['datetime'])
        time_mask = time_diff <= timedelta(hours=2)
        
        if not time_mask.any():
            return None
        
        # Ищем по количеству литров (с учетом погрешности ±10%)
        liters_diff = abs(glonass_refuels['Заправлено'] - krassula_refuel['liters'])
        liters_mask = liters_diff <= krassula_refuel['liters'] * 0.1
        
        # Ищем пересечение по времени и количеству
        final_mask = time_mask & liters_mask
        
        if final_mask.any():
            return glonass_refuels[final_mask].iloc[0].to_dict()
        
        return None
    
    def calculate_fuel_consumption(self) -> Dict[str, List[Dict]]:
        """
        Рассчитывает расход топлива для каждого автомобиля
        
        Returns:
            Dict: Результаты расчета расхода топлива
        """
        logger.info("Начинаем расчет расхода топлива...")
        
        consumption_results = {}
        
        for vehicle_number, refuels in self.results.items():
            if not refuels:
                continue
            
            # Сортируем заправки по дате
            refuels_sorted = sorted(refuels, key=lambda x: x['date'])
            
            consumption_data = []
            
            for i, refuel in enumerate(refuels_sorted):
                if refuel['status'] != 'matched' or refuel['odometer'] is None:
                    continue
                
                # Находим предыдущую заправку с пробегом
                prev_odometer = None
                for j in range(i-1, -1, -1):
                    if (refuels_sorted[j]['status'] == 'matched' and 
                        refuels_sorted[j]['odometer'] is not None):
                        prev_odometer = refuels_sorted[j]['odometer']
                        break
                
                if prev_odometer is not None:
                    # Рассчитываем расход
                    distance = refuel['odometer'] - prev_odometer
                    if distance > 0:
                        consumption = (refuel['krassula_liters'] / distance) * 100
                        consumption = round(consumption, 2)
                    else:
                        consumption = None
                else:
                    consumption = None
                
                consumption_data.append({
                    'date': refuel['date'],
                    'liters': refuel['krassula_liters'],
                    'odometer': refuel['odometer'],
                    'distance': refuel['odometer'] - prev_odometer if prev_odometer else None,
                    'consumption': consumption,
                    'difference': refuel['difference'],
                    'status': refuel['status']
                })
            
            consumption_results[vehicle_number] = consumption_data
        
        logger.info(f"Расчет расхода завершен для {len(consumption_results)} автомобилей")
        return consumption_results
    
    def generate_excel_report(self, output_path: str) -> bool:
        """
        Генерирует итоговый Excel отчет
        
        Args:
            output_path: Путь для сохранения отчета
            
        Returns:
            bool: True если отчет создан успешно
        """
        try:
            logger.info(f"Создаем Excel отчет: {output_path}")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Основной лист с результатами
                main_data = []
                for vehicle_number, refuels in self.results.items():
                    for refuel in refuels:
                        main_data.append({
                            'Автомобиль': vehicle_number,
                            'Дата': refuel['date'],
                            'Литры (Крассула)': refuel['krassula_liters'],
                            'Литры (ГЛОНАСС)': refuel['glonass_liters'],
                            'Погрешность': refuel['difference'],
                            'Пробег': refuel['odometer'],
                            'Статус': refuel['status'],
                            'АЗС': refuel['azs']
                        })
                
                if main_data:
                    main_df = pd.DataFrame(main_data)
                    main_df.to_excel(writer, sheet_name='Основные данные', index=False)
                
                # Лист с уведомлениями
                if self.notifications:
                    notifications_df = pd.DataFrame(self.notifications)
                    notifications_df.to_excel(writer, sheet_name='Уведомления', index=False)
                
                # Лист со сливами
                if not self.glonass_drain_data.empty:
                    self.glonass_drain_data.to_excel(writer, sheet_name='Сливы', index=False)
            
            logger.info("Excel отчет успешно создан")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при создании Excel отчета: {e}")
            return False
    
    def print_notifications(self):
        """Выводит уведомления в консоль"""
        if not self.notifications:
            print("Уведомлений нет.")
            return
        
        print(f"\n=== УВЕДОМЛЕНИЯ ({len(self.notifications)}) ===")
        for i, notification in enumerate(self.notifications, 1):
            print(f"{i}. {notification['type'].upper()}")
            print(f"   Автомобиль: {notification['vehicle']}")
            print(f"   Дата: {notification['date']}")
            print(f"   Сообщение: {notification['message']}")
            print()

def main():
    """Основная функция программы"""
    print("=== АНАЛИЗАТОР РАСХОДА ТОПЛИВА ===")
    print("Программа для сопоставления данных Крассулы и ГЛОНАСС")
    print()
    
    analyzer = FuelConsumptionAnalyzer()
    
    # Пример использования (закомментирован)
    # analyzer.load_krassula_data("путь_к_файлу_крассулы.xlsx")
    # analyzer.load_glonass_data("путь_к_файлу_глонасс.xlsx")
    # analyzer.load_card_mapping({"0249": "497", "1234": "203"})
    # analyzer.match_refuels()
    # analyzer.calculate_fuel_consumption()
    # analyzer.generate_excel_report("отчет_расход_топлива.xlsx")
    # analyzer.print_notifications()
    
    print("Программа готова к использованию!")
    print("Используйте методы класса FuelConsumptionAnalyzer для загрузки данных и анализа.")

if __name__ == "__main__":
    main()
