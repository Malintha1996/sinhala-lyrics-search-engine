import json
from googletrans import Translator
import re
import os

separator = ','
translator=Translator()

with open('lyrics.json' , encoding='utf-8') as f:
  object_list = json.load(f)

formatted_list= []

def format_multiple(multiple):
  multiple = multiple.strip().split(separator)
  translated = []
  for one in multiple:
    translated.append(translator.translate(one,dest="si").text)
  if(len(translated)!=1):
   return separator.join(translated)
  else: 
   return translated[0]

def gen_title_si(title_mix,title_sin):
  if(title_sin == None):
    return translator.translate (re.split(', |_|-|!|', song['title_mix'])[1],dest='si').text
  else:
    return title_sin

def gen_title_sien(title_mix):
  if(title_mix == None):
    return None
  else:
    return song['title_mix'].strip().split('|')[0]


def format_song(song,id):
  obj = {
    "id": id,
    "title_sien" :  gen_title_sien(song['title_mix']),
    "title_si" : gen_title_si(song['title_mix'],song['title_sin']),
    "artist" :  format_multiple(song['artist']),
    "genre" : format_multiple(song['genre']),
    "writer" : format_multiple(song['writer']),
    "music" : format_multiple(song['music']),
    "rating" : int(song['rating'].replace(",","")),
    "lyrics" : song['song'].strip()
  }
  return obj

count = 1
for song in object_list:
    obj = format_song(song,count) 
    print(obj)
    formatted_list.append(obj)
    count +=1

with open('lyrics-processed.json' ,'w', encoding='utf-8') as outf:
  json.dump(formatted_list,outf,indent=4,ensure_ascii=False)

