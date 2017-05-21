import socket
import urllib
import json
import sys

RANKLIST_BASE_URL = 'https://www.codechef.com/api/rankings/'
RANKLIST_PARAMS = {'sortBy':'rank', 'order':'asc', 'page':'1', 'itemsPerPage':'10'}

HOST, PORT = '', 8888

def get_request_info(request):
    return request.splitlines()[0].split()[1].split('/')

def get_contest_code(request_info):
    if len(request_info) > 1:
        institution_name = request_info[1]
    else:
        institution_name = ''
    return institution_name

def get_institution_name(request_info):
    if len(request_info) > 2:
        institution_name = urllib.unquote(request_info[2]).decode('UTF-8')
    else:
        institution_name = 'National Institute of Technology, Durgapur'
    return institution_name

def get_request_url(contest_code, institution_name):
    ranklist_base_url = RANKLIST_BASE_URL + contest_code
    ranklist_params = RANKLIST_PARAMS
    ranklist_params['filterBy'] = 'Institution='+institution_name
    ranklist_url = '%s?%s' % (ranklist_base_url, urllib.urlencode(ranklist_params))
    return ranklist_url


def get_ranklist(contest_code, institution_name):
    if contest_code == 'favicon.ico':
        result = ''
    elif contest_code == '':
        result = 'Please enter a contest code in the url'
    else:
        ranklist_url = get_request_url(contest_code, institution_name)
        print ranklist_url
        response = urllib.urlopen(ranklist_url).read()
        response_json = json.loads(response)
        ranklist = response_json['list']
        result = '%s is over and here are the top 10 from our college.\n' % (contest_code)
        i = 0
        if not len(ranklist):
            result = "No ranklist found for %s in %s" % (institution_name, contest_code)
        for user in ranklist:
            i += 1
            result += '\n%s. %s (%s)' % (i, user['name'].title(), user['rank'])
    return result



listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print 'Open localhost:8888/<contest_code>/<college_name> where college_name is an optional field (Default: National Institute of Technology, Durgapur).' 
while True:
    try:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        request_info = get_request_info(request)
        contest_code = get_contest_code(request_info)
        institution_name = get_institution_name(request_info)
        result = get_ranklist(contest_code, institution_name)
        http_response = "HTTP/1.1 200 OK\n\n%s" % (result)
    except Exception as e:
        http_response = "HTTP/1.1 500 Internal Server Error\n\n%s" % (e)
    finally:
        client_connection.sendall(http_response)
        client_connection.close()
