
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
from random import randint
from urllib.parse import urlparse
import re
from functions import *

path = ".\chromedriver" #Ruta del driver
driver = webdriver.Chrome(path)

url= "https://mercadolibre.com.ar"
search = "playstation 4 pro"

driver.get(url)

#cookies handle
try:
       cookie_btn = driver.find_element(By.XPATH, "//div[@class='cookie-consent-banner-opt-out__actions']/button[contains(@data-testid,'action:understood-button')]")
       time.sleep(randint(1,5))
       cookie_btn.click()
except NoSuchElementException:
        pass

#navigation bar handle
nav_search = driver.find_element(By.XPATH, "//form[@class='nav-search']/input[@class='nav-search-input']")
nav_search.clear()
nav_search.send_keys(search)
nav_search.send_keys(Keys.RETURN)                       

pagination = driver.find_element(By.XPATH, "//div[@class='ui-search-pagination']/ul/li[2]").text
pagination = [ int(s) for s in pagination.split() if s.isdigit()][0]
pagination = 1 # cantidad de páginas, comentar la linea para todas las páginas.
records = []
k=0

start = time.time()
for i in range(1,pagination+1):
        if i != pagination:
                next_page_button = driver.find_element(By.XPATH, "//div[@class='ui-search-pagination']/ul/li[contains(@class, '--next')]/a")
        #página
        page = BeautifulSoup(driver.page_source,'html.parser')
        #título
        title_products = driver.find_elements(By.XPATH, "//h2[@class='ui-search-item__title']")
        title_products = [ title.text  for title in title_products ]
        #precio
        price_products = driver.find_elements(By.CLASS_NAME, "price-tag-fraction")
        price_products = [ price.text for price in price_products  ]
        #link
        link_products = driver.find_elements(By.XPATH, "//div[@class='ui-search-item__group ui-search-item__group--title shops__items-group']/a[1]")
        link_products = [ link.get_attribute("href") for link in link_products   ]
        
        j = 1 
        
        article_location = []
        article_province = []
        article_status = []
        article_qty = []
        seller_profile_name = []
        seller_profile_link = []

        for articles in page.find_all('li', attrs={'class':'ui-search-layout__item'}):

                print("Página", i, "de", pagination,"|| Artículo", j, "de", len(link_products), "||", title_products[j-1])
                
                driver.execute_script("window.open('"+link_products[j-1]+"')") # Open new window
                driver.switch_to.window(driver.window_handles[-1]) #https://stackoverflow.com/questions/17325629/how-to-open-a-new-window-on-a-browser-using-selenium-webdriver-for-python
                
                article = BeautifulSoup(driver.page_source,'html.parser')
                
                ubication = article.find('p', attrs={'class':'ui-seller-info__status-info__subtitle'})
                profile = article.find('a',attrs={'class':'ui-pdp-media__action ui-box-component__action'})
                sell_condition = article.find('span',attrs={'class':'ui-pdp-subtitle'})

                if ubication:                        
                        province = return_ubication(ubication.text, "provincia") #Provincia                       
                        location = return_ubication(ubication.text, "localidad") #Localidad
                        article_location.append(location)
                        article_province.append(province)
                        #driver.close()
                        #driver.switch_to.window(driver.window_handles[0])
                else:
                        print('location not available')
                        article_location.append('')
                        article_province.append('')
                        #driver.close()
                        #driver.switch_to.window(driver.window_handles[0])
                
                if profile:
                        parsed = urlparse(profile['href'])
                        profile_name = re.sub("\/","",parsed.path)
                        seller_profile_name.append(profile_name)
                        seller_profile_link.append(profile['href'])
                        #print("Perfil:",profile_name)
                else: 
                        #print("profile not available")
                        seller_profile_name.append('')
                        seller_profile_link.append('')

                if sell_condition:
                        article_status.append(status(sell_condition))
                        article_qty.append(qty(sell_condition))
                        #print(status(sell_condition),"| Vendidos:", qty(sell_condition))
                else:   
                        #print("Reacondicionado")
                        article_status.append('Reacondicionado')
                        article_qty.append('')
       
                time.sleep(randint(1,3))
                j=j+1 # total por página
                k=k+1 # total
                
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                '''
                print("name_product", len(title_products))
                print("status_products", len(article_status))
                print("price_product", len(price_products))
                print("article_qty", len(article_qty))
                print("link_product",len(link_products))
                print("provincia_product", len(article_province))
                print("localidad_product", len(article_location))
                print("seller_profile_name",len(seller_profile_name))
                print("seller_profile_link",len(seller_profile_link))
                '''
        data_products = {
                "name_product":title_products,
                "status_product":article_status,
                "price_product":price_products,
                "article_qty":article_qty,
                "profile_name":seller_profile_name,
                "provincia_product":article_province,
                "localidad_product":article_location,
                "link_product":link_products,
                "profile_link":seller_profile_link
        }
        df =  pd.DataFrame(data_products)
        records.append(df)
        
        if i != pagination:
                driver.execute_script("arguments[0].click()", next_page_button)
                page = BeautifulSoup(driver.page_source,'html.parser')
      
df = pd.concat(records)
end = time.time()

print("Cantidad de articulos:",len(df))

#print(f"Tiempo transcurrido {human_time}")
human_time = ss_to_hhmmss(int(end-start))
print("Tiempo transcurrido:", human_time)

#df = df.sort_values(by=['PRICE'], ascending=[True])
df.to_csv(r'./lista.csv', index=True, header=True, encoding='utf-8-sig')
time.sleep(randint(1,3))
driver.close