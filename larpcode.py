import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions, ActionChains
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import pickle
import pyclip
from openai import OpenAI

print("Leetcode non-premium can do like around 100-200 problems and premium does like 500 before rate limit FYI")
problems_to_do = input("Enter how many problems you want to do")
open_ai_key = input("Enter api key for chatgpt")

options = webdriver.ChromeOptions()
driver = uc.Chrome(options=options)
driver.get("https://leetcode.com/accounts/login/")

def get_code_from_gpt(prompt : str) -> str:
    client = OpenAI(api_key=open_ai_key)
    result = client.responses.create(
        model="gpt-5.6-terra",
        input=f"""Don't use any imports and Solve this leetcode problem in python3 and return only the code you generate and nothing else, don't use any imports, make sure the solution's main return function isn't wrong like it was last time, make sure to include the default solution structure from leetcode:
            {prompt}
        """,
        reasoning={"effort": "high"}
    )

    return result.output_text


def wait_for(search_type, path_string, timeout = 15, list_of_elements=False) -> WebElement | list[WebElement]:
    waiter = WebDriverWait(driver, timeout)
    if list_of_elements:
        return waiter.until(EC.presence_of_all_elements_located((search_type, path_string)))
    else:
        return waiter.until(EC.presence_of_element_located((search_type, path_string)))

def perform_setup():
    print("Login to start (60 second timeout)")
    WebDriverWait(driver, 60).until(EC.url_to_be("https://leetcode.com/"))
    print("Logged in!")
    driver.get("https://leetcode.com/problems/two-sum/description/")

    listButton = wait_for(By.CSS_SELECTOR, '[aria-label="Expand Panel"]')
    listButton.click()
    time.sleep(1)
    filterButton = wait_for(By.XPATH, "//button[@class='relative inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-sd-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-sd-secondary/80 rounded-full h-8 gap-2 bg-sd-accent py-2 text-sm text-sd-blue-400 px-2']", list_of_elements=True)[1]
    filterButton.click()

    filter_popup = wait_for(By.CSS_SELECTOR, 'div[data-radix-popper-content-wrapper]')
    filter_popup.click()

    statusButton = filter_popup.find_elements(By.XPATH, ".//button[@role='combobox']")[3]
    statusButton.click()

    time.sleep(0.5)
    ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
    time.sleep(0.5)
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    emptyFilterBox = filter_popup.find_elements(By.XPATH,".//div[@aria-haspopup='menu']")[2]
    emptyFilterBox.click()

    solvedButton = wait_for(By.XPATH,"//div[contains(@class,'cursor-pointer')][.//div[normalize-space()='Solved']]")
    solvedButton.click()

    emptyLanguageBox = filter_popup.find_elements(By.XPATH,".//div[@aria-haspopup='menu']")[5]
    emptyLanguageBox.click()

    python3Button = wait_for(By.XPATH,"//div[contains(@class,'cursor-pointer')][.//div[normalize-space()='Python3']]")
    python3Button.click()

    ActionChains(driver).send_keys(Keys.ESCAPE).pause(1).send_keys(Keys.ESCAPE).pause(1).perform()

    ProgrammingLanguageButton = wait_for(By.XPATH, "//button[normalize-space()='C++']")
    ProgrammingLanguageButton.click()

    Python3Button = wait_for(By.XPATH, "//div[contains(text(),'Python3')]")
    Python3Button.click()

    ActionChains(driver).key_down(Keys.LEFT_CONTROL).send_keys(Keys.ARROW_RIGHT).key_up(Keys.LEFT_CONTROL).perform()
    ActionChains(driver).key_down(Keys.LEFT_CONTROL).send_keys(Keys.ARROW_RIGHT).key_up(Keys.LEFT_CONTROL).perform()
    ActionChains(driver).key_down(Keys.LEFT_CONTROL).send_keys(Keys.ARROW_LEFT).key_up(Keys.LEFT_CONTROL).perform()
    time.sleep(3)

def attempt_problem() -> bool:
    time.sleep(3)
    if driver.find_elements(By.XPATH, '//a[starts-with(@href, "/subscribe/") and normalize-space()="Subscribe"]'):
        return False

    instructions = wait_for(By.XPATH, "//div[@data-track-load='description_content']")
    code_window = wait_for(By.XPATH,"//div[@id='editor']/div[@class='flex flex-col min-h-0 flex-1 pb-2']/div[@class='relative min-h-0 flex-1']/div[@class='relative h-full w-full']/div[@class='monaco-editor no-user-select  showUnused showDeprecated vs-dark']/div[@class='overflow-guard']/div[@class='monaco-scrollable-element editor-scrollable vs-dark']/div[@class='lines-content monaco-editor-background']/div[@class='view-lines monaco-mouse-cursor-text']")
    leetcode_function = code_window.text
    code_answer = get_code_from_gpt(f"Use this leetcode function: {leetcode_function} and now here are the instructions {instructions.text}")

    pyclip.copy(code_answer)

    code_window.click()

    ActionChains(driver).key_down(Keys.LEFT_CONTROL).send_keys("a").key_up(Keys.LEFT_CONTROL).pause(0.5).send_keys(Keys.BACKSPACE).perform()
    ActionChains(driver).key_down(Keys.LEFT_CONTROL).send_keys("v").key_up(Keys.LEFT_CONTROL).pause(0.5).perform()

    submit_button = wait_for(By.XPATH, "//button[@data-e2e-locator='console-submit-button']", list_of_elements=True)[0]
    submit_button.click()

    try:
        accepted_text = wait_for(By.XPATH, "//span[@data-e2e-locator='submission-result']", list_of_elements=True, timeout=11)[0]
        return True

    except Exception as e:
        return False

def next_problem() -> None:
    ActionChains(driver).key_down(Keys.LEFT_CONTROL).send_keys(Keys.ARROW_RIGHT).key_up(Keys.LEFT_CONTROL).perform()

def main():
    perform_setup()
    problems_completed = 0
    problems_to_complete = problems_to_do
    while problems_to_complete > problems_completed:
        attempt = attempt_problem()
        if attempt:
            problems_completed += 1
            print(f"Success! {problems_completed} problems now completed out of {problems_to_complete}")
        else:
            print("failed skipping")

        next_problem()

    print("Completed!")

if __name__ == "__main__":
    main()



