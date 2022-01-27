# import csv
import os
import json
import random
import time

from PIL import Image
import requests
from io import BytesIO

from urllib.request import urlopen

import argparse
import argcomplete

import xlsxwriter

from bs4 import BeautifulSoup

# -is_creature
# -is_commander
# -legal_commander (-is_legendary?)
# -is_
# -start_year
# -usd_max


def url2str(url):
    page = urlopen(url)
    html_bytes = page.read()
    return html_bytes.decode("utf-8")


def get_card_pool(search_str):  # PULL DATA FROM SEARCH LINK
    printing = True

    html_string = url2str(search_str)
    cards = []
    has_more = True
    if printing: print("get_card_pool: loop opened")
    while has_more:
        jver = json.loads(html_string)
        cards += jver["data"]
        if printing: print("get_card_pool:", len(cards), "/", jver["total_cards"])
        if jver["has_more"]:
            if printing: print("get_card_pool: has more...")
            html_string = url2str(jver["next_page"])
            # cards += json.loads(url2str(jver["next_page"]))["data"]
        else:
            has_more = False
            if printing: print("get_card_pool: loop closed")

    return cards


def extract_toplist(toplist_path, toplist_max):  # EXTRACT DATA FROM FILES
    toplist_string = open(toplist_path, "r")
    toplist_soup = BeautifulSoup(toplist_string, 'html.parser')
    toplist_soup_text = toplist_soup.get_text()
    toplist_soup_lines = toplist_soup_text.split("\n")
    toplist = []
    i = 4
    while i < len(toplist_soup_lines):
        toplist.append(toplist_soup_lines[i])
        i += 6
    toplist = toplist[0:toplist_max]
    return toplist


def get_toplist(toplist_path, toplist_max):  # EXTRACT DATA FROM FILES
    # printing = True

    with open(toplist_path, encoding='utf8') as tf:
        toplist_str = tf.read()
    toplist = toplist_str.split('\n')
    if toplist[-1] == '':
        toplist.pop()
    toplist = toplist[0:toplist_max]

    return toplist


# with open(result_path, encoding='utf8') as jf:
    #     cards = json.load(jf)
    # for c_card in cards:
    #     print(c_card["name"])
    # print(len(cards))

    # Kenna 82
    # ? 42?
    # Oli 27
    # Nick 437
    # lil 2 368
    # pat 2 394204
    # peter reroll 275837856
    # me 1809
    # Nicholas2 564387934
    # Nicole 638919684
    # Olver 69696969
    # Sam 345796742


def filter_toplist_from_cards(cards, toplist):
    printing = True

    invalid_cnames = []
    valid_cards = []
    for c_card in cards:
        if c_card['name'] in toplist:
            invalid_cnames.append(c_card)
        else:
            valid_cards.append(c_card)
    if printing: print("filter_toplist_from_cards: total invalid cards:", len(invalid_cnames))

    return cards


def randomly_select_cards(valid_cards, random_seed, output_num):
    # printing = True

    random.seed(random_seed)
    rand_ind = []
    while len(rand_ind) < output_num:  # TODO predefine number of cmndrs to gen
        r = random.randint(0, len(valid_cards) - 1)
        if r not in rand_ind:
            rand_ind.append(r)

    chosen_cards = []
    for i in rand_ind:
        chosen_cards.append(valid_cards[i])

    return chosen_cards


def save_to_xlsx(chosen_cards, result_path, player_name, random_seed):
    workbook = xlsxwriter.Workbook(result_path)
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, time.strftime('%d/%m/%y %H:%M%p'))
    worksheet.write(0, 1, player_name)
    worksheet.write(0, 2, str(random_seed))
    for i, c_card in enumerate(chosen_cards):
        worksheet.write(0, i + 3, c_card['name'])
    workbook.close()

# def save_to_txt(chosen_cards, result_path, player_name, random_seed):
#     c_txt = with


def show_cards(chosen_cards, player_name):
    printing = False

    comb_im = Image.new('RGB', (1864, 880), (255, 255, 255))
    for i, c_card in enumerate(chosen_cards):
        if printing: print("show_cards:", c_card)
        if "card_faces" in c_card and c_card["layout"] != 'flip':
            normal_uri = c_card["card_faces"][0]['image_uris']['normal']
        else:
            normal_uri = c_card['image_uris']['normal']
        response = requests.get(normal_uri)
        c_im = Image.open(BytesIO(response.content))
        position = (100 + (i * 588), 100)
        comb_im.paste(c_im, position)

    comb_im.save(player_name + '.jpg')
    comb_im.show()


def main(options):
    cards = get_card_pool(options.search_str)

    toplist = extract_toplist(options.toplist_path, options.toplist_max)

    valid_cards = filter_toplist_from_cards(cards, toplist)

    chosen_cards = randomly_select_cards(valid_cards, options.random_seed, options.output_num)

    save_to_xlsx(chosen_cards, options.result_path, options.player_name, options.random_seed)

    show_cards(chosen_cards, options.player_name)


# input: player name, rand num, images/json or both
# output: card names, linked, time/date rolled, player name,

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ScuffleGen")
    parser.add_argument('-pn', '--player_name', default='test_player', type=str)
    parser.add_argument('-rs', '--random_seed', default=time.gmtime(), type=int)
    parser.add_argument('-on', '--output_num', default=3, type=int)
    parser.add_argument('-ss', '--search_str', default="https://api.scryfall.com/cards/search?q=t%3Acreature+is%3Acommander+f%3Acommander+year%3E%3D2000+%28usd%3C5%29", type=str)  # break to form from options
    parser.add_argument('-tm', '--toplist_max', default=30, type=int)
    parser.add_argument('-tp', '--toplist_path', default=os.path.join("resources", "toplist_raw.html"), type=str)
    parser.add_argument('-rp', '--result_path', default="results_collated.xlsx", type=str)

    argcomplete.autocomplete(parser)

    main(parser.parse_args())