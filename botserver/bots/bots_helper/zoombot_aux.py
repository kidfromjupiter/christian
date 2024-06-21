from argparse import Action
from multiprocessing import Queue
import re
from time import sleep
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from .aux import send_status  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException,StaleElementReferenceException

WAIT_BETWEEN_ACTION = 0.5
is_in_viewport_script = """
    var elem = arguments[0],                 // Element to check
        parent = arguments[1],               // Parent element
        elemRect = elem.getBoundingClientRect(),
        parentRect = parent.getBoundingClientRect();
    return (
        elemRect.top >= parentRect.top &&
        elemRect.left >= parentRect.left &&
        elemRect.bottom <= parentRect.bottom &&
        elemRect.right <= parentRect.right
    );
    """
def spotlight(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names) -> None:
    try:
        lg.info("spotlight")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
        )
        participant_search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[contains(@class,"participants-search-box__input")]'))
        )

        participant_search.send_keys(100*"\b")
        for name in names:
            participant_search.send_keys(name)
            participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")
            for element in participant_list:
                ActionChains(driver).move_to_element(element).click().perform()
                sleep(WAIT_BETWEEN_ACTION)
                more_button = element.find_element(By.XPATH,".//span[text()='More']")
                WebDriverWait(driver,5).until(
                    EC.element_to_be_clickable(more_button)
                )
                more_button.click()

                try:
                
                    spotlight_button = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()="Spotlight for Everyone" or text()="Add Spotlight"]'))
                    )
                    spotlight_button.click()
                    lg.info("clicked spotlight button")
                    send_status(userid, "Spotlighted", channel_layer)
                except TimeoutException:
                        lg.error("Spotlight button not found. Likely the user is not a host")
            participant_search.send_keys(len(name)*"\b")
    except Exception as e:
        send_status(userid, "Couldn't spotlight. Is bot host or co-host? Does the user have video turned on?", channel_layer)
        driver.save_screenshot("spotlight_error.png")
        print(e)

def removespotlights(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names:list[str]):
    try:
        lg.info("removing spotlights")
        # setting gallery view
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[text()="View"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[text()="Gallery View"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="gallery-video-container__main-view"]'))
        )
        spotlight_participant_frames = driver.find_elements(By.XPATH, "//i[contains(@class, 'spotlight-icon')]/ancestor::*[contains(@class, 'gallery-video-container__video-frame')]")
    
        for frame in spotlight_participant_frames:
            try:
                name = frame.find_element(By.XPATH,".//div[@class='video-avatar__avatar-footer']/span").text
                if len(names) == 0:
                    WebDriverWait(driver,5).until(
                        EC.element_to_be_clickable(frame)
                    )
                    ActionChains(driver).move_to_element(frame).click().perform()
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

    except Exception as e:
        lg.error(e)
        driver.save_screenshot("remove_spotlight_error.png")

def mute(driver: WebDriver, lg, q: Queue, userid: str, channel_layer,*names) -> None:
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    participant_search = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[contains(@class,"participants-search-box__input")]'))
            )
    
    participant_search.send_keys(100*'\b')

    try:
        for name in names:
            participant_search.send_keys(name)
            participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")
            for element in participant_list:
                ActionChains(driver).move_to_element(element).click().perform()
                sleep(WAIT_BETWEEN_ACTION)
                mute_button = element.find_element(By.XPATH,".//button[text()='Mute']")
                mute_button.click()

            lg.info("clicked mute button")
            participant_search.send_keys(len(name)*'\b')
        send_status(userid, "Muted", channel_layer)
    except Exception as e:
        driver.save_screenshot("mute_Error.png")
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
        driver.save_screenshot("muteall_error.png")

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
        driver.save_screenshot("requestall_unmute_error.png")

def request_cameras(driver: WebDriver,names:list[str], lg, q: Queue, userid: str, channel_layer):
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    participant_search = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[contains(@class,"participants-search-box__input")]'))
            )
    participant_search.send_keys(100*"\b")

    try:
        if len(names) > 0:
            for name in names:
                participant_search.send_keys(name)
                participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")
                for element in participant_list:
                    ActionChains(driver).move_to_element(element).click().perform()
                    sleep(WAIT_BETWEEN_ACTION)
                    more_button = element.find_element(By.XPATH,".//span[text()='More']")
                    WebDriverWait(driver,5).until(
                        EC.element_to_be_clickable(more_button)
                    )
                    more_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                    ).click()
                participant_search.send_keys(len(name)*"\b")
        else:
            participant_container = driver.find_element(By.XPATH,"//div[contains(@class,'participants-list-container participants-ul')]")
            # offsetHeight = driver.execute_script("return arguments[0].offsetHeight;",participant_container)
            # scrollHeight = driver.execute_script("return arguments[0].scrollHeight;",participant_container)
            driver.execute_script("arguments[0].scrollTop = 0;",participant_container)
            # participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")
            participant_list = driver.find_elements(By.XPATH,"//div[@class='participants-item-position']")
            for element in participant_list:
                is_in_viewport = driver.execute_script(is_in_viewport_script, element, participant_container) 
                if not is_in_viewport:
                    # need to scroll down
                    driver.execute_script("arguments[0].scrollIntoView({block:'end',inline:'nearest',behaviour:'instant'})",element)    
                    # breaking out of for loop to get the participant_list again
                ActionChains(driver).move_to_element(element).click().perform()
                sleep(WAIT_BETWEEN_ACTION)

                try:
                    more_button = element.find_element(By.XPATH,".//span[text()='More']")
                    WebDriverWait(driver,2).until(
                        EC.element_to_be_clickable(more_button)
                    )
                    more_button.click()
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                    ).click()
                except:
                    pass


        send_status(userid, "Asked for video", channel_layer)
    except Exception as e:
        print(e)
        driver.save_screenshot("request_start_Video_error.png")

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
            driver.execute_script("arguments[0].scrollIntoView({behaviour:'instant',block:'end'});",element)
            name = element.find_element(By.XPATH,".//span[@class='participants-item__display-name']").text
            if name in names:
                ActionChains(driver).move_to_element(element).click().perform()
                sleep(WAIT_BETWEEN_ACTION)
                mute_button = element.find_element(By.XPATH,".//button[text()='Mute']")
                mute_button.click()

        lg.info("clicked mute button")
        send_status(userid, "Muted", channel_layer)
    except Exception as e:
        print(e)
        driver.save_screenshot("mute_but_host_error.png")
