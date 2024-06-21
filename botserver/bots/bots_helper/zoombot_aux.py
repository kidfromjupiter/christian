from multiprocessing import Queue
import re
from time import sleep
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from .aux import send_status  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


def spotlight(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names:list[str]) -> None:
    try:
        lg.info("spotlight")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
        )
        participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")

        for element in participant_list:
            name = element.find_element(By.XPATH,".//span[@class='participants-item__display-name']").text
            if name in names:
                ActionChains(driver).move_to_element(element).perform()
                sleep(5)
                more_button = element.find_element(By.XPATH,".//span[text()='More']")
                more_button.click()

                try:
                
                    spotlight_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()="Spotlight for Everyone" or text()="Add Spotlight"]'))
                    )
                    spotlight_button.click()
                    lg.info("clicked spotlight button")
                    send_status(userid, "Spotlighted", channel_layer)
                except TimeoutException:
                    lg.error("Spotlight button not found. Likely the user is not a host")
                    break;
        send_status(userid, "Couldn't spotlight. Is bot host or co-host? Does the user have video turned on?", channel_layer)
    except Exception as e:
        print(e)

def removespotlights(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names:list[str]):
    lg.info("removing spotlights")
    # setting gallery view
    view_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//span[text()="View"]'))
    )
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH,"//div[@class='main-layout']")).perform()
    sleep(1)
    view_button.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[text()="Gallery View"]'))
    ).click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="gallery-video-container__main-view"]'))
    )
    participant_frames = driver.find_elements(By.XPATH, '//div[contains(@class,"gallery-video-container__video-frame")]')
    
    for frame in participant_frames:
        try:
            # if spotlight icon exists, the user is spotlighted
            frame.find_element(By.XPATH,".//i[contains(@class,'spotlight-icon')]")
            name = frame.find_element(By.XPATH,".//div[@class='video-avatar__avatar-footer']/span").text
            if len(names) == 0:
                frame.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,".//button[@aria-label='More managing options']"))
                ).click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[text()="Remove Spotlight"]'))
                ).click()
            elif name in names:
                frame.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,".//button[@aria-label='More managing options']"))
                ).click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[text()="Remove Spotlight"]'))
                ).click()
                

        except:
            lg.error("UnSpotlight button not found. Likely the bot is not a host/co-host")

def mute(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names:list[str]) -> None:
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")

    try:
        for element in participant_list:

            driver.execute_script("arguments[0].scrollIntoView();",element)
            name = element.find_element(By.XPATH,".//span[@class='participants-item__display-name']").text
            if name in names:
                ActionChains(driver).move_to_element(element).perform()
                sleep(5)
                mute_button = element.find_element(By.XPATH,".//button[text()='Mute']")
                mute_button.click()

        lg.info("clicked mute button")
        send_status(userid, "Muted", channel_layer)
    except Exception as e:
        print(e)
def muteall(driver: WebDriver, lg, q: Queue, userid: str, channel_layer):
    lg.info("muteall")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    try:
        #participant panel is open, continue
        mute_all_button = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"//button[text()='Mute All']"))
        )
        mute_all_button.click()
        mute_all_continue_button = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,"//button[text()='Continue']"))
        )
        mute_all_continue_button.click()
    except Exception as e:
        lg.error(e)
        send_status(userid, "Couldn't mute all. Is bot host or co-host?", channel_layer)

def request_all_to_unmute(driver: WebDriver, lg, q: Queue, userid: str, channel_layer):
    lg.info("request all to unmute")
    participant_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    try:
        #participant panel is open, continue
        participant_section.find_element(By.XPATH,".//button[text()='More']").click()
        all_to_unmute_btn = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH,"//a[text()='Ask All to Unmute']"))
        )
        all_to_unmute_btn.click()
    except Exception as e:
        lg.error(e)
        send_status(userid,"Couldn't request all to unmute. Is bot host or co-host?",channel_layer)

def request_cameras(driver: WebDriver,names:list[str], lg, q: Queue, userid: str, channel_layer):
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")

    try:
        for element in participant_list:
            name = element.find_element(By.XPATH,".//span[@class='participants-item__display-name']").text
            driver.execute_script("arguments[0].scrollIntoView();",element)
            if len(names) > 0:
                if name in names:
                    ActionChains(driver).move_to_element(element).perform()
                    sleep(5)
                    more_button = element.find_element(By.XPATH,".//span[text()='More']")
                    more_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                    ).click()
            else:
                ActionChains(driver).move_to_element(element).perform()
                sleep(5)
                more_button = element.find_element(By.XPATH,".//span[text()='More']")
                more_button.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                ).click()

        send_status(userid, "Asked for video", channel_layer)
    except Exception as e:
        print(e)

def mutebuthost(driver: WebDriver,lg, q: Queue, userid: str, channel_layer):
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")

    try:
        for element in participant_list:
            matches = re.findall(r'\([^()]*\)',element.text)
            for match in matches:
                if "Host" in match:
                    return
            driver.execute_script("arguments[0].scrollIntoView();",element)
            name = element.find_element(By.XPATH,".//span[@class='participants-item__display-name']").text
            if name in names:
                ActionChains(driver).move_to_element(element).perform()
                sleep(5)
                mute_button = element.find_element(By.XPATH,".//button[text()='Mute']")
                mute_button.click()

        lg.info("clicked mute button")
        send_status(userid, "Muted", channel_layer)
    except Exception as e:
        print(e)
