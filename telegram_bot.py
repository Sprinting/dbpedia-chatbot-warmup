from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, RegexHandler,ConversationHandler
from telegram import ReplyKeyboardMarkup,ReplyKeyboardRemove
import requests as  r 
import logging,sys,time
import telegram
import re as regex
import telegram_config as bot_config
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, 
							ChatMigrated, NetworkError) 
import ast
import wap
#start logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot():
	'''
		This class instantiates the telegram bot
		Only the self.start() method is to be used to start the bot
		the bot requires a token issued by @BotFather and an API access token
		for the knowledge engine you happen to use
		For now, we need to edit the query_kb if we change the Q/A system endpoint
		This bot current uses wolfram|alpha
	'''
	def __init__(self,knowledge_base,token):
		'''
			knowlege_base - dict :
				keys : url,name,api_key
			token : bot- token given for telegram 
		'''	
		self.text_only_str = 'Only text'
		self.image_str = 'Text and images'
		self.status = False # is conversation cancelled?
		self.kb_url = knowledge_base['url']
		self.kb_name = knowledge_base['name']
		self.kb_api_key=knowledge_base['api_key']
		self.null_result = 'Sorry I could not find anything'
		self.token = token
		self.entry_points = [CommandHandler('start',self.cmd_start)]
		self.can_ask,self.can_choose = 0,1
		self.prev_question =''
		#bot state determines what actions the user is 
		#allowed to perform. see the telegram documentation
		#there are two states here 
		# 0 - user can ask question
		# 1 - user can choose response type
		self.states ={
            self.can_ask: [MessageHandler(Filters.text, self.cmd_question)],
            self.can_choose: [RegexHandler('^'+regex.escape(self.text_only_str)+
							'|'+regex.escape(self.image_str)+'$',self.cmd_choose)]
        }
		self.text_req,self.image_req = 0,1
		
	def cmd_start(self,bot,update):
			'''
				This callback is called when the /start command is issued
				for the first time. Rentry is not allowed
				Sets bot state to can_ask when it returns
			'''
			update.message.reply_text(
				'Hi, I fetch answers from '+self.kb_name+
				'\n Say /bye to end the session!'
			)
			return self.can_ask 
	
	def cmd_question(self,bot,update):
		reply_keys = [[self.text_only_str,self.image_str]]
		self.prev_question = update.message.text
		update.message.reply_text(
			'Please choose the result type you want\n',
			 reply_markup = ReplyKeyboardMarkup(reply_keys,
												one_time_keyboard=True))
		
		return self.can_choose

	def cmd_choose(self,bot,update):
		result = self.query_kb(self.prev_question)
		fail = ast.literal_eval(result.IsError()[0].title()) or not ast. \
									literal_eval(result.IsSuccess()[0].title())  
		if fail:
			print result,result.IsError(),result.IsSuccess()
			update.message.reply_text(self.null_result,
									reply_markup=ReplyKeyboardRemove())
		else:
			update.message.reply_text('I found this for you!!',
								reply_markup=ReplyKeyboardRemove())
			for pod in result.Pods():
				output = ''
				waPod = wap.Pod(pod)
				if not ast.literal_eval(result.IsError()[0].title()):
					output = output + '<b>'+waPod.Title()[0]+'</b>'
					bot.sendMessage(chat_id=update.message.chat_id,
						text=output, parse_mode=telegram.ParseMode.HTML)
					for subpod in waPod.Subpods():
						waSubpod = wap.Subpod(subpod)
						
						plaintext = waSubpod.Plaintext()[0]
						img = waSubpod.Img()
						img_src = wap.scanbranches(img[0],'src')[0]
						update.message.reply_text(plaintext)
						try:
							if update.message.text == self.image_str:
								bot.sendPhoto(chat_id = update.message.chat_id,
								photo = img_src)
						# we need to catch TelegramError here
						# beacause wolfram-alpha passes malformed web-content
						# which is rejected while being posted to Telegram
						except TelegramError as te:
							print te
						except Exception as e:
							print e
				else:
					pass # Just pass on subpods which report errors
		update.message.reply_text("That's it. Thanks for asking")
		return self.can_ask
		
	def bye(self,bot,update):
		'''
			user can issuse /bye to end the session
		'''
		update.message.reply_text('Bye! I hope you liked me!')
		return ConversationHandler.END
	
	# log all errors
 	def error(self,bot,update,error):
		logger.warn('Update "%s" caused error "%s"' % (update, error))		
		return self.can_ask
    	
	
	def start(self):
		'''
		This method creates the updater and starts polling telegram for updates
		updater.idle() blocks since updater.start_polling() itself is 
		non-blocking
		'''
		print 'Starting'
		updater = Updater(self.token)
		dispatcher = updater.dispatcher
		# ConversationHandler was explicitly made to handle 
		# conversations with users		
		conv_handler = ConversationHandler(
        
		# commands wich serve as entry points
        entry_points=[CommandHandler('start', self.cmd_start)],

        states=self.states,

        fallbacks=[CommandHandler('bye', self.bye)]
    )

		
		dispatcher.add_handler(conv_handler)
		dispatcher.add_error_handler(self.error) 
		
		updater.start_polling()
		updater.idle()
	
	def query_kb(self,query): 
		'''
		Uses the wrapper provided by WolframAlpha to query the wolfram api
	    endpoint
		EDIT THIS if changing Knowledge engine API endpoint
		'''
		uri = self.kb_url
		api_key = self.kb_api_key
		
		#instantiates the engine
		waeo = wap.WolframAlphaEngine(api_key,uri)
		
		queryStr = waeo.CreateQuery(query)
		wap.WolframAlphaQuery(queryStr,api_key)
		result = waeo.PerformQuery(queryStr)
		result = wap.WolframAlphaQueryResult(result)
		#print result
		return result
		
		
		 
if __name__ == "__main__":
	sample_config = bot_config.config['bot_config']
	mybot = TelegramBot(sample_config,bot_config.config['token'])
	mybot.start()
