a helper prompt to play magic w only numbered cards

decks are in decks/

2018 World Champion Deck List:
https://decks.tcgplayer.com/magic/deck/search?location=2018-world-championships

COMMANDS

all : list all ~20k cards
mapped : print a list of all mapped ids
list : list mapped ids and all mapped/loaded cards
list transforms : lists all transforms that have been recorded
list decks : list all saved decks
list saved : list all saved mappings 
clear : clear all mapped cards
save {mapname} : save mappings under mapname
loadmap {mapname} : load mappings from saved file {mapname}
transform {cardname} : display card data of transformed card {cardname}
> {cardname} : display card data of transformed card {cardname}
{card1} > {card2} : save transform of {card1} to {card2}
load {deckname} : load cards in deck file {deckname} to mappings list
stats {deckname} : show stats for {deckname}
test {deckname} : draws 7 cards random cards from deck {deckname}
colors : list all color symbols and their meanings
full {cardname} : dump all raw card data for card {cardname}
{cardID} : show card data for card corresponding to {cardID}
{cardname} : show card data for card {cardname}
exit : exit prompt

