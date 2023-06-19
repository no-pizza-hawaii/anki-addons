#!/bin/python3

from typing import Dict, List
import requests as re
from bs4 import BeautifulSoup, Tag


def fetch(verb: str) -> Dict[str, List[str]]:
    url = 'https://www.coniugazione.it/verbo/{}.php'.format(verb)
    dic = dict()

    # Get hmtl from url
    response: re.Response = re.get(url)
    if not response.ok:
        raise RuntimeError(f'Verb \'{verb}\' not found.')
    soup = BeautifulSoup(response.text, features='lxml')  # parse html with bs4
    soup = soup.find('div', {'id': 'contenu'})  # find relevant content node

    modus = ''
    for tag in soup.contents:
        # Skip all non Tag elements and invalid tags
        if not isinstance(tag, Tag) or 'class' not in tag.attrs:
            continue

        # If mode tag is encountered, set tense mode / mood to its content
        elif 'mode' in tag['class']:
            modus = str(tag.string)

        # If tense tag is encountered, parse contents and add entry
        elif 'tempstab' in tag['class']:
            # Concat mode and tense
            header = modus + ' ' + str(tag.find('h3', {'class': 'tempsheader'}).string)
            contents = tag.find('div', {'class': 'tempscorps'}).contents  # Get list of html elements
            contents = ''.join([str(x) for x in contents]).split('<br/>')  # Concat all elements and split by line break
            contents = [x for x in contents if x.strip() != '']  # only keep non empty lines
            dic[header] = contents

    # Get translation to german
    tag = soup.find('img', {'src': '/img/l/de.png'})
    if not tag or not tag.next_sibling:
        dic['Traduzione'] = ["not available"]
    else:
        dic['Traduzione'] = [str(tag.next_sibling).strip()]

    return dic


def main():
    import sys
    if len(sys.argv) <= 1:
        print(f'Usage: {sys.argv[0]} <verb>')
        return

    try:
        voc = fetch(sys.argv[1])
        for k in voc:
            print(k)
            for v in voc[k]:
                print('', v.replace('<b>', '').replace('</b>', ''))
            print('')

        print(voc.keys())

    except RuntimeError as ex:
        print('Error:', ex)


if __name__ == '__main__':
    main()
