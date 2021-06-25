### Последовательности запуска в Jenkins
1) Selenoid;
2) MySQL Percona;
3) Mock VK API;
4) Приложение для тестирования (myapp);
5) Фреймворк для тестирования (tests).

### Необходимые плагины в Jenkins

* Allure
* Post Build Script

### Настройки Item'а в Jenkins
1) Название проекта: "<b>ApplicationTestingV2</b>";
2) Выбираем пункт: "<b>Удалять устаревшие сборки</b>";
3) Выбираем пункт: "<b>Разрешить параллельный запуск</b>";
4) Для управления исходным кодом используем текущий репозиторий с исходным проектом:
   1) Ссылка на git: ```git@github.com:MatveevKirill/2021-1-MAILRU-SDET-Python-K-Matveev.git```;
   2) Данные для входа: по SSH или по паролю;
   3) Ветка: ```*/main```.
5) Выбираем пункт: "<b>Delete workspace before build starts</b>";
6) В "<b>Среде сборки</b>" выполняем команду shell:
```shell
# Задать имя сети в переменной окружения.
export NETWORK_NAME="network_${JOB_NAME}_${BUILD_NUMBER}"

# Создание директорий для отчётов.
mkdir $WORKSPACE/alluredir
mkdir $WORKSPACE/logs
mkdir $WORKSPACE/selenoid/logs

# Сменить директорию на финальный проект.
cd final_project

# Создать docker-сеть.
docker network create ${NETWORK_NAME}

# Запуск compose.
docker-compose --file prod.docker-compose.yml --abort-on-container-exit
```
7) В "<b>Послесборочной операции</b>" выбираем шаг "<b>Execute scripts</b>" и выполняем команду shell:
```shell
# Сменить директорию на финальный проект.
cd final_project

# Остановка всех контейнеров.
docker-compose --file prod.docker-compose.yml down

# Удаление docker-сети.
docker network rm network_${JOB_NAME}_${BUILD_NUMBER}
```
8)  В "<b>Послесборочной операции</b>" выбираем "<b>Allure Report</b>" и вводим директорию для отчётов: ```/reports/alluredir```
