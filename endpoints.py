"""
API MAPPING for Payoneer

"""
# TODO: make default settings for a mapping item to remove duplicates

mapping_table = {
    'list_preauth_transactions': {
        'path': '/MainPage/Transactions.aspx/GetPreauthTranscationsDataJSON',
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
    },
    # 'login': {
    #     'path': '/Login/Login.aspx',
    #     'method': 'GET',
    #     'status': 200,
    # },
}
