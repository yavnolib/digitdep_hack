# Dockerfile for ubuntu_client
FROM ubuntu:latest

# Устанавливаем зависимости и настраиваем локаль
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y locales postgresql-client python3 python3-pip python3-venv libpq-dev && \
    locale-gen en_US.UTF-8 && \
    export LANG=en_US.UTF-8 && \
    export LC_ALL=en_US.UTF-8

# Создаем виртуальное окружение и устанавливаем зависимости из requirements.txt
RUN python3 -m venv /mnt/venv
COPY requirements.txt /mnt/requirements.txt
RUN /mnt/venv/bin/pip install -r /mnt/requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /mnt
ENTRYPOINT ["sleep", "infinity"]
