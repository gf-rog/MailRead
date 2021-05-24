#coding=UTF-8
from datetime import datetime
from datetime import date
import time
from time import sleep

import random
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pprint import pprint
import platform

import calendar
import locale
locale.setlocale(locale.LC_ALL, "pl_PL")

import argparse
parser = argparse.ArgumentParser(description="Przeczytaj maila ze skrzynki nauczyciela")
parser.add_argument("--login", dest="login", required=True, help="login do poczty")
parser.add_argument("--pass", dest="passwd", required=True, help="hasło do poczty")
parser.add_argument("--power-off", dest="poweroff", action="store_true", help="wyłącz komputer po przeczytaniu maila")
args = parser.parse_args()

login = args.login
passwd = args.passwd
teacher = "Kowalski Jan"
when = {"środa":		"7:20"}

url = "https://uonetplus.edu.gdansk.pl/gdansk"
url_mail = "https://uonetplus-uzytkownik.edu.gdansk.pl/gdansk/"

def error_msg(msg):
	log_msg(msg)
	input()
	driver.close()
	sys.exit(-1)

def log_msg(msg):
	print(datetime.now(),"\t",msg)

def click_mail():
	log_msg("Odczytuję maila...")
	
	driver = webdriver.Edge()
	driver.switch_to.window(driver.current_window_handle)
	driver.get(url)

	if driver.current_url != url:
		login_e = driver.find_element_by_id("UsernameTextBox")
		login_e.clear()
		login_e.send_keys(login)
		
		passwd_e = driver.find_element_by_id("PasswordTextBox")
		passwd_e.clear()
		passwd_e.send_keys(passwd)
		passwd_e.send_keys(Keys.RETURN)

	# Czekaj na załadowanie strony
	wait = WebDriverWait(driver, 10)
	try:
		wait.until(lambda driver: driver.find_element_by_id("panel_wiadomosci"))
	except selenium.common.exceptions.TimeoutException:
		error_msg("Nie udało się zalogować! Może masz zły login/hasło?")

	driver.get(url_mail)

	# Czekaj na załadowanie strony
	test_mail = "//span/b[contains(text(),'{0}')]".format(teacher)
	while True:
		wait.until(lambda driver: driver.find_element_by_id("gridview-1042-body"))
		teacher_mail = driver.find_elements_by_xpath(test_mail)
		if teacher_mail != []: break
			
		log_msg("Nie ma na razie nowej wiadomości! Spróbuję za minutę...")
		sleep(60)
		driver.refresh()
	
	for mail in teacher_mail:
		mail.click()
	driver.close()
	
	log_msg("Odczytałem wiadomość!")
	if args.poweroff:
		if platform.system() == "Windows":
			os.system("shutdown /s")
		else:
			os.system("systemctl poweroff")
		sys.exit(0)

print("Mail Read v1.0 by gf-rog")

today_wday = datetime.today().weekday()
today_time = datetime.now().time()
for wday, times in when.items():
	wday_num = list(calendar.day_name).index(wday)
	if today_wday <= wday_num:
		for t in times.split():
			next_time = datetime.strptime(t, "%H:%M").time()
			if today_wday == wday_num:
				if today_time < next_time:
					log_msg("Dzisiaj jest dzień na przeczytanie!")
				else:
					break
			time_wait = (datetime.combine(datetime.today(), next_time) - datetime.now()).total_seconds() + (wday_num - today_wday) * 3600 * 24
			log_msg("Czekam na {0}, {1}... (≈{2} sekund)".format(wday, t, round(time_wait)))
			
			sleep(time_wait)
			random_time = random.uniform(60, 200)
			log_msg("Teraz czekam ≈{0} sekund...".format(round(random_time)))
			sleep(random_time)
			click_mail()