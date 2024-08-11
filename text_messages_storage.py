import config

def message_definer(code_name: int) -> str:
    if code_name == 1:
        s = """Привет! На связи компания «ВЕКТРА». С 2016 года мы профессионально решаем задачи тысяч монтажных компаний в России и СНГ.

Это бот регистрации участников закрытого клуба «МОНТАЖНИКИ ВЕКТРА».

Участники клуба получают заказы на строительство и монтаж зданий из сэндвич-панелей.

Вы готовы зарабатывать больше?"""
        return s
    if code_name == 2:
        s = """В компанию «ВЕКТРА» ежегодно обращаются более 45 000 клиентов в поисках профессиональных услуг. Чтобы ускорить поиск подрядчиков, мы создали «закрытый клуб монтажников».
И мы готовы направить вам более 3500 заявок на монтаж, которые получаем каждый месяц, даже зимой.

Наша задача — создать «нового Монтажника»! Мы устанавливаем новые стандарты качества обслуживания на рынке. Хотим, чтобы работа монтажника приносила радость и удовлетворение как ему самому, так и его клиенту, а доход монтажника зависел от нашего общего успеха."""
        return s
    if code_name == 3:
        s = """— Мы предоставляем квоты на внеочередную отгрузку даже на пике сезона.
Как такое возможно? Участники закрытого клуба монтажников смогут воспользоваться квотами на срочную отгрузку товаров с 20 производственных площадок, расположенных на территории России и СНГ.
— Юридическое сопровождение на всех этапах сделки. Мы предоставляем экспертную помощь на каждом этапе, от первой коммуникации до получения денег.
— Размещение нестандартных заказов по индивидуальным проектам. Поможем спроектировать и сэкономить на заказе.
— Фиксируем цены на момент заказа. Без привязки к экономической ситуации.
— Дополнительные комплектующие и фурнитура без наценки завода. Уплотнители, химия, крепежи из разных точек России с оперативной доставкой на объект.
— Возврат в течение 1 дня денежных средств, в случае, если размещение сэндвич-панелей не состоялось.
— Индивидуальные условия поставки. Отправим машину в любом порядке, для удобства монтажа.
— Аудит вашего проекта. Аудит поможет вам уложиться в сроки и избежать финансовых потерь и утраты доверия со стороны заказчика.

Ну что, вы с нами?"""
        return s
    if code_name == 4:
        s = """Как правило каждый второй клиент заключает договор с участником клуба.

Только для вас станут доступны эксклюзивные квоты на внеочередной прокат и отгрузку с производственной площадки.

Чтобы воспользоваться этими и другими привилегиями, укажите ближайший к вам город на этом шаге и радиус вокруг него на следующем.

Если вы работаете по всей России, укажите ваш домашний город."""
        return s
    if code_name == 5:
        s = """Мы оказываем полную поддержку на всех этапах строительства.
Более подробную информацию вы сможете получить у своего персонального менеджера до получения заявки на монтаж.

Чтобы координатор клуба знал географию ваших работ, укажите радиус от выбранного вами города.

Если вы работаете по всей стране, просто нажмите 'Далее' 

Если вы находитесь на месте, которое хотите принять за постоянное, нажмите 'Поделиться геолокацией', иначе пришлите, какое место хотите принять по умолчанию (скрепка в углу экрана -> геолокация).
"""
        return s
    if code_name == 6:
        s = """Наши многочисленные производственные площадки позволяют подобрать наиболее выгодный вариант по срокам, цене и качеству.


Чтобы мы могли с вами связаться, пожалуйста, поделитесь вашим контактом или укажите номер телефона."""
        return s
    if code_name == 7:
        s = """
Все верно? Если необходимо что-то изменить, вы можете сделать это сейчас или в любой другой момент позднее.

Нажимая на кнопку "Завершить регистрацию", вы автоматически соглашаетесь с правилами клуба."""
        return s
    if code_name == 8:
        s = """
Сэндвич-панели для вашей компании, подарки — для вас!

Все участники клуба автоматически становятся частью программы лояльности «ВЕКТРА».

Как это работает? За каждую покупку сэндвич-панелей вы будете получать 0,05% от стоимости продукции в виде баллов.
1 балл = 1 рубль.

Баллы начисляются после завершения покупки и оплаты заказа.
Накопленные баллы можно использовать для оплаты логистики, проектов, получения специальных условий софинансирования ваших проектов, а также для заказа подарков из каталога «ВЕКТРА».

За прохождение регистрации вам будет начислено 1 000 бонусных баллов.        
"""
        return s
    if code_name == 9:
        s = """В зависимости от вашего уровня можно увеличить процент от стоимости в виде баллов:
Базовый уровень — 0,05% от стоимости в виде баллов;
Серебряный уровень — 0,10% от стоимости в виде баллов;
Золотой уровень — 0,15% от стоимости в виде баллов;
Платиновый уровень — 0,20% от стоимости в виде баллов.
Увеличить свой уровень и получить значительную скидку просто — она напрямую зависит от суммы выкупа. Все честно: заказал больше — больше уровень и количество баллов."""
        return s
    if code_name == 10:
        s = f"""— Участники программы могут обменивать накопленные баллы  на привилегии, а это:  оплата накопленными баллами логистики,  проекты,  софинансировнание сделки и юридическое сопровождение и аудит.
— А также на баллы можно приобрести товары из нашего каталога подарков  {config.link_to_our_catalog()}.  """
        return s
    if code_name == 11:
        s = """— Приведите друга и получите дополнительные баллы за его первые покупки! Ваш коллега или друг также получит приветственные бонусы;
— Мы обязательно поздравим вас  днем рождения и с профессиональными праздниками и подарим подарки;
— Больше баллов при высоком спросе (например, зимой вам зачислится )
 — Бонус за крупный заказ;
— Бонус за ежегодное обновление членства клуба;
 — Эксклюзивные предложения  для клиентов платинового уровня;"""
        return s
    if code_name == 12:
        s = """Я буду присылать вам уведомления о заказах, начислять вам бонусы и баллы, информировать о скидках и акциях, держать связь с вашим менеджером"""
        return s
    if code_name == 13:
        s = """Благодарим вас за регистрацию в профессиональном строительном сообществе "ВЕКТРА", ваш баланс бонусных баллов составляет: 1 000 (@переменная)

Совсем скоро я подберу для вас персонального менеджера, который будет отвечать за ваше развитие в рамках клуба."""
        return s
    if code_name == 14:
        s = """Как только заказчику потребуются ваши услуги, я вышлю вам уведомление о сделке, информация по заявке следующая:
1. Адрес объекта
2. Тип объекта
3. Количество м2 (по полу)
4. Что необходимо сделать?
5.Статус проекта на момент составления заявки

От вас необходимо подтвердить интерес к данному объекту, нажав на кнопку: "мне интересно"
"""
        return s
    elif code_name == 15:
        s = """Я подобрала вам клиента!
На связи виртуальный ассистент клуба @name (Надо придумать)

Заявка на @вид_работ
Объект по адресу: @адрес_объекта
Объем: @м2
"""
        return s
