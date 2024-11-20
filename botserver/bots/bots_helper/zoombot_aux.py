import re
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .aux import send_status

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
is_above_or_below_script = """
    var elem = arguments[0],                 // Element to check
        parent = arguments[1],               // Parent element
        elemRect = elem.getBoundingClientRect(),
        parentRect = parent.getBoundingClientRect();
    
    if (elemRect.bottom < parentRect.top) {
        return 'above';
    } else if (elemRect.bottom > parentRect.bottom) {
        return 'below';
    } else {
        return 'within';
    }
"""


def spotlight(driver: WebDriver, lg, userid: str, channel_layer, *names) -> None:
    try:
        lg.info("spotlight")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
        )
        search_available = True
        try:
            participant_search = driver.find_element(By.XPATH,
                                                     '//input[contains(@class,"participants-search-box__input")]')
        except:
            search_available = False

        if search_available:
            participant_search.send_keys(100 * "\b")
            for name in names:
                participant_search.send_keys(name)
                participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
                for element in participant_list:
                    ActionChains(driver).move_to_element(element).click().perform()
                    sleep(WAIT_BETWEEN_ACTION)
                    more_button = element.find_element(By.XPATH, ".//span[text()='More']")
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(more_button)
                    )
                    more_button.click()

                    try:

                        spotlight_button = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//button[text()="Spotlight for Everyone" or text()="Replace Spotlight"]'))
                        )
                        spotlight_button.click()
                        lg.info("clicked spotlight button")
                        send_status(userid, "Spotlighted", channel_layer)
                    except TimeoutException:
                        lg.error("Spotlight button not found. Likely the user is not a host")
                participant_search.send_keys(len(name) * "\b")
        else:
            participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")

            for element in participant_list:
                name = element.find_element(By.XPATH, ".//span[@class='participants-item__display-name']").text
                if name in names:
                    ActionChains(driver).move_to_element(element).click().perform()
                    sleep(WAIT_BETWEEN_ACTION)
                    more_button = element.find_element(By.XPATH, ".//span[text()='More']")
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(more_button)
                    )
                    more_button.click()

                    try:
                        spotlight_button = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//button[text()="Spotlight for Everyone" or text()="Replace Spotlight"]'))
                        )
                        spotlight_button.click()
                        lg.info("clicked spotlight button")
                        send_status(userid, "Spotlighted", channel_layer)
                    except TimeoutException:
                        lg.error("Spotlight button not found. Likely the user is not a host")

    except Exception as e:
        send_status(userid, "Couldn't spotlight. Is bot host or co-host? Does the user have video turned on?",
                    channel_layer)
        driver.save_screenshot("spotlight_error.png")
        print(e)


def removespotlights(driver: WebDriver, lg, userid: str, channel_layer):
    try:
        ActionChains(driver).move_to_element(driver.find_element(By.XPATH, "//video-player-container"))
        sleep(0.5)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Remove Spotlight"]'))
        ).click()
        lg.info("removing spotlights")

    except Exception as e:
        lg.error(e)
        driver.save_screenshot("remove_spotlight_error.png")


def mute(driver: WebDriver, lg, userid: str, channel_layer, *names) -> None:
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    search_available = True
    try:
        participant_search = driver.find_element(By.XPATH, '//input[contains(@class,"participants-search-box__input")]')
    except:
        search_available = False

    if search_available:
        participant_search.send_keys(100 * '\b')

    try:
        if search_available:
            for name in names:
                participant_search.send_keys(name)
                participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
                for element in participant_list:
                    ActionChains(driver).move_to_element(element).click().perform()
                    sleep(WAIT_BETWEEN_ACTION)
                    mute_button = element.find_element(By.XPATH, ".//button[text()='Mute']")
                    mute_button.click()

                lg.info("clicked mute button")
                participant_search.send_keys(len(name) * '\b')
        else:
            participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
            for element in participant_list:
                name = element.find_element(By.XPATH, ".//span[@class='participants-item__display-name']").text
                if name in names:
                    ActionChains(driver).move_to_element(element).click().perform()
                    sleep(WAIT_BETWEEN_ACTION)
                    mute_button = element.find_element(By.XPATH, ".//button[text()='Mute']")
                    mute_button.click()

        send_status(userid, "Muted", channel_layer)
    except Exception as e:
        driver.save_screenshot("mute_Error.png")
        print(e)


def muteall(driver: WebDriver, lg, userid: str, channel_layer):
    lg.info("muteall")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    try:
        # participant panel is open, continue
        mute_all_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Mute All']"))
        )
        mute_all_button.click()
        mute_all_continue_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Continue']"))
        )
        mute_all_continue_button.click()
    except Exception as e:
        lg.error(e)
        send_status(userid, "Couldn't mute all. Is bot host or co-host?", channel_layer)
        driver.save_screenshot("muteall_error.png")


def request_all_to_unmute(driver: WebDriver, lg, userid: str, channel_layer):
    lg.info("request all to unmute")
    participant_section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    try:
        # participant panel is open, continue
        participant_section.find_element(By.XPATH, ".//button[text()='More']").click()
        all_to_unmute_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Ask All to Unmute']"))
        )
        all_to_unmute_btn.click()
    except Exception as e:
        lg.error(e)
        send_status(userid, "Couldn't request all to unmute. Is bot host or co-host?", channel_layer)
        driver.save_screenshot("requestall_unmute_error.png")


def request_cameras(driver: WebDriver, names: list[str], lg, userid: str, channel_layer):
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    search_available = True
    try:
        participant_search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[contains(@class,"participants-search-box__input")]'))
        )
    except:
        search_available = False
    if search_available:
        participant_search.send_keys(100 * "\b")
    try:
        if len(names) > 0:
            for name in names:
                if search_available:
                    participant_search.send_keys(name)
                participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
                for element in participant_list:
                    if not search_available and name not in element.text:
                        return

                    ActionChains(driver).move_to_element(element).click().perform()
                    sleep(WAIT_BETWEEN_ACTION)
                    more_button = element.find_element(By.XPATH, ".//span[text()='More']")
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(more_button)
                    )
                    more_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                    ).click()
                if search_available:
                    participant_search.send_keys(len(name) * "\b")
        else:
            id_list = []
            participant_container = driver.find_element(By.XPATH,
                                                        "//div[contains(@class,'participants-list-container participants-ul')]")
            offsetHeight = driver.execute_script("return arguments[0].offsetHeight;", participant_container)
            scrollHeight = driver.execute_script("return arguments[0].scrollHeight;", participant_container)
            driver.execute_script("arguments[0].scrollTop = 0;", participant_container)

            scrollTop = 0
            if scrollTop + offsetHeight == scrollHeight:
                participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
                for element in participant_list:

                    send_status(userid, "Requesting Camera from participants", channel_layer)
                    # checking whether we already checked this participant
                    element_id = element.find_element(By.XPATH,
                                                      ".//div[contains(@class,'participants-li')]").get_attribute("id")
                    if element_id not in id_list:
                        # getting the position of element relative to parent viewport. If above, do nothing, if below, scroll down. If within, do the thing
                        relative_pos = driver.execute_script(is_above_or_below_script, element, participant_container)
                        if relative_pos == 'below':
                            # break out of for loop, which will cause a scroll down
                            break
                        if relative_pos == "within":
                            # do some stuff
                            ActionChains(driver).move_to_element(element).click().perform()
                            id_list.append(element_id)
                            sleep(WAIT_BETWEEN_ACTION)

                            try:
                                more_button = element.find_element(By.XPATH, ".//span[text()='More']")
                                WebDriverWait(driver, 2).until(
                                    EC.element_to_be_clickable(more_button)
                                )
                                more_button.click()
                                WebDriverWait(driver, 2).until(
                                    EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                                ).click()
                            except:
                                pass

                sleep(0.5)
            # need to scroll
            while scrollTop + offsetHeight < scrollHeight:
                scrollTop = driver.execute_script("return arguments[0].scrollTop;", participant_container)
                participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
                for element in participant_list:

                    send_status(userid, "Requesting Camera from participants", channel_layer)
                    # checking whether we already checked this participant
                    element_id = element.find_element(By.XPATH,
                                                      ".//div[contains(@class,'participants-li')]").get_attribute("id")
                    if element_id not in id_list:
                        # getting the position of element relative to parent viewport. If above, do nothing, if below, scroll down. If within, do the thing
                        relative_pos = driver.execute_script(is_above_or_below_script, element, participant_container)
                        if relative_pos == 'below':
                            # break out of for loop, which will cause a scroll down
                            break
                        if relative_pos == "within":
                            # do some stuff
                            ActionChains(driver).move_to_element(element).click().perform()
                            id_list.append(element_id)
                            sleep(WAIT_BETWEEN_ACTION)

                            try:
                                more_button = element.find_element(By.XPATH, ".//span[text()='More']")
                                WebDriverWait(driver, 2).until(
                                    EC.element_to_be_clickable(more_button)
                                )
                                more_button.click()
                                WebDriverWait(driver, 2).until(
                                    EC.presence_of_element_located((By.XPATH, '//button[text()="Ask For Start Video"]'))
                                ).click()
                            except:
                                pass

                driver.execute_script(f"arguments[0].scrollTop += {offsetHeight}", participant_container)
                sleep(0.5)

        send_status(userid, "Asked for video", channel_layer)
    except Exception as e:
        print(e)
        driver.save_screenshot("request_start_Video_error.png")


def mutebuthost(driver: WebDriver, lg, userid: str, channel_layer):
    lg.info("cameras")
    # Get the participant button
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"participants-section-container")]'))
    )
    participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")

    try:
        id_list = []
        participant_container = driver.find_element(By.XPATH,
                                                    "//div[contains(@class,'participants-list-container participants-ul')]")
        offsetHeight = driver.execute_script("return arguments[0].offsetHeight;", participant_container)
        scrollHeight = driver.execute_script("return arguments[0].scrollHeight;", participant_container)
        driver.execute_script("arguments[0].scrollTop = 0;", participant_container)

        scrollTop = 0
        if scrollTop + offsetHeight == scrollHeight:
            # dont need to scroll. so scroll logic is not required
            participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
            for element in participant_list:
                send_status(userid, "Muting people", channel_layer)
                # checking whether we already checked this participant
                element_id = element.find_element(By.XPATH, ".//div[contains(@class,'participants-li')]").get_attribute(
                    "id")
                if element_id not in id_list:
                    # do some stuff
                    try:
                        id_list.append(element_id)
                        matches = re.findall(r'\([^()]*\)', element.text)
                        participant_is_host = False
                        for match in matches:
                            if "Host" in match:
                                participant_is_host = True
                                # this is a host. go to the next participant
                        if not participant_is_host:
                            ActionChains(driver).move_to_element(element).click().perform()
                            sleep(WAIT_BETWEEN_ACTION)
                            mute_button = element.find_element(By.XPATH, ".//button[text()='Mute']")
                            WebDriverWait(driver, 0.5).until(
                                EC.element_to_be_clickable(mute_button)
                            )
                            ActionChains(driver).move_to_element(mute_button).click_and_hold().pause(
                                0.25).release().perform()
                    except:
                        pass

        while scrollTop + offsetHeight < scrollHeight:
            scrollTop = driver.execute_script("return arguments[0].scrollTop;", participant_container)
            participant_list = driver.find_elements(By.XPATH, "//div[@class='participants-item-position']")
            for element in participant_list:

                send_status(userid, "Muting people", channel_layer)
                # checking whether we already checked this participant
                element_id = element.find_element(By.XPATH, ".//div[contains(@class,'participants-li')]").get_attribute(
                    "id")
                if element_id not in id_list:
                    # getting the position of element relative to parent viewport. If above, do nothing, if below, scroll down. If within, do the thing
                    relative_pos = driver.execute_script(is_above_or_below_script, element, participant_container)
                    if relative_pos == 'below':
                        # break out of for loop, which will cause a scroll down
                        break
                    if relative_pos == "within":
                        # do some stuff
                        try:
                            id_list.append(element_id)
                            matches = re.findall(r'\([^()]*\)', element.text)
                            participant_is_host = False
                            for match in matches:
                                if "Host" in match:
                                    participant_is_host = True
                                    # this is a host. go to the next participant
                            if not participant_is_host:
                                ActionChains(driver).move_to_element(element).click().perform()
                                sleep(WAIT_BETWEEN_ACTION)
                                mute_button = element.find_element(By.XPATH, ".//button[text()='Mute']")
                                WebDriverWait(driver, 0.5).until(
                                    EC.element_to_be_clickable(mute_button)
                                )
                                ActionChains(driver).move_to_element(mute_button).click_and_hold().pause(
                                    0.25).release().perform()
                        except:
                            pass

            driver.execute_script(f"arguments[0].scrollTop += {offsetHeight}", participant_container)
            sleep(0.5)
    except Exception as e:
        lg.error(e)
        driver.save_screenshot("mute_but_host_error.png")


def send_msg_to_chat(driver: WebDriver, message: str, lg):
    try:
        chat_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class,"chat-rtf-box__editor-wrapper")//*[@contenteditable="true"]]'))
        )
        chat_container.click()
        chat_container.send_keys(message)
        chat_container.send_keys(Keys.RETURN)
    except Exception as e:
        lg.error(e)
