from elasticsearch import Elasticsearch
from sinling import SinhalaTokenizer
from sinling import word_splitter
es  = Elasticsearch()
tokenizer = SinhalaTokenizer()
artist_boosters = ["ගේ","ගෙ","කියන","ගායනා","කිව්ව","ගැයූ","ගයපු"]
writer_boosters = ["රචනා","ලිව්ව","ලියන","ලියපු","රචිත"]
music_boosters = ["වාදනය","සංගීතය","නාද"]
genre_boosters = ["පොප්","නව","පැරණි","ක්ලැසික්"]
rating_boosters = ["හොදම","ප්‍රමුඛතම","ප්‍රධාන","ජනප්‍රිය","ගෝල්ඩන්","චිත්‍රපට","ජනප්‍රියම","ප්‍රධානතම","සුපිරි","සුපිරිතම"]
boosts_default = {"title_si":1,"artist":1,"writer":1,"music":1,"genre":1,"lyrics":1}

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
        boosts = {"title_si":1,"artist":1,"writer":1,"music":1,"genre":1.0,"lyrics":1}
        additional_tokens =[]
        print(tokens)
        for token in tokens:
            #split the tokens to identify affixes
            splits = word_splitter.split(token)
            additional_tokens.append(splits['base'])
            #add base to query depending on the threshold
            if(token in rating_boosters or splits['affix'] in rating_boosters or splits['base'] in rating_boosters):
                boost_params.append("rate")
            if(token in artist_boosters or splits['affix'] in artist_boosters or splits['base'] in artist_boosters):
                boost_params.append("artist")
                boosts['artist'] = 2
            if(token in writer_boosters or splits['affix'] in writer_boosters or splits['base'] in writer_boosters):
                boost_params.append("writer")
                boosts['writer'] = 2
            if(token in music_boosters or splits['affix'] in music_boosters or splits['base'] in music_boosters):
                boost_params.append("music")
                boosts['music'] = 2
            if(token in genre_boosters or splits['affix'] in genre_boosters or splits['base'] in genre_boosters):
                boost_params.append("genre")
                boosts['genre'] = 2
            #append music as well.
        query_mod = " ".join(tokens+additional_tokens)
        return set(boost_params),boosts,query_mod
            

    @classmethod
    def process(self,query):
        tokens = tokenizer.tokenize(query)
        boosts_params,boosts,query_mod= self.predictQType(tokens)
        if("rate" in boosts_params and len(boosts_params)>1):
            sortByRate = True
            res = es.search(index='hela-songs',body = self.mmatch_with_agg(query_mod,boosts,sortByRate))
        elif("rate" in boosts_params and len(boosts_params)==1):
            sortByRate = True
            if(len(tokens) == 1):
                res = es.search(index='hela-songs',body = self.allmatch_best_with_aggs(sortByRate))
            else:
                res = es.search(index='hela-songs',body = self.mmatch_with_agg(query_mod,boosts,sortByRate))
        else:
            sortByRate = False
            res = es.search(index='hela-songs',body = self.mmatch_with_agg(query_mod,boosts,sortByRate))
        return res

    def mmatch_with_agg(query,boosts,sortByRate):
        # aggregate by terms in genre
        body = {
            "query":{
                "multi_match": {
                    "query": query,
                    "operator":"or",
                    "fields":[
                        "title_si^"+str(boosts["title_si"]),
                        "artist^"+str(boosts['artist']),
                        "music^"+str(boosts["music"]),
                        "writer^"+str(boosts["writer"]),
                        "genre^"+str(boosts["genre"]),
                        "lyrics^"+str(boosts["lyrics"])]
                } 
        }
        }
        if(sortByRate):
            body["sort"] = [{"rating" : {"order" : "desc"}}]
            
        body["aggs"] =  {
                "genre_agg":{
                    "terms": {
                        "field":"genre.keyword",
                        "size":10
                    }
                }
        }
        return body
    
    def allmatch_best_with_aggs(sortByRate):
        body = {
            "query":{
                "match_all": {} 
            }
        }
        if(sortByRate):
            body["sort"]=[{"rating" : {"order" : "desc"}}]
        body["aggs"] =  {
                "artist_agg": {
                    "terms": {
                        "field":"artist.keyword",
                        "size":20
                    }
                },
                "genre_agg":{
                    "terms": {
                        "field":"genre.keyword",
                        "size":10
                    }
                }
            }
        return body
        
        