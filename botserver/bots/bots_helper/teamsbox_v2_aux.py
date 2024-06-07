
from logging import Logger
from multiprocessing import Queue
from time import sleep
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from .aux import send_status  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

def switch_to_participant(driver):
    WebDriverWait(driver, 5).until(
      EC.presence_of_element_located((By.XPATH, "//button[@id='chat-button']"))
     ).click()
    WebDriverWait(driver,30).until(
        EC.presence_of_element_located((By.XPATH,"//h2[text()='Participants']"))
    )
def switch_to_chat(driver):
    WebDriverWait(driver, 5).until(
      EC.presence_of_element_located((By.XPATH, "//button[@id='roster-button']"))
     ).click()
    WebDriverWait(driver,30).until(
        EC.presence_of_element_located((By.XPATH,"//h3[text()='Meeting chat']"))
    )

def spotlight(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names:list[str]):
    switch_to_participant(driver)
    WebDriverWait(driver,5).until(
        EC.presence_of_element_located((By.XPATH,"//li[@data-cid='roster-participant' and contains(@data-tid, 'participantsInCall')]"))
    )
    participant_list = driver.find_elements(By.XPATH,"//li[@data-cid='roster-participant' and contains(@data-tid, 'participantsInCall')]")
    try:
        for participant in participant_list:
            name = participant.text
            if name in names:
                driver.execute_script("arguments[0].scrollIntoView();",participant)
                sleep(2)
                participant.click()
                participant.find_element(By.XPATH,".//button[@data-cid='ts-participant-action-button']").click()
                driver.find_element(By.XPATH,"//span[text()='Spotlight for everyone']").click()

                WebDriverWait(driver,5).until(
                    EC.presence_of_element_located((By.XPATH,"//button[text()='Spotlight for everyone' and @data-tid='confirm-spotlight-change-button']"))
                ).click()

    except Exception as e:
        raise e
    finally:
        switch_to_participant(driver)

def unspot(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names:list[str]):
    pass
