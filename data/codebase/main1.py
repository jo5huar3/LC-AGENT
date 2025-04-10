import csv
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

RETRY = 1
    
def sendkeys_ENSURE(driver: webdriver.Chrome, id: str, sec: float = 0.25) -> int:
    """
    Sends keys to a web element identified by its ID and ensures the action is completed by adding a delay.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the web element.
        sec (float, optional): The delay in seconds after sending keys. Defaults to 0.25.    

    Returns:
        int: 0 if successful, exception if an error occurs.
    """
    try:
        element = driver.find_element(By.ID, id)
        element.clear()
        element.send_keys(val)
        element.send_keys(Keys.TAB)
        time.sleep(sec)
        return 0
    except Exception as e:
        return e

def tabout_FOCUS(driver: webdriver.Chrome, id: str, sec: float = 0.25) -> int:
    """
    Sends a TAB key to a web element to move focus away and ensures the action is completed by adding a delay.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the web element.
        sec (float, optional): The delay in seconds after sending the TAB key. Defaults to 0.25.

    Returns:
        int: 0 if successful, exception if an error occurs.
    """
    try:
        element = driver.find_element(By.ID, id)
        element.send_keys(Keys.TAB)
        time.sleep(sec)
        return 0
    except Exception as e:
        return e
    
def exec_ENSURE(driver: webdriver.Chrome, id: str, script: str, sec: float = 0.25) -> int:   
    """
    Executes a JavaScript script on a web element identified by its ID and ensures the action is completed by adding a delay.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the web element.
        script (str): The JavaScript script to execute.
        sec (float, optional): The delay in seconds after executing the script. Defaults to 0.25.

    Returns:
        int: The response from the script execution or 0 if successful, exception if an error occurs.
    """
    try:
        element = driver.find_element(By.ID, id)
        response = driver.execute_script(script, element)
        time.sleep(sec)
        return response or 0
    except Exception as e:
        return e

def select_option(driver: webdriver.Chrome, id: str, option: str, sec: float) -> int:        
    """
    Selects an option from a dropdown menu identified by its ID.

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the dropdown menu.
        option (str): The option to select.
        sec (float): The delay in seconds after finding the options.

    Returns:
        int: 0 if successful, exception if an error occurs.
    """
    try:
        container = driver.find_element(By.ID, id)
        options = container.find_elements(By.TAG_NAME, 'option')
        time.sleep(sec)
        for i, opt in enumerate(options):
            if opt.text == option:
                exec_ENSURE(driver, f"{id}", f"arguments[0].selectedIndex = {i};", 0.25)     
                break
        return 0
    except Exception as e:
        return e
    
def refresh_iframe(driver: webdriver.Chrome, id: str, sec: float, bckout: bool = True) -> int:
    """
    Refreshes an iframe identified by its ID and optionally switches to the default content. 

    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the iframe.
        sec (float): The delay in seconds after switching to the iframe.
        bckout (bool, optional): Whether to switch to the default content before refreshing. Defaults to True.

    Returns:
        int: 0 if successful, exception if an error occurs.
    """
    try:
        if bckout:
            driver.switch_to.default_content()
        IFRAME = driver.find_element(By.ID, id)
        driver.switch_to.frame(IFRAME)
        time.sleep(sec)
        return 0
    except Exception as e:
        return e
    
def Automate(input_set: dict[list], driver: webdriver.Chrome, url_start: str):
    """
    Automates the process of interacting with a web application using Selenium.

    Args:
        input_set (dict[list]): A dictionary containing input data for automation.
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        url_start (str): The starting URL for the automation process.

    Returns:
        dict: A dictionary containing failed automation attempts.
    """
    fail_set = {}
    for emplid in input_set.keys():
        try:
            driver.get(url_start)
            refresh_iframe(driver, "ptifrmtgtframe", 0.25, False)
            el_ = driver.find_element(By.ID, "PEOPLE_SRCH_EMPLID")
            el_.clear()
            el_.send_keys(emplid + Keys.ENTER)
            time.sleep(0.15)
        except:
            fail_set[emplid] = [v for v in input_set[emplid]]
            continue
        for val in input_set[emplid]:
            try:
                refresh_iframe(driver, "ptifrmtgtframe", 0.25, True)
                element = driver.find_elements(By.CLASS_NAME, "PSGRIDCOUNTER")[0]
                result = str(driver.execute_script('return arguments[0].textContent;', element))
                result_split = result.split(' ')
                SCROLLONESIZE = int(result_split[len(result_split) - 1])
                if SCROLLONESIZE > 1:
                    exec_ENSURE(driver, "$ICField3$hviewall$0", "arguments[0].click();", 0.25)
                row_i = -1
                for i in range(SCROLLONESIZE):
                    element = driver.find_element(By.ID, f'EXTERNAL_SYSKEY_EXTERNAL_SYSTEM${i}')
                    SYSID = driver.execute_script('return arguments[0].options[arguments[0].selectedIndex].textContent;', element)
                    if SYSID == "Open Researcher & Contributor":
                        row_i = i
                        break
                if row_i == -1:
                    exec_ENSURE(driver, f'$ICField3$new${SCROLLONESIZE - 1}$$0', "arguments[0].click();", 0.25)
                    select_option(driver, f"EXTERNAL_SYSKEY_EXTERNAL_SYSTEM${SCROLLONESIZE}", "Open Researcher & Contributor", 0.15)
                    tabout_FOCUS(driver, f"EXTERNAL_SYSKEY_EXTERNAL_SYSTEM${SCROLLONESIZE}", 0.15)
                    row_i = SCROLLONESIZE 

                if row_i < SCROLLONESIZE:
                    exec_ENSURE(driver, f'EXTERNAL_SYSTEM$new${row_i}$${row_i}', "arguments[0].click();", 0.5)
                exec_ENSURE(driver, f'EXTERNAL_SYSTEM_EXTERNAL_SYSTEM_ID${row_i}', f"arguments[0].value = '{val}';", 0.25)
                tabout_FOCUS(driver, f'EXTERNAL_SYSTEM_EXTERNAL_SYSTEM_ID${row_i}', 0.75)    
                exec_ENSURE(driver, f'#ICSave', "arguments[0].click();", 0.0) # Does not trigger dynamic content.
                driver.switch_to.default_content()
                element = wait_ALERT(driver, 'alertmsg', 0.0)
                if element:
                    raise Exception
            except:# element not found or execute script error
                if emplid in fail_set.keys():
                    fail_set[emplid].append(val)
                else:
                    fail_set[emplid] = [val]

    return fail_set

def Start(input_set: dict[list]):
    """
    Starts the automation process and retries if necessary.

    Args:
        input_set (dict[list]): A dictionary containing input data for automation.

    Returns:
        dict: A dictionary containing failed automation attempts.
    """
    fail_set = {}
    options = Options()
    options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    url_start = driver.current_url
    i = 1
    fail_set = Automate(input_set, driver, url_start)
    while i < RETRY and len(fail_set) > 0:
        i += 1
        fail_set = Automate(fail_set, driver, url_start)
    return fail_set

if __name__ == "__main__":
    input = {}
    with open(sys.argv[1], 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            emplid = row[0]
            extID = row[1]
            if emplid not in input.keys():
                input[emplid] = []
            if extID not in input[emplid]:
                input[emplid].append(extID)
    fail_set = Start(input)
    input_sz = sum([len(input[k]) for k in input.keys()])
    if len(fail_set) == 0:
        print(f"Automation complete for {input_sz} input with 0 errors.")
    else:
        print(f"Automation complete for {input_sz} input with {fail_set_sz} errors. The task could not be automated for the following input:")
        for emplid in fail_set.keys():
            print(str(emplid) + ": ", end="")
            for val in fail_set[emplid]:
                print(str(val), end=" ")
            print('')
