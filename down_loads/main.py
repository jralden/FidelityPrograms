import os, shutil
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select


# sign on credentials
url = 'https://digital.fidelity.com/prgw/digital/login/full-page'
id = "485527382"
pw = "LaPushP0rtT0wnsend"
download_folder = "C:/Users/johnr/Downloads"

search_results_file_path = "C:/Users/johnr/Downloads/Fidelity_FixedIncome_SearchResults.csv"
portfolio_builder_bonds_csv = "D:/Development/FinancialDevelopment/PortfolioBuilder/portfolio_builder/bonds.csv"


def create_web_driver(url) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    time.sleep(3)
    return driver


def login(driver, id=None, pw=None):
    driver.find_element(By.ID, "userId-input").send_keys(id)
    driver.find_element(By.ID, "password").send_keys(pw)
    driver.find_element(By.ID, "fs-login-button").click()


def signoff(webdriver: webdriver.Chrome):
    webdriver.find_element(By.CSS_SELECTOR, ".pntlt > .pnlogin > .pnls > a").click()

def clean_up_downloads(fileName: str) -> None:
    # find every .csv file in the download folder that starts with the fileName, and delete it
    for file in os.listdir(download_folder):
        print(f"filename {file}")
        # is file a .csv file?  and does it start with the fileName?
        if file.endswith(".csv") and file.startswith(fileName):
            file_path = os.path.join(download_folder, file)
            print(f"****removing {file_path}")
            os.remove(file_path)

def move_and_rename_file(source_file_path: str, destination_file_path) -> None:
    shutil.move(source_file_path, destination_file_path)

def download_fidelity_positions(webdriver: webdriver.Chrome, signOff=False) -> None:
    # assumes sign on complete, choosing the  Positions option
    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".new-tab-root:nth-child(2) .new-tab__text-wrapper")))
    webdriver.find_element(By.CSS_SELECTOR, ".new-tab-root:nth-child(2) .new-tab__text-wrapper").click()

    # selecting the download button
    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".posweb-grid_top-download-button")))
    webdriver.find_element(By.CSS_SELECTOR, ".posweb-grid_top-download-button").click()

    if signOff: signOff(webdriver)


def download_fidelity_bonds(webdriver: webdriver.Chrome, signOff=False) -> None:

    clean_up_downloads("Fidelity_FixedIncome_SearchResults")

# region ------------------------- drive the website -------------------------#
    # assumes sign on complete, choosing the News & Research option
    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "News & Research")))
    webdriver.find_element(By.LINK_TEXT, "News & Research").click()

    # selecting the Fixed Income, Bonds & CDs option
    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Fixed Income, Bonds & CDs")))
    webdriver.find_element(By.LINK_TEXT, "Fixed Income, Bonds & CDs").click()

    # selecting the Bonds option
    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.ID, "ui-id-4")))
    webdriver.find_element(By.ID, "ui-id-4").click()

    webdriver.execute_script("window.scrollTo(0,559)")
    # selecting the Corporate Bonds option
    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#corporate > a")))
    webdriver.find_element(By.CSS_SELECTOR, "#corporate > a").click()

    element = webdriver.find_element(By.CSS_SELECTOR, "#corporate > a")
    actions = ActionChains(webdriver)
    actions.move_to_element(element).perform()
    element = webdriver.find_element(By.CSS_SELECTOR, "body")
    actions = ActionChains(webdriver)
    # actions.move_to_element(element, 0, 0).perform()
    webdriver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").click()
    webdriver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").send_keys("01/2026")
    webdriver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").click()

    webdriver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").click()
    webdriver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").clear()
    webdriver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").send_keys("12/2038")

    webdriver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec > .default-attributes-box").click()

    webdriver.find_element(By.ID, "advCorpInvGradeSec_eitherRatingsInd").click()

    time.sleep(2)

    select_pd = Select(webdriver.find_element(By.ID, "advCorpInvGradeSec_minmoody"))
    select_pd.select_by_visible_text("A3")

    select_pd = Select(webdriver.find_element(By.ID, "advCorpInvGradeSec_maxmoody"))
    select_pd.select_by_visible_text("Aaa")

    select_pd = Select(webdriver.find_element(By.ID, "advCorpInvGradeSec_minsandp"))
    select_pd.select_by_visible_text("A-")

    select_pd = Select(webdriver.find_element(By.ID, "advCorpInvGradeSec_maxsandp"))
    select_pd.select_by_visible_text("AAA")

    webdriver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec #adv_SeeResults").click()

    WebDriverWait(webdriver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Download Data to Spreadsheet")))
    webdriver.find_element(By.LINK_TEXT, "Download Data to Spreadsheet").click()

# endregion

    if signOff: signOff(webdriver)

    time.sleep(10)  # needs some time to appear in the directory
    move_and_rename_file(search_results_file_path, portfolio_builder_bonds_csv)


if __name__ == '__main__':
    webdriver = create_web_driver(url)
    login(webdriver, id=id, pw=pw)
    # download_fidelity_positions(webdriver, signOff=True)
    download_fidelity_bonds(webdriver, signOff=False)

    # pause to visually assure it's working - remove when implementing for real
    time.sleep(20)
    signoff(webdriver)
