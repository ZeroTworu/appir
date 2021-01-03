### Whereby Wipe v0.2.6

#### История версий
* v0.0.1 - первый рабочий прототип
* v0.1.0 - стабильно работающий прототип, только на FireFox
* v0.2.0 - стабильно работающий прототип с поддержкой Firefox и Chrome
* v0.2.3 - стабильно работающий прототип с WebUI
* v0.2.4 - не стабильная версия, поломан Chrome, добавлен `ControlThread` проверяющий на пидорнутость во время вайпа.
* v0.2.5  
  * добавлен генератор ников для ботов, на выбор `uuid`, `russian`, `english`, `mixed` и `zalgo`
    как не сложно догадаться самый красивый - `zalgo`, он же теперь по умолчанию.
  * Новые ключи `--name-generator` - задаёт используемый генератор и `--name-length` - задаёт длину ника
  * Исправлены работы стратегий `fill` и `youtube` теперь они работают стабильней.
  * Chrome опять начал работать, но на долголи - хз.
  * Мелкие правки в работе драйверов для FF/Chrome
* v0.2.6
  * Добавлена новая стратегия `EnterExitStrategy` - рандом залетает в комнату на короткое время (от 1й до 5ти секунд)
    после чего выходит в сочетании с `--fake-media=1` и `--max-users=5` (ну около 5, не сильно много в общем)
    выглядит просто адава например. название для запуска `ee`
  * Добавлена проверка на `You’ve not been granted access` чёт новое в аппире, борются с вайпами как могут видимо.
  * Добавлен context manager `StructureExceptionHandler` контролирующий работу стратегий и перезапускающий стратегию в
    случае необработанного исключения. `KeyboardInterrupt` он пропускает, так что по `ctrl+c` убить всё ещё можно.
  * Отключена загрузка картинок, для ускорения работы и уменьшения жора памяти
  * Пофикшена работа с Fire Fox 84
* v0.3.0
  * Многопоточность, проверял со всеми стратегиями крому `youtube` и `flood` т.к. там это лишено смысла.
  * Новая стратегия `EnterRefreshStrategy`, для запуска `er` то же самое что `ee` - только работает быстрее и хорошо
    ложиться на многопоток
  * `--threads=` - кол-во потоков для вайпа.
  * `--use-barrier=` `1` - включает барьер, по дефолту `0` - выключено. Эксперементальная пока опция, застравляет потоки
    ждать пока все подсоеденятся к аппиру и только потом ломиться в конфу.

#### Простой запуск
* Шаг 1:
```
docker run -p 5000:5000 hanyuu/wwipe:<нужная версия>
```
* Шаг 2:
  Открыть http://127.0.0.1:5000/
  На данный момент, `WebUI` сильно не дотягивает до консольного режима, ждём кеапыню когда он напишит нормальный.

#### Памятка для любителей Шиндоус

* Docker работает только в десяточке
* Доки [тут](https://docs.docker.com/docker-for-windows/)

#### Для любителей консолечки-пердолечки

* Python >= 3.8
  * Для винды последний 3.8 качаем [отсюда](https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe), прыщебляди
    ставят из своего пакетного менеджера.
* Установить [chromedriver](https://chromedriver.chromium.org/)
  или [geckodriver](https://github.com/mozilla/geckodriver/releases) (можно оба, если будешь юзать FF и Chrome)
  * Скаченный driver положить туда, куда смотрит переменная окружения `PATH` (для винды это `c:\windows`, а прыщебляди и
    так знают)
* Устанавливаем `git` для винды [тут](https://git-scm.com/download/win) линуксоиды как обычно идут в свой менеджер
  пакетов.
* открываем коммандную строку (`пуск->выполнить->cmd`)
  * пишем `git https://github.com/Hanyuusha/wwipe.git`
  * Переходим в склонированную директорию с вайпалкой.
  * `pip install poetry`
  * `poetry install`
* Пример запуска `python main.py fill https://whereby.com/123 --headless=1 --fake-media=1 --browser=chrome`
* Ещё всегда есть `python main.py -h`

#### краткая справка по параметрам

* `python main.py <strategy> <url>` запуск с полностью дефолтными параметрами с выбранной стратегией вайпа на указанную
  конфу
  * `fill` - Стратегия пытающаяся заполнить комнату до лимита
  * `youtube` включает на короткое время ролики с ютуба в конфе, требует параметр `--link=YOUTUBE URL` со ссылкой на
    ютуб или `--file=PARH TO FILE` с полным путём до майла со ссылками на ютуб-ролики (один ролик - одна строка)
  * `flood` - флудит в чятик, требует или `--file=PATH TO FILE` путь до файла со списком фраз, или `--phrase=PHRASE` для
    флуда одной фразой
  * `ee` EnterExit, в комнату заходит чувак на сулчайный промежуток времени. Особенно эффективно
    с `--threads=NUM OF THREADS`, `--max-users=NUM OF MUX USERS PER THREAD`
    и `--fake-media=1`
  * `er` EnterRefresh - гораздо более весёлая стратегия чем предыдущая, не тратится время на полный перезаход в комнату,
    только на обновление страницы. В силу это пока для неё не работает параметр `--max-users`

#### Дополнительные параметры

* `--use-barrier=1` использовать паттерн "барьер", имеет смысл только в многопотоке (при `--threads=2` или более), по
  умолчанию `0`
* `--browser=BROWSER` какой браузер использовать `firefox` или `chrome` хром чуть быстрее показал себя, но у него
  скучный `--fake-media` а кроме того, даже в инкогнито режиме, он логинится только один раз.
* `--fake-media=` принимает `1` или `0` для Firefox тогда будут красивые переливающиеся квадраты, для Chrome - экран "
  радара" с обратным отсчётом, по умолчанию `1`
* `--headless=` принимает `1` или `0` по умолчанию `1` - браузер запускается без графического режима, если же некуда
  девать память или охота посмотреть на дестрой учинённый вайпалкой можно выставить в `0`
  Firefox работает странно под webdriver и открывает куча новых окон, вместо кучи вкладок, имей это ввиду включая вывод
  графики!

#### Известные баги

* v.0.2.4 - поломан Chrome