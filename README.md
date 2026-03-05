<div align="center">
  <h1>👕 Clothify – Telegram Shop Bot (MVP)</h1>
  <p><b>Готовое решение для запуска интернет-магазина в Telegram: каталог, корзина и админ-панель </b></p>

---

## 📱 Демонстрация интерфейса

<table align="center">
  <tr>
    <td align="center">
      <b>🛍 Каталог товаров</b><br>
      <img src="https://github.com/user-attachments/assets/fc15cee8-5509-441a-815c-660919c32d92" width="400" />
    </td>
    <td align="center">
      <b>📏 Карточка и выбор размера</b><br>
      <img src="https://github.com/user-attachments/assets/a9623bc7-31d4-4f95-b4ab-dde65083b41f" width="400" />
    </td>
  </tr>
  <tr>
    <td align="center">
      <b>⚙️ Панель управления (Admin)</b><br>
      <img src="https://github.com/user-attachments/assets/ce6b83ab-6d63-49f0-b06b-5300dadee0d9" width="400" />
    </td>
    <td align="center">
      <b>➕ Добавление товара</b><br>
      <img src="https://github.com/user-attachments/assets/cea9dbe0-9635-48e6-a85b-eed496d8c6d5" width="400" />
    </td>
  </tr>
</table>

<br>

<div align="center">
  <h3>🚀 Процесс покупки (Видео-демо)</h3>
  <video src="https://via.placeholder.com/280x600/151B23/FFFFFF?text=Video+Placeholder" width="280" autoplay loop muted playsinline style="border-radius: 20px;"></video>
</div>

---

## ✨ Основной функционал (Value Proposition)

Полноценная витрина внутри мессенджера — покупка в 3 клика без переходов на внешние сайты.

### 👤 Для покупателей
* 🛍 **Интерактивный каталог:** Удобный просмотр товаров с фотографиями, ценами и подробным описанием.
* 📏 **Умный выбор:** Встроенная система выбора размера или модификации перед добавлением в корзину.
* 📍 **Быстрый чекаут:** Минималистичная форма оформления заказа (только адрес и username).
* 🌐 **Мультиязычность (i18n):** Автоматическое определение языка пользователя (RU / EN).

### 🛡 Для администраторов (`/admin`)
* ⚙️ **Управление витриной:** Добавление, редактирование и удаление ассортимента прямо со смартфона.
* 📦 **Менеджмент заказов:** Моментальные уведомления о новых продажах и удобное изменение их статусов.
* 📊 **Аналитика:** Отслеживание конверсий, общего количества продаж и выручки.
* 🔐 **Безопасность:** Строгий контроль доступа по Telegram ID.

---

## 🏗 Архитектура и под капотом

Проект построен на современной асинхронной базе с упором на производительность и расширяемость:

* **Стек:** `Python 3.10+`, `aiogram 3.x`, `aiosqlite`.
* **Паттерны:** Router-based (строгая модульная структура) и FSM (Finite State Machine) для защиты от сбоев в процессе диалога оформления заказа.
* **База данных:** Легковесная SQLite для мгновенного развертывания MVP.

<details>
<summary><b>📂 Посмотреть структуру проекта</b></summary>
<br>

```text
├── core/             # Глобальные конфиги и настройки
├── database/         # Слой асинхронной работы с БД
├── filters/          # Кастомные фильтры (защита Admin-зоны)
├── handlers/         # Обработчики команд и пользовательских ивентов
├── keyboards/        # Сборка динамических Inline и Reply клавиатур
├── locales/          # Система интернационализации (i18n)
├── scripts/          # Скрипты для сидирования (наполнения) базы
├── states/           # Состояния FSM (чекаут, админка)
└── utils/            # Вспомогательные хелперы
```
</details>

---

## 🚀 Быстрый старт

### 1. Подготовка окружения
Склонируйте репозиторий и создайте файл конфигурации:
```bash
git clone [https://github.com/m1sstak3/clothify-tg-bot.git](https://github.com/m1sstak3/clothify-tg-bot.git)
cd clothify-tg-bot
cp .env.example .env
```
*Укажите в `.env` ваш `BOT_TOKEN` и `ADMIN_IDS` (свой ID можно узнать у @userinfobot).*

### 2. Установка и запуск (Локально)
```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install -r requirements.txt

# Наполните базу данных тестовыми товарами
python scripts/seed.py

# Запустите бота
python main.py
```

---

## 📈 Планы по развитию (Roadmap)

- [ ] Интеграция с Telegram Payments (Stripe, ЮKassa, CloudPayments).
- [ ] Система промокодов, скидок и реферальных ссылок.
- [ ] Интеграция с логистическими API (СДЭК / Почта РФ) для расчета доставки.
- [ ] Полноценная админ-панель через Telegram WebApp (Mini Apps).

---

<div align="center">
  <p>Проект распространяется под лицензией MIT. Подробности в файле <a href="LICENSE">LICENSE</a>.</p>
  <b>Developed with ❤️ by m1sstak3</b>
</div>
