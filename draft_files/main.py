from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
from selenium.webdriver.common.by import By

USER = "standard_user" 
PASSWORD = "secret_sauce"  

def main():
    service = Service(ChromeDriverManager().install())
    option = webdriver.ChromeOptions()
    #option.add_argument("--headless")
    option.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service,option=option)
    driver.get("https://saucedemo.com/")

    #LOGIN
    driver.find_element(By.ID,"user-name").send_keys(USER)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()


    #COMPRAS
    driver.find_element(By.NAME, "add-to-cart-sauce-labs-bolt-t-shirt").click()
    driver.find_element(By.ID, "add-to-cart-test.allthethings()-t-shirt-(red)").click()

    #CARRITO
    driver.find_element(By.XPATH, "_______________").click()
    driver.find_element(By.ID, "checkout").click()

    #PAGAR
    driver.find_element(By.ID,"fist-name").send_keys("test")
    driver.find_element(By.ID, "last-name").send_keys("test")
    driver.find_element(By.ID, "postal-code").send_keys("12345")
    time.sleep(2)

    driver.find_element(By.ID, "continue").click()
    time.sleep(4)
    
    driver.find_element(By.ID, "finish").click()

    time.sleep(10)
    driver.quit()
    



if __name__ == "__main__":
    main()

