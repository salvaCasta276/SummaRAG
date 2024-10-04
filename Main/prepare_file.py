import os
import json

for title in os.listdir('summaries'):

    with open(f'summaries/{title}', 'r') as summ:
        lines = summ.readlines()
    with open(f'summaries/{title}', 'w') as summ:
        summ.writelines(lines[6:])

    for json_name in os.listdir('output'):
        with open(f'output/{json_name}', 'r') as json_file:
            data = json.load(json_file)
        if title[:-4] == data['title']:
            json_title = data['title']
            with open(f'docs/{json_title}.txt', 'w') as txt_file:
                txt_file.write(data['content'])