import os
from time import sleep
# from .teamsbot_v2_aux import spotlight
from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from .teamsbox_v2_aux import spotlight, unspotall
from .aux import Message,send_message,send_status
from channels.layers import get_channel_layer
from datetime import datetime
import logging as lg
from multiprocessing import Queue
lg.basicConfig(level=lg.DEBUG, filename="py_log.log",filemode="w")

NAME="Meetingheld.in"
WAIT_ADMIT_TIME = 120
MESSAGE_POLL_RATE = 0.1

def create_msg(current_msg) -> Message:
    message_content = current_msg.find_element(By.XPATH, './/div[@data-tid="chat-pane-message"]')
    message_text = message_content.text
    message_id = message_content.get_attribute("id")
    message_author = current_msg.find_element(By.XPATH, './/span[@data-tid="message-author-name"]').text
    try:
        message_avatar = current_msg.find_element(By.XPATH,'.//span[@data-tid="message-avatar"]/img').get_attribute("src")
    except:
        message_avatar = ""
    return Message("teams",message_author,message_text,message_avatar,message_id)

def run_teamsbot(meeting_link,userid,timeout,q:Queue):
    startTime = datetime.now()
    channel_layer = get_channel_layer()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    # chrome_options.add_argument("--user-data-dir=chrome-data")
    if not settings.DEV:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(chrome_options)
    lg.info("got chrome driver")
    try:
        driver.get(meeting_link)
        sleep(5)
        url = driver.current_url
        lg.info(f"Current URL: {url}")

        if not settings.DEV:
            lg.info("Muting mic and cameras")
            mic_mute = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="Microphone"]/div'))
            )
            mic_mute.click()
            cam_off = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="Camera"]/div'))
            )
            sleep(2)
            cam_off.click()

        input_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"][@placeholder="Type your name"]'))
        )
        lg.info("got input element")

        # Click the input element
        input_element.click()
        lg.info("clicked input element")
        input_element.send_keys(NAME)
        lg.info("sent keys")

        # Get the button with id "prejoin-join-button"
        join_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'prejoin-join-button'))
        )
        lg.info("got join button")

        # Click the join button
        join_button.click()
        lg.info("clicked join button")
        send_status(userid,"If wait room is enabled, admit bot now",channel_layer)


        chat_button = WebDriverWait(driver, WAIT_ADMIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='chat-button']"))
        )
        lg.info("got chat button")
        view_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@id="view-mode-button"]'))
        )
        lg.info("got view button")

        send_status(userid,"Admitted to meeting",channel_layer)

        # Click the view more button
        view_button.click()
        lg.info("clicked view button")

        # Get the div with role "menuitem" and title "More options"
        more_options_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="menuitem"][@title="More options"]'))
        )
        lg.info("got more options div")

        # Click the more options div
        more_options_div.click()
        lg.info("clicked more options div")

        # Get the element with text "Turn off incoming video"
        turn_off_video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="incoming-video-button"]'))
        )
        lg.info("got turn off video element")

        # Click the turn off incoming video element
        turn_off_video_element.click()
        lg.info("clicked turn off video element")
        chat_button.click()
        lg.info("clicked chat button")

        # Get the div with data-tid "message-pane-list-viewport"
        messages_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="chat-pane-list"]'))
        )
        lg.info("got messages container")

        spotlights:list[str] = []
        sent_id_list:list[str] = []
        while True:
            if not q.empty():
                command = q.get()
                # ! is removed in consumers.py
                command, *args = command.split("#")
                print(args)
                match command:
                    case "spotlight":
                        print("spotlight")
                        spotlights = [*args,*spotlights]
                        spotlight(driver,lg,q,userid,channel_layer,*args)
                    case "unspot":
                        unspotall(driver,lg,q,userid,channel_layer,args)

            now = datetime.now()
            time_difference = now - startTime
            if time_difference.total_seconds() > timeout * 60 * 60:
                lg.error("Timeout Reached")
                raise Exception("Timeout Reached")

            messages_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="chat-pane-list"]'))
            )
            send_status(userid,"Listening for messages",channel_layer)
            messages = messages_container.find_elements(By.XPATH, './/div[@data-testid="message-wrapper"]')
            if len(messages) ==0:
                sleep(MESSAGE_POLL_RATE)
                continue

            if len(sent_id_list) == 0:
                new_msg = create_msg(messages[0])
                sent_id_list.append(new_msg.contentId)
                #send message
                send_message(userid,new_msg.stringify(),channel_layer)
                sleep(MESSAGE_POLL_RATE)
                continue
            for current_msg in messages:
                current_id= current_msg.find_element(By.XPATH, './/div[@data-tid="chat-pane-message"]').get_attribute("id")
                if current_id not in sent_id_list:
                    new_msg = create_msg(current_msg)
                    sent_id_list.append(new_msg.contentId)
                    #send message
                    send_message(userid,new_msg.stringify(),channel_layer)
                    print(f"Sending message: {new_msg.chatmessage}")
            sleep(MESSAGE_POLL_RATE)
    except Exception as e:
        lg.error(e)
        elements = driver.find_elements(By.ID, 'hangup-button')
        send_status(userid,"Bot ended",channel_layer)
        if elements:
            driver.save_screenshot(f"error.png")
            #go for the retry
        else:
            #meeting possibly ended
            print("Element is not present")
            driver.save_screenshot(f"exit.png")
            page = driver.page_source
            url = driver.current_url
            with open("page.html", "w") as file:
                file.write(page)
            with open("url.txt", "w") as file:
                file.write(url)
        driver.quit()
        driver = None
