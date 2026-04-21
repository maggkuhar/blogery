PLATFORMS = ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"]
STATUSES = ["новый", "в работе", "сотрудничество", "отказ"]

ROLES = ["разведчик", "контакт"]
BOT_STATUSES = ["активен", "отключён", "заблокирован", "прогрев"]

BOT_TEMPLATES = [
    {
        "id": "scout",
        "name": "Разведчик",
        "icon": "🔍",
        "color": "#1a7f4b",
        "description": "Мониторит группы и каналы, собирает данные об участниках сообщества",
        "use_case": "Нужно найти целевую аудиторию и собрать контакты",
        "hint": "После создания зайди в Настройки бота и укажи платформы, тематики и ключевые слова",
        "fields": [
            {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": "Разведчик-TG-1", "required": True},
            {"name": "platform", "label": "Платформа", "type": "select", "options": ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"], "required": True},
            {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
        ],
    },
    {
        "id": "parser",
        "name": "Парсер",
        "icon": "🕷",
        "color": "#8e44ad",
        "description": "Парсит списки участников, посты, контакты и контент из групп и каналов",
        "use_case": "Нужно собрать базу контактов или выгрузить все посты из канала",
        "hint": "После создания укажи источник и что именно парсить в Настройках",
        "fields": [
            {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": "Парсер-VK-1", "required": True},
            {"name": "platform", "label": "Платформа", "type": "select", "options": ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"], "required": True},
            {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
        ],
    },
    {
        "id": "poster",
        "name": "Постер",
        "icon": "📢",
        "color": "#e67e22",
        "description": "Автоматически размещает контент по расписанию в группах и каналах",
        "use_case": "Нужно публиковать посты по расписанию без ручного труда",
        "hint": "После создания укажи канал и расписание публикаций в Настройках",
        "fields": [
            {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": "Постер-TG-1", "required": True},
            {"name": "platform", "label": "Платформа", "type": "select", "options": ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"], "required": True},
            {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
        ],
    },
    {
        "id": "commenter",
        "name": "Комментатор",
        "icon": "💬",
        "color": "#2980b9",
        "description": "Оставляет комментарии под постами по ключевым словам для привлечения внимания",
        "use_case": "Нужно прогреть аккаунт или привлечь внимание через комментарии",
        "hint": "После создания укажи хэштег, шаблон комментария и задержки в Настройках",
        "fields": [
            {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": "Комментатор-IG-1", "required": True},
            {"name": "platform", "label": "Платформа", "type": "select", "options": ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"], "required": True},
            {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
        ],
    },
    {
        "id": "inviter",
        "name": "Инвайтер",
        "icon": "🤝",
        "color": "#16a085",
        "description": "Приглашает пользователей в группы и каналы из других источников",
        "use_case": "Нужно набрать участников в свою группу из целевой аудитории",
        "hint": "После создания укажи откуда брать и куда приглашать в Настройках",
        "fields": [
            {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": "Инвайтер-TG-1", "required": True},
            {"name": "platform", "label": "Платформа", "type": "select", "options": ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"], "required": True},
            {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
        ],
    },
    {
        "id": "analyst",
        "name": "Аналитик",
        "icon": "📊",
        "color": "#c0392b",
        "description": "Отслеживает статистику каналов и профилей: охваты, рост, активность",
        "use_case": "Нужно следить за конкурентами или своими показателями в динамике",
        "hint": "После создания укажи профиль для анализа и частоту сбора в Настройках",
        "fields": [
            {"name": "bot_name", "label": "Имя бота", "type": "text", "placeholder": "Аналитик-TG-1", "required": True},
            {"name": "platform", "label": "Платформа", "type": "select", "options": ["Telegram", "WhatsApp", "Instagram", "ВКонтакте", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен"], "required": True},
            {"name": "token", "label": "API токен / аккаунт", "type": "password", "placeholder": "Токен или @username", "required": True},
        ],
    },
]

TEMPLATE_ROLE = {
    "scout": "разведчик", "parser": "парсер", "poster": "постер",
    "commenter": "комментатор", "inviter": "инвайтер", "analyst": "аналитик",
}

SCOUT_PLATFORMS = {
    "Мессенджеры": ["Telegram", "WhatsApp"],
    "Социальные сети": ["ВКонтакте", "Instagram", "TikTok", "YouTube", "Rutube", "Одноклассники", "Дзен", "Facebook"],
    "Бизнес каталоги": ["2GIS", "Яндекс.Карты", "Google Maps", "Zoon", "Flamp"],
    "Доски объявлений": ["Авито", "Юла", "HH.ru", "SuperJob"],
    "Профессиональные": ["LinkedIn", "Behance", "GitHub"],
    "Поисковики": ["Google Поиск", "Яндекс Поиск"],
    "Маркетплейсы": ["Wildberries (продавцы)", "Ozon (продавцы)"],
}

SCOUT_TOPICS = [
    "Саморазвитие", "Психология", "Бизнес и предпринимательство", "Маркетинг и SMM",
    "Здоровье и фитнес", "Красота и уход", "Образование", "Финансы и инвестиции",
    "Путешествия", "Еда и кулинария", "Мода и стиль", "Искусство и творчество",
    "Технологии и IT", "Недвижимость", "Авто", "Спорт", "Семья и дети",
    "Экология", "Религия и духовность", "Юмор и развлечения",
]

SCOUT_REGIONS = [
    "Вся Россия", "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
    "Казань", "Нижний Новгород", "Краснодар", "Ростов-на-Дону", "Уфа",
    "СНГ", "Беларусь", "Казахстан", "Украина", "Весь мир",
]

SCOUT_CONTACT_TYPES = ["Email", "Телефон", "Telegram", "WhatsApp", "Ссылка на профиль"]

SCOUT_ENTRY_POINTS = {
    "Telegram": "Написать админу в личку",
    "ВКонтакте": "Сообщение в сообщество",
    "Instagram": "Комментарий + директ",
    "TikTok": "Комментарий + директ",
    "YouTube": "Комментарий + email из описания",
    "Одноклассники": "Сообщение в сообщество",
    "Facebook": "Сообщение в группу",
    "2GIS": "Звонок или email",
    "Яндекс.Карты": "Звонок или email",
    "Google Maps": "Звонок или email",
    "Авито": "Написать продавцу",
    "HH.ru": "Email из профиля",
    "LinkedIn": "Запрос в контакты + сообщение",
    "Сайт": "Форма обратной связи",
    "Google Поиск": "Email с сайта",
    "Яндекс Поиск": "Email с сайта",
}

SCOUT_OFFERS = [
    "IWS — Умный дневник 365 дней",
    "IWS — Колода МАК карт",
    "IWS — Настольная игра",
    "IWS — Онлайн игра @iwsgamebot",
    "SMM — Ведение соцсетей",
    "SMM — Создание контента",
    "Внешний трафик — Продвижение через блогеров",
    "Alex Wake — Продажа картин",
    "Партнёрство — Реферальная программа",
    "Сотрудничество — Взаимный пиар",
]

TEMPLATE_FORMATS = {
    "сообщения": ["Первый контакт", "Вопросы", "Ответы", "Фолоу-ап", "Ответ на отказ"],
    "предложения": ["Платное сотрудничество", "Бартер"],
}

SMM_STATUSES_ACCOUNT = ["активен", "заморожен", "забанен", "отключён"]
SMM_STATUSES_POST = ["черновик", "запланирован", "опубликован", "ошибка"]
