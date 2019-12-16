# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from urllib.parse import quote
from pokedex.items import PokedexItem
from scrapy_splash import SplashRequest
from pyquery import PyQuery as pq
import re
import json
import requests

script = """
function main(splash, args)
  HEADERS = {
	['Host']= 'www.pokedex.app',
	['User-Agent']= 'Enter your user agent',
	['Accept']= 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	['Accept-Language']= 'en-US,en;q=0.5',
	['Connection']= 'keep-alive',
	['Cookie']= 'Enter your cookie',
	['Upgrade-Insecure-Requests']= '1',
  }
  splash:set_custom_headers(HEADERS)
  splash.images_enabled = false
  splash:go(args.url)
  return splash:html()
end
"""

class PokedexSpider(Spider):
	name = 'pokedex_spider'
	allowed_domains = ['www.pokedex.app']
	base_url = 'https://www.pokedex.app/zh/pokemon-'

	def start_requests(self):
		for pokemon_id in range(self.settings.get('START_ID'), self.settings.get('END_ID')+1):
			url = self.base_url + str(pokemon_id)
			# yield SplashRequest(url, cookies=self.settings.get('COOKIES'), headers=self.settings.get('HEADERS'), callback=self.parse, endpoint='execute',
			# 					args={'lua_source': script, 'wait': 5, 'http_method': 'GET'})
			yield SplashRequest(url, callback=self.parse, endpoint='execute',
								args={'lua_source': script, 'wait': 5})

	def parse(self, response):
		# right_section = response.xpath('//section[@class="float-right box pokemon-sprites"]')

		# print(response.text)
		doc = pq(response.text)
		# find the contains letter
		items = doc('script:contains("app.factory")')
		# filter the text
		datas = re.search("return(.*); ", items.text())
		# convert to json
		orignal = json.loads(datas.group(1))

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
		# pokemon['hp'] = orignal.get("base_stat")[0]
		# pokemon['att'] = orignal.get("base_stat")[1]
		# pokemon['defe'] = orignal.get("base_stat")[2]
		# pokemon['sp_att'] = orignal.get("base_stat")[3]
		# pokemon['sp_def'] = orignal.get("base_stat")[4]
		# 'speed': orignal.get("base_stat")[5],
		pokemon['type_chart'] = ','.join(str(num) for num in orignal.get("type_chart")[0])
		# 'fire_type': orignal.get("type_chart")[0][1],
		# 'water_type': orignal.get("type_chart")[0][2],
		# 'glass_type': orignal.get("type_chart")[0][3],
		# 'elect_type': orignal.get("type_chart")[0][4],
		# 'normal_type': orignal.get("type_chart")[0][5],
		# 'fight_type': orignal.get("type_chart")[0][6],
		# 'fly_type': orignal.get("type_chart")[0][7],
		# 'bug_type': orignal.get("type_chart")[0][8],
		# 'poison_type': orignal.get("type_chart")[0][9],
		# 'rock_type': orignal.get("type_chart")[0][10],
		# 'ground_type': orignal.get("type_chart")[0][11],
		# 'steel_type': orignal.get("type_chart")[0][12],
		# 'ice_type': orignal.get("type_chart")[0][13],
		# 'psych_type': orignal.get("type_chart")[0][14],
		# 'dark_type': orignal.get("type_chart")[0][15],
		# 'ghost_type': orignal.get("type_chart")[0][16],
		# 'drag_type': orignal.get("type_chart")[0][17],
		# 'fairy_type': orignal.get("type_chart")[0][18],

		# print(pokemon)
		yield pokemon
