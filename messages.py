start_message = """
Это телеграмм бот, который поможет тебе следить за всем, что связанно с инвестициями,
а так же за  своим портфелем Тинькофф Инвестиции (если ты являешься их клиентом). 
С помощью этого бота ты сможешь получить красивое и информативное представление о ценных 
бумагах и о состоянии своего портфеля. Более того, есть возможность совершать операции 
с ценными бумагами прям из бота! Все функции бота можно получить командой /help \n
Ну а для того что бы все эти возможности были доступны, тебе необходимо зарегестрироваться 
"""

help_message = """
Список доступным функций:\n
• /help - список доступных фукнций.\n
• /settoken - установить/изменить токен (для пользователей Тинькофф Инвестиций).\n
• /set_shares - установить список любимых акций для отслеживания стоимости.\n
• /show_shares - показать список выбранных акций.\n
• /get_portfolio - показать состояние портфеля (для пользователей Тинькофф).\n
• /portfolio - показать состояние стоимости <i>любимых акций.</i>\n
• /show_graphics - ссылка на интерактивный график свеч.
"""

functional_message = """
"""

choose_accounts_message = """
Токен авторизирован. Теперь Вам нужно выбрать с каким аккаунтом Тинькофф Инвестиции мы будем 
работать. Для этого укажите номер этого счета.
"""

set_shares_message = """
Теперь вам предоставляется возможность выбрать до 10 интересующих Вас ценных бумаг. После выбора, ежедневно в 11 дня 
Вам будет приходить информация о выбранных ценных бумагах - процент изменения за предыдущий день. Для выбора введите /set_shares
"""