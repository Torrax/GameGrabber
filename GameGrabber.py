import discord
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
PATH = "C:\Program Files (x86)\chromedriver.exe"
URL = ""
global count
count = 0
link = ["","","","","","","","","",""]

######## Discord Connect #############
client = discord.Client()

@client.event
async def on_ready():
  print ('We have logged in as {0.user}'
  .format(client))

@client.event
async def on_message(message):
  global count
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('$check'):
    count = 1
    gameReq = msg.split('$check ',1)[1]
    #await message.channel.send('Price checking ' + gameReq.title() + '...')
    await message.add_reaction('\U0001F911')
    searchString = gameReq
    steamSearchString = searchString.replace(" ", "+")
    cdKeysSearchString = searchString.replace(" ", "%20")
    g2aSearchString = searchString.replace(" ", "%20")
    g2aSearchString += " GLOBAL"
    
    ############ STEAM ##########
    URL = "https://store.steampowered.com/search/?term=" + steamSearchString + "&cc=ca"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    containers = soup.find_all("a", {"class": "search_result_row ds_collapse_flag"})

    reply = "***STEAM PRICES***\n**-----------------------------------------**\n"
    print("STEAM PRICES")
    print("-----------------------------------------")
    i = 0
    for container in containers:
      if (i < 3):
        name = container.findAll("span", {"class": "title"})
        if container.findAll("div", {"class": "col search_price responsive_secondrow"}):
          price = container.findAll("div", {"class": "col search_price responsive_secondrow"})
          name = name[0].text
          price = price[0].text
          price = price.replace(" ", "").replace('\r', '').replace('\n', '').replace('CDN', '').replace('USD', '').replace('FreetoPlay', 'Free')
          print(name + '  -----  ' + price)
          reply += (str(count) + ". " + name.title() + '  **--------**  ' + price + '\n')
          print ("URL:", container['href'])
          link[count] = ('steam://openurl/' + container['href'] + "?cc=ca")
          count += 1
        else:
          price = container.findAll("div", {"class": "col search_price discounted responsive_secondrow"})
          discount = container.findAll("div", {"class": "col search_discount responsive_secondrow"})
          discount = discount[0].text
          discount = discount.replace(" ", "").replace('\r', '').replace('\n', '').replace('-', '')
          name = name[0].text
          price = price[0].text
          price = price.replace(" ", "").replace('\r', '').replace('\n', '').replace('CDN', '').replace('USD', '').replace('FreetoPlay', 'Free')
          remove = (price[1:].index("$")) + 1
          price = price[remove:]
          print(name + '  --------  ' + price + '   **' + discount + ' OFF**')
          reply += (str(count) + ". " + name.title() + '  **--------**  ' + price + '   **' + discount + ' OFF**\n')
          print ("URL:", container['href'])
          link[count] = ('steam://nav/console' + container['href'] + "?cc=ca")
          count += 1
        i += 1


    ############## CD KEYS ##################
    URL = "https://www.cdkeys.com/catalogsearch/result/?q="+ cdKeysSearchString +"&platforms=Steam&region=Worldwide&currency=CAD"
    driver = webdriver.Chrome(PATH)
    driver.get(URL)
    content = driver.find_element_by_id("instant-search-results-container")
    reply += "\n***CDKEYS PRICES***\n**-----------------------------------------**\n"
    print("CDKEYS PRICES")
    print("-----------------------------------------")
    i = 0
    while (i < 3):
        results = content.find_elements_by_css_selector("li.ais-InfiniteHits-item.product-item__in-region")
        if i < (len(results)):
          results = results[i]
          name = results.find_element_by_css_selector("h3.result-title.text-ellipsis")
          price = results.find_element_by_css_selector("span.after_special")
          links = results.find_element_by_css_selector("h3.result-title.text-ellipsis > a").get_attribute('href')
          name = name.text
          name = name.replace(' PC', '').replace(' -', '').replace(':', '')
          price = price.text
          price = price.replace('CA', '').replace('US', '')
          print(name.title() + '  --------  ' + price)
          link[count] = links
          reply += (str(count) + ". " + name.title() + '  **--------**  ' + price + '\n')
          count += 1
        i += 1
    driver.quit()

    ############## G2A KEYS ##################
    URL = "https://www.g2a.com/category/gaming-c1?f[drm][0]=1&query=" + g2aSearchString + "&currency=CAD"
    driver = webdriver.Chrome(PATH)
    driver.get(URL)
    content = driver.find_element_by_css_selector("section.indexes__ContentSlot-wklrsw-193.bbJYLf")

    reply += "\n***G2A PRICES***\n**-----------------------------------------**\n"
    print("G2A PRICES")
    print("-----------------------------------------")
    i = 0
    while (i < 3):
        name = content.find_elements_by_css_selector("h3.indexes__ve-wklrsw-118.jDoEKD.hTAfZi")
        price = content.find_elements_by_css_selector("span.indexes__A1-wklrsw-93.jckuPr")
        elems = content.find_elements_by_css_selector("div.indexes__I-wklrsw-91.indexes__ye-wklrsw-112.ggXzuE.jBmMTn > a")
        links = [elem.get_attribute('href') for elem in elems]
        if i < (len(price)):
            name = name[i].text
            name = name.replace(' Steam Key', '').replace(' Gift', '').replace(' Steam', '').replace(' GLOBAL', '').replace(' (PC)', '').replace(' -', '').replace(':', '')
            price = price[i].text
            price = "$" + price
            print(name + '  --------  ' + price)
            link[count] = links[i]
            reply += (str(count) + ". " + name.title() + '  **--------**  ' + price + '\n')
            count += 1
        i += 1
    driver.quit()
    await message.channel.send(reply)

  if msg == '$1':
    if count > 1:
        reply = 'Link # 1'
        print("Sending Link 1")
        await message.channel.send(link[1])

  if msg == '$2':
    if count > 2:
        reply = 'Link # 2'
        print("Sending Link 2")
        await message.channel.send(link[2])

  if msg == '$3':
    if count > 3:
        reply = 'Link # 3'
        print("Sending Link 3")
        await message.channel.send(link[3])

  if msg == '$4':
    if count > 4:
        reply = 'Link # 4'
        print("Sending Link 4")
        await message.channel.send(link[4])

  if msg == '$5':
    if count > 5:
        reply = 'Link # 5'
        print("Sending Link 5")
        await message.channel.send(link[5])

  if msg == '$6':
    if count > 6:
        reply = 'Link # 6'
        print("Sending Link 6")
        await message.channel.send(link[6])

  if msg == '$7':
    if count > 7:
        reply = 'Link # 7'
        print("Sending Link 7")
        await message.channel.send(link[7])

  if msg == '$8':
    if count > 8:
        reply = 'Link # 8'
        print("Sending Link 8")
        await message.channel.send(link[8])

  if msg == '$9':
    if count > 9:
        reply = 'Link # 9'
        print("Sending Link 9")
        await message.channel.send(link[9])
  
client.run("TOKEN")
