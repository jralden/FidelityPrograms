import os, shutil
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import Select


def signOff(webdriver: webdriver.Chrome):
    webdriver.find_element(By.CSS_SELECTOR, ".pntlt > .pnlogin > .pnls > a").click()
    pass


class FidelityWebAccess:

    def __init__(self, url):
        self.driver: webdriver.Chrome = self.create_web_driver(url)
        self.url = url

    @staticmethod
    def create_web_driver(url) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        time.sleep(3)
        return driver

    def login(self, cid=None, pw=None):
        self.driver.find_element(By.ID, "userId-input").send_keys(cid)
        self.driver.find_element(By.ID, "password").send_keys(pw)
        self.driver.find_element(By.ID, "fs-login-button").click()

    def signoff(self):
        self.driver.find_element(By.CSS_SELECTOR, ".pntlt > .pnlogin > .pnls > a").click()

    @staticmethod
    def clean_up_downloads(fileName: str, download_folder) -> None:
        # find every .csv file in the download folder that starts with the fileName, and delete it
        for file in os.listdir(download_folder):
            # is file a .csv file?  and does it start with the fileName?
            if file.endswith(".csv") and file.startswith(fileName):
                file_path = os.path.join(download_folder, file)
                print(f"****removing {file_path}")
                os.remove(file_path)

    @staticmethod
    def locate_file(directory_path: str, partial_match: str, file_type: str) -> str | None:
        for file in os.listdir(directory_path):
            if file.endswith(file_type) and file.startswith(partial_match):
                return directory_path + "/" + file
        return None

    @staticmethod
    def move_and_rename_file(source_file_path: str, destination_file_path) -> None:
        shutil.move(source_file_path, destination_file_path)

    def download_fidelity_positions(self, should_signOff=False) -> None:
        fidelity_positions_csv = "D:/Development/FinancialDevelopment/FidelityPositions/positions.csv"
        download_folder = "C:/Users/johnr/Downloads"
        self.clean_up_downloads("Portfolio_Positions", download_folder)

        # assumes sign on complete, choosing the  Positions option
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".new-tab-root:nth-child(2) .new-tab__text-wrapper")))
        self.driver.find_element(By.CSS_SELECTOR, ".new-tab-root:nth-child(2) .new-tab__text-wrapper").click()

        # selecting the download button
        WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".posweb-grid_top-download-button")))
        self.driver.find_element(By.CSS_SELECTOR, ".posweb-grid_top-download-button").click()

        if should_signOff: signOff()

        time.sleep(4)  # needs some time to appear in the directory
        results_file_path = self.locate_file(download_folder, "Portfolio_Positions", ".csv")
        self.move_and_rename_file(results_file_path, fidelity_positions_csv)

    def download_fidelity_bonds(self, should_signOff=False) -> None:
        portfolio_builder_bonds_csv = "D:/Development/FinancialDevelopment/PortfolioBuilder/portfolio_builder/bonds.csv"
        download_folder = "C:/Users/johnr/Downloads"
        search_results_file_path = download_folder + "/Fidelity_FixedIncome_SearchResults.csv"
        self.clean_up_downloads("Fidelity_FixedIncome_SearchResults", download_folder)

        # region ------------------------- drive the website -------------------------#
        # assumes sign on complete, choosing the News & Research option
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.LINK_TEXT, "News & Research")))
        # self.driver.find_element(By.LINK_TEXT, "News & Research").click()
        #
        # # selecting the Fixed Income, Bonds & CDs option
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.LINK_TEXT, "Fixed Income, Bonds & CDs")))
        # self.driver.find_element(By.LINK_TEXT, "Fixed Income, Bonds & CDs").click()
        # time.sleep(3)
        # self.driver.find_element(By.ID, "ui-id-4").click()
        # self.driver.find_element(By.CSS_SELECTOR, "#corporate > a").click()
        # element = self.driver.find_element(By.CSS_SELECTOR, "#corporate > a")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element).perform()
        # element = self.driver.find_element(By.CSS_SELECTOR, "body")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element, 0, 0).perform()
        # time.sleep(2)
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").click()
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").send_keys("01/2026")
        # element = self.driver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec > .default-attributes-box")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element).click_and_hold().perform()
        # element = self.driver.find_element(By.CSS_SELECTOR, ".loading-indicator--modal-overlay-mask:nth-child(11)")
        # actions = ActionChains(self.driver)
        # actions.move_to_element(element).release().perform()
        # self.driver.find_element(By.CSS_SELECTOR, "body").click()
        # # selecting the Bonds option
        # # WebDriverWait(self.driver, 30).until(
        # #     EC.element_to_be_clickable((By.ID, "ui-cid-4")))
        # # self.driver.find_element(By.ID, "ui-cid-4").click()
        # #
        # # self.driver.execute_script("window.scrollTo(0,559)")
        # # # selecting the Corporate Bonds option
        # # WebDriverWait(self.driver, 30).until(
        # #     EC.element_to_be_clickable((By.CSS_SELECTOR, "#corporate > a")))
        # # self.driver.find_element(By.CSS_SELECTOR, "#corporate > a").click()
        # #
        # # element = self.driver.find_element(By.CSS_SELECTOR, "#corporate > a")
        # # actions = ActionChains(self.driver)
        # # actions.move_to_element(element).perform()
        # # element = self.driver.find_element(By.CSS_SELECTOR, "body")
        # # actions = ActionChains(self.driver)
        # # # actions.move_to_element(element, 0, 0).perform()
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").click()
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").send_keys("01/2026")
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").click()
        #
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").click()
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").clear()
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").send_keys("12/2038")
        #
        # self.driver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec > .default-attributes-box").click()
        #
        # self.driver.find_element(By.ID, "advCorpInvGradeSec_eitherRatingsInd").click()

        # time.sleep(2)
        #
        # select_pd = Select(self.driver.find_element(By.ID, "advCorpInvGradeSec_minmoody"))
        # select_pd.select_by_visible_text("A3")
        #
        # select_pd = Select(self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmoody"))
        # select_pd.select_by_visible_text("Aaa")
        #
        # select_pd = Select(self.driver.find_element(By.ID, "advCorpInvGradeSec_minsandp"))
        # select_pd.select_by_visible_text("A-")
        #
        # select_pd = Select(self.driver.find_element(By.ID, "advCorpInvGradeSec_maxsandp"))
        # select_pd.select_by_visible_text("AAA")
        #
        # self.driver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec #adv_SeeResults").click()
        #
        # WebDriverWait(self.driver, 30).until(
        #     EC.element_to_be_clickable((By.LINK_TEXT, "Download Data to Spreadsheet")))
        # self.driver.find_element(By.LINK_TEXT, "Download Data to Spreadsheet").click()

        # endregion
        # time.sleep(6)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Fixed Income, Bonds & CDs")))
        self.driver.find_element(By.LINK_TEXT, "Fixed Income, Bonds & CDs").click()
        self.driver.find_element(By.ID, "ui-id-4").click()
        self.driver.execute_script("window.scrollTo(0,559)")
        self.driver.find_element(By.CSS_SELECTOR, "#corporate > a").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_minmaturity").send_keys("01/2026")
        self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").click()
        self.driver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec .field-box02").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmaturity").send_keys("12/2037")
        self.driver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec > .default-attributes-box").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_eitherRatingsInd").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_minsandp").click()
        dropdown = self.driver.find_element(By.ID, "advCorpInvGradeSec_minsandp")
        dropdown.find_element(By.XPATH, "//option[. = 'A-']").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_maxsandp").click()
        dropdown = self.driver.find_element(By.ID, "advCorpInvGradeSec_maxsandp")
        dropdown.find_element(By.XPATH, "//option[. = 'AAA']").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_minmoody").click()
        dropdown = self.driver.find_element(By.ID, "advCorpInvGradeSec_minmoody")
        dropdown.find_element(By.XPATH, "//option[. = 'A3']").click()
        self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmoody").click()
        dropdown = self.driver.find_element(By.ID, "advCorpInvGradeSec_maxmoody")
        dropdown.find_element(By.XPATH, "//option[. = 'Aaa']").click()
        self.driver.find_element(By.CSS_SELECTOR, "#Corporate_Investment_Grade_Sec #adv_SeeResults").click()
        self.driver.find_element(By.LINK_TEXT, "Download Data to Spreadsheet").click()
        # region ------------------------- download the data -------------------------#
        if should_signOff: signOff()

        time.sleep(4)  # needs some time to appear in the directory
        self.move_and_rename_file(search_results_file_path, portfolio_builder_bonds_csv)



