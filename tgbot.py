import telebot as tb
import dotenv 

def main():
    token = dotenv.dotenv_values('.env','TOKEN')['TOKEN']
    bot = tb.TeleBot(token)

    @bot.message_handler(commands=["test"])
    def test(message):
        bot.reply_to(message=message, text="yo")
    
    bot.polling()

if __name__ == "__main__":
    main()