# a python interface for the magic game

import json
import csv
import os
import random
from colors import *

DECK_DIR = 'decks/'
DECK_SUFFIX = '.deck'
ALL_CARDS_FID = 'magic_all_cards.json'
CUSTOM_CARDS_FID = 'magic_custom_cards.json'
CARD_MAP_FID = 'magic_card_map.json'
CARD_MAP_SUFFIX = '.magiccardmap'
DATA_FID = 'data.json'
PLAYER_DIR = 'players/'

lists = ['library','hand','board','graveyard','exile']

def clear_players():
  for r, d, f in os.walk(PLAYER_DIR):
    for fid in f:
      if '.json' in fid:
        os.remove(PLAYER_DIR+fid)

def prompt_for_player(player):
  while not player:
    val = raw_input('Set Player: ').strip()
    if os.path.isfile(PLAYER_DIR+val+'.json'):
      return val
    else:
      print('Player {} does not exist'.format(val))

def remove_card_from_player(player,card_id):
  def f(data):
    for list_name in lists:
      if card_id in data[list_name]:
        data[list_name].remove(card_id)
        return True
  return work_with('{}{}.json'.format(PLAYER_DIR,player),f)

def log_move(player,cmd):
  def f(data):
    data['history'].append(cmd)
  work_with('{}{}.json'.format(PLAYER_DIR,player),f)

def init_player(player_id,deck_vals):
  library = [str(e) for e in deck_vals]
  random.shuffle(library)
  player = {
    'id':player_id,
    'library':library[7:],
    'hand':library[:7],
    'board':[],
    'graveyard':[],
    'exile':[],
    'history':[],
  }
  save_json(PLAYER_DIR+player_id+'.json',player)

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

def work_with(fid, callback):
  data = load_json(fid)
  res = callback(data) 
  save_json(fid,data)
  return res

def transform(cardname):
  data = load_json(DATA_FID) 
  if cardname in data['transforms']:
    return data['transforms'][cardname]
  else:
    print('No Transform Exists for: {}'.format(cardname))
    return None

def save_transform(card_1,card_2):
  data = load_json(DATA_FID) 
  data['transforms'][card_1] = card_2
  data['transforms'][card_2] = card_1
  save_json(DATA_FID, data)

def load_cards():
 cards = {}
 cards.update(load_json(ALL_CARDS_FID))
 cards.update(load_json(CUSTOM_CARDS_FID))
 return cards

def load_deck_to_list(fid):
  card_map = load_card_map()
  max_idx = 1 if not card_map else max(map(int,card_map.keys()))+1
  idx = max_idx
  try:
    f = open(DECK_DIR+fid)
  except:
    print('No Deck: {} '.format(fid))
    return

  card_vals = []
  for line in f:
    if line.strip() == 'SIDEBOARD':
      break
    if len(line.split()) > 0:
      n = line.split()[0]
      if n.isdigit():
        card_name = line[len(n)+1:].strip()
        for i in range(int(n)):
          card_vals.append(idx)
          card_map[idx] = card_name 
          idx += 1
  init_player(fid.split('.')[0],card_vals)
  print('Loaded {} Cards'.format(idx-max_idx))
  f.close()
  save_json(CARD_MAP_FID,card_map)

def old_load_library(name,card_vals):
  def f(data):
    data['libraries'][name] = card_vals[:]
  work_with(DATA_FID,f)

def load_card_map():
  return load_json(CARD_MAP_FID)

def format_card(cards, cardname):
  if '//' in cardname:
    print(white(cardname))
    card_1 = cardname.split('//')[0].strip()
    card_2 = cardname.split('//')[1].strip()
    card_str = format_card_compact(cards,card_1)
    card_str += format_card_compact(cards,card_2)
  else:
    card_str = format_card_compact(cards,cardname)
  return card_str 

def format_card_compact(cards, cardname):
  if cardname not in cards:
    print ('Card Not Present: {}'.format(cardname)) 
    return
  c = cards[cardname]
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
        if type(card[attr]) in [list,str,unicode]:
          if attr_val in card[attr]:
            hits += 1
        elif attr_val == card[attr]:
          hits += 1

    if hits == len(filters): new_cards[name] = card
  return new_cards

def list_decks():
   for fid in os.listdir('./decks'):
     if DECK_SUFFIX in fid:
       print(fid.split('.')[0])
def list_saved():
   for fid in os.listdir('.'):
     if CARD_MAP_SUFFIX in fid:
       print(fid.split('.')[0])

def save_map(save_fid):
  card_map = load_card_map()
  save_json( save_fid, card_map )

def load_deck(deck_name):
  fid = deck_name+'.deck'
  try:
    f = open(DECK_DIR+fid)
  except:
    print('No Deck: {} '.format(fid))
    deck = None
    return deck
  deck = []
  for line in f:
    if line.strip() == 'SIDEBOARD':
      break
    if len(line.split()) > 0:
      n = line.split()[0]
      if n.isdigit():
        card_name = line[len(n)+1:].strip()
        for i in range(int(n)):
          deck.append(card_name)
  f.close()
  return deck

def getManaCost(cards, cardname):
  card = cards[cardname]
  colorID = '({})'.format(','.join(card['colorIdentity']))
  return colorID if 'manaCost' not in card else card['manaCost']

def getConvertedManaCost(cards, cardname):
  if '//' in cardname:
    card_1 = cardname.split('//')[0].strip()
    card_2 = cardname.split('//')[1].strip()
    cost_1 = cards[card_1]['convertedManaCost']
    cost_2 = cards[card_2]['convertedManaCost']
    return cost_1+cost_2
  else:
    return cards[cardname]['convertedManaCost']

def deck_stats(cards,deck_name):
  deck = load_deck(deck_name)
  if not deck: return 
  n = len(deck)
  freqs = [(name,deck.count(name)) for name in set(deck)]
  order = lambda c: getConvertedManaCost(cards,c[0])
  freqs.sort(key=order)
  for name,freq in freqs:
    nameID = name.split('//')[0].strip() if '//' in name else name
    card = cards[nameID]
    percent = int(freq/(n+0.0)*100)
    percent_f = (' ' if len(str(percent)) == 1 else '')+str(percent) 
    freq_f =  (' ' if len(str(freq)) == 1 else '')+str(freq) 
    colorID = '({})'.format(','.join(card['colorIdentity']))
    typeID = card['types'][0][0]
    mana = colorID if 'manaCost' not in card else card['manaCost']
    mana_f = (' '*(15-len(mana)))+mana
    print('{}% - {} - {} {} {}'.format(percent_f,freq_f,mana_f,typeID,name))
  freqs = {}
  mana_types = ['B','W','R','U','G']
  mana_freqs = {mt:0 for mt in mana_types}
  total_mana_cost = 0
  for name in deck:
    nameID = name.split('//')[0].strip() if '//' in name else name
    card = cards[nameID]
    cmc = card['convertedManaCost'] 
    total_mana_cost += int(cmc)
    if cmc not in freqs: 
      keys = ['L','C','S','I','A','E','P','Total']
      freqs[cmc] = {k:0 for k in keys}
    freqs[cmc]['Total'] += 1
    types = card['types']
    if 'Land' in types: freqs[cmc]['L'] += 1
    elif 'Creature' in types: freqs[cmc]['C'] += 1
    elif 'Sorcery' in types: freqs[cmc]['S'] += 1
    elif 'Instant' in types: freqs[cmc]['I'] += 1
    elif 'Artifact' in types: freqs[cmc]['A'] += 1
    elif 'Enchantment' in types: freqs[cmc]['E'] += 1
    elif 'Planeswalker' in types: freqs[cmc]['P'] += 1
    if 'manaCost' in card: 
      for mt in mana_types:
        mana_freqs[mt] += card['manaCost'].count(mt)
  
  cost_freqs = freqs.items()
  cost_freqs.sort(key=lambda e:e[0])
  print('Converted Mana Cost Frequencies:')
  print(' Cost | L | C | S | I | A | E | P | %')
  for cmc,freqs in cost_freqs:
    cmc_f = ' '*(4-len(str(int(cmc)))) + str(int(cmc)) 
    format_freq = lambda e:' '*(3-len(e))+e
    l=format_freq(str(freqs['L']) if freqs['L'] else ' ')
    c=format_freq(str(freqs['C']) if freqs['C'] else ' ')
    s=format_freq(str(freqs['S']) if freqs['S'] else ' ')
    i=format_freq(str(freqs['I']) if freqs['I'] else ' ')
    a=format_freq(str(freqs['A']) if freqs['A'] else ' ')
    e=format_freq(str(freqs['E']) if freqs['E'] else ' ')
    p=format_freq(str(freqs['P']) if freqs['P'] else ' ')
    prop_f = ' '+str(int(((freqs['Total']+.0) / n)*100)) + '%'
    cols = (' {}'*9)
    print(cols.format(cmc_f,l,c,s,i,a,e,p,prop_f))
  print('Mana Costs:')
  for mt,freq in mana_freqs.items():
    format_freq = lambda e:' '*(3-len(e))+e
    freq_f = format_freq(str(freq))
    percent_f = format_freq(str(int(float(freq)/total_mana_cost*100)))
    print('{} : {}  {}%'.format(mt,freq_f,percent_f))
  print('{} Cards'.format(len(deck)))

def test_hand(cards,deck_name):
  fid = deck_name+'.deck'
  try:
    f = open(DECK_DIR+fid)
  except:
    print('No Deck: {} '.format(fid))
    return
  test_deck = []
  for line in f:
    if line.strip() == 'SIDEBOARD':
      break
    if len(line.split()) > 0:
      n = line.split()[0]
      if n.isdigit():
        card_name = line[len(n)+1:].strip()
        for i in range(int(n)):
          test_deck.append(card_name)
  random.shuffle(test_deck)
  for i in range(7):
    card_name = test_deck.pop()
    print(format_card_one_line(cards, card_name))
  f.close()

def format_card_one_line(cards,card_name):
  if '//' in card_name:
    card_1 = card_name.split('//')[0].strip()
    card_2 = card_name.split('//')[1].strip()
    formatted_1 = format_card_one_line(cards, card_1)
    formatted_2 = format_card_one_line(cards, card_2)
    return formatted_1 + ' // ' + formatted_2
  else:
    if card_name not in cards:
      print('Card Does Not Exist: {}'.format(card_name))
      return 'DNE'
    card = cards[card_name]
    manaCost = getManaCost(cards, card_name)
    return '{} {}'.format(card['name'],manaCost)

def all_attrs(cards):
  attrs = []
  for c in cards.values():
    for attr in c:
      if attr not in attrs:
        attrs.append(attr)
  return attrs

def magic_prompt():
  val = '' 
  cards = load_cards()
  player = None

  attrs = all_attrs(cards) 

  while val != 'exit':
    val = raw_input('> ').strip()
    try:
      evaluated = eval(val)
    except:
      evaluated = None
    if not val:
      continue
    elif val == 'all':
      for name in cards: 
        print(name)
      print('')

    # PLAYER COMMANDS
    elif val.split()[0] == 'players':
      for r, d, f in os.walk(PLAYER_DIR):
        for fid in f:
          if '.json' in fid:
            print(fid.replace('.json',''))
    elif val.split()[0] == 'player':
      if len(val.split()) > 1:
        player_name = val.split()[1]
        if os.path.isfile(PLAYER_DIR+player_name+'.json'):
          player = player_name
          print(pink(player_name.upper()))
        else:
          print('Player {} does not exist'.format(player_name))
    elif val.split()[0] == 'put' and len(val.split()) >= 3:
      if not player: player = prompt_for_player(player)
      idx = 0
      if len(val.split()) == 4:
        idx_str = val.split()[3].strip()
        if idx_str.isdigit(): idx = int(idx_str)
        if idx_str.strip() == 'bottom': idx = 100000
      card_id = val.split()[1]
      list_name = val.split()[2]
      if card_id.isdigit() and list_name in lists:
        success = remove_card_from_player(player,card_id)
        if success:
          def f(data):
            data[list_name].insert(idx,card_id)
          print('Put card {} in {}'.format(card_id, list_name))
          work_with('{}{}.json'.format(PLAYER_DIR,player),f)
          log_move(player,val)
    elif val == 'draw':
      if not player: player = prompt_for_player(player)
      def f(data): 
        card_id = data['library'].pop(0)
        data['hand'].append(card_id)
        print('draw {}'.format(card_id))
      card_id = work_with('{}{}.json'.format(PLAYER_DIR,player),f)
      log_move(player,val)
    elif val.split()[0] == 'play' and len(val.split())==2:
      if not player: player = prompt_for_player(player)
      card_id = val.split()[1].strip()
      if card_id.isdigit():
        if not player: player = prompt_for_player(player)
        def f(data):
          if card_id in data['hand']:
            data['hand'].remove(card_id)
            data['board'].append(card_id)  
          else: 
            print('Card Not in Hand: {}'.format(card_id))
        work_with('{}{}.json'.format(PLAYER_DIR,player),f)
        log_move(player,val)
    elif val.split()[0] == 'shuffle':
      if not player: player = prompt_for_player(player)
      if len(val.split()) == 2 and val.split()[1] in lists:
        list_name = val.split()[1]
        def f(data):
          random.shuffle(data[list_name])
        work_with('{}{}.json'.format(PLAYER_DIR,player),f)
        print(list_name+' shuffled')
        log_move(player,val)
    elif val.split()[0] in lists:
      if not player: player = prompt_for_player(player)
      list_name = val.split()[0]
      n = None
      if len(val.split()) == 2:
        n = val.split()[1]
        if not n.isdigit(): n = None
        else: n = int(n)
      def f(data):
        print(pink(list_name.upper()))
        card_map = load_card_map()
        for card_id in data[list_name][:n]:
          print(card_id +u' : '+format_card_one_line(cards,card_map[card_id]))
      work_with('{}{}.json'.format(PLAYER_DIR,player),f)
      log_move(player,val)
    elif val == 'history':
      if not player: player = prompt_for_player(player)
      def f(data):
        for cmd in data['history']:
          print(cmd)
      work_with('{}{}.json'.format(PLAYER_DIR,player),f)
    # END PLAYER COMMANDS

    elif val == 'mapped':
      card_map = load_card_map()
      sorted_ids = sorted([int(e) for e in card_map.keys()])
      print(','.join([str(e) for e in sorted_ids]))
    elif val == 'attributes':
      for attr in attrs:
        print(attr)
    elif val.split()[0] == 'list' and len(val.split()) == 2 and val.split()[1] in attrs:
      attr = val.split()[1]
      attr_type_freqs = {}
      for c in cards.values():
        if attr in c:
          v = c[attr]
          if type(v) is list:
            for e in v:
              if e not in attr_type_freqs:
                attr_type_freqs[e] = 0
              attr_type_freqs[e] += 1
          else:
            if v not in attr_type_freqs:
              attr_type_freqs[v] = 0
            attr_type_freqs[v] += 1

      # Display
      attr_type_freqs_items = attr_type_freqs.items()
      attr_type_freqs_items.sort(key=lambda e:e[0])
      for attr_type, freq in attr_type_freqs_items:
        print(u'{} : {}'.format(attr_type, freq))
    elif val == 'list':
      card_map = load_card_map()
      sorted_map = sorted([(int(i),c) for i,c in card_map.items()])
      for card_id, card_name in sorted_map:
        formatted_card = format_card_one_line(cards, card_name)
        print(str(card_id) + ' : '+formatted_card)
    elif val == 'list transforms':
      data = load_json(DATA_FID) 
      for k,v in data['transforms'].items():
        print('{} > {}'.format(k,v))
    elif val == 'list decks':
      list_decks() 
    elif val == 'list saved':
      list_saved()  
    elif val == 'clear':
      confirmed = raw_input('Are you sure you want to clear all mappings? (y/n): ')
      if confirmed == 'y':
        card_map = {}
        data = load_json(DATA_FID) 
        data['libraries'] = {}
        data['hands'] = {}
        save_json(DATA_FID,data)
        save_json(CARD_MAP_FID,card_map)
        clear_players()
        player = None
    elif val.split()[0] == 'save':
      save_name = val[5:] 
      save_map(save_name+CARD_MAP_SUFFIX+'.json')
    elif val.split()[0] == 'transform':
      cardname = val[10:] 
      transformed_cardname = transform(cardname)
      print(format_card(cards, transformed_cardname))
    elif val[0] == '>':
      cardname = val[2:].strip()
      transformed_cardname = transform(cardname)
      print(format_card(cards, transformed_cardname))
    elif '>' in val:
      tokens = val.split('>')
      card_1 = tokens[0].strip()
      card_2 = tokens[1].strip()
      save_transform(card_1, card_2)
    elif val.split()[0] == 'load':
      deck_name = val[5:] 
      load_deck_to_list(deck_name+'.deck')
    elif val.split()[0] == 'stats':
      deck_name = val[6:] 
      deck_stats(cards, deck_name)
    elif val.split()[0] == 'loadmap':
      load_name = val[8:] 
      card_map = load_json(load_name+CARD_MAP_SUFFIX+'.json')
      save_json(CARD_MAP_FID,card_map)
    elif val == 'colors':
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
    elif val.split()[0] == 'test':
      deck_name = val[4:].strip()
      test_hand(cards, deck_name)
    elif val.split()[0] == 'full':
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
    elif val=='help':
      f = open('README.md')
      at_cmds = False
      for line in f:
        if line.strip() == 'COMMANDS':
          at_cmds = True
        if at_cmds:
          print(line.strip())
      f.close()
    elif val=='exit':
      return
    elif '//' in val:
     pass 
    else:
      # assume input is a card name
      cardname = val.strip()
      print(format_card(cards, cardname))
      
if __name__ == '__main__':
  magic_prompt()      
       

