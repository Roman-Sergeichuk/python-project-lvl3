# Page-loader by Roman-Sergeichuk

[![Maintainability](https://api.codeclimate.com/v1/badges/2acfcaa2ce739e74d45e/maintainability)](https://codeclimate.com/github/Roman-Sergeichuk/python-project-lvl3/maintainability)

[![Test Coverage](https://api.codeclimate.com/v1/badges/2acfcaa2ce739e74d45e/test_coverage)](https://codeclimate.com/github/Roman-Sergeichuk/python-project-lvl3/test_coverage)

[![Build Status](https://travis-ci.com/Roman-Sergeichuk/python-project-lvl3.svg?branch=master)](https://travis-ci.com/Roman-Sergeichuk/python-project-lvl3)

## Описание
CLI-утилита для скачивания веб-страниц из интернета.
Возможности утилиты:
Помимо самой html-страницы, скачивает в отдельную папку локальные ресурсы (картинки, ссылки, скрипты), необходимые для правильного отображения страницы на локальной машине. Производит логирование в отдельный файл (уровень логирования и директорию скачивания можно задать при запуске утилиты).

## Установка
Для установки пакета воспользуйтесь следующей командой:

    python3 -m pip install --user --upgrade --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple page-loader-by-roman-sergeichuk

Пример установки и запуска утилиты показан ниже.

### Загрузка веб-страницы в виде одного html-файла
[![asciicast](https://asciinema.org/a/OnSawt87QlJKfVZvFe5EtIV2f.svg)](https://asciinema.org/a/OnSawt87QlJKfVZvFe5EtIV2f)
### Загрузка веб-страницы с локальными ресурсами
[![asciicast](https://asciinema.org/a/bDnkMPCKI1dlKZnufiLttqLix.svg)](https://asciinema.org/a/bDnkMPCKI1dlKZnufiLttqLix)
### Загрузка веб-страницы с функцией логирования
[![asciicast](https://asciinema.org/a/FuaquONrFhtThvMwW22GDswy5.svg)](https://asciinema.org/a/FuaquONrFhtThvMwW22GDswy5)
### Обработка ошибок
[![asciicast](https://asciinema.org/a/oO6iajhRAzPKuCTn5OaTDH8UP.svg)](https://asciinema.org/a/oO6iajhRAzPKuCTn5OaTDH8UP)
### Детализированный процесс загрузки
[![asciicast](https://asciinema.org/a/4zkm6PuPSi6QQqBZKMKzOwOdU.svg)](https://asciinema.org/a/4zkm6PuPSi6QQqBZKMKzOwOdU)
### Работа версии 0.6.0 (Одна полоска прогресса вместо трех)
[![asciicast](https://asciinema.org/a/DDuFeRPaYAhOjGE4EtUa5Gvoj.svg)](https://asciinema.org/a/DDuFeRPaYAhOjGE4EtUa5Gvoj)