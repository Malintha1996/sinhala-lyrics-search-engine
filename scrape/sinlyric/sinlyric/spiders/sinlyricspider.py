import scrapy
import requests
from scrapy.spiders import SitemapSpider
from scrapy.http.request import Request
import re
import os

class SongBookSpider(scrapy.Spider):
    name = "SongBook"
    allowed_domains = ["sinhalasongbook.com"]
    start_urls   = ["https://sinhalasongbook.com/all-sinhala-song-lyrics-and-chords/?_page=" + str(i) for i in range(1, 22)]
    count = 0

    def parse_song(self, response):
        separator = ','
        song_page = response
        title_mix = (song_page.xpath('//div[@class="entry-content"]/h2/text()')).get()
        title_sin = (song_page.xpath('//span[@class="sinTitle"]/text()')).get()

        artist = song_page.xpath('//div[@class="su-row"]//span[@class="entry-categories"]//a/text()').extract()
        artist_data = (separator.join(artist))

        genre = song_page.xpath('//div[@class="su-row"]//span[@class="entry-tags"]//a/text()').extract()
        genre_data = (separator.join(genre))
        
        writer = song_page.xpath('//div[@class="su-row"]//span[@class="lyrics"]//a/text()').extract()
        writer_data = (separator.join(writer))
        
        music  = song_page.xpath('//div[@class="su-row"]//span[@class="music"]//a/text()').extract()
        music_data = (separator.join(music))

        rating = song_page.xpath('//div[@class="tptn_counter"]/text()').extract()
        rating_data = separator.join(rating).replace("Visits","").replace("-","").strip()

        songBody = (song_page.xpath('//div[@class="entry-content"]//pre/text()').extract())
        songBodySplit = []
        for parts in songBody:
            lines = parts.split('\n')
            for line in lines:
                songBodySplit.append(line)
        
        song = ""
        chords = ""

        for line in songBodySplit:
            if(re.search('[a-zA-Z]', line)):
               chords = chords + line +"\n"
            else:
                if(len(line)!=0):
                    line = line.replace('+','')
                    line = line.replace('|','')
                    line.strip()
                    song = song + line + os.linesep
                
        
        yield {
            'title_mix': title_mix,
            'title_sin': title_sin,
            'artist' : artist_data,
            'genre' : genre_data,
            'rating': rating_data,
            'writer' : writer_data,
            'music' : music_data,
            'song' : song
        }
        

    def parse(self, response):
        song_hrefs = response.xpath('//div[@class="col-md-6 col-sm-6 col-xs-12 pt-cv-content-item pt-cv-1-col"]//a/@href').extract()
        for song in song_hrefs:
            self.count = self.count + 1
            yield scrapy.Request(
                song,
                callback=self.parse_song
            )

            

        print("-----------------------count--------", self.count)
