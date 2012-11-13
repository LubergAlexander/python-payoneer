"""
API MAPPING for Payoneer

"""
payload = {
        'currPage': 1,
        'searchString': '',
        'searchOption': '',
        'searchParamFormat': '',
        'searchParam': '',
        'sortParam': '',
        'sortDirection': '',
        'opaque': '',
        'startDate': '01/01/1900',
        'endDate': '01/01/2300',
        'PayoneerInternalId': ''
}
# TODO: make default settings for a mapping item to remove duplicates
mapping_table = {
    # TODO: for some reasons it does not returns preauth transactions until we request the page
    'pre_list_preauth_transactions': {
            'path': '/MainPage/Transactions.aspx',
            'method': 'GET',
            'status': 200,
    },
    'list_preauth_transactions': {
        'prerequisite': True,
        'path': '/MainPage/Transactions.aspx/GetPreauthTranscationsDataJSON',
        'valid_params': {
            'startDate': '',
            'endDate': '',
        },
        'method': 'POST',
        'status': 200,
    },
    'list_transactions': {
        'path': '/MainPage/Transactions.aspx/GetTranscationsDataJSON',
        'method': 'POST',
        'status': 200,
    },
    'list_loads': {
        'path': '/MainPage/LoadList.aspx/GetLoadListDataJSON',
        'method': 'POST',
        'status': 200,
    }
    # 'login': {
    #     'path': '/Login/Login.aspx',
    #     'method': 'GET',
    #     'status': 200,
    # },
}
