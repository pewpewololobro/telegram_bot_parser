from aiogram.utils import executor
from aiogram import Bot, types, Dispatcher
import os 
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import kbuttons
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from bs4 import BeautifulSoup
import urllib.request
import asyncio

'''====================================================================='''
storage=MemoryStorage()
url = ''
message = ''

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)

'''=Информирование что бот запустился='''
async def on_startup(_):
	print('Bot started')

'''=========Стейк-машина для сохранения нового сервера============='''
class FSMServer(StatesGroup):
	code_server = State()
	url_server = State()
'''=========Стейк-машина для нахождения сервера в списке============='''
class FSMParser(StatesGroup):
	url_for_parse = State()
'''===============================FAQ====================================='''
@dp.message_handler(commands=['start', 'commands'])
async def commands_start(message : types.Message):
	info = ['/start : начало работы','/ports : актуальный список серверов','/append : добавление нового сервера','/parse : парсинг информации с выбранного сервера']
	infos = ''
	for i in info:
		infos += i + '\n'
	try:
		await bot.send_message(message.from_user.id, 'Список команд:\n'+ str(infos), reply_markup=kbuttons)
		await message.delete()
	except:
		await message.reply('Напишите в ЛС, если бот не сработал, вот он @F_Words_Count_bot:')
'''=============================Получение списка серверов================================'''
@dp.message_handler(commands=['ports'])
async def Create_Server_List(message: types.Message):
	Server_List = []
	with open('servers.ini') as f:
		size=len([0 for _ in f])
	with open('servers.ini') as f:
		text = f.readlines()
		for i in range(size):
			Server_List.append((text[i].split(':'))[0])
	await message.delete()
	await bot.send_message(message.from_user.id, 'Доступные порты серверов:' + str(Server_List))
'''===============================Добавление сервера========================================='''
@dp.message_handler(commands=['append'], state=None)
async def Start_Server_Info(message : types.Message, state=FSMContext):
	await FSMServer.code_server.set()
	await message.reply('Введите код сервера для добавления:')
'''===============================Спрашиваем code========================================='''
@dp.message_handler(state=FSMServer.code_server)
async def CServer(message : types.Message, state=FSMContext):
	if message.text.lower() == 'cancel':
		await state.finish()
		await message.reply("Добавление отменено. Для повтора введите команду 'append'")
	if message.text.isdigit() == True:
		async with state.proxy() as data:
			data['code_server'] = message.text
		await FSMServer.next()
		await message.reply('Введите url сервера:')
	if (message.text.isdigit() == False) and (message.text.lower() != 'cancel'):
		await message.reply('Не правельный формат кода, введите число...')
'''===============================Спрашиваем url========================================='''
@dp.message_handler(state=FSMServer.url_server)
async def UServer(message : types.Message, state=FSMContext):
	async with state.proxy() as data:
		data['url_server'] = message.text
	with open('servers.ini', 'a') as f:
			f.write('\n' + data['code_server'] + ':' + data['url_server'])
	await message.reply('Данные сервера успешно добавленны!')
	await state.finish()
'''================================Парсинг на новые задачи==================================='''
async def parser(message, url):
	html = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(html, 'lxml')
	server = soup.find_all('p')
	server_list = []

	for i in server:
		server_list.append(str(i))
		buf = server_list[0].split('{')

	server_list = []
	for i in range(2,len(buf)):
		server_list.append(buf[i])

	for i in range(len(server_list)):
		one_server_data = []
		#Сервер
		one_server_data.append(server_list[i].split(':')[4].split(',')[0].split('"')[1])
		#№ модема
		one_server_data.append(server_list[i].split(':')[5].split(',')[0].split('.')[2])
		#Город
		one_server_data.append(server_list[i].split(':')[6].split(',')[0].split('"')[1])
		#Оператор
		one_server_data.append(server_list[i].split(':')[7].split(',')[0].split('}',-1)[0].split('"')[1])
		#Время
		one_server_data.append(server_list[i].split(':')[1].split(',')[0] + ' ' + server_list[i].split(':')[1].split(',')[1]
												+ ':' + server_list[i].split(':')[2].split(',')[0]
												+ ':' + server_list[i].split(':')[3].split(',')[0])

		dict_data_servers = {'Server' : one_server_data[0],
									'Modem' : one_server_data[1],
									'City' : one_server_data[2],
									'Operator' : one_server_data[3],
									'DataTime' : one_server_data[4]
									}
		#создаем файл с данными сервера если его нет
		#если файл есть проверяем если запись в нем и записываем если нет
		with open(str(dict_data_servers['Server'])+'.ini', 'a+', encoding='utf-8') as f:
			f.seek(0)
			if str(dict_data_servers['DataTime']) not in f.read():
				f.write(str(dict_data_servers)+'\n')
				await bot.send_message(message, 'Сервер: ' + dict_data_servers['Server'] + '\n' + 'Модем: ' + dict_data_servers['Modem'] + '\n' + 'Город: ' + dict_data_servers['City'] + '\n' + 'Оператор: ' + dict_data_servers['Operator'] + '\n' + 'Дата: ' + dict_data_servers['DataTime'] + '\n\n')
'''=========Спрашиваем сервер и запоминаем его======================='''
@dp.message_handler(commands=['parse'], state=None)
async def StartParsing(message : types.Message, state = FSMContext):
	await FSMParser.url_for_parse.set()
	await message.delete()
	await message.answer('Введите код сервера для поиска данных:')
'''==============Находим соответсвующий url============================'''
@dp.message_handler(state=FSMParser.url_for_parse)
async def Save_Url(message : types.Message, state=FSMContext):
	url = ''
	async with state.proxy() as data:
		data['url_for_parse'] = message.text
		with open('servers.ini') as f:
			size=len([0 for _ in f])
		with open('servers.ini') as f:
			text = f.readlines()
			for i in range(size):
				if (text[i].split(':'))[0] == data['url_for_parse']:
					url = (text[i].split(':'))[1] + ':' + (text[i].split(':'))[2]
					message = message.from_user.id
	if url == '':
		await message.answer('Такого сервера нет в списке, проверьте введные данные или добавьте их...')
		await state.finish()
	else:
		await parse_every_minute(message, url)
		await state.finish()

async def parse_every_minute(user_id, url):
	while True:
		parse_data = parser(user_id, url)

		if parse_data != None:
			await parser(user_id, url)
		else:
			await bot.send_message(user_id, 'Пока нету новых записей...')
		await asyncio.sleep(5)

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.create_task(parse_every_minute(message, url))
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup)