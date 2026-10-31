#!/usr/bin/env bash
# Запуск тестов проекта: сначала unit_tests, затем integration_tests.
# Остановка при первом упавшем тесте (-x), а ненулевой код выхода
# сообщает TeamCity, что шаг завершился с ошибкой.
set -euo pipefail

cd "$(dirname "$0")"

echo "=== Unit tests ==="
python -m pytest tests/unit_tests -x

echo "=== Integration tests ==="
python -m pytest tests/integration_tests -x

echo "=== Все тесты пройдены ==="