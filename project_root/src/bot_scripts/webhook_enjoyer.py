import requests

def upload_to_gofile(file_path):

        # Открываем файл в бинарном режиме
        with open(file_path, 'rb') as file:
            # Делаем запрос на получение информации о сервере загрузки
            server_response = requests.get("https://api.gofile.io/getServer")
            server_data = server_response.json()

            if server_data['status'] == 'ok':
                # Получаем название сервера для загрузки
                server = server_data['data']['server']

                # Загружаем файл на полученный сервер
                upload_response = requests.post(
                    f"https://{server}.gofile.io/uploadFile",
                    files={'file': file}
                )
                upload_data = upload_response.json()

                if upload_data['status'] == 'ok':
                    # Получаем ссылку на загруженный файл
                    file_link = upload_data['data']['downloadPage']
                    return file_link
                else:
                    print(f"Ошибка при загрузке файла: {upload_data['status']}")
                    return None
            else:
                print(f"Ошибка при получении сервера: {server_data['status']}")
                return None


# Пример использования функции
file_path = 'Согласие.pdf'  # Замените на путь к вашему файлу
uploaded_file_link = upload_to_gofile(file_path)
if uploaded_file_link:
    print(f"Файл успешно загружен! Ссылка на файл: {uploaded_file_link}")
else:
    print("Не удалось загрузить файл.")
