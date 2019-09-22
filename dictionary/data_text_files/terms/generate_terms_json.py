import argparse
import io
import json
import os
import re
import sys

import unidecode

pk = 1


def slugify(text):
    text = unidecode.unidecode(text).lower()
    slug = re.sub(r'[\W_]+', '-', text)
    if slug.startswith('-'):
        slug = slug[1:]
    if slug.endswith('-'):
        slug = slug[:-1]
    return slug


def is_valid_txt_file(input_file):
    return os.path.isfile(input_file) and os.path.splitext(input_file)[-1].lower() == '.txt'


def is_valid_path(output_path):
    return os.path.isdir(output_path)


def yes_or_no(question):
    prompt = question + " (y/n): "
    answer = input(prompt).lower().strip()
    print("")
    while not (answer == "y" or answer == "yes" or
               answer == "n" or answer == "no"):
        print("Input yes or no")
        answer = input(prompt).lower().strip()
        print("")

    if answer[0] == "y":
        return True
    else:
        return False


def generate_json(input_file, output_path):
    if not is_valid_txt_file(input_file):
        print(f'Skipping input file ({input_file}) as it is not a txt file')
        return

    global pk

    if 'american_football' in input_file:
        sport_name = 'American Football'
    elif 'basketball' in input_file:
        sport_name = 'Basketball'
    elif 'table_tennis' in input_file:
        sport_name = 'Table Tennis'
    elif 'tennis' in input_file:
        sport_name = 'Tennis'
    elif 'football' in input_file:
        sport_name = 'Football'
    elif 'golf' in input_file:
        sport_name = 'Golf'
    elif 'cricket' in input_file:
        sport_name = 'Cricket'
    elif 'boxing' in input_file:
        sport_name = 'Boxing'
    elif 'rugby' in input_file:
        sport_name = 'Rugby'
    elif 'motorsports' in input_file:
        sport_name = 'Motorsports'
    elif 'combatsport' in input_file:
        sport_name = 'Combat Sports'
        emoji = '🤼‍♂️'
    elif 'baseball' in input_file:
        sport_name = 'Baseball'
    elif 'hockey' in input_file:
        sport_name = 'Hockey'
    elif 'bowling' in input_file:
        sport_name = 'Bowling'
        emoji = '🎳'
    elif 'volleyball' in input_file:
        sport_name = 'Volleyball'
        emoji = '🏐'
    elif 'badminton' in input_file:
        sport_name = 'Badminton'
        emoji = '🏸'
    elif 'cycling' in input_file:
        sport_name = 'Cycling'
        emoji = '🚴‍♂️'
    elif 'billiards' in input_file:
        sport_name = 'Billiards'
        emoji = '🎱'
    elif 'chess' in input_file:
        sport_name = 'Chess'
        emoji = '♟️'
    elif 'fishing' in input_file:
        sport_name = 'Fishing'
        emoji = '🎣'
    elif 'skateboarding' in input_file:
        sport_name = 'Skateboarding'
        emoji = '🛹'
    elif 'ultimate_frisbee' in input_file:
        sport_name = 'Ultimate Frisbee'
        emoji = '🥏'
    elif 'archery' in input_file:
        sport_name = 'Ice skating'
        emoji = '⛸'
    else:
        print(f'Skipping input file ({input_file}) as the file name does provide a match with the known list of sports '
              f'which would break the relation field in the term model to a sport row in the db as it requires a '
              f'valid natural key')
        return

    try:
        f = open(input_file, encoding="utf-8")
    except FileNotFoundError as err:
        print(str(err))

    data = []

    date = '2019-09-01T00:00:00.000Z'

    line = f.readline()
    while line:
        unaccented_string = unidecode.unidecode(line[:-1]) if line.endswith('\n') else unidecode.unidecode(line)
        term = {
            'model': 'dictionary.term',
            'pk': pk,
            'fields': {
                'text': unaccented_string,
                'slug': slugify(unaccented_string),
                'created': date,
                'last_updated': date,
                'approvedFl': True,
                'sport': (sport_name,)
            }
        }
        data.append(term)
        pk = pk + 1
        line = f.readline()

    f.close()

    json_file = os.path.splitext(input_file)[-2] + '.json'
    json_file_path = output_path + json_file
    with io.open(json_file_path, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def main(args):
    output_path = args.output_path
    if not is_valid_path(args.output_path):
        use_current_dir = yes_or_no(
            f'Output path ({output_path}) is not a valid path. Enter y to use the current directory or n '
            f'to quit')

        if not use_current_dir:
            sys.exit()
        else:
            output_path = './'

    # loop over the input the files and attempt to generate the fixture file
    for input_file in args.input_files:
        generate_json(input_file, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate django fixture(s) in json given a list of input txt files')

    # Required positional argument
    parser.add_argument("input_files", nargs='+',
                        help="the input txt files to convert to json fixtures for the term model")

    # Optional argument flag which defaults to the current directory
    parser.add_argument("-o", "--output", default='./', dest='output_path',
                        help='the path in which to output the txt file(s)')

    args = parser.parse_args()
    main(args)
