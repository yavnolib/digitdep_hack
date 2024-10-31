# Dockerfile for ubuntu_client
FROM ubuntu:latest

# Устанавливаем зависимости и настраиваем локаль
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y locales postgresql-client python3 python3-pip libpq-dev && \
    locale-gen en_US.UTF-8 && \
    export LANG=en_US.UTF-8 && \
    export LC_ALL=en_US.UTF-8

# Копируем requirements.txt
COPY requirements.txt /mnt/requirements.txt
COPY . /mnt/
# Устанавливаем зависимости из requirements.txt с использованием --break-system-packages
RUN pip3 install --break-system-packages -r /mnt/requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /mnt

# Команда для запуска вашего скрипта и затем bash
CMD ["bash", "-c", "python3 /mnt/db_controller.py --mode 0 --cache_folder /mnt/cache && exec bash"]
