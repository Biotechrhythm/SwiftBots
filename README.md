## TODO:
#### Ядро:
- Разделить бота на production и developer
- Нужно сделать некоторые команды плагинов исполняющимися без участия ядра. 
  Пример: tg_view должна без участия ядра исполнять некоторые команды adminpanel
- Сделать адекватным назначение main_view
- Кронтабы пока отключены
- Перенести конфиг в sqlite
- Разобраться, где error а где report
- Перегрузить SuperView.report, чтобы без аутентичного стиля отправлять в кор
- Реализовать как systemd сервис
- Мб засунуть в докер
- Было бы круто перебрать все try и определиться с единым поведением для отлавливания ошибок
- Через main.py создавать новые плагины и вьюшки
- Удалить мусорные скрипты, которые уже не используются
#### AI бот:
- Загрузку файлов сделать
- Справку по промптам
- Через час архивировать контекст
- Клавиатуру сделать с управлением контекстами
- Сделать выбор моделек, чисто потестить
- Сделать чо нибудь на /start
#### ВК:
- Адаптировать вк бота для новой версии станции
#### Admin Panel:
- Также администрирование кронтабов
- Администрирование ядра из под админ панели и из под main.py