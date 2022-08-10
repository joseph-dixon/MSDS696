from requests import get

from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["msds696"]
mycol = mydb["climate_score_corpus"]


# Define training data
data = {
 'climate_friendly': [
                       'Joe Biden', # Federal
                       'Pete Buttigieg', # Federal
                       'Ed Markey', # Senate
                       'Bernie Sanders', # Senate
                       'Alexandria Ocasio-Cortez', # House
                       'Diana DeGette', # House
                       'Jay Inslee', # Governor
                       'Kate Brown', # Governor
                       'Michelle Wu', # Mayor
                       'Michael Hancock' # Mayor
                       'Elizabeth Warren', # Senate
                       'Maggie Hassan', # Senate
                       'Brian Schatz', # Senate
                       'Richard Blumenthal', # Senate
                       'John Hickenlooper', # Senate
                       'Cori Bush', # House
                       'Ro Khanna', # House
                       'Jason Crow', # House
                       'Adam Schiff', # House
                       'Nancy Pelosi' # House
                       ],

 'climate_neutral': [
                      'Jerome Powell', # Federal
                      'Janet Yellen', # Federal
                      'Joe Manchin', # Senate
                      'Kyrsten Sinema', # Senate
                      'Jared Golden', # House
                      'Adam Kinzinger', # House
                      'Phil Scott', # Governor
                      'Ron DeSantis', # Governor
                      'Lenny Curry', # Mayor
                      'Eric Adams'# Mayor
                      ],

 'climate_hostile': [
                      'Donald Trump', # Federal
                      'Scott Pruitt', # Federal
                      'Ted Cruz', # Senate
                      'Mitch McConnell', # Senate
                      'Jim Jordan', # House
                      'Lauren Boebert', # House
                      'Greg Abbot', # Governor
                      'Kristi Noem', # Governor
                      'Mike Dunleavy', # Governor
                      'Mike Dewine' # Governor
                      'Marsha Blackburn', # Senate
                      'Tom Cotton', # Senate
                      'Rick Scott', # Senate
                      'Marco Rubio', # Senate
                      'Cynthia Lummis', # Senate
                      'Marjorie Taylor Greene', # House
                      'Paul Gosar', # House
                      'Louie Gohmert', # House
                      'Kevin McCarthy', # House
                      'Madison Cawthorn' # House
                      ],

            'test': [
                     'Michael Bennet',
                     "Joe O'Dea",
                     'Jared Polis',
                     'Heidi Ganahl'
                     ]
    }



def read_article(url):
    """
    Accepts URL as input and returns plain text from URL.
    """

    response = get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.getText()
    return text


def build_corpus(name, label, collection):
    """
    Accepts list of dictionaries. Google Searches each, then compiles list of 10 non-duplicate URLs.
    For each link, calls read_article function and then builds a dictionary to write to DB.
    Returns logging message indicating success or failure.
    """

    # Set Selenium options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chromedriver_autoinstaller.install()


    # Submit search phrase to Google
    print('Searching for {}'.format(name))
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('http://www.google.com')
    element = driver.find_element(by=By.NAME, value="q")
    element.send_keys("{} climate".format(name))
    element.submit()


    # Compile list of 10 unique URLs
    links = []
    counter = 0
    while len(links) < 10:
        try:
            headings = driver.find_elements(By.XPATH, '//div[@class = "g"] | //div[@class = "g Ww4FFb tF2Cxc"] | //div[@class = "g Ww4FFb vt6azd tF2Cxc"]')
            result = headings[counter].find_element(By.CSS_SELECTOR, '.yuRUbf>a')
            url = result.get_attribute("href")
            if url not in links:
                links.append(url)
                counter += 1
            else:
                counter += 1
        except:
            next_page = driver.find_element(By.XPATH, '//a[@aria-label = "Page 2"]')
            next_page.click()
            counter = 0
    print('Links compiled for {}'.format(name))


    # # Iterate through links and build text corpus
    corpus = ''
    for link in links:
        corpus += read_article(link)
        corpus += ':delimit:'


    # Insert document to MongoDB collection
    to_insert = {'name' : name,
                 'label' : label,
                 'corpus' : corpus
                 }
    collection.insert_one(to_insert)
    print('Document added for {}'.format(name))


    driver.quit()

for label in data:
    for name in data[label]:
        build_corpus(name, label, mycol)
        sleep(10)
