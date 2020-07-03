from elasticsearch import Elasticsearch,helpers
import json


with open('lyrics.json' , encoding='utf-8') as infile:
  object_list = json.load(infile)

es  = Elasticsearch()
helpers.bulk(es,object_list,index="hela-songs",doc_type='_doc')