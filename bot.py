import telebot
from config import *
from logic import DB_questions
from telebot import TeleBot
import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

default_questions = {
    "Как оформить заказ?": "Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку 'Добавить в корзину', затем перейдите в корзину и следуйте инструкциям для завершения покупки.",
    "Как узнать статус моего заказа?": "Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел 'Мои заказы'. Там будет указан текущий статус вашего заказа.",
    "Как отменить заказ?": "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.",
    "Что делать, если товар пришел поврежденным?": "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара.",
    "Как связаться с вашей технической поддержкой?":"Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота.",
    "Как узнать информацию о доставке?":"Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки."
}



bot = telebot.TeleBot(TOKEN)
db_commands = DB_questions()
@bot.message_handler(commands=['start'])
def start(message):
    check = db_commands.check_id(user_id=message.from_user.id )
    if check:
        bot.send_message(message.chat.id,'Привет админ!')
    else:
        bot.send_message(message.chat.id,'Привет я бот тех поддержка! Задай свой вопрос написав questions')

@bot.message_handler(commands=['faq'])
def faq_questions(message):
    info = db_commands.get_list_faq()
    if info:
        text = "Часто задаваемые вопросы:\n" + "\n".join([f'- {x[0]} \n {x[1]}' for x in info])
    else:
        text = 'Часто задаваемых вопросов нет'
    
    bot.send_message(message.chat.id, text)
    
@bot.message_handler(commands=['questions'])
def question_user(message):
    user_question = message.text[10:].strip()
    if user_question:
        matched_answers = []  
        user_words = set(user_question.lower().split()) 


        for question, answer in default_questions.items():
            question_words = set(question.lower().split())  
            common_words = user_words & question_words  

        
            if len(common_words) >= 3:
                matched_answers.append(answer)

        
        if matched_answers:
            for response in matched_answers:
                bot.send_message(message.chat.id, response)
        else:
            
            bot.send_message(message.chat.id, 'К сожалению я не нашел ответ на ваш вопрос, перенаправляю его к специалистам.\n Вы также можете посмотреть часто задаваемые вопросы -/faq-')
            db_commands.save_user_question(user_id=message.from_user.id, question=user_question)
    else:
        bot.send_message(message.chat.id, "Пожалуйста задайте вопрос после команды.")



@bot.message_handler(commands=['questions_list'])
def show_questions(message):
    questions = db_commands.get_pending_questions() 
    check = db_commands.check_id(user_id=message.from_user.id )
    if check:
        if not questions:
            bot.send_message(message.chat.id,'Сейчас нет вопросов ожидающих ответа')
            return
        markup = InlineKeyboardMarkup()
        for question in questions:
            question_id = question[0] 
            question_text = question[2]  
            btn = InlineKeyboardButton(f"Вопрос {question_id}: {question_text[:30]}", callback_data=f"respond_question_{question_id}")
            markup.add(btn)
        bot.send_message(message.chat.id, "Выберите вопрос для решения:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id,'У тебя нет доступа к этой функции!')

@bot.callback_query_handler(func=lambda call: call.data.startswith("respond_question_"))
def handle_callback(call):
    question_id = int(call.data.split("_")[2]) 
    check = db_commands.check_id(user_id=call.from_user.id )
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if check:
        markup = InlineKeyboardMarkup()
        but1 = InlineKeyboardButton("Ответить на вопрос", callback_data=f"respond_{question_id}")
        markup.add(but1)
        bot.send_message(call.message.chat.id, "Напишите ответ на вопрос:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id,'У тебя нет доступа к этой функции!')

admin_response = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("respond_"))
def handle_respond_button(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    question_id = int(call.data.split("_")[1])
    admin_response[call.from_user.id] = question_id
    bot.send_message(call.message.chat.id, "Введите текст ответа на этот вопрос")

@bot.message_handler(func=lambda message: message.from_user.id in admin_response)
def handle_admin_reply(message):
    markup = InlineKeyboardMarkup()
    admin_id = message.from_user.id
    question_id = admin_response.pop(admin_id)
    answer = message.text
    question = db_commands.get_id(question_id)
    if question:
        user_id = question[1]
        but1 = InlineKeyboardButton("Вопрос еще актуален", callback_data=f"actual_{question_id}")
        but2 = InlineKeyboardButton("Вопрос решен", callback_data=f"resolved_{question_id}")
        markup.add(but1, but2)
        bot.send_message(user_id, f"Ответ на ваш вопрос:\n{answer}")
        bot.send_message(user_id, "Был ли решен ваш вопрос?", reply_markup=markup)
        bot.send_message(admin_id, "Ответ успешно отправлен пользователю")
    else:
        bot.send_message(admin_id, "Вопрос не найден.")


@bot.callback_query_handler(func=lambda call: call.data.startswith(('actual_', 'resolved_')))
def update_status(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    question_id = int(call.data.split('_')[1])
    if call.data == f'resolved_{question_id}': 
        db_commands.update_question_status(status='Решен', question_id=question_id)
        bot.answer_callback_query(callback_query_id=call.id, text = f"Статус вопроса изменен на Решен", show_alert = False)
        bot.send_message(call.message.chat.id, f"Вопрос решен")
    else:
        db_commands.update_question_status(status='Ожидание', question_id=question_id)
        bot.answer_callback_query(callback_query_id=call.id, text = 'Я оставил статус вопроса на ожидание', show_alert = False)
        bot.send_message(call.message.chat.id,'Я оставил статус вопроса в ожидании, ожидайте ответа специалиста')

@bot.message_handler(commands=['questions_resolved'])
def resolved_questions(message):
    resolv_questions = db_commands.get_resolved_questions() 
    check = db_commands.check_id(user_id=message.from_user.id )
    if check:
        if not resolv_questions:
            bot.send_message(message.chat.id,'Сейчас нет решенных вопросов')
            return
        markup = InlineKeyboardMarkup()
        for del_question in resolv_questions:
            del_question_id = del_question[0] 
            del_question_text = del_question[1]  
            btn = InlineKeyboardButton(f"Вопрос {del_question_id}: {del_question_text[:30]}", callback_data=f"choose_question_{del_question_id}")
            markup.add(btn)
        bot.send_message(message.chat.id, "Выберите вопрос для удаления:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id,'У тебя нет доступа к этой функции!')

@bot.callback_query_handler(func=lambda call: call.data.startswith("choose_question_"))
def del_callback(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    question_id = int(call.data.split("_")[2]) 
    check = db_commands.check_id(user_id=call.from_user.id )
    if check:
        markup = InlineKeyboardMarkup()
        but1 = InlineKeyboardButton("Удалить вопрос", callback_data=f"delete_{question_id}")
        markup.add(but1)
        bot.send_message(call.message.chat.id, "Удаление вопроса:", reply_markup=markup)
    else:
        bot.send_message(call.message.chat.id,'У тебя нет доступа к этой функции!')

@bot.callback_query_handler(func=lambda call: call.data.startswith(('delete_')))
def delete_question(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    question_id = int(call.data.split('_')[1])
    if call.data == f'delete_{question_id}': 
        db_commands.delete_user_question(question_id = question_id)
        bot.answer_callback_query(callback_query_id=call.id, text = f"Вопрос #{question_id} был удален", show_alert = False)
        bot.send_message(call.message.chat.id, f"Вопрос #{question_id} был удален")
    else:
        bot.send_message(call.message.chat.id, 'Что то пошло не так')



bot.infinity_polling()