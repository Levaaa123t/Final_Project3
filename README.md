# Final_Project3
## 👋 Всем привет! 
Это наш совместный проект и в этом файле будет не большая инструкция-документация как им пользоваться:
--- 
### 1. 🧠 О чем наш бот?
Наш проект это телеграм бот для тех-поддержки где есть 2 стороны:
- **Пользователь**
- **Администратор(сама тех-поддержка)**
--- 
### 2. ⚙️ Что умеет наш бот?
- Со стороны пользователя бот может вам отвечать на *часто задаваемые вопросы(`FAQ`)*, а также принимать вопрос для тех-поддержки.
- Со стороны администратора вы можете отвечать на вопросы пользователей и помогать с решением их проблемы через бота.
---
### 3.  💬  Команды бота
> ####  3.1. Команды для администраторов:
>  - `/question_list` 
>  - `question_resolved`
> #### 3.1.1. `/question_list` - Команда показывающая все вопросы ожидаемые ответа от специалистов, если вопросов нет, бот выдаст заготовленную фразу `"Вопросов ожидаемых ответа пока нет"`. Если же вопросы есть то выйдет список вопросов и админ уже сможет выбрать на какой ответить. После того как админ выбрал вопрос он может на него ответить и после этого пользователю будет предложенно выбрать статус вопроса:
> - `"Решён"` - Значит ответ устроил пользователя.
> - `"Вопрос еще актуален"` - Значит ответ не устроил пользователя.
> #### 3.1.2. `/questions_resolved` - Команда показывающая решенные вопросы которые админ сможет удалить из базы данных и если вопрос будет удален бот ответит `"Вопрос с #id был удален"`
> #### 3.2. Команды для пользователей:
> - `/questions`
> - `/faq`
> #### 3.2.1. `/questions` -  Команда это задавание вопроса пользователя, бот может определить если вопрос часто задаваемый, после чего сразу же ответит пользователю. Если же бот не находит ответ в списке часто задаваемых вопросов, вопрос отправляется в тех-поддержку. Пользователь вводит свой вопрос после команды и после отправки вопрос получает статус `"Ожидает ответа"`.
> #### 3.2.2. `/faq`  - Команда выдает список часто задаваемыех вопросов где пользователь может найти ответ на свой вопрос и не нагружать лишний раз администартора.
---
### 4. ℹ️ Примечания:
- ❗Всегда вводите команды используя `/`, пример - `/start`.
- ❗Админами становятся только те пользователи, у которых телеграм id указаны в базе данных.
---
### 5. 📦 Все команды:
```bash
/questions
/faq
/question_list
/questions_resolved
```
---

## Авторы
### Смирнов Лев
### Данила Украинцев
