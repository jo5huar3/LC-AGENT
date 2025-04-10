import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

RETRY = 1
Js = {
    "clck": "arguments[0].click()",
    "set-txt": "arguments[0].value = ",
    "get-txt": "return arguments[0].value;",
    "get-selectedOptTxtCnt": "return arguments[0].options[arguments[0].selectedIndex].textContent;",
    "get-txtCnt": "return arguments[0].textContent;",
    "set-selectInd": "arguments[0].selectedIndex = ",
    "srch-set-OPT": "for (let i = 0; i < arguments[0].length; i++) {if (arguments[0][i].text == arguments[1]) { arguments[0].selectedIndex = i; break; }}"
}

def sendkeys_ENSURE(driver: webdriver.Chrome, id: str, val: str, sec: float = 0.2) -> int:
    """
    Sends keys to a web element identified by its ID, ensuring the element is cleared before sending keys.
    
    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the web element.
        val (str): The value to send to the web element.
        sec (float, optional): The time to wait after sending keys. Defaults to 0.2 seconds.
    
    Returns:
        int: 0 if successful, or an exception if an error occurs.
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

def exec_ENSURE(driver: webdriver.Chrome, id: str, script: str, sec: float = 0.2) -> int:
    """
    Executes a JavaScript script on a web element identified by its ID.
    
    Args:
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        id (str): The ID of the web element.
        script (str): The JavaScript script to execute.
        sec (float, optional): The time to wait after executing the script. Defaults to 0.2 seconds.
    
    Returns:
        int: The response from the script execution or 0 if successful, or an exception if an error occurs.
    """
    try:
        element = driver.find_element(By.ID, id)
        response = driver.execute_script(script, element)
        time.sleep(sec)
        return response or 0
    except Exception as e:
        return e

def Automate(input_set: list, driver: webdriver.Chrome, url_start: str, password_new: str):
    """
    Automates the password reset process for a list of employee IDs.
    
    Args:
        input_set (list): A list of employee IDs.
        driver (webdriver.Chrome): The Selenium WebDriver instance.
        url_start (str): The starting URL for the automation process.
        password_new (str): The new password to set for each employee.
    
    Returns:
        list: A list of employee IDs for which the password reset failed.
    """
    line_buffer = []
    for emplid in input_set:
        try:
            driver.get(url_start)
            driver.switch_to.frame(driver.find_element(By.ID, "ptifrmtgtframe"))
            sendkeys_ENSURE(driver, "PSOPRDEFN_SRCH_OPRID", emplid)
            driver.find_element(By.ID, "#ICSearch").click()
            driver.execute_script(
                f'if(document.getElementById("ICTAB_0").getAttribute("aria-selected") == "false") {{ document.getElementById("ICTAB_0").click(); }}'
            )
            exec_ENSURE(driver, "PSUSRPRFL_WRK_CHANGE_PWD_BTN", Js['clck'])
            sendkeys_ENSURE(driver, "PSUSRPRFL_WRK_OPERPSWD", password_new)
            sendkeys_ENSURE(driver, "PSUSRPRFL_WRK_OPERPSWDCONF", password_new)
            driver.find_element(By.ID, "#ICSave").click()
            exec_ENSURE(driver, "#ICSave", Js['clck'], 0.75)
            driver.execute_script(
                f'if(document.getElementById("PSUSRPRFL_WRK_OPERPSWD")) {{throw new Error("Password did not save.");}}'
            )
        except:
            line_buffer.append(emplid)
    try:
        driver.get(url_start)
    except:
        pass
    return line_buffer

def Start(input_set: list, password_new: str):
    """
    Initiates the password reset automation process and retries if necessary.
    
    Args:
        input_set (list): A list of employee IDs.
        password_new (str): The new password to set for each employee.
    
    Returns:
        list: A list of employee IDs for which the password reset failed after retries.
    """
    fail_set = []
    options = Options()
    options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    url_start = driver.current_url
    i = 1
    fail_set = Automate(input_set, driver, url_start, password_new)
    while i < RETRY and len(fail_set) > 0:
        i += 1
        fail_set = Automate(fail_set, driver, url_start, password_new)
    return fail_set

if __name__ == "__main__":
    input = []
    with open(sys.argv[1], 'r') as file:
        input = file.read().split("\n")
    unique_list = []
    [unique_list.append(val) for val in input if val not in unique_list]
    password_new = sys.argv[2]
    fail_set = Start(unique_list, password_new)
    input_sz = len(input)
    fail_set_sz = len(fail_set)
    if len(fail_set) == 0:
        print(f"Automation complete for {input_sz} input with 0 errors.")
    else:
        print(f"Automation complete for {input_sz} input with {fail_set_sz} errors. The task could not be automated for the following input:")
        for fail in fail_set:
            print("\n" + str(fail), end=" ")