from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)



@app.route('/webhook_test', methods=['POST'])
@cross_origin()
def webhook():
    if request.headers.get('content-type') == 'application/json':
        data = request.json  # Получение JSON данных из POST-запроса
        print(f"Получены данные: {data}")
        # Обработка данных
        return 'OK', 200
    else:
        return 'Unsupported Media Type', 415


if __name__ == '__main__':
    # Запуск сервера на порту 5000
    app.run(host='0.0.0.0', port=5000)
