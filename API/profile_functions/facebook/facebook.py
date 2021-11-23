import string 
import random
import os
import time
import logging
import sys
import platform

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# default wait time so that elements load
# might be overriden
WAIT_TIME = 10

# Configure logging
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

def realistic_sleep_timer_inbetween_actions():
    """
    	Wait 1 - 4 secs inbetween actions to make the simulation more realistic

    	:return:	s:		the sleep time
    """
    s = random.random()* 3 + 1
    logging.info(f"(Sleep Time inbetween actions to make the simulation more realistic)Sleep time = {s:.2f} secs")
    time.sleep(s)
    return s

def realistic_sleep_timer_inbetween_sessions():
	"""
		Wait 7 - 10 secs inbetween sessions to make the simulation more realistic

		:return:	s:		the sleep time
	"""
	s = random.random()* 3 + 7
	logging.info(f"(Sleep Time inbetween sessions to make the simulation more realistic)Sleep time = {s:.2f} secs")
	time.sleep(s)
	return s

def click_on_valid_link(driver, elements):
	""" 
		Clicks on a random link in browsing mode.

		Each time 10 attempts are tolerated of trying to locate a valid link.
		For each failed attempt a new link is selected.
		If 10 attempts are made and no valid link is found the process is aborted
		and the error code -1 is returned

		:param 		elements:    list of "clickable" elements found on a page
    	:return:    -1:			 in case no valid link is found
	"""

	cnt = 0
	while True:
		try:
			random.choice(elements).click()
			logging.info(f"(facebook)Clicked on link successfully")
			break
		except Exception as e:
			logging.info(f"(facebook)Error clicking on link: " + str(e))
			logging.info(f"(facebook)Trying another link")

			# 10 trials of clicking a links on the current page are tolerated
			# For each failed attempt a new link is selected
			cnt += 1
			if cnt < 10:
				continue
			else:
				logging.info(f"(facebook)10 trials made, aborting..")
				return -1

def get_clickable_elements(driver):
	"""
		Locates all the @href elements on a page and returns them.

		If no @href elements are located -1 is returned (that is highly unlucky
		to happen on any given fb page though). 
		Note that the @href elements might not be trully clickable.
		Thus a first filter is applied on the elements via the .is_displayed() method.

    	:return:	elements: 	If the procedure was successful 
    	:return:	-1:  		If any error occured    
	"""
	# Sleeping 2 seconds for page to load all elements
	time.sleep(2)

	# Fetch clickable elements
	elements = driver.find_elements_by_xpath("//a[@href]")
	logging.info(f"(facebook)Links found: {len(elements)}")

	# Check whether elements could be determined (empty list)
	if not elements:
		logging.info(f"(facebook)click_on_stuff() error: No elements found")
		return -1

	# Filtering all links that are not active (eg generated by JS)
	try:
		valid_elements = [element for element in elements if element.is_displayed()]	
	except Exception as e:
		logging.info(f"(facebook)click_on_stuff() error: is_displayed() exception: " + str(e))
		return -1
	return elements

def click_on_stuff(driver):
	"""
		Wrapper function for the click_on_valid_lick() function.

		Initially the facebook_search_queries.txt is opened and the search queries 
		are stored on the l[] list.
		
		Then a click is made on a random element via the click_on_valid_lick() function
		and a sleep of 1-4 secs is initiated to give the impression of human-like behaviour. 
		 
    	:return:	-1:  						If any error occured
    	:return: 	time_spent_on_function:		time spent while on the function 
	"""
	
	# Open the facebook_search_queries.txt that contains possible search queries
	try:
		logging.info("(facebook)Opening file: facebook_search_queries.txt")
		file = open(os.path.join(sys.path[0], "profile_functions/facebook/facebook_search_queries.txt"), "r")

	except OSError:
		logging.info("(facebook)Could not open/read file: facebook_search_queries.txt")
		return -1

	# Create a list with the search queries and close the file
	logging.info("(facebook)Creating search queries list")
	l = []
	for search_query in file: 
		l.append(search_query.rstrip())
	file.close() 

	search_query = random.choice(l)
	s1 = search_element(search_query, driver)
	elements = get_clickable_elements(driver)
	click_on_valid_link(driver, elements)

	# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
	s2 = realistic_sleep_timer_inbetween_actions()
	
	time_spent_on_function = s1 + s2

	return time_spent_on_function

def accept_cookies(driver):
	"""
		Locate the accept cookies pop up and click on it.

    	:return:	-1:  		If any error occured 
	"""
	try:
		logging.info("(facebook)Locating Accept Cookies element")
		cookiesAcceptButton = WebDriverWait(driver, WAIT_TIME).until(
		EC.presence_of_element_located((By.XPATH, '//button[@title="Αποδοχή όλων των cookies"]'))
		)
		
		cookiesAcceptButton.click()
		logging.info("(facebook)Accept Cookies button clicked succesfully")
	except Exception as e:
		logging.info("(facebook)Could not locate Accept Cookies element")
		return -1

def search_element(element, driver):
	""" 
		Function that searches for an element.

		The facebook search form might act really weird. It might be clicked with
		the cursor blinking and yet the strokes of the keys are not getting recorded!
		THUS after the form is filled the ESC button is hit and then the form is 
		reselected and the Enter initiated. 
		The above workaround was tested thoroughly and makes the function work
		with no problems

		Inbetween steps that are supposedly made by human user sleep timers of
		1-4 seconds are initiated so that the simulation is more realistic.

    	:return:	-1:  						If any error occured
    	:return: 	time_spent_on_function:		Time spent while on the function 
	"""
	try:
		logging.info("(facebook)Locating search form")
		search = WebDriverWait(driver, WAIT_TIME).until(
			EC.presence_of_element_located((By.XPATH, '//input[@type="search"]'))
		)
		logging.info(f"(facebook)Filling search form with {element}")
		search.clear()
		search.send_keys(element)
		search.send_keys(Keys.ESCAPE)
		search.click()

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s1 = realistic_sleep_timer_inbetween_actions()

		search.send_keys(Keys.RETURN)

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s2 = realistic_sleep_timer_inbetween_actions()

	except Exception as e:
		logging.info("(facebook)Error in: Searching element")
		logging.info("(facebook)Error description: " + str(e))
		logging.info("(facebook)Searching aborted..")
		return -1

	time_spent_on_function = s1 + s2

	return time_spent_on_function


def facebook_sign_in(driver, username, password):
	"""
		Handles the sing in functionality.

		Fills the username form and the password form.
		Then "Enter" is sent.

		:param:		username: 					The username of the user 
    	:param:		password:					The password of the user 
    	:return:	-1:							If any errors occurs
    	:return: 	time_spent_on_function:		Time spent while on the function 
	"""
	try:
		logging.info("(facebook)Locating email form")
		email = driver.find_element_by_id("email")
		logging.info("(facebook)Filling email form")
		email.clear()
		email.send_keys(username)

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s1 = realistic_sleep_timer_inbetween_actions()

		logging.info("(facebook)Locating password form")
		pwrd = driver.find_element_by_id("pass")
		logging.info("(facebook)Filling password form")
		pwrd.clear()
		pwrd.send_keys(password)

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s2 = realistic_sleep_timer_inbetween_actions()

		pwrd.send_keys(Keys.RETURN)

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s3 = realistic_sleep_timer_inbetween_actions()

	except Exception as e:
		logging.info("(facebook)Error in: Signing in")
		logging.info("(facebook)Error description: " + str(e))
		logging.info("(facebook)Signing in aborted..")
		return -1

	time_spent_on_function = s1 + s2 + s3

	return time_spent_on_function

def click_messenger_button(driver):
	"""
		Clicks the messenger icon.

		The process is made in two steps, following the facebook UI.

		:return:	-1:							If any errors occurs
		:return: 	time_spent_on_function:		Time spent while on the function 
	"""
	try:
		logging.info("(facebook)Locating messenger button")
		messenger_button = WebDriverWait(driver, WAIT_TIME).until(
		EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label,"Messenger")]'))
		)
		messenger_button.click()
		logging.info("(facebook)Messenger button clicked succesfully")
		logging.info("(facebook)Locating go to messenger tab")

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s1 = realistic_sleep_timer_inbetween_actions()

		go_to_messenger = WebDriverWait(driver, WAIT_TIME).until(
		EC.presence_of_element_located((By.XPATH, '//a[contains(text(),"Εμφάνιση όλων στο Messenger")]'))
		)
		go_to_messenger.click()
		logging.info("(facebook)Go to messenger tab clicked successfully")

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s2 = realistic_sleep_timer_inbetween_actions()

	except Exception as e:
		logging.info("(facebook)Error in: Clicking on messenger")
		logging.info("(facebook)Error description: " + str(e))
		logging.info("(facebook)Clicking on messenger aborted..")
		return -1

	time_spent_on_function = s1 + s2

	return time_spent_on_function

def send_message_to_a_random_contact(driver):
	"""
		Sends a message on a random contact.

		Firstly the contacts tab is selected.
		Then a random contact is selected.
		The message is a random sequence of characters.	

		:param: 	duration:	Time in seconds that the session should last.
		:return:	-1:			If any errors occurs
		:return: 	time_spent_on_function:		Time spent while on the function
	"""
	# select the ascii characters
	letters = string.ascii_letters
	try:
		time.sleep(2)

		logging.info("(facebook)Locating contacts list")
		contacts =  WebDriverWait(driver, WAIT_TIME).until(
		EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="mwthreadlist-item"]'))
		)
		random.choice(contacts).click()
		logging.info("(facebook)Contacts list clicked successfully")

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s1 = realistic_sleep_timer_inbetween_actions()

		logging.info("(facebook)Locating chat form")
		chat = WebDriverWait(driver, WAIT_TIME).until(
		EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Μήνυμα"]'))
		)
		logging.info("(facebook)Filling chat form")
		chat.send_keys(''.join(random.choice(letters) for i in range(100)))

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s2 = realistic_sleep_timer_inbetween_actions()

		logging.info("(facebook)Sending message")
		chat.send_keys(Keys.RETURN)
		
		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s3 = realistic_sleep_timer_inbetween_actions()

	except Exception as e:
		logging.info("(facebook)Error in: Sending message on messenger")
		logging.info("(facebook)Error description: " + str(e))
		logging.info("(facebook)Sending message on messenger aborted..")
		return -1

	time_spent_on_function = s1 + s2 + s3

	return time_spent_on_function



def facebook(duration_list, interarrivals_list, url=None):
	"""
		Handles the facebook browsing.

		The parameters interarrivals_list and duration_list are
		received as Strings, with their values separated by a comma.
		The function transforms them to float type lists.
		For example if "100, 20" is received, it is transformed to [100.0, 20.0].

		The two lists must have the same length.

		The param:duration_list holds the list with values that represents the total time 
		that will be spent on facebook on each senario.

		Inbetween the restarting of the senarios there is "break" time that lasts 
		as much as the value taken form the param:interarrivals_list each time accordingly.

		############################################################

		In between each action that represents a real human action there is a wait time
		so that the simulation is closer to human behaviour. 
		It is implemented with the realistic_sleep_timer_inbetween_actions() and the
		realistic_sleep_timer_inbetween_sessions() functions.
		
		############################################################

		The url param is not used. It's there because the wrapper function that 
		calls the facebook function as well as other functions,on some occassions 
		might need a url param.
		Not the best implementation and will be fixed.

		############################################################

		The password and email of the user are stored on a .env file for
		safety reasons.
		The .env file should have entries as follows:

		FACEBOOK_EMAIL1="xxxx@xxx.xxx"
		FACEBOOK_PASSWORD1="xxxxxxxxx"

		############################################################

		The browsing sequence is:
		1.accept cookies (if possible)
		2.sign in
		3.accept cookies (if possible)
		4.50% chance to browse on random facebook pages and 50% time
		  to use messenger
		5.sleep 7-10 seconds
		6.repeat steps 4-5 until duration is over

		:param: 	duration_list:			String with the duration of each session.
		:param: 	interarrivals_list:		String with the break duration inbetween sessions.
		:param:		url:					Not being used. Set to none

	"""

	# Make the received strings into lists that contain float type numbers.
	duration_list = [float(s) for s in duration_list.split(',')]
	interarrivals_list = [float(s) for s in interarrivals_list.split(',')]
	logging.info("Setting up facebook browsing..")
	logging.info(f"  --duration_list(secs): {duration_list}")
	logging.info(f"  --interarrivals_list(secs): {interarrivals_list}")

	load_dotenv()
	password = os.environ.get('FACEBOOK_PASSWORD1')
	email = os.environ.get('FACEBOOK_EMAIL1')

	for duration, interarrival in zip(duration_list, interarrivals_list):
		# Log in to facebook
		logging.info("Opening website: facebook.com")
		if "Linux" in platform.platform():
			driver = webdriver.Firefox()
			logging.info("Operating System Linux detected")
			logging.info("Using Firefox as browser")
		else:
			driver = webdriver.Chrome()
			logging.info("Operating System Windows detected")
			logging.info("Using Chrome as browser")
		driver.get("https://el-gr.facebook.com/")

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s1 = realistic_sleep_timer_inbetween_actions()

		accept_cookies(driver)

		# Wait 1 - 4 secs inbetween actions to make the simulation more realistic
		s2 = realistic_sleep_timer_inbetween_actions()

		s3 = facebook_sign_in(driver, email, password)

		accept_cookies(driver)

		# update the remaining duration after the initial steps and their sleep time
		duration = duration - s1 - s2 - s3

		# Boolean variable that is used so that after the second time on messenger and onwards
		# a .back() (<-- icon) should be clicked. This way the messenger icon will always be present
		first_time_in_loop = True

		while duration > 0:
			#50-50 to browse or send a message			

			if random.random() < 0.5:
				logging.info(f"(facebook)Mode:Browsing")
				session_duration = click_on_stuff(driver)
				logging.info(f"(facebook)Ending Mode:browsing after {session_duration:.2f} secs")

			else:
				if not first_time_in_loop:
					logging.info("(facebook) Going back to facebook home page...")
					driver.back()
					time.sleep(2)

				logging.info(f"(facebook)Mode:Going on messenger")
				s4 = click_messenger_button(driver)
				s5 = send_message_to_a_random_contact(driver)

				session_duration = s4 + s5
				logging.info(f"(facebook)Ending Mode:messenger after {session_duration:.2f} secs")

			s6 = realistic_sleep_timer_inbetween_sessions()

			# update the duration variable by subtracting the time spent on the application
			# and another 10 seconds that is roughly the time spent waiting on loading 
			# elements and websites
			duration = duration - session_duration - s6 - 10

			# Set the variable to false so that next time a .back() is initiated
			first_time_in_loop = False

		driver.quit()


		logging.info(f"(facebook)Time sleeping until next initiation of senario: {interarrival} secs")
		time.sleep(interarrival)
	logging.info("(facebook)Browsing ended successfully.")

if __name__ == "__main__":

	# Test the function here!
	# ATTENTION: just the messenger functionality!! 
	# The path to the facebook_search_queries.txt works only from the API!!
	facebook("100,20", "2,2")