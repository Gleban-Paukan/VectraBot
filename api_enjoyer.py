from amocrm.v2 import tokens, Lead
tokens.default_token_manager(
    client_id="19c77149-b80a-4b49-88a1-e400f3f70bac",
    client_secret="y0fnkZ0Bc2Qodcf6gLUOuiq9rHYWCyTX43xzmH8mIvH8xETo6DnJxvvgHzHEgu0H",
    subdomain="vektra",
    redirect_url="https://yandex.ru",
    storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
)
lead = Lead(
    name='Test1',
    price=10000,  # Цена лида
)

# Сохранение лида в AmoCRM
lead.save()

print(f"Лид создан с ID: {lead.id}")
# import requests
#
# # URL вашего сервера
# url = 'http://192.168.0.79:5000/webhook_test'
#
# # Данные, которые вы хотите отправить
# data = {
#     "name": "John Doe",
#     "email": "john.doe@example.com",
#     "message": "Hello from the other side!"
# }
#
# # Отправка POST-запроса с JSON данными
# response = requests.post(url, json=data)
#
# # Печать ответа сервера
# print(f"Status Code: {response.status_code}")
# print(f"Response Text: {response.text}")
