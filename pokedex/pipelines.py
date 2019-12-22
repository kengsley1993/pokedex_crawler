# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# import pymysql
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import os
from scrapy.utils.misc import md5sum
from scrapy import Request
from scrapy.exceptions import DropItem
# from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline

class MysqlPipeline():
	def __init__(self, host, database, user, password, port):
		self.host = host
		self.database = database
		self.user = user
		self.password = password
		self.port = port

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			host=crawler.settings.get('MYSQL_HOST'),
			database=crawler.settings.get('MYSQL_DATABASE'),
			user=crawler.settings.get('MYSQL_USER'),
			password=crawler.settings.get('MYSQL_PASSWORD'),
			port=crawler.settings.get('MYSQL_PORT'),
		)

	def open_spider(self, spider):
		self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
		self.cursor = self.db.cursor()

	def close_spider(self, spider):
		self.db.close()

	def process_item(self, item, spider):
		data = dict(item)
		keys = ', '.join(data.keys())
		values = ', '.join(['%s']*len(data))
		insert_sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)
		# update_sql = 'update %s set %s=%s where %s=%s'
		self.cursor.execute(insert_sql, tuple(data.values()))
		self.db.commit()
		return item

class FilePipeline(FilesPipeline):
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