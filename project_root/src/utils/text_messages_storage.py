import src.utils.config as config


def message_definer(code_name: int) -> str:
    if code_name == 1:
        s = """Привет! 👋🏻 Это бот регистрации в закрытом клубе <b>«МОНТАЖНИКИ ВЕКТРА»</b>, участники которого получают заказы на строительство и монтаж зданий из сэндвич-панелей. 

С 2016 года решаем задачи тысяч монтажных компаний в России и СНГ.

<b>Вы готовы зарабатывать больше?</b> 👇"""
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

Только для вас станут доступны эксклюзивные квоты на внеочередной прокат и отгрузку с производственной площадки 🔥

Чтобы воспользоваться этими и другими привилегиями, укажите город или список городов (через пробел), в которых вы планируете брать заявки на монтаж (Если работаете по всей России, нажмите на кнопку <b>"Вся Россия"</b>:"""
        return s
    if code_name == 5:
        s = """Чтобы координатор клуба знал географию ваших работ и вы смогли получить более подробную информацию, укажите радиус от выбранного вами города 📍

Если вы работаете по всей стране, просто нажмите «Далее»

Если вы находитесь на месте, которое хотите принять за постоянное, нажмите «Поделиться геолокацией» или пришлите, какое место хотите принять по умолчанию (скрепка в углу экрана ➡️ геолокация)"""
        return s
    if code_name == 6:
        s = """Наши многочисленные производственные площадки позволяют подобрать наиболее выгодный вариант по срокам, цене и качеству ⚡️

<b>Чтобы мы могли с вами связаться, пожалуйста, поделитесь вашим контактом.</b>"""
        return s
    if code_name == 7:
        s = """
Все верно? Если необходимо что-то изменить, вы можете сделать это сейчас или в любой другой момент позднее.

Нажимая на кнопку "Завершить регистрацию", вы автоматически соглашаетесь с правилами клуба."""
        return s
    if code_name == 8:
        s = """
<b>Сэндвич-панели для вашей компании, подарки — для вас!</b> 🎁

Все участники клуба автоматически становятся частью программы лояльности «ВЕКТРА».     
"""
        return s
    if code_name == 9:
        s = """В зависимости от вашего уровня можно увеличить процент от стоимости в виде баллов:
<b>Базовый уровень — 0,05%</b> от стоимости в виде баллов;
<b>Серебряный уровень — 0,10%</b> от стоимости в виде баллов;
<b>Золотой уровень — 0,15% от</b> стоимости в виде баллов;
<b>Платиновый уровень — 0,20%</b> от стоимости в виде баллов.
Увеличить свой уровень и получить значительную скидку просто — она напрямую зависит от суммы выкупа. Все честно: заказал больше — больше уровень и количество баллов."""
        return s
    if code_name == 10:
        s = f"""— Участники программы могут обменивать накопленные баллы  на привилегии, а это:  оплата накопленными баллами логистики,  проекты,  софинансировнание сделки и юридическое сопровождение и аудит.
— А также на баллы можно приобрести товары из нашего каталога подарков  {config.link_to_our_catalog()}.  """
        return s
    if code_name == 11:
        s = """<b>Участникам клуба доступна программа лояльности, которая предлагает следующие бонусы:</b>

— Приведите друга и получите дополнительные баллы за его первые покупки! Ваш коллега или друг также получит приветственные бонусы;
— Мы обязательно поздравим вас днем рождения и с профессиональными праздниками и подарим подарки;
— Больше баллов при высоком спросе;
— Бонус за крупный заказ;
— Бонус за ежегодное обновление членства клуба;
— Эксклюзивные предложения для клиентов платинового уровня;"""
        return s
    if code_name == 12:
        s = """Я буду присылать вам уведомления о заказах, начислять вам бонусы и баллы, информировать о скидках и акциях, держать связь с вашим менеджером"""
        return s
    if code_name == 13:
        s = """ZAGLUSHKA?"""
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
    if code_name == 15:
        s = """Я подобрала вам клиента!
На связи виртуальный ассистент клуба @name (Надо придумать)

Заявка на @вид_работ
Объект по адресу: @адрес_объекта
Объем: @м2
"""
        return s
    if code_name == 16:
        s = """
Спасибо, что зарегистрировались в нашем клубе! Мы надеемся, что наше сотрудничество будет продуктивным и интересным 🧡

<b>Бонусные баллы уже на вашем счету.</b>
<b>Баланс:</b> 1 000 баллов

Как правило, первая заявка на монтаж для новых членов клуба поступает на 12 день. Сообщение о заявках на монтаж придет в чате и через бот, если заказ близко к вам (в рамках указанного вами радиуса).<b> Пожалуйста, не выключайте уведомления, чтобы не пропустить первый заказ! </b>⚡️

Если у вас есть объект и требуется просчёт, свяжитесь с персональным менеджером клуба. Если у вас возникнут вопросы или проблемы — не стесняйтесь обращаться. Мы всегда рады помочь!        
"""
        return s
    if code_name == 17:
        s = """
Здравствуйте!👷🏼‍♀️

Я заметила, что вы очень давно не обращались к нашему чат-боту. Возможно, у вас возникли какие-то вопросы или проблемы?

Я буду рада помочь вам решить любые проблемы или ответить на вопросы. <b>Пожалуйста, дайте знать, чем я могу быть полезна для вас 🧡</b>
        """
        return s
    if code_name == 18:
        s = """
Давно не общались! 

Если у вас возникли какие-либо вопросы или проблемы, я готова помочь. <b>Пожалуйста, свяжитесь с нами, если вам нужна помощь или у вас есть какие-то вопросы.</b>
        """
        return s
    if code_name == 19:
        s = """Я соскучилась! 🥹

Заметила, что вы совсем пропали. Может быть я смогу чем-то помочь или у вас остались вопросы? Давайте обсудим"""
        return s
    if code_name == 20:
        s = """Привет!
На связи виртуальный ассистент клуба — <b>Вира</b>👷🏼‍♀️ Мое имя на строительном языке означает «Вверх!»

Я буду присылать вам уведомления о заказах, начислять вам бонусы и баллы, информировать о скидках и акциях, держать связь с вашим менеджером🧡"""
        return s
    if code_name == 21:
        s = """Сообщение будет выглядеть вот так:

<b>Я подобрала вам клиента!
На связи виртуальный ассистент клуба — Вира👷🏼‍♀️

Заявка на 
— Монтаж металлоконструкций
— Монтаж сэндвич-панелей

Объект по адресу: Самара, улица Академика Павлова, 35 
Объем: @200
Статус проекта на момент составления заявки: залит фундамент</b>
"""
        return s
    if code_name == 22:
        s = """
<b>К сожалению, у вас пока нет заказов😞</b>

Обычно мы передаем первую заявку на монтаж в течение двух недель.

Для участников нашего клуба мы предлагаем особые условия: около 100 квот на срочный прокат сэндвич-панелей по всей России, сроком до 14 дней        
"""
        return s
    if code_name == 23:
        s = """
⚡️Отвечаем на часто задаваемые вопросы⚡️

<b>. Как получать заявки? </b>
Чтобы получать заявки на монтаж или другой вид работ, вам необходимо:
1. Перейти в чат-бот в Telegram
2. Пройти регистрацию в чат-боте "монтажники ВЕКТРА"
3. Стать участником клуба и подписаться на закрытый чат в Telegram
4. После этого вы сможете получать новые заявки на монтаж! 

<b>2. А что я получу, если стану участником клуба? </b>
Давайте рассмотрим, какие привилегии предоставляет закрытый клуб монтажников: 
— Мы предоставляем квоты на внеочередную отгрузку даже на пике сезона. Как такое возможно? Участники закрытого клуба монтажников смогут воспользоваться квотами на срочную отгрузку товаров с 20 производственных площадок, расположенных на территории России и СНГ.

— Юридическое сопровождение на всех этапах сделки. Мы предоставляем экспертную помощь на каждом этапе, от первой коммуникации до получения денег.

— Размещение нестандартных заказов по индивидуальным проектам. Поможем спроектировать и сэкономить на заказе.

— Фиксируем цены на момент заказа. Без привязки к экономической ситуации.

— Дополнительные комплектующие и фурнитура без наценки завода. Уплотнители, химия, крепежи из разных точек России с оперативной доставкой на объект.

— Возврат в течение 1 дня денежных средств, в случае, если размещение сэндвич-панелей не состоялось.

— Индивидуальные условия поставки. Отправим машину в любом порядке, для удобства монтажа.

—  Аудит вашего проекта. Аудит поможет вам уложиться в сроки и избежать финансовых потерь и утраты доверия со стороны заказчика.

<b>3. В чем смысл клуба? </b>
В компанию «ВЕКТРА» ежегодно обращаются более 45 000 клиентов в поисках профессиональных услуг. Чтобы ускорить поиск подрядчиков, мы создали «закрытый клуб монтажников».
И мы готовы направить вам более 3500 заявок на монтаж, которые получаем каждый месяц, даже зимой.

Наша задача — создать «нового Монтажника»! Мы устанавливаем новые стандарты качества обслуживания на рынке. Хотим, чтобы работа монтажника приносила радость и удовлетворение как ему самому, так и его клиенту, а доход монтажника зависел от нашего общего успеха.

<b>4. Вступление в клуб — платное? </b>
Нет, вступление в клуб абсолютно бесплатное. К тому же, для вас это отличная возможность заработать на монтаже. 

<b>5. Куда написать, если у меня есть собственная заявка на монтаж? </b>
Вы можете связаться с менеджером по телефону: +79370602463
Или написать на электронную почту: m.lukyanova@vektra.online

<b>6. Что мне даст участие в программе лояльности? </b>
В зависимости от вашего уровня можно увеличить процент от стоимости в виде баллов:
Базовый уровень — 0,05% от стоимости в виде баллов;
Серебряный уровень — 0,10% от стоимости в виде баллов;
Золотой уровень — 0,15% от стоимости в виде баллов;
Платиновый уровень — 0,20% от стоимости в виде баллов.
Увеличить свой уровень и получить значительную скидку просто — она напрямую зависит от суммы выкупа. Все честно: заказал больше — больше уровень и количество баллов.

Но это еще не все! Сейчас расскажем, какие дополнительные преимущества вы получите, воспользовавшись нашей программой лояльности:
— Участники программы могут обменивать накопленные баллы  на привилегии, а это:  оплата накопленными баллами логистики,  проекты,  софинансировнание сделки и юридическое сопровождение и аудит.
— А также на баллы можно приобрести товары из нашего каталога подарков. 

Акции и бонусы в рамках программы:
— Приведите друга и получите дополнительные баллы за его первые покупки! Ваш коллега или друг также получит приветственные бонусы;
— Мы обязательно поздравим вас днем рождения и с профессиональными праздниками и подарим подарки;
— Больше баллов при высоком спросе (например, зимой вам зачислится )
— Бонус за крупный заказ;
— Бонус за ежегодное обновление членства клуба;
— Эксклюзивные предложения для клиентов платинового уровня;

<b>7. На что я смогу потратить свои баллы?</b>
На баллы можно приобрести товары из нашего каталога подарков.
"""
        return s
    if code_name == 24:
        s = """
Если у вас есть проект, в котором нужны сэндвич-панели, отправьте его своему персональному менеджеру. Он рассчитает стоимость и предоставит лучшие сроки проката🔥
<b>
Связаться с менеджером: +7 937 060 24 63
Узнать подробнее про <a href="https://xn----8sbncpikoejeh3a0k.xn--p1ai/">готовые типовые проекты зданий</a></b>
"""
        return s
    if code_name == 25:
        s = """
<b>⚡️Мы предоставляем квоты на внеочередную отгрузку даже на пике сезона.</b> Как такое возможно? Участники закрытого клуба монтажников смогут воспользоваться квотами на срочную отгрузку товаров с 20 производственных площадок, расположенных на территории России и СНГ.

<b>⚡️ Юридическое сопровождение на всех этапах сделки.</b> Мы предоставляем экспертную помощь на каждом этапе, от первой коммуникации до получения денег.

<b>⚡️ Размещение нестандартных заказов по индивидуальным проектам.</b> Поможем спроектировать и сэкономить на заказе.

<b>⚡️ Фиксируем цены на момент заказа.</b> Без привязки к экономической ситуации.

<b>⚡️ Дополнительные комплектующие и фурнитура без наценки завода.</b> Уплотнители, химия, крепежи из разных точек России с оперативной доставкой на объект.

<b>⚡️ Возврат в течение 1 дня денежных средств</b>, в случае, если размещение сэндвич-панелей не состоялось.

<b>⚡️ Индивидуальные условия поставки.</b> Отправим машину в любом порядке, для удобства монтажа.

<b>⚡️ Аудит вашего проекта. </b>Аудит поможет вам уложиться в сроки и избежать финансовых потерь и утраты доверия со стороны заказчика.

Ну что, вы с нами?👇🏻        
"""
        return s
    if code_name == 26:
        s = """
При использовании цифровых сервисов компании <b>«ВЕКТРА»</b> вы автоматически соглашаетесь с условиями и правилами клуба.

Подробные условия и правила нашего клуба доступны по <b><a href="https://docs.google.com/document/d/15daP4xQcmiSKHTGxKbNw2ccSN9kkFzA15g5S4A6SJ30/edit?usp=sharing">ссылке</a></b>
"""
        return s