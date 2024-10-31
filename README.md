# **ЧЕРНОВОЙ ВАРИАНТ** сервиса автоматического лотирования заявок на закупку МТР

## Описание
В настоящее время процесс ручного формирования лотов на закупки ресурсов является довольном проблематичным: много видов закупаемых материалов, разные даты поставки и формирования заявок, закупщики находятся в разных городах на довольно больших расстояниях друг от друга. Данный алгоритм предназначен для автоматизации процесса лотирования заявок на закупку материально-технических ресурсов (МТР). Он позволяет эффективно распределять заявки по лотам, учитывая различные критерии, такие как местоположение грузополучателей, время и виды поставляемых товаров.

Граммотное и качественное формирование лотов позволит повысить интерес к лоту у поставщиков, предоставляя лоты, наиболее релевантные возможностям поставщиков. Правильное формирование лотов также позволяет снизить затраты на логистику.

## Алгоритм
Сервис призван автоматизировать формирование лотов на закупку ресурсов. Проблемы ручной разметки: слишком большое количество ресурсов, разные даты поставки и формирования заявок

## Установка из переданных докер-образов (!РЕКОМЕНДУЕТСЯ!)
1. В качестве финального решения репозиторий был передан в формате двух докер-образов: `ubuntu_client_image_latest.tar.gz` и `gpn_postgres_db_image_latest.tar.gz`.
2. Чтобы установить и запустить сервис из переданных докер образов введите:
   ```
   docker network create db_network
   docker run --name gpn_postgres_db --network db_network -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=12345678 -e POSTGRES_DB=lotdb -p 7799:5432 gpn_postgres_db_image
   ```
   Далее, после сообщений о том, что образ запущен и база данных работает, необходимо ввести в новом терминале:
   ```
   docker run -it --name ubuntu_client --network db_network -p 7892:8080 ubuntu_client_image
   ```
3. На этом моменте сервис является полностью запущенным и готовым к работе. Для тестирования перейдите по ссылке:
   ```
   https://0.0.0.0:7892
   ```

## Установка из репозитория. Внимание! Необходимо наличие переданного архива data.zip.

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/yavnolib/digitdep_hack.git
   ```
   or
   ```bash
   git clone git@github.com:yavnolib/digitdep_hack.git
   ```
2. Перейдите в директорию проекта:
   ```bash
   cd digitdep_hack
   ```
3. Скачайте предоставленный архив data.zip и распакуйте его в корне проекта:
   ```
   unzip data.zip
   ```
4. Запустите и дождитесь окончания сборки проекта:
```
docker compose build --no-cache
```
5. Запустите сервис:
```
docker compose up
```
6. Бэкенд будет полностью готов к работе через 10 секунд. Войдите в контейнер `ubuntu_client`:
```
docker exec -it ubuntu_client bash
```

## Дополнительно

1. При необходимости запустить парсер координат адресов **новых** грузополучателей (например, из файла /mnt/buyer.xlsx в котором **нет координат**) и обновления базы данных координат грузополучателей введите:
```
python3 db_controller.py --mode 1 --buyer_path /mnt/buyer.xlsx
```

2. Чтобы обновить базу данных координат грузополучателей из файла buyer.xlsx **с уже имеющимися координатами** введите:
```
python3 db_controller.py --mode 2 --buyer_path /mnt/buyer.xlsx
```
Внимание! CSV-файл в таком случае должен быть вида:
```
code, addr, geo
1234,"Адрес","100.0,110.0"
```
где координаты записаны в формате: `"<degrees NORTH latitude>,<degrees EAST longitude>"`. Если получатель с таким кодом уже есть в базе данных, то он НЕ будет перезаписан.

### Параметры:
- `input`: путь к файлу с заявками на закупку (формат: .xlsx)
