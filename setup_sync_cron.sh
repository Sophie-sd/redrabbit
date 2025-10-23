#!/bin/bash

# Скрипт для налаштування автоматичної синхронізації з картинками
# Запуск: ./setup_sync_cron.sh

set -e

PROJECT_DIR="/Users/sofiadmitrenko/Sites/intshop"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        НАЛАШТУВАННЯ СИНХРОНІЗАЦІЇ З КАРТИНКАМИ                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Створюємо cron job файл
CRON_FILE="/tmp/intshop_sync_cron.txt"

# Поточні cron jobs
crontab -l > "$CRON_FILE" 2>/dev/null || true

# Видаляємо старі завдання якщо є
grep -v "sync_with_images\|download_all_images\|update_prices" "$CRON_FILE" > "${CRON_FILE}.tmp" 2>/dev/null || true
mv "${CRON_FILE}.tmp" "$CRON_FILE" 2>/dev/null || true

echo "Налаштовуємо автоматичну синхронізацію..."
echo ""

# Додаємо нові завдання
echo "" >> "$CRON_FILE"
echo "# Автоматична синхронізація товарів з картинками (кожні 2 години)" >> "$CRON_FILE"
echo "0 */2 * * * cd $PROJECT_DIR && source venv/bin/activate && python3 sync_with_images.py >> /tmp/intshop_sync.log 2>&1" >> "$CRON_FILE"

echo "" >> "$CRON_FILE"
echo "# Повний імпорт товарів (щодня о 8 ранку)" >> "$CRON_FILE"
echo "0 8 * * * cd $PROJECT_DIR && source venv/bin/activate && python3 initial_import.py >> /tmp/intshop_import.log 2>&1" >> "$CRON_FILE"

echo "" >> "$CRON_FILE"
echo "# Масове завантаження картинок для товарів без зображень (щодня о 3 ранку)" >> "$CRON_FILE"
echo "0 3 * * * cd $PROJECT_DIR && source venv/bin/activate && python3 download_all_images.py >> /tmp/intshop_images.log 2>&1" >> "$CRON_FILE"

# Встановлюємо crontab
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "✅ Автоматична синхронізація налаштована успішно!"
echo ""
echo "📋 Розклад завдань:"
echo "   • Синхронізація (ціни + картинки): кожні 2 години"
echo "   • Повний імпорт: щодня о 8:00"
echo "   • Масове завантаження картинок: щодня о 3:00"
echo ""
echo "📁 Логи:"
echo "   • Синхронізація: /tmp/intshop_sync.log"
echo "   • Імпорт: /tmp/intshop_import.log"
echo "   • Картинки: /tmp/intshop_images.log"
echo ""
echo "🛠️  Корисні команди:"
echo "   • Переглянути поточні завдання: crontab -l"
echo "   • Редагувати завдання: crontab -e"
echo "   • Переглянути логи: tail -f /tmp/intshop_*.log"
echo ""
