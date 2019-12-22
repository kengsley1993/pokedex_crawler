# Pokemon crawler v0.1

## Purpore
Create a crawler to download all pokemon detail into owner pokedex for future project from 'www.pokedex.app'

## Usage
*   Python 3.6
*   urllib
*   pyquery
*   PyMySQL
*   MySQL
*   pyspider
*   Scrapy
*   Scrapy-Splash

## Setup
Create a project folder:
```bash
scrapy startproject pokedex_crawler
```
Create a spider crawl into project folder:
```bash
scrapy spider pokedex_spider www.pokedex.app
```

## Information
The information need to crawl:

*   pokemon's id
*   pokemon's name (tc, en, jp, kr)
*   pokemon's height and weight
*   pokemon's image (icon, pgl, normal front/back, shiny front/back)
*   descrpition of pokemon (sun, moon, us, um, sword, shield)
*   base_statement (base abilty statement)
*   type chart

## Project
### 1. Spider (pokedex_spider)
#### 1.1 Send Requests
Cannot capture information from XHR, because of the page was rendering by js.
Capture pokemon's detail from html, send the request via SphashRequest (basic you can use Scrapy.Request if don't use 'execute' function).
```python
base_url = 'https://www.pokedex.app/zh/pokemon-'

def start_requests(self):
    for pokemon_id in range(self.settings.get('START_ID'), self.settings.get('END_ID')+1):
        url = self.base_url + str(pokemon_id)
        yield SplashRequest(url, callback=self.parse, endpoint='execute',
                            args={'lua_source': script, 'wait': 5})
```

#### 1.2 Data Collect
Find out the location of function to load pokemon's information in html by using F12 (Inspect Element), and filte it out by using pyquery and re. Then, convert it to json for next step.
```python
doc = pq(response.text)
# find the contains letter
items = doc('script:contains("app.factory")')
# filter the text
datas = re.search("return(.*); ", items.text())
# convert to json
orignal = json.loads(datas.group(1))
```

#### 1.3 Store Item
Collect the data json (from prev step) into your own database settings format for store into mysql and download images in local folder.
```python
# you can cap and edit the data you want
pokemon = PokedexItem()
pokemon['id'] = orignal.get("nat_id")
pokemon['image_icon'] = 'https://s.pokeuniv.com/pokemon/icon/'+str(orignal.get("nat_id"))+'.png'
pokemon['image_pgl'] = 'https://s.pokeuniv.com/pokemon/pgl/'+str(orignal.get("nat_id"))+'.png'
image_url_name = ['front', 'back', 'front-shiny', 'back-shiny']
image_item_name = ['image_normal_front', 'image_normal_back', 'image_shiny_front', 'image_shiny_back']
for index, name in enumerate(image_url_name):
    url = 'https://s.pokeuniv.com/pokemon/sprite/'+name+'/'+str(orignal.get("nat_id"))+'.gif'
    response_image = requests.get(url)
    if (response_image.status_code == 200):
        pokemon[image_item_name[index]] = 'https://s.pokeuniv.com/pokemon/sprite/'+name+'/'+str(orignal.get("nat_id"))+'.gif'
    else:
        pokemon[image_item_name[index]] = 'https://s.pokeuniv.com/pokemon/sprite/'+name+'/'+str(orignal.get("nat_id"))+'.png'
pokemon['name_tc'] = orignal.get("name_tc")
pokemon['name_en'] = orignal.get("name_en")
pokemon['name_jp'] = orignal.get("name_jp")
pokemon['name_kr'] = orignal.get("name_kr")
pokemon['height'] = orignal.get("height")
pokemon['weight'] = orignal.get("weight")
pokemon['description_sun'] = orignal.get("description_sun")
pokemon['description_moon'] = orignal.get("description_moon")
pokemon['description_us'] = orignal.get("description_us")
pokemon['description_um'] = orignal.get("description_um")
pokemon['description_sword'] = orignal.get("description_sword")
pokemon['description_shield'] = orignal.get("description_shield")
pokemon['base_stat'] = ','.join(str(num) for num in orignal.get("base_stat"))
pokemon['type_chart'] = ','.join(str(num) for num in orignal.get("type_chart")[0])
yield pokemon
```

### 2. Items
Setup the data elements for data storing and usage in item pipeline.
```python
collection = table = 'pokemon'
id = Field()
image_icon = Field()
image_pgl = Field()
image_normal_front = Field()
image_normal_back = Field()
image_shiny_front = Field()
image_shiny_back = Field()
name_tc = Field()
name_en = Field()
name_jp = Field()
name_kr = Field()
height = Field()
weight = Field()
description_sun = Field()
description_moon = Field()
description_us = Field()
description_um = Field()
description_sword = Field()
description_shield = Field()
base_stat = Field()
type_chart = Field()
```

### 3. Pipelines
#### 3.1 MySQL Pipeline
Init the settings:
```python
class MysqlPipeline():
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
```
Output the setting informations:
```python
@classmethod
def from_crawler(cls, crawler):
    return cls(
        host=crawler.settings.get('MYSQL_HOST'),
        database=crawler.settings.get('MYSQL_DATABASE'),
        user=crawler.settings.get('MYSQL_USER'),
        password=crawler.settings.get('MYSQL_PASSWORD'),
        port=crawler.settings.get('MYSQL_PORT'),
    )
```
Connect to MySQL database:
```python
def open_spider(self, spider):
    self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
    self.cursor = self.db.cursor()
```
Turn off the MySQL database:
```python
def close_spider(self, spider):
    self.db.close()
```
Insert the data into MySQL table:
```python
def process_item(self, item, spider):
    data = dict(item)
    keys = ', '.join(data.keys())
    values = ', '.join(['%s']*len(data))
    insert_sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)
    self.cursor.execute(insert_sql, tuple(data.values()))
    self.db.commit()
    return item
```

#### 3.2 ImagePipeline
Download the file or image and store into local folder.
```python
def file_path(self, request, response=None, info=None):
    url = request.url
    file_name = url.split('/')[-1].split('.')[0] +"/"+ url.split('/')[-2] + "_" + url.split('/')[-1]
    return file_name

def item_completed(self, results, item, info):
    image_paths = [x['path'] for ok, x in results if ok]
    if not image_paths:
        raise DropItem('Image Downloaded Failed')
    return item

def get_media_requests(self, item, info):
    image_name = ['image_icon', 'image_pgl', 'image_normal_front', 'image_normal_back', 'image_shiny_front', 'image_shiny_back']
    for name in image_name:
        yield Request(item[name])
```
Use to download the gif images without store in png:
```python
def check_gif(self, image):
    if image.format is None:
        return True

def persist_gif(self, key, data, info):
    root, ext = os.path.splitext(key)
    absolute_path = self.store._get_filesystem_path(key)
    self.store._mkdir(os.path.dirname(absolute_path), info)
    f = open(absolute_path, 'wb')  # use 'b' to write binary data.
    f.write(data)

def image_downloaded(self, response, request, info):
    try:
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            width, height = image.size
            if self.check_gif(image):
                self.persist_gif(path, response.body, info)
            else:
                self.store.persist_file(
                    path, buf, info,
                    meta={'width': width, 'height': height},
                    headers={'Content-Type': 'image/jpeg'})
            return checksum
    except:
        pass
```

### 4. Settings
Enter the splash_url to connect Splash
```python
SPLASH_URL = 'http://localhost:8050'
```
Enter the element of PyMQL for setup database env.
```python
MYSQL_HOST = 'Enter your host of database'
MYSQL_DATABASE = 'Enter the name of database'
MYSQL_USER = 'Enter the username of database'
MYSQL_PASSWORD = 'Enter the password of database'
MYSQL_PORT = 3306
```
Setup the item pipelines:
```python
ITEM_PIPELINES = {
    'pokedex.pipelines.FilePipeline': 300,
    'pokedex.pipelines.MysqlPipeline': 302,
}

IMAGES_STORE = './images'
FILES_STORE = './images'
```

## Run
Start the crawler, store the image and information into local
```bash
scrapy crawl pokedex_spider
```
