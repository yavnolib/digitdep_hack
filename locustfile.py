# from locust import HttpUser, task, between


# class FlaskUser(HttpUser):
#     # Интервал времени между задачами
#     wait_time = between(1, 3)

#     @task
#     def test_async_example(self):
#         # Путь к маршруту Flask, который будем тестировать
#         with open("./flask-app/uploaded_files/SIPGA Project List.csv") as f:
#             self.client.post("/api/upload", data=f)
from locust import HttpUser, TaskSet, task, between

class UploadTaskSet(TaskSet):
    @task
    def upload_file(self):
        # Указываем путь к тестовому файлу, который будет отправлен на сервер
        file_path = '/home/igor/git/repositories/digitdep_hack/flask-app/uploaded_files/SIPGA Project List.xlsx'  # Замените на реальный файл

        # Открываем файл в бинарном режиме
        with open(file_path, 'rb') as file:
            # Определяем файл для загрузки
            files = {
                'file': (file_path, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }

            # Отправляем POST-запрос с файлом
            response = self.client.post("/api/upload", files=files)
            
            # Проверка успешного ответа
            if response.status_code == 200:
                print("Загрузка файла успешна")
            else:
                print(f"Ошибка загрузки файла: {response.status_code}")

class UploadTestUser(HttpUser):
    tasks = [UploadTaskSet]
    wait_time = between(1, 5)  # Задаем интервал ожидания между запросами
    host = "http://localhost:8080"  # Указываем адрес хоста
