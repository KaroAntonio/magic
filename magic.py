# a python interface for the magic game

import json
import csv
import os
from colors import *

DECK_DIR = 'decks/'
ALL_CARDS_FID = 'magic_all_cards.json'
CUSTOM_CARDS_FID = 'magic_custom_cards.json'
CARD_MAP_FID = 'magic_card_map.json'
CARD_MAP_SUFFIX = '.magiccardmap'

def load_json(fid,default={}):
  try:
    with open(fid) as f:
      data = json.load(f)
  except:
    data = default
  return data

def save_json(fid, data):
  with open(fid, 'w') as f:
    json.dump(data, f) 

def load_cards():
 cards = {}
 cards.update(load_json(ALL_CARDS_FID))
 cards.update(load_json(CUSTOM_CARDS_FID))
 return cards

def load_deck(fid):
  card_map = load_card_map()
  max_idx = 1 if not card_map else max(map(int,card_map.keys()))+1
  idx = max_idx
  try:
    f = open(DECK_DIR+fid)
  except:
    print('No Deck: {} '.format(fid))
    return
  for line in f:
    if line.strip() == 'SIDEBOARD':
      break
    if len(line.split()) > 0:
      n = line.split()[0]
      if n.isdigit():
        card_name = line[len(n)+1:].strip()
        for i in range(int(n)):
          card_map[idx] = card_name 
          idx += 1
  print('Loaded {} Cards'.format(idx-max_idx))
  f.close()
  save_json(CARD_MAP_FID,card_map)

def load_card_map():
  return load_json(CARD_MAP_FID)

def format_card(cards, cardname):
  return format_card_compact(cards, cardname)

def format_card_compact(cards, card_name):
  if card_name not in cards:
    print ('Card Not Present: {}'.format(card_name)) 
    return
  c = cards[card_name]
  card_str = u''
  card_str+=u'---------------------\n'
  card_str+=white(c['name'])
  card_str+=white(' ('+','.join(c['colorIdentity'])+')')
  card_str+=(' '+teal(c['manaCost'])) if 'manaCost' in c  else ''
  card_str+=u'\n'
  card_str+=','.join(c['types']) 
  card_str+=(' - '+','.join(c['subtypes'])) if ('subtypes' in c and c['subtypes']) else ''
  card_str+=' - ' + blue(c['power']+'/'+c['toughness']) if 'power' in c else ''
  card_str+=' - '+blue(c['loyalty']) if 'loyalty' in c else '' 
  card_str+=u'\n'
  card_str+=u'\n'
  card_str+=c['text'] if 'text' in c else ''
  card_str+=u'\n---------------------'
  return card_str

def format_card_list(cards, card_name):
  if card_name not in cards:
    print ('Card Not Present: {}'.format(card_name)) 
    return
  c = cards[card_name]

  keys_to_list = [
    'name',
    'colorIdentity',
    'manaCost',
    'power',
    'toughness',
    'loyalty',
    'types',
    'subtypes',
    'text'
  ]

  card_str = ''
  for k in keys_to_list:
    if k in c:
      v = c[k]
    else:
      v = None
    card_str+=u'{} : {}\n'.format(k,v)
  return card_str

def show_full_card_details(cards, card_name):
  if card_name not in cards:
    print ('Card Not Present: {}'.format(card_name)) 
    return
  
  c = cards[card_name]
  for k,v in c.items():
    print(u'{} : {}'.format(k,v))

def filter_cards(cards,filters):
  new_cards = {}
  for name,card in cards.items():
    hits = 0
    for attr, attr_val in filters.items():
      if attr in card:
        if type(card[attr]) is list:
          if attr_val in card[attr]:
            hits += 1
        elif attr_val == card[attr]:
          hits += 1
    if hits == len(filters): new_cards[name] = card
  return new_cards

def list_saved():
   for fid in os.listdir('.'):
     if CARD_MAP_SUFFIX in fid:
       print(fid.split('.')[0])

def save_map(save_fid):
  card_map = load_card_map()
  save_json( save_fid, card_map )

def magic_prompt():
  val = '' 
  cards = load_cards()

  attrs = ['types','subtypes','colorIdentity']
  while val != 'exit':
    val = raw_input('> ')
    try:
      evaluated = eval(val)
    except:
      evaluated = None

    if val == 'ALL':
      for name in cards: 
        print(name)
      print('')
    elif val == 'MAPPED':
      card_map = load_card_map()
      sorted_ids = sorted([int(e) for e in card_map.keys()])
      print(','.join([str(e) for e in sorted_ids]))
    elif val == 'LIST':
      card_map = load_card_map()
      sorted_map = sorted([(int(i),c) for i,c in card_map.items()])
      for card_id, card_name in sorted_map:
        print('{} : {}'.format(card_id, card_name))
    elif val == 'LIST SAVED':
      list_saved()  
    elif val == 'CLEAR':
      confirmed = raw_input('Are you sure you want to clear all mappings? (y/n): ')
      if confirmed == 'y':
        card_map = {}
        save_json(CARD_MAP_FID,card_map)
    elif not val:
      continue
    elif val.split()[0] == 'SAVE':
      save_name = val[5:] 
      save_map(save_name+CARD_MAP_SUFFIX+'.json')
    elif val.split()[0] == 'LOAD':
      deck_name = val[5:] 
      load_deck(deck_name+'.deck')
    elif val.split()[0] == 'LOADMAP':
      load_name = val[8:] 
      card_map = load_json(load_name+CARD_MAP_SUFFIX+'.json')
      save_json(CARD_MAP_FID,card_map)
    elif val == 'COLORS':
      print('W - white')
      print('U - blue')
      print('B - black')
      print('G - green')
      print('R - red')
    elif evaluated and type(evaluated) is dict:
      # print only cards sattisfying this attr
      filtered_cards = filter_cards(cards, evaluated) 
      for name in filtered_cards: 
        print(name)
      print('Total: {}'.format(len(filtered_cards)))
      print('')
    elif val.split()[0] == 'FULL':
      name = val[4:].strip()
      show_full_card_details(cards, name)
    elif val.strip().isdigit():
      card_id = val.strip()
      card_map = load_card_map()
      if card_id not in card_map:
        print('Card ID Not Present: {}'.format(card_id))
      else:
        card_name = card_map[card_id]
        print(format_card(cards, card_name))
    elif val.split()[0].isdigit():
      # mapping is being entered
      card_map = load_card_map()
      card_id = val.split()[0]
      card_name = val.strip(card_id).strip()
      card_map[card_id] = card_name
      save_json(CARD_MAP_FID,card_map)
    elif val=='exit':
      return
    else:
      # assume input is a card name
      print(format_card(cards,val.strip()))

if __name__ == '__main__':
  magic_prompt()      
       

