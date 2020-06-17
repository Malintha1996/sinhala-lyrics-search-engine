from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

url = "https://sinhalasongbook.com/"
uClient = uReq(url)
html_content = uClient.read()
uClient.close()

soup_content = soup(html_content,"html.parser")

print(soup_content)