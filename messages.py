start_message = """
Это телеграмм бот, который поможет тебе следить за всем, что связанно с инвестициями,
а так же за  своим портфелем Тинькофф Инвестиции (если ты являешься их клиентом). 
С помощью этого бота ты сможешь получить красивое и информативное представление о ценных 
бумагах и о состоянии своего портфеля. Более того, есть возможность совершать операции 
с ценными бумагами прям из бота! Все функции бота можно получить командой /help \n
Ну а для того что бы все эти возможности были доступны, тебе необходимо зарегестрироваться 
"""

help_message = """
Список доступныx функций:\n
• /help - список доступных фукнций.
• /set_shares - установить список любимых акций для отслеживания стоимости.
• /show_shares - показать список выбранных акций.
• /set_level_price - установить уровень стоимости акции для отслеживания
• /get_portfolio - показать состояние портфеля (для пользователей Тинькофф).
• /show_graphics - ссылка на интерактивный график свеч.
• /send_share_graph - фото графиков акций
• /get_book - актуальный стакан
• /operations - функция для операций с ценными бумагами.
• /analyzer - запуск технического анализа.
• /change_account - сменить аккаунт Тинькофф Инвестиций.
• /settoken - установить/изменить токен.
• /delete - удалить профиль.\n
Вы их можете вызвать из главного меню.
"""

functional_message = """
"""
set_token_message = """
Введите токен от своего аккаунта Тинькофф Инвестиции(<a href="https://developer.tinkoff.ru/docs/intro/manuals/self-service-auth">как получить токен</a>). Вы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей. Для этого напиши /without_token
"""
choose_accounts_message = """
Токен авторизирован.
Теперь Вам нужно выбрать с каким аккаунтом Тинькофф Инвестиции мы будем 
работать.
Для этого укажите порядковый номер аккаунта из списка:
"""

set_shares_message = """
Теперь вам предоставляется возможность выбрать до 10 интересующих Вас ценных бумаг.
После выбора, ежедневно в 11 дня Вам будет приходить информация о выбранных ценных бумагах - процент изменения за предыдущий день. 
Для выбора введите /set_shares
"""

operation_message = '''
    Доступные операции
    1 : Покупка по рынку
    2 : Продажа по рынку
    3 : Лиминая заявка на покупку
    4 : Лимитная заявка на продажу
'''
buying_message_m = '''
Введите: (ТИКЕР) (КОЛ-ВО_ЛОТОВ) (ЦЕНА - опционально). Важно вводить именно в таком порядке. 
Пример запроса: 
<b>SBER 10 298.5</b> - купить 10 акций Cбербанка по цене 298.5
<b>SMLT 2</b>- купить 2 акции Самолет по "лучшей цене"
(Дробную цену нужно писать через точку)
'''

selling_message_m = '''
Введите: (ТИКЕР) (КОЛ-ВО_ЛОТОВ) (ЦЕНА - опционально). Важно вводить именно в таком порядке. 
Пример запроса: 
<b>SBER 10 298.5</b> - продать 10 акций Cбербанка по цене 298.5
<b>SMLT 2</b>- продать 2 акции Самолет по "лучшей цене"
(Дробную цену нужно писать через точку)
'''

selling_message_l = '''
Введите: (ТИКЕР) (КОЛ-ВО_ЛОТОВ) (ЦЕНА - обязательно). Важно вводить именно в таком порядке. 
Пример запроса: 
<b>SBER 10 298.5</b> - продать 10 акций Cбербанка по цене 298.5
<b>SMLT 2 170</b>- продать 2 акции Самолет по цене 170
(Дробную цену нужно писать через точку)
'''
buying_message_l= '''
Введите: (ТИКЕР) (КОЛ-ВО_ЛОТОВ) (ЦЕНА - обязательно). Важно вводить именно в таком порядке. 
Пример запроса: 
<b>SBER 10 298.5</b> - купить 10 акций Cбербанка по цене 298.5
<b>SMLT 2 170</b>- купить 2 акции Самолет по цене 170
(Дробную цену нужно писать через точку)
'''

exeptions= {
    '-1' : 'Ошибка!',
    '0' : 'Эта функция доступна только пользователем с Токеном\nЧто бы ввести токен есть функция /settoken',
    '1' : 'Что-то не так',
    '2' : 'Уровень доступа Токена не позваляет совершать операции с данным аккаунтом',
    '3' : 'Такой акции не существует, повторите попытку с корректным тикером',
    '4' : 'Что- то сломалось',
    '30079' : 'Инструмент недоступен для торгов',
    '30017' : 'Входной параметр price является обязательным. Укажите корректный параметр price. Значение параметра price должно быть положительным.',
    '30018' : 'Входной параметр price имеет некорректное значение. Укажите корректный параметр price',
    '30034' : '	Недостаточно средств для совершения сделки',
    '30042' : 'Недостаточно активов для маржинальной сделки.',
    '30047' : 'Валюта цены не совпадает с валютой расчётов по инструменту. Этот момент пока не продуман в нашем боте',
    '30049' : 'Ошибка метода выставления торгового поручения.',
    '30052' : 'Для данного инструмента недоступна торговля через API.',
    '30054' : 'Тип инструмента не инвестиционный фонд или акция',
    '30068' : 'В настоящий момент возможно выставление только лимитного торгового поручения',
    '30077' : 'Метод недоступен для внебиржевых инструментов.',
    '30080' : 'Количество лотов должно быть положительным числом',
    '30081' : 'Аккаунт закрыт',
    '30082' : 'Аккаунт заблокирован',
    '30084' : 'Превышен лимит запрашиваемого периода',
    '30092' : 'Торги недоступны по нерабочим дням.',
    '30094' : 'Выставление заявок по опционам недоступно.',
    '30095' : 'Заявка не исполнена биржей.\nЛимитная заявка может не исполняться по причине недостижения установленной цены на бирже.Рыночная же может не исполняться по причине отсутствия сделок с данными инструментов (низкая ликвидность)',
    '30096' : 'Заявка отклонена, попробуйте повторить позже',
    '30097' : 'Сейчас эта сессия не идёт.',
    '30098' : 'Торги по этому финансовому инструменту сейчас не проводятся. Проверьте актуальный торговый статус инструмента',
    '30099' : 'Цена вне лимитов по инструменту или цена сделки вне лимита.',
    '30100' : 'Цена должна быть положительной',
    '30101' : 'Для торговли этим инструментом пройдите тестирование. О том, как сдать тестирование и кому оно нужно читайте в статье https://www.tinkoff.ru/finance/blog/test-invest/',
    '30103' : 'Для инструмента доступно выставление заявки только типа "лучшая цена"',
    '40002' : 'Недостаточно прав для совершения операции. Токен доступа имеет уровень прав read-only, либо у токена нет доступа к указанному счету.',
    '40003' : 'Токен доступа не найден или не активен.',
    '40004' : 'Выставление заявок недоступно с текущего аккаунта. Брокерский счет не найден, не принадлежит пользователю или закрыт, либо на пользователе ограничения (от Tinkoff Invest API или от биржи). В этом случае нужно обратиться в техподдержку',
    '50002' : 'Инструмент не найден. Укажите корректный идентификатор инструмента',
    '50008' : 'Отсутствует источник данных по стаканам',
    '70001' : 'Внутренняя ошибка сервиса. Если ошибка повторяется, обратитесь в службу технической поддержки',
    '70002' : 'Неизвестная сетевая ошибка, попробуйте выполнить запрос позднее.',
    '70003' : 'Внутренняя ошибка сервиса, попробуйте выполнить запрос позднее.',
    '80002' : 'Превышен лимит запросов в минуту',
    '90001' : 'Требуется подтверждение операции. Операция возможна только в приложении Тинькофф Инвестиции',
    '90002' : 'Торговля этим инструментом доступна только квалифицированным инвесторам',
    '90003' : 'Цена заявки слишком высокая. Разбейте заявку на заявки меньшего размера.'
}

cancelling = '''Отмена действия.
'''

set_price_level = ''' Для отслеживания стоимости акции введите данные в следующем формате (без скобок):
(ТИКЕР) ("+" отслеживание превышения стоимости / "-" ниже стоимости) (Стоимость для отслеживания).
<b>Пример ввода для отслеживания превышения стоимости Сбербанка в 250 рублей:</b>
SBER + 250
'''

analyzer_message_tickers = '''Нажмите "Использовать shares" или введите тикеры акций через пробел.
<i>Например: SBER AAPL</i>'''

analyzer_message_date = '''Теперь через пробел введите дату начала и дату конца периодна анализа (в формате <b>yyyy-mm-dd</b>)
<i>Например: 2022-06-04 2023-04-23</i>'''
