#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from lxml.html import fromstring
__version__ = "0.0.4"


class Payoneer:
    """ Python Payoneer wrapper"""

    api_url = 'https://myaccount.payoneer.com'

    login_url = api_url + '/Login/Login.aspx'
    transactions_url = api_url + '/MainPage/Transactions.aspx'
    loads_url = api_url + '/MainPage/LoadList.aspx'
    transactions_json_url = api_url + '/MainPage/Transactions.aspx/GetTranscationsDataJSON'
    preauth_transactions_json_url = api_url + '/MainPage/Transactions.aspx/GetPreauthTranscationsDataJSON'
    loads_json_url = api_url + '/MainPage/LoadList.aspx/GetLoadListDataJSON'
    transaction_details_html_url = api_url + '/MainPage/TransactionDetailsTemplate.aspx'
    preauth_transaction_details_html_url = api_url + '/MainPage/TransactionDetailsPreAuthTemplate.aspx'
    load_details_html_url = api_url + '/MainPage/LoadListDetailsTemplate.aspx'

    default_payload = {
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
    }

    payoneer_internal_payload = {
        'PayoneerInternalId': ''
    }

    headers = {
        'Content-Type': 'application/json'
    }

    last_pre_request = None

    def _do_json_request(self, url, method="POST", payload=None):
        response = self.session.request(
                method=method,
                url=url,
                data=json.dumps(payload),
                headers=self.headers
            )
        return response.json

    def _do_html_request(self, url, method="GET", query_params=None):
        response = self.session.request(
                method=method,
                url=url,
                params=query_params,
                headers=self.headers
            )
        return response.content

    def __init__(self, username=None, password=None):
        """
        Instantiates an instance of Payoneer. Takes optional parameters for
        Authentication

        Parameters:
        username - Specific to your Payoneer account (typically email)
        password - Specific to your Payoneer account or your account's
        """

        self.session = requests.session()
        response = self.session.get(self.login_url)
        dom = fromstring(response.content)

        data = dict((x.name, x.value) for x in dom.cssselect('#form1 input'))
        data['__EVENTTARGET'] = 'btLogin'
        data['txtUserName'] = username
        data['txtPassword'] = password
        self.payoneer_internal_payload["PayoneerInternalId"] = data['payoneer-internal-id']

        # TODO: Check response for authentication errors
        response = self.session.post(self.login_url, data=data)

    def _prerequisite(self, url):
        if self.last_pre_request is not url:
            self._do_html_request(url)
            self.last_pre_request = url

    def _pagination(self, data_function):
        json_data = data_function()
        numberOfPages = json_data["numberOfPages"]
        data = json_data["Data"]

        for page in range(2, numberOfPages + 1):
            json_data = data_function(page=page)
            data.extend(json_data["Data"])

        return data

    def _request_data(self, url, details_function, page):
        payload = self.default_payload.copy()
        payload.update(self.payoneer_internal_payload)
        payload['currPage'] = page
        data = self._do_json_request(url, payload=payload)

        items_unpacked = json.loads(data["d"])
        items = items_unpacked["Data"]
        detailed_data = []
        for index, item in enumerate(items):
            details = details_function(row=index, page=page)
            item.update(details)
            detailed_data.append(item)
        # replace Data section to the one with all details
        items_unpacked["Data"] = detailed_data
        return items_unpacked

    def _request_details(self, url, query_params, output_format, row, page):
        query_params['rowindex'] = row
        query_params['currPage'] = page
        data = self._do_html_request(url, query_params=query_params)
        return self._html_handler(output_format, data)

    def _pre_transactions_page(self):
        return self._prerequisite(self.transactions_url)

    def _pre_loads_page(self):
        return self._prerequisite(self.loads_url)

    def list_loads(self, page=1):
        self._pre_loads_page()
        return self._request_data(self.loads_json_url, self._get_load_details, page)

    def list_transactions(self, page=1):
        self._pre_transactions_page()
        return self._request_data(self.transactions_json_url, self._get_transaction_details, page)

    def list_preauth_transactions(self, page=1):
        self._pre_transactions_page()
        return self._request_data(self.preauth_transactions_json_url, self._get_preauth_transaction_details, page)

    def list_all_transactions(self):
        self._pre_transactions_page()
        return self._pagination(self.list_transactions)

    def list_all_loads(self):
        return self._pagination(self.list_loads)

    def list_all_preauth_transactions(self):
        return self._pagination(self.list_preauth_transactions)

    def _get_transaction_details(self, row=0, page=1):
        query_params = {
            'transactionDetails': 'true',
            'AuditId': ''
        }
        output_format = {
            'Date': 'span#lblDate',
            'AuthNumber': 'span#lblAuthNumber',
            'TerminalID': 'span#lblTerminalId',
            'TerminalAddress': 'span#lblTerminalAddress',
            'TerminalCity': 'span#lblTerminalCity',
            'TerminalStateAndCountry': 'span#lblTerminalStateAndCountry',
            'LocalCurrencyAmount': 'span#lblLocalCurrencyAmount',
            'USDAmount': 'span#lblUSDAmount',
            'FeeAmount': 'span#lblFee'
        }
        return self._request_details(self.transaction_details_html_url, query_params, output_format, row, page)

    def _get_load_details(self, row=0, page=1):
        query_params = {
            'loadlistDetails': 'true',
            'PaymentId': ''
        }
        output_format = {
            'PaymentId': 'span#lblPaymentID',
            'Date': 'span#lblPaymentDate',
            'LoadStatus': 'span#lblLoadStatus',
            'AmountToLoad': 'span#lblAmountToLoad',
            'LoaderDetails': 'span#lblLoaderDetails',
            'PayeeId': 'span#lblPayeeId'
        }
        return self._request_details(self.load_details_html_url, query_params, output_format, row, page)

    def _get_preauth_transaction_details(self, row=0, page=1):
        query_params = {
            'transactionDetails': 'true',
            'AuditId': ''
        }
        output_format = {
            'Date': 'span#lblDate',
            'TerminalID': 'span#lblTerminalId',
            'TerminalType': 'span#lblTerminalType',
            'TerminalAddress': 'span#lblTerminalAddress',
            'Description': 'span#lblDescription',
            'LocalCurrencyAmount': 'span#lblLocalCurrencyAmount',
            'USDAmount': 'span#lblUSDAmount'
        }
        return self._request_details(self.preauth_transaction_details_html_url, query_params, output_format, row, page)

    def _html_handler(self, format, content):
        # Go through the format dictionary of value : css_class and return a dict of corresponding values
        result = dict.fromkeys(format)
        dom = fromstring(content)

        for key, value in format.iteritems():
            selector = dom.cssselect(value)
            if selector:
                result[key] = selector[0].text

        return result
