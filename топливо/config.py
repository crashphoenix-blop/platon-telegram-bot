#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационный файл для анализатора расхода топлива
"""

# Настройки сопоставления заправок
MATCHING_SETTINGS = {
    # Максимальное время между заправками для сопоставления (в часах)
    'max_time_diff_hours': 2,
    
    # Максимальная разница в количестве литров для сопоставления (в процентах)
    'max_liters_diff_percent': 10,
    
    # Минимальный пробег для расчета расхода (в км)
    'min_distance_km': 10
}

# Настройки уведомлений
NOTIFICATION_SETTINGS = {
    # Включить уведомления о несоответствиях
    'enable_notifications': True,
    
    # Включить уведомления о сливах
    'enable_drain_notifications': True,
    
    # Максимальная погрешность ДУТ (в литрах)
    'max_dut_error_liters': 20
}

# Настройки расчета расхода
CONSUMPTION_SETTINGS = {
    # Округление расхода до знаков после запятой
    'consumption_decimal_places': 2,
    
    # Минимальный расход для валидации (л/100км)
    'min_consumption': 5,
    
    # Максимальный расход для валидации (л/100км)
    'max_consumption': 100
}

# Настройки файлов
FILE_SETTINGS = {
    # Кодировка для чтения файлов
    'encoding': 'utf-8',
    
    # Формат даты в файлах
    'date_format': '%d.%m.%Y %H:%M:%S',
    
    # Разделитель в CSV файлах
    'csv_delimiter': ';'
}

# Настройки логирования
LOGGING_SETTINGS = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'fuel_analysis.log'
}
