import json

import bcrypt
# ---------------------------------------------------- SELENIUM
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class MyChromeDriverPolytech:

    def __init__(self, url:str, display_window:bool):
        # -- Set the options about the driver
        options = Options()
        if display_window:
            options.add_experimental_option("detach", True)
            options.add_argument("start-maximized")
        else:
            options.add_argument("--headless")

        # -- Set the driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

    def accept_cookies(self):
        # Wait for 10s the element appear on the page
        btn_refuse = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[3]/button[2]'))
        )

        if btn_refuse is not None: btn_refuse.click()

    def login_intranet(self, login, pwd):
        input_pseudo = self.driver.find_element(By.ID, "user")
        input_pseudo.send_keys(login)

        input_pwd = self.driver.find_element(By.ID, "pass")
        input_pwd.send_keys(pwd)

        input_btn = self.driver.find_element(By.XPATH, '/ html / body / section[3] / div / div / div / div / div / form / fieldset / input[3]')
        input_btn.click()

    def go_to_page_prog_inge(self):
        link_prog_inge = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div/div[1]/ul/li[3]/ul/li[2]/a')),
            # EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div/div[1]/ul/li[3]/ul/li[2]/a'))
        )
        print(link_prog_inge)
        if link_prog_inge: link_prog_inge.click()


    def research_idu_program(self):
        radio_idu = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div[5]/div[2]/div/div/form/ul/li[2]/div/input[4]')
        if radio_idu: radio_idu.click()

        btn_search = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div[5]/div[2]/div/div/form/div[2]/button[1]')
        if btn_search: btn_search.click()

    def get_list_prof(self, nb_prof):
        # -- Get Container of all items (of all lines of the array)
        container_items = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div[5]/div[3]/div/div/div[2]/div[2]')

        # -- Get All Items in the container
        items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'item'))
            )


        list_prof = []

        for i in range(1, len(items)):
            link_xpath = "/html/body/div[2]/div/div/div/div[2]/div/div[5]/div[3]/div/div[2]/div[2]/div["+str(i)+"]/div[2]/ul/li[4]/a"


            # -- GET link matiere and click on
            link_matiere = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, link_xpath))
            )
            if link_matiere: link_matiere.click()

            # -- GET resp matiere and add in list
            resp_matiere = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/div[5]/div[3]/div/div[2]/div[2]/div[3]/div[1]/div[2]"))
            )
            if resp_matiere:
                # -- Split if 2 names in the same responsable
                # - If separator is "et"
                if " et " in resp_matiere.text:
                    names = resp_matiere.text.split(" et ")
                # - Elif separator is ","
                elif ", " in resp_matiere.text:
                    names = resp_matiere.text.split(", ")
                # - Elif separator is ";"
                elif " ; " in resp_matiere.text:
                    names = resp_matiere.text.split("; ")
                else:
                    names = [resp_matiere.text]

                for name in names:
                    if name not in list_prof: list_prof.append(name)


            # -- GET link close current matiere and click on
            btn_close_current_matiere = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div[5]/div[3]/div/div[2]/div[1]/div[1]/div[2]/a'))
            )
            if btn_close_current_matiere: btn_close_current_matiere.click()


            if i > nb_prof: return list_prof


class MyChromeDriverArticle:
    def __init__(self, url: str, display_window: bool):
        # -- Set the options about the driver
        options = Options()
        if display_window:
            options.add_experimental_option("detach", True)
            options.add_argument("start-maximized")
        else:
            options.add_argument("--headless")

        # -- Set the driver
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(url)

    def make_first_search(self, first_prof:str):
        # -- Input Search
        input_search = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div[7]/div[1]/div[2]/form/div/input'))
        )
        if input_search: input_search.send_keys(first_prof)

        # -- Btn Search
        btn_search = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div[7]/div[1]/div[2]/form/button'))
        )
        if btn_search: btn_search.click()

        # -- Link First Result
        link_first_result = self.get_first_article()

        if link_first_result is not None:
            dict_prof = {"prof_name": first_prof, "prof_url": link_first_result.get_attribute('href')}
        else:
            dict_prof = {"prof_name": first_prof, "prof_url": "Pas d'articles publies"}

        return dict_prof


    def search_all_prof(self, list_prof_name):
        # -- Make the first research (where the interface is different)
        dict_fist_prof = self.make_first_search(list_prof_name[0])

        list_prof_info = [dict_fist_prof]

        # -- For all ohter porf
        for prof_name in list_prof_name[1:]:
            # -- Input Search
            input_search = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div/div[8]/div[1]/div/form/div/input'))
            )
            if input_search:
                input_search.clear()
                input_search.send_keys(prof_name)

            # -- Btn Search
            btn_search = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div/div[8]/div[1]/div/form/button'))
            )
            if btn_search: btn_search.click()

            # -- Link First Result
            link_first_result = self.get_first_article()

            # -- Add Prof to the list
            if link_first_result is not None:
                 list_prof_info.append({"prof_name": prof_name, "prof_url": link_first_result.get_attribute('href')})
            else:
                list_prof_info.append({"prof_name": prof_name, "prof_url": "Pas d'articles publies"})

        Prof.write_in_json(list_prof_info)


    def get_first_article(self):
        # -- Try to get the first article
        link_first_result = None
        try:
            link_first_result = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="gs_rt"]/a'))
            )
        except:
            pass

        return link_first_result


class Prof:

    def __init__(self, name, url):
        self.name = name
        self.url = url

    @staticmethod
    def write_in_json(list_prof):
        with open("profs.json", "r+") as profs_file:
            json.dump(list_prof, profs_file, indent=4)


if __name__ == '__main__':
    my_chrome_driver_polytech = MyChromeDriverPolytech("https://www.polytech.univ-smb.fr/intranet/", True)
    my_chrome_driver_polytech.accept_cookies()

    login = input("Entrer votre login")
    pwd = input("Entrer votre pwd")

    my_chrome_driver_polytech.login_intranet(login, pwd)
    my_chrome_driver_polytech.go_to_page_prog_inge()
    my_chrome_driver_polytech.research_idu_program()
    list_prof_name = my_chrome_driver_polytech.get_list_prof(4)

    print(list_prof_name)
    # print(list_prof[1:])

    my_chrome_driver_article = MyChromeDriverArticle("https://scholar.google.fr/", True)
    # my_chrome_driver_article.make_first_search( list_prof[0] )
    my_chrome_driver_article.search_all_prof(list_prof_name)

















