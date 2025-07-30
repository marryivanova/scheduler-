# 🗓 Scheduler System API

## 📌 Overview
Система управления расписанием сотрудников с возможностью:
- Просмотра занятых/свободных интервалов
- Проверки доступности временных слотов
- Поиска окон для задач заданной длительности

## 🚀 Quick Start

### Установка
```bash
git clone https://github.com/marryivanova/scheduler-.git
cd scheduler
pip install poetry
poetry install
```

Пример взаимодействия:

```bash
========================================
SCHEDULER SYSTEM MENU
========================================
1. View busy time slots for a date
2. View free time slots for a date
3. Check time slot availability
4. Find first available slot for duration
5. Exit
========================================
Enter your choice (1-5): 1
Enter date (YYYY-MM-DD): 2025-02-15

Busy time slots for 2025-02-15:
- 17:30 to 20:00
- 09:00 to 12:00

Press Enter to continue...

========================================
SCHEDULER SYSTEM MENU
========================================
1. View busy time slots for a date
2. View free time slots for a date
3. Check time slot availability
4. Find first available slot for duration
5. Exit
========================================
Enter your choice (1-5): 5
Exiting the Scheduler System. Goodbye!
```

Как запустить тесты -> `py -m pytest tests/`

Получаем:

```bash
tests/test_real_all_api.py::test_get_busy_slots PASSED                                                                                                    [  8%]
tests/test_real_all_api.py::test_get_free_slots PASSED                                                                                                    [ 16%] 
tests/test_real_all_api.py::test_is_available PASSED                                                                                                      [ 25%] 
tests/test_real_all_api.py::test_real_is_available PASSED                                                                                                 [ 33%] 
tests/test_real_all_api.py::test_real_find_slot_for_duration PASSED                                                                                       [ 41%] 
tests/test_real_all_api.py::test_real_api_errors PASSED                                                                                                   [ 50%]
tests/test_unit_mock.py::test_api_response_structure PASSED                                                                                               [ 58%]
tests/test_unit_mock.py::test_get_busy_slots PASSED                                                                                                       [ 66%] 
tests/test_unit_mock.py::test_get_free_slots PASSED                                                                                                       [ 75%] 
tests/test_unit_mock.py::test_is_available PASSED                                                                                                         [ 83%] 
tests/test_unit_mock.py::test_find_slot_for_duration PASSED                                                                                               [ 91%] 
tests/test_unit_mock.py::test_api_error_handling PASSED                                                                                                   [100%] 

====================================================================== 12 passed in 0.81s ====================================================================== 
```