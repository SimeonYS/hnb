import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import HnbItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class HnbSpider(scrapy.Spider):
	name = 'hnb'
	start_urls = ['https://www.hnb.hr/javnost-rada/novosti',
				  'https://www.hnb.hr/priopcenja/pretrazivanje?p_p_id=archivefilterassetpublisher_WAR_hnbportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_archivefilterassetpublisher_WAR_hnbportlet_pagingExecuted=true&p_r_p_ddmId=d8df8af7-f826-4e9e-b766-76a819a3bad3&_archivefilterassetpublisher_WAR_hnbportlet_resetCur=false&_archivefilterassetpublisher_WAR_hnbportlet_cur=1'
				  ]

	def parse(self, response):
		post_links = response.xpath('//h4/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//ul[@class="lfr-pagination-buttons pager"]/li[3]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//span[@class="displayDate"]/text()').get()
		date = re.findall(r'\d+\.\d+\.\d+',date)
		title = response.xpath('//div[@class="article"]/h2/text()').get()
		content = response.xpath('//div[@class="article-text"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=HnbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
