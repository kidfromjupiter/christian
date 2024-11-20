from multiprocessing import Queue
from time import sleep

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def switch_to_participant(driver):
    # double clicking to make sure it loads
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//button[@id='roster-button']"))
    ).click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//h2[text()='Participants']"))
    )


def switch_to_chat(driver):
    # double clicking to make sure it loads
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//button[@id='chat-button']"))
    ).click()
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//h3[text()='Meeting chat']"))
    )


def is_substring_of_initial_string(name_list, initial_str):
    # checks whether any of the elements in name_list is a substring of intial_str
    for name in name_list:
        if name in initial_str:
            return True
    return False


def spotlight(driver: WebDriver, lg, q: Queue, userid: str, channel_layer, *names: list[str]):
    switch_to_participant(driver)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, "//li[@data-cid='roster-participant' and contains(@data-tid, 'participantsInCall')]"))
    )
    participant_list = driver.find_elements(By.XPATH,
                                            "//li[@data-cid='roster-participant' and contains(@data-tid, 'participantsInCall')]")
    try:
        for participant in participant_list:
            name = participant.text
            if is_substring_of_initial_string(names, name):
                driver.execute_script("arguments[0].scrollIntoView();", participant)
                sleep(2)
                participant.click()
                participant.find_element(By.XPATH, ".//button[@data-cid='ts-participant-action-button']").click()
                driver.find_element(By.XPATH, "//span[text()='Spotlight for everyone']").click()

                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "//button[text()='Spotlight for everyone' and @data-tid='confirm-spotlight-change-button']"))
                ).click()

    except Exception as e:
        print(e)
    finally:
        switch_to_chat(driver)


def unspotall(driver: WebDriver, lg, q: Queue, userid: str, channel_layer, *names: list[str]):
    switch_to_participant(driver)
    try:
        # WebDriverWait(driver, 5).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "//div[@data-tid='calling-right-side-panel']//button[@data-tid='more-menu-trigger']"))
        # ).click()
        # WebDriverWait(driver, 5).until(
        #     EC.presence_of_element_located((By.XPATH, "//span[text()='Stop all spotlights']"))
        # ).click()
        # WebDriverWait(driver, 5).until(
        #     EC.presence_of_element_located((By.XPATH, "//button[@data-tid='confirm-spotlight-change-button']"))
        # ).click()

        participant_video_containers = driver.find_elements(By.XPATH,
                                                            "//div[contains(@aria-label, 'spotlighted') and @data-cid='calling-participant-stream']")
        for container in participant_video_containers:
            ActionChains(driver).move_to_element(container).context_click().perform()

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-track-action-outcome='stopSpotlight']"))
            ).click()

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[@data-tid='confirm-spotlight-change-button']"))
            ).click()

    except Exception as e:
        print(e)
    finally:
        switch_to_chat(driver)


def send_to_chat(driver: WebDriver, message: str):
    try:
        input_field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-tid='ckeditor']"))
        )
        input_field.send_keys(message)
        input_field.send_keys(Keys.RETURN)
    except:
        pass
