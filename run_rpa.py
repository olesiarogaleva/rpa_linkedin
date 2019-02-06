# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
from time import sleep
import json
import sys


companies = open('companies.txt', 'r').readlines()
LN_LOGIN = raw_input('Enter your login:')
LN_PASS = raw_input('Enter your pass:')
LN_TITLES = raw_input('Enter job titles, comma separated:').split(",")


class Ln(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_ln(self):
        driver = self.driver
        count = 0
        done_accs = []

        driver.get("https://www.linkedin.com/")
        driver.find_element_by_id("login-email").click()
        driver.find_element_by_id("login-email").clear()
        driver.find_element_by_id("login-email").send_keys(LN_LOGIN)
        driver.find_element_by_id("login-password").clear()
        driver.find_element_by_id("login-password").send_keys(LN_PASS)
        driver.find_element_by_id("login-submit").click()

        sleep(2)

        for comp in companies:
            try:
                driver.get("https://www.linkedin.com/search/results/companies/?keywords=" + comp + "&origin=GLOBAL_SEARCH_HEADER")
                sleep(1)
                driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Companies'])[1]/following::h3[2]").click()
                sleep(2)
                empl_href = driver.find_element_by_xpath('//a[@data-control-name="topcard_see_all_employees"]').get_attribute("href")
                founder_hrefs = []

                pages = len(driver.find_elements_by_xpath('//button[@data-ember-action=""]'))

                for i in range(1, pages - 1):

                    driver.get(empl_href + "&page=" + str(i))
                    sleep(2)
                    driver.execute_script("window.scrollTo(0, 1000);")
                    sleep(1)

                    empls = driver.find_elements_by_xpath("//*[@class='search-result search-result__occluded-item ember-view']")
                    for j in empls:
                        el_html = j.find_element_by_xpath('.//*[@class="subline-level-1 t-14 t-black t-normal search-result__truncate"]').get_attribute("outerHTML").lower()

                        if len([t for t in LN_TITLES if t.lower().strip() in el_html.lower().strip()]) > 0:
                            el_href = j.find_element_by_xpath('.//a[@class="search-result__result-link ember-view"]').get_attribute("href")
                            founder_hrefs.append(el_href)

                for i in founder_hrefs:
                    try:
                        driver.get(i)
                        sleep(1)
                        page = driver.find_element_by_xpath('.//div[@class="pv-content profile-view-grid neptune-grid two-column ghost-animate-in "]').get_attribute("outerHTML")
                        
                        if "pv-s-profile-actions pv-s-profile-actions--connect button-primary-large mr2 mt2 pv-s-profile-actions--pending" in page:
                            continue  
                        if "pv-s-profile-actions pv-s-profile-actions--message button-primary-large mr2 mt2" in page:
                            continue
                        if "pv-s-profile-actions pv-s-profile-actions--send-in-mail button-primary-large mr2 mt2" in page:
                            continue

                        driver.find_element_by_xpath('.//button[@class="pv-s-profile-actions pv-s-profile-actions--connect button-primary-large mr2 mt2"]').click()
                        sleep(1)
                        driver.find_element_by_xpath('.//button[@class="button-primary-large ml1"]').click()
                        sleep(2)
                        count += 1 
                        print("added: " + str(count))
                        print(i)
                        done_accs.append(i)
                    except:
                        print('except')
                        continue
            except:
                print('except company')
                continue

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
