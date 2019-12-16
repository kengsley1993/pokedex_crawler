# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class PokedexItem(Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
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
	# hp = Field()
	# att = Field()
	# defe = Field()
	# sp_att = Field()
	# sp_def = Field()
	# speed = Field()
	type_chart = Field()
	# fire_type = Field()
	# water_type = Field()
	# glass_type = Field()
	# elect_type = Field()
	# normal_type = Field()
	# fight_type = Field()
	# fly_type = Field()
	# bug_type = Field()
	# poison_type = Field()
	# rock_type = Field()
	# ground_type = Field()
	# steel_type = Field()
	# ice_type = Field()
	# psych_type = Field()
	# dark_type = Field()
	# ghost_type = Field()
	# drag_type = Field()
	# fairy_type = Field()
