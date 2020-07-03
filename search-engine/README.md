# Search Engine for Sinhala Song Lyrics

### contents
- [core -  Query processor and UI](#core)
- [elasticsearch - Elastic search ingestion, indexing, mapping logics](#es)
- [scrape - Web scraping logic](#scrape)

<a name="core"></a>
## Core - Query Processor and UI
The  core consists of the ```queryprocessor``` and ```ui```.
The queryprocessor has the rule based processing logic to support complex user queries such as below.

- ```අමරදේවයන්ගේ හොදම ගීත```
- ```ජනප්‍රියම ගීත```
- ```රෝහන බැද්දගේ රචනා කල ගීත```

To support these complex queries the query processor uses text classification techniques. A language processing tool called [sinling](https://github.com/ysenarath/sinling) is used to tokenize the query. Moreover techniques such as word splitting is used to identify phrases such as ```යන්ගේ,ගේ ``` inorder to boosts certain fields.

Types of elastcic search queries used
- multi_match with boosting and sorting
- match_all with sorting
- range_queries

The system is equipped with a simple UI. Showing search results along with few aggregations.
![Image of Yaktocat](/search-engine/resources/basic.png)

![Image of Yaktocat](/search-engine/resources/basic-2.png)

![Image of Yaktocat](/search-engine/resources/basic-3.png)

<a name="es"></a>
## Elastcisearch - Elastic search ingestion, indexing, mapping logics

Following is the optimized idexing configuration for creating the index in elastic search.

```json
"settings": {
        "index": {
              "number_of_shards": 1,
              "number_of_replicas": 1
        },
        "analysis": {
          "analyzer": {
            "sinhala-analyzer-1": {
                "type": "custom",
                "tokenizer": "icu_tokenizer",
                "char_filter": ["punctuation_char_filter"],
                "filter": ["stop_word_filter","edge_n_gram_filter"]      
            },
            "sinhala-analyzer-2": {
                "type": "custom",
                "tokenizer": "icu_tokenizer",
                "char_filter":["punctuation_char_filter"],
                "filter": ["stop_word_filter"]  
            },
            "english-analyzer": {
                "type": "custom",
                "tokenizer": "classic",
                "char_filter":["punctuation_char_filter"],
                "filter": ["edge_n_gram_filter"]
            },
            "sinhala-search-analyzer" : {
                "type": "custom",
                "tokenizer": "standard",
                "char_filter":["punctuation_char_filter"]
            },
            "english-search-analyzer" : {
                "type": "custom",
                "tokenizer": "classic",
                "char_filter":["punctuation_char_filter"]
            }
          },
          "char_filter": {
             "punctuation_char_filter":{
                "type":"mapping",
                "mappings":[".=>","|=>","-=>","_=>","'=>","/=>",",=>"]
             }
          },
          "filter": {
                "edge_n_gram_filter": {
                     "type" : "edge_ngram",
                     "min_gram":"2",
                     "max_gram":"20",
                     "side":"front"
                },
                "stop_word_filter": {
                     "type":"stop",
                     "stopwords":["සහ","හා", "වැනි", "සේ", "‌මෙන්", "සමග","ත්","ගීත","සින්දු","ගෙ","ගේ","ගී"]
                }
          }
        }
       }
```
- ICU tokenizer - A tokenizer for Asian languages
- Punctuation char filter - To filter out punctuation symbols and   other unwanted characters
- Stop word filter - A list of stop words was specified to be ignored in the indexing mechanism
- Edge N-gram filter - To create indices for word grams.

Following is the mapping of attributes of records into fields in elastcisearch.

```json
"mappings": {
            "properties": {
              "id": {
                   "type": "integer"
              },
              "titile_sien": {
                   "type": "text",
                   "analyzer":"english-analyzer",
                   "search_analyzer": "english-search-analyzer"
              },
              "title_si": {
                   "type": "text",  
                   "analyzer": "sinhala-analyzer-1",
                   "search_analyzer":"sinhala-search-analyzer"
              },
              "artist": {
                   "type": "text",
                   "analyzer":"sinhala-analyzer-1",
                   "search_analyzer": "sinhala-search-analyzer",
                   "fields": {
                        "keyword":{
                           "type":"keyword"
                        }
                    }
              },
              "genre": {
                   "type": "text",
                   "analyzer": "sinhala-analyzer-1",
                   "search_analyzer": "sinhala-search-analyzer",
                   "fields": {
                         "keyword":{
                              "type":"keyword"
                         }
                   }
              },
              "writer": {
                   "type": "text",
                   "analyzer": "sinhala-analyzer-1",
                   "search_analyzer": "sinhala-search-analyzer",
                   "fields": {
                     "keyword":{
                        "type":"keyword"
                     }
                   }
              },
              "music": {
                   "type": "text",
                   "analyzer": "sinhala-analyzer-1",
                   "search_analyzer": "sinhala-search-analyzer",
                   "fields": {
                     "keyword":{
                        "type":"keyword"
                     }
                   }
              },
              "rating": {
                   "type": "integer"
              },
              "lyrics": {
                   "type":"text",
                   "analyzer":"sinhala-analyzer-2",
                   "search_analyzer": "sinhala-search-analyzer"
              }
          }
        } 
```

<a name="scrape"></a>
## Scrape - Web scraping logic

Python scrapy was used to web scrape web sites with sinhal song lyrics for educational purposes.