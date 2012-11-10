#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from endpoints import mapping_table
from lxml.html import fromstring
import re

__version__ = "0.0.1"

# TODO: Implement auth errors class


class Payoneer:
    """ Python Payoneer wrapper"""

    # default url
    api_url = 'https://myaccount.payoneer.com'

    # TODO: probably better to login through endpoints too
    login_url = api_url + '/Login/Login.aspx'

    # TODO: make it customisable through endpoint params
    payload = {
        'currPage': 1,
        'searchString': '',
        'searchOption': '',
        'searchParamFormat': '',
        'searchParam': '',
        'sortParam': '',
        'sortDirection': 'asc',
        'opaque': '',
        'startDate': '01/01/2008',
        'endDate': '11/10/2012',
        'PayoneerInternalId': ''
    }

    headers = {
        'Content-Type': 'application/json'
    }

    def __init__(self, username=None, password=None):
        """
        Instantiates an instance of Payoneer. Takes optional parameters for
        Authentication

        Parameters:
        username - Specific to your Payoneer account (typically email)
        password - Specific to your Payoneer account or your account's
        """

        self.mapping_table = mapping_table

        self.session = requests.session()
        response = self.session.get(self.login_url)
        dom = fromstring(response.content)

        data = dict((x.name, x.value) for x in dom.cssselect('#form1 input'))
        # TODO: get btLogin from DOM instead of hardcoding
        data['__EVENTTARGET'] = 'btLogin'
        data['txtUserName'] = username
        data['txtPassword'] = password
        self.payload["PayoneerInternalId"] = data['payoneer-internal-id']

        # TODO: Check response for authentication errors
        response = self.session.post(self.login_url, data=data)

    def __getattr__(self, api_call):
        """
        Instead of writing out each API endpoint as a method here or
        binding the API endpoints at instance runttime, we can simply
        use an elegant Python technique to construct method execution on-
        demand. We simply provide a mapping table between REST API calls
        and function names (with necessary parameters to replace
        embedded keywords on GET or json data on POST/PUT requests).

        __getattr__() is used as callback method implemented so that
        when an object tries to call a method which is not defined here,
        it looks to find a relationship in the the mapping table.  The
        table provides the structure of the API call and parameters passed
        in the method will populate missing data.

        """

        def call(self, *args, **kwargs):
            # if args:
            #     msg = "%s() got unexpected positional arguments: %s"
            #     raise TypeError(msg % (api_call, args))
            api_map = self.mapping_table[api_call]
            method = api_map['method']
            path = api_map['path']
#           status = api_map['status']
            valid_params = api_map.get('valid_params', {})

            # Assign default values to keyword arguments.
            for key, value in api_map.get('defaults', {}).iteritems():
                kwargs.setdefault(key, value)

            # Substitute mustache placeholders with data from keywords
            url = re.sub(
                '\{\{(?P<m>[a-zA-Z_]+)\}\}',
                # Optional pagination parameters will default to blank
                lambda m: "%s" % kwargs.pop(m.group(1), ''),
                self.api_url + path
            )

            # Validate remaining kwargs against valid_params and add
            # params url encoded to url variable.
            msg = "%s() got an unexpected keyword argument '%s'"
            params = self.payload

            for kw, value in kwargs.iteritems():
                param = valid_params.get(kw, None)
                if not param:
                    raise TypeError(msg % (api_call, kw))

                params[param] = value

            response = self.session.request(
                method=method,
                url=url,
                data=json.dumps(params),
                headers=self.headers
            )
            result = {}
            if response.json:
                json_data = json.loads(response.json["d"])
                pages = json_data["numberOfPages"]
                result = json_data["Data"]
                if pages > 1:
                    for page in range(2, pages):
                        self.payload["currPage"] = page
                        response = self.session.request(
                            method=method,
                            url=url,
                            data=json.dumps(params),
                            headers=self.headers
                        )
                        result.extend(json.loads(response.json["d"])["Data"])

            return result

        # Missing method is also not defined in our mapping table
        if api_call not in self.mapping_table:
            raise AttributeError('Method "%s" Does Not Exist' % api_call)

        # Execute dynamic method and pass in keyword args as data to API call
        return call.__get__(self)
