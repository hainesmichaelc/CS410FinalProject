

import urllib3
import bs4

http = urllib3.PoolManager()

imdb_url = "https://www.imdb.com/find?q=star+war"
r = http.request('GET', imdb_url)
soup = bs4.BeautifulSoup(r.data,'html.parser')
str_imdb_results = soup.findAll('div',{'class':'lister-item-content'})
print(str_imdb_results)
