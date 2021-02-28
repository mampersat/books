from googleapiclient.discovery import build
import time
service = build('books', 'v1')
sheets_service = build('sheets', 'v4')

request = sheets_service.spreadsheets().get(spreadsheetId='15viB2N19RnIV0QMV2Pwb-0TV7f5luu0c81PHUuaHB7k')
response = request.execute()
sheet = response['sheets'][0]

file = open('book_list', 'r')

lines = file.readlines()

def get_volume(name):
    """gets single volume info from books api

    Args:
        name: name from directory name

    Returns:
        title(str) and rating(str)
    """
    request = service.volumes().list(q= name)
    response = request.execute()

    title = 'error'
    rating = 0

    try:
        title = response['items'][0]['volumeInfo']['title']
        rating = response['items'][0]['volumeInfo']['averageRating']
    except:
        pass

    return title, rating

values = []
line_number = 1

for line in lines:
    line_number += 1

    # 2020-02-28 4:10pm - processed 599, hit req/day limit
    if line_number < 599:
        print(f'skipping {line_number}')
        continue

    stripped = line.strip()
    name_only = stripped.split('.')[0]
    title, rating = get_volume(name_only)
    print(name_only, title, rating)
    
    values.append([stripped, title, rating])

    range = f'A{line_number}'

    if not (line_number % 10):
        body = {'values': values}
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId = '15viB2N19RnIV0QMV2Pwb-0TV7f5luu0c81PHUuaHB7k', 
            body=body, range= range, valueInputOption='RAW').execute()
        values = []
    
    # avoid quotas
    time.sleep(5)

service.close()
sheets_service.close()