from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sqlite3




# driver = webdriver.Firefox()



from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
# chrome_options.add_argument("--window-size=1920x1080")
# driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

# from pymongo import MongoClient

# options = Options()

now = str(datetime.now())

placeName = {}
with open("assets/name.csv", "r", encoding="utf-8") as fp:
    lines = fp.readlines()
    for line in lines:
        placeItem = line.replace("\n", "").split(",")
        placeName[placeItem[0]] = placeItem[1]

url = "https://voice.baidu.com/act/newpneumonia/newpneumonia"
# browser = webdriver.Chrome("C:\workspace\chromedriver.exe")
#browser = webdriver.Firefox(options=options, executable_path=r'/home/zhaobo/geckodriver', service_log_path = "/home/zhaobo/geckodriver.log")
browser = webdriver.Chrome( chrome_options=chrome_options, executable_path=r'/home/zhaobo/chromedriver')



browser.get(url)


unfolds = browser.find_elements_by_xpath("//div[starts-with(@class,'Common')]")

for unfold in unfolds:
    if unfold.text == "展开全部":
        unfold.click()


browser.find_element_by_xpath("//table[starts-with(@class,'VirusTable')]").find_elements_by_tag_name("tr")
soup = BeautifulSoup(browser.page_source, 'html.parser')

time.sleep(4)
sqls = "INSERT OR REPLACE INTO virus ('datetime'"
sqle = ") VALUES ('" + now + "', "

items = soup.find_all("tr")
for item in items:
    chname = ""
    confirmed, recovered, death = 0, 0, 0,
    try:
        chname = item.find_all("td")[0].text
    except:
        pass

    if (chname in placeName.keys()):
        confirmed = item.find_all("td")[1].text.strip()
        recovered = item.find_all("td")[2].text.strip()
        death = item.find_all("td")[3].text.strip()
        if recovered == "":
            recovered = "0"
        if death == "":
            death = "0"
        if confirmed == "":
            confirmed = "0"
        print(chname, placeName[chname], confirmed, recovered, death)
        sqls += ", '" + placeName[chname].strip() + "'"
        sqle += "'" + confirmed + "-0-" + recovered + "-" + death + "', "

browser.close()

conn = sqlite3.connect("assets/virus.db")
cursor = conn.cursor()

insert_record_sql = sqls + sqle[0: len(sqle) -2] + ")"
cursor.execute(insert_record_sql)
conn.commit()
cursor.execute("SELECT * from virus")
col_name_list = [tuple[0] for tuple in cursor.description]


with open("assets/virus.csv", "w", encoding="utf-8") as fp:
    fp.write(str(col_name_list)[1:len(str(col_name_list))-1].replace("\'", "").replace(", ", ",") + "\n")
    for row in cursor.execute("SELECT * from virus"):
        fp.write(str(row)[1:len(str(row))-1].replace("\'", "").replace("None", "").replace(", ", ",") + "\n")

conn.close()
print("finished!")
