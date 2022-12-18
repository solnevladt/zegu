from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from multiprocessing.dummy import Pool
from loguru import logger
from sys import stderr, platform, version_info
from msvcrt import getch
from ctypes import windll
from urllib3 import disable_warnings
from os import system
from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
from time import sleep

if platform == "win32" and (3, 8, 0) <= version_info < (3, 9, 0):
	set_event_loop_policy(WindowsSelectorEventLoopPolicy())

class Wrong_Username_or_Email(BaseException):
	def __init__(self, message):
		self.message = message

class Wrong_Password(BaseException):
	def __init__(self, message):
		self.message = message

class Need_Confirmation_Code(BaseException):
	def __init__(self, message):
		self.message = message

disable_warnings()
def clear(): return system('cls')
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")
windll.kernel32.SetConsoleTitleW('Twitter Cookies Grabber [BETA] | by NAZAVOD')
print('Telegram channel - https://t.me/n4z4v0d\n')

accounts_folder = str(input('Перетяните .txt с аккаунтами (user:pass:2fadata): '))

with open(accounts_folder, 'r', encoding = 'utf-8') as file:
	accounts_data = [row.strip() for row in file]

threads = int(input('Threads: '))
use_proxies = str(input('Использовать Proxy? (y/N): ')).lower()

if use_proxies == 'y':
	proxy_type = str(input('Введите тип Proxy (http; https; socks4; socks5): '))

	proxies = []

def take_proxies():
	with open('proxies.txt') as file:
		proxies = [row.strip() for row in file]

	return(proxies)

def mainth(data):
	email = data[0].split(':')[0]
	password = data[0].split(':')[1]
	two_fa_info = data[0].split(':')[-1]
	proxy = data[1]

	for _ in range(3):
		try:
			if proxy:
				options = {
				'proxy': {
						'http': f'{proxy_type}://{proxy}',
						'https': f'{proxy_type}://{proxy}',
						'no_proxy': 'localhost,127.0.0.1'
					}
				}

			else:
				options = {}

			co = webdriver.ChromeOptions()
			co.add_argument('--disable-gpu')
			co.add_argument('--disable-infobars')
			co.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
			co.add_argument("lang=en-US")
			co.page_load_strategy = 'eager'
			co.add_argument("--mute-audio")
			co.add_argument('log-level=3')
			co.add_argument("--headless")
			co.add_experimental_option('excludeSwitches', ['enable-logging'])


			driver = webdriver.Chrome(seleniumwire_options=options, options = co)
			wait = WebDriverWait(driver, 60)
			driver.get('https://twitter.com/i/flow/login')
			wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]'))).send_keys(email)
			wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]'))).click()

			for _ in range(20):
				try:
					driver.find_element(By.XPATH, '//span[text()="Phone or username"]').send_keys(two_fa_info)

				except exceptions.NoSuchElementException:
					pass

				try:
					driver.find_element(By.XPATH, '//span[text()="Sorry, we could not find your account."]')

					raise Wrong_Username_or_Email('Wrong Username/Email')

				except exceptions.NoSuchElementException:
					pass

				try:
					driver.find_element(By.XPATH, '//input[@autocomplete="current-password"]')

					break

				except exceptions.NoSuchElementException:
					pass

				sleep(1)

			wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]'))).send_keys(password)
			wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]'))).click()

			for _ in range(20):
				try:
					driver.find_element(By.XPATH, '//span[text()="Wrong password!"]')

					raise Wrong_Password('Wrong Password')

				except exceptions.NoSuchElementException:
					pass

				try:
					driver.find_element(By.XPATH, '//span[text()="Confirmation code"]')

					raise Need_Confirmation_Code('Need confirmation code')

				except exceptions.NoSuchElementException:
					pass

				try:
					driver.find_element(By.CLASS_NAME, 'public-DraftEditorPlaceholder-inner')

					break

				except exceptions.NoSuchElementException:
					pass

				sleep(1)

			wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'public-DraftEditorPlaceholder-inner')))

		except Wrong_Username_or_Email as error:

			try:
				driver.quit()

			except:
				pass

			with open('wrong_username_or_email.txt', 'a') as file:
				file.write(f'{email}:{password}:{two_fa_info}\n')

			logger.error(f'{email}:{password}:{two_fa_info} | Wrong Username or Email')

			return

		except Wrong_Password as error:

			try:
				driver.quit()

			except:
				pass

			with open('wrong_password.txt', 'a') as file:
				file.write(f'{email}:{password}:{two_fa_info}\n')

			logger.error(f'{email}:{password}:{two_fa_info} | Wrong password')

			return

		except Need_Confirmation_Code as error:

			try:
				driver.quit()

			except:
				pass

			with open('need_confirmation_code.txt', 'a') as file:
				file.write(f'{email}:{password}:{two_fa_info}\n')

			logger.error(f'{email}:{password}:{two_fa_info} | Need confirmation code')

			return

		except Exception as error:
			logger.error(f'{email}:{password}:{two_fa_info} | Unexpected error: {error}')

		else:

			try:
				driver.quit()

			except:
				pass

			with open('cookies.txt', 'a') as file:
				file.write(f'{driver.get_cookies()}\n')

			logger.success(f'{email}:{password}:{two_fa_info} | Cookies have been successfully received')

			return

	try:
		driver.quit()

	except:
		pass

	with open('errors.txt', 'a') as file:
		file.write(f'{data[0]}\n')

if __name__ == '__main__':
	clear()

	if use_proxies == 'y':
		while len(proxies) < len(accounts_data):
			proxies.append(list(current_proxy for current_proxy in take_proxies())[0])

	else:
		proxies = [None for _ in range(len(accounts_data))]

	logger.info(f'Loaded {len(accounts_data)} accounts | {len(proxies)} proxies\n')

	pool = Pool(threads)
	pool.map(mainth, list(zip(accounts_data, proxies)))

	logger.success('Работа успешно завершена')
	print('\nPress Any Key To Exit..')
	getch()
	exit()
