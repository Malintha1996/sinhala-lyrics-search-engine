from elasticsearch import Elasticsearch
from sinling import SinhalaTokenizer
from sinling import word_splitter
es  = Elasticsearch()
tokenizer = SinhalaTokenizer()
artist_boosters = ["ගේ","ගෙ","කියන","ගායනා","කිව්ව","ගැයූ","ගයපු"]
writer_boosters = ["රචනා","ලිව්ව","ලියන","ලියපු","රචිත"]
music_boosters = ["වාදනය","සංගීතය","නාද"]
genre_boosters = ["පොප්","නව","පැරණි","ක්ලැසික්"]
rating_boosters = ["හොදම","ප්‍රමුඛතම","ප්‍රධාන","ජනප්‍රිය","ගෝල්ඩන්","චිත්‍රපට"]
boosts_default = {"title_si":1.0,"artist":1.0,"writer":1.0,"music":1.0,"genre":1.0,"lyrics":1.0}

class QueryProcessor :
    def __init__(self):
        print("init")

    @classmethod
    def processQ(self,query):
        res = self.process(query)
        print(res)
        return res
  
    @classmethod
    def predictQType(self,tokens):
        boost_params = []
        boosts = {"title_si":1.0,"artist":1.0,"writer":1.0,"music":1.0,"genre":1.0,"lyrics":1.0}
        for token in tokens:
            splits = word_splitter.split(token)
            if(token in rating_boosters or splits['affix'] in rating_boosters or splits['base'] in rating_boosters):
                boost_params.append("rate")
            if(token in artist_boosters or splits['affix'] in artist_boosters or splits['base'] in artist_boosters):
                boost_params.append("artist")
                boosts['artist'] = 2.0
            if(token in writer_boosters or splits['affix'] in writer_boosters or splits['base'] in writer_boosters):
                boost_params.append("writer")
                boosts['writer'] = 2.0
            if(token in music_boosters or splits['affix'] in music_boosters or splits['base'] in music_boosters):
                boost_params.append("music")
                boosts['music'] = 2.0
            if(token in genre_boosters or splits['affix'] in genre_boosters or splits['base'] in genre_boosters):
                boost_params.append("genre")
                boosts['genre'] = 2.0
            #append music as well.
        return set(boost_params),boosts
            

    @classmethod
    def process(self,query):
        tokens = tokenizer.tokenize(query)
        boosts_params,boosts = predictQType(tokens)
        if len(boosts_params) !=0:
            if("rate" in boosts_params):
                sortByRate = True
            else:
                sortByRate = False
            res = es.search(index='hela-songs',body = self.mmatch_boost_query(tokens,boosts,sortByRate))
        else: 
            res = es.search(index='hela-songs',body = self.mmatch_with_agg(query))
        return res

    def mmatch_with_agg(query):
        # aggregate by terms in genre
        body = {
            "query":{
                "multi_match": {
                    "query": query
                    "operator":"or"
                    "fields":["title_si","artist","music","writer","genre","lyrics"]
                }
            },
            "aggs": {
                "genre_agg": {
                    "terms": {
                        "field":"genre",
                        "size": 10
                    }
                }
            }
        }
        return body
    
    def mmatch_boost_query(tokens,boosts,sortByRate):
        #boost query
        body = {
            "query": {
                "bool":{
                    "should": {
                        "terms":{
                            "title_si":tokens,
                            "boost":boosts['title_si']
                        },
                        "terms":{
                            "artist":tokens,
                            "boosts":boosts['artist']
                        },
                        "terms":{
                            "writer":tokens,
                            "boosts":boosts['writer']
                        },
                        "terms":{
                            "music":tokens,
                            "boosts":boosts['music']
                        },
                        "terms":{
                            "genre":tokens,
                            "boosts":boosts['genre']
                        },
                        "terms":{
                            "lyrics":tokens,
                            "boosts":boosts['lyrics']
                        }

                    }
                }
            },
            "aggs":{
                "genre_agg": {
                    "terms": {
                        "field":"genre",
                        "size": 10
                    }
                }
            }
        }