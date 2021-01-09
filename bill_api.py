import requests
from requests.exceptions import HTTPError

api_key = 'Ebqy46zKgPyDOZTjgMkkETTPECqfO7fpKC4jwlOn'
bill_type_mapper = {'J': 'jres', 'C': 'conres', 'R': 'res' }

# e.g.
# H.R.1234 => hr1234
# S. 5568  =>  s5568
# H.Res.41 => hres41
# S.Res.66 => sres66
# H.J.Res.1=> hjres1
# S.ConRes1=> sconres1
def parse_bill(bill_string):
    chamber, bill_type, bill_num = bill_string[1:-1].split(',')
    if bill_type == '':
        if chamber == 'H':
            return 'hr', bill_num
        elif chamber == 'S':
            return 's', bill_num
        else:
            raise ValueError('Invalid bill chamber')

    return chamber.lower() + bill_type_mapper[bill_type], bill_num

def request_bill_info(bill_type, bill_number, congress_num):
    bill = bill_type + str(bill_number)
    url = 'https://api.propublica.org/congress/v1/{}/bills/{}.json'.format(congress_num, bill)

    try:
        response = requests.get(url, headers={'X-API-Key': api_key})
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code

def parse_response(json_obj):
    bill_info = json_obj['results'][0]
    bill_num = bill_info['number']
    title = bill_info['title']
    short_title = bill_info['short_title']

    return bill_num, title, short_title

def get_bill_info(bill_string, congress_num):
    bill_type, bill_num = parse_bill(bill_string)
    request_response = request_bill_info(bill_type, bill_num, congress_num)
    if type(request_response) != int:
        return parse_response(request_response)
    else:
        return (request_response, request_response, request_response)

def short_test():
    # H.Con.Res.8, 111th congress
    print(get_bill_info('(H,C,8)', 106))
    print(get_bill_info('(S,J,11)', 111))
    print(get_bill_info('(S,R,28)', 107))
    print(get_bill_info('(H,,7610)', 116))
    print(get_bill_info('(S,,347)', 108))

short_test()
