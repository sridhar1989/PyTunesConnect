# standard library
import json
import datetime
import re
import time
import shutil

# third party modules
from requests import session
from lxml.html import fromstring, tostring

class PyTunesConnect:

    def __init__(self, accountName, password):
        self.setup_session(accountName,password)

        self.headers = headers = {
                            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding':'gzip, deflate, sdch',
                            'Accept-Language':'en-US,en;q=0.8',
                            'Connection':'keep-alive',
                            'Host':'itunesconnect.apple.com',
                            'Upgrade-Insecure-Requests':1,
                            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
                        }

        self.app_analytics_exceptions = {
                            'appVersion': ['pageViewCount','units','iap','sales','payingUsers'],
                            'campaignId' : ['crashes'],
                            'platformVersion' : [],
                            'platform':[],
                            'region':['crashes'],
                            'storefront':['crashes'],
                            'domainReferrer':['crashes']
                        }

        self.app_analytics_measures = {
            'App Store Views' : 'pageViewCount',
            'App Units' : 'units',
            'In-App Purchases' : 'iap',
            'Sales' : 'sales',
            'Paying Users' : 'payingUsers',
            'Installations' : 'installs',
            'Sessions' : 'sessions',
            'Active Devices' : 'activeDevices',
            'Active Last 30 Days' : 'rollingActiveDevices',
            'Crashes' :  'crashes'
        }

        self.app_analytics_dimensions = {
            'App Version' : 'appVersion',
            'Campaign' : 'campaignId', # (insufficient data for campaign)
            'Device' : 'platform',
            'Platform Version' : 'platformVersion',
            'Region' : 'region',
            'Territory' : 'storefront',
            'Website' : 'domainReferrer'
        }

        self.sales_and_trends_dimensions = {
            'Territory' : 'piano_location',
            'Device' : 'platform',
            'Category' : 'Category',
            'Content Type' : 'content_type',
            'Transaction Type' : 'transaction_type',
            'CMB' : 'purch_type_ext',
            'Version' : 'version_desc_piano'
        }


        self.sales_and_trends_measures = {
            'Units' : 'units_utc',
            'Proceeds' : 'Royalty_utc',
            'Sales' : 'total_tax_usd_utc'
        }

        self.sales_and_trends_intervals = {
            'Days' : 'day',
            'Weeks' : 'week',
            'Months' : 'month',
            'Quarters' : 'quarter',
            'Years' : 'year'

        }

        with open('optionkeys.json','r') as jsonfile:
            self.sales_and_trends_option_keys = json.load(jsonfile)

        self.index = 1457547810096

    def setup_session(self, accountName, password):

        self.session = session()

        payload = {
            'accountName': accountName,
            'password': password,
            'rememberMe': False,
        }

        headers = {
            'Content-Type':'application/json',
            'X-Apple-Widget-Key':'22d448248055bab0dc197c6271d738c3',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Accept':'application/json',
            'Referrer':'https://idmsa.apple.com',
        }

        r = self.session.post('https://idmsa.apple.com/appleauth/auth/signin', json=payload, headers=headers)

        r = self.session.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa')
    
        if 'myacinfo' not in self.session.cookies.get_dict().keys():
            raise Exception('Didn\'t get the myacinfo cookie')

        # Requests itunes connect page that will give us itCtx cookie needed for api requests
        
        r = self.session.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa', allow_redirects=False)
    
        if 'itctx' not in self.session.cookies.get_dict().keys():
            raise Exception('Didn\'t obtain the itctx cookie')


    def get_apps(self):

        headers = {
            'Host':'analytics.itunes.apple.com',
            'Origin':'https://analytics.itunes.apple.com',
            'Referer':'https://analytics.itunes.apple.com/',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Upgrade-Insecure-Requests':1,
            'X-Requested-By':'analytics.itunes.apple.com',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        }

        r = self.session.get('https://analytics.itunes.apple.com/analytics/api/v1/app-info/app', headers=headers)

        data = json.loads(r.text)

        return data

    def get_adam_ids(self):

        data = self.get_apps()

        adamIds ={}

        for app in data['results']:
            adamIds[app['adamId']] = app['name']

        return adamIds

    def get_app_analytics_data(self, adamId, startdate, enddate, measure, dimension):

        startTime = startdate.strftime('%Y-%m-%dT%H:%M:%SZ')
        endTime = enddate.strftime('%Y-%m-%dT%H:%M:%SZ')

        payload = {
            'adamId':[adamId],
            'startTime':startTime,
            'endTime':endTime,
            'frequency':'DAY',
            'measures':[self.app_analytics_measures[measure]],
            'group':{
                'metric':self.app_analytics_measures[measure],
                'dimension':self.app_analytics_dimensions[dimension],
                'rank':'DESCENDING',
                'limit':3
            },
            'dimensionFilters':[]
        }

        payload = json.dumps(payload)

        headers = {
            'Host':'analytics.itunes.apple.com',
            'Origin':'https://analytics.itunes.apple.com',
            'Referer':'https://analytics.itunes.apple.com/',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Upgrade-Insecure-Requests':1,
            'X-Requested-By':'analytics.itunes.apple.com',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        }

        r = self.session.post('https://analytics.itunes.apple.com/analytics/api/v1/data/time-series', data=payload, headers=headers)

        return r.text

    def get_sales_and_trends_data(self, dimension, measure, interval, startdate, enddate, filters=None):

        itunesfilters = []

        if filters:
            for dim, filtervalues in filters.items():
                if filtervalues:
                    itunesfilterval = {
                        'dimension_key':self.sales_and_trends_dimensions[dim],
                        'option_keys':[]
                    }
                    for filtervalue in filtervalues:
                        itunesfilterval['option_keys'].append(self.sales_and_trends_option_keys[filtervalue])
                    itunesfilters.append(itunesfilterval)

        payload = {
            'filters':itunesfilters,
            'group':self.sales_and_trends_dimensions[dimension],
            'interval':self.sales_and_trends_intervals[interval],
            'start_date':startdate.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'end_date':enddate.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'sort':'descending',
            'limit':100,
            'measures':[self.sales_and_trends_measures[measure]]
        }

        r = self.session.post('https://reportingitc2.apple.com/api/data/timeseries', json=payload, headers=self.headers)

        return r.text

    def get_sales_and_trends_metadata(self):
        r = self.session.get('https://reportingitc2.apple.com/api/all_metadata?_=%s' % self.index)
        self.index += 1
        return json.loads(r.text)

    def get_sales_and_trends_metadata_options(self):

        data = self.get_sales_and_trends_metadata()

        optionkeys = {}

        for dimension in data['dimensions']:
            if dimension['type'] == 'options':
                for option in dimension['options']:
                    optionkeys[option['title']] = option['key']

        return optionkeys

    def get_latest_reported_earnings(self):

        r = self.session.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/da/jumpTo?page=paymentsAndFinancialReports')

        tree = fromstring(r.text)

        headings = tree.xpath("//div[@class='earnings-middle']//div[@class='heading']")
        tables = tree.xpath("//div[@class='earnings-middle']//table")

        earnings = {}

        for heading, table in zip(headings, tables):
            earnings[heading.text] = []
            for row in table.xpath(".//tr"):
                currency = unicode(row[0].text).strip()
                amount = unicode(row[1].text).strip()
                earnings[heading.text].append({currency : amount})

        return earnings

    def get_earnings(self, contentProviderId, vendornumber, year, month, path='output.zip'):

        headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'en-US,en;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Content-Length':640,
            'Content-Type':'multipart/form-data; boundary=----WebKitFormBoundaryq447WLYMWLPQsVFC',
            'Host':'itunesconnect.apple.com',
            'Origin':'https://itunesconnect.apple.com',
            'Referer':'https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/wo/27.0.0.11.5.0.9.3.1',
            'Upgrade-Insecure-Requests':1,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
        }


        regionCurrencyIds = [
        10000,
        10005,
        10001,
        10063,
        10062,
        10003,
        10064,
        10067,
        10068,
        10069,
        10006,
        10008,
        10007,
        10060,
        10002,
        10070,
        10071,
        10065,
        10072,
        10061,
        10020,
        10066,
        10073,
        10074,
        10004]
        
        payload = {
            'year':year,
            'month':month,
            'regionCurrencyIds': ','.join(str(i) for i in regionCurrencyIds),
            'reportTypes':'FINANCIAL_REPORT'
        }

        url = 'https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/paymentConsolidation/providers/%s/sapVendorNumbers/%s/reports' % (contentProviderId, vendornumber)

        r = self.session.get(url, params=payload, headers=headers)

        data = json.loads(r.text)
        
        print 'Sleeping for:', data['data']['estimatedWaitingTime']
        time.sleep(data['data']['estimatedWaitingTime'])
        
        r = self.session.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/wa/downloadBatchFinancialReport?uuid=%s' % data['data']['uuid'], headers=headers, stream=True)
        
        if r.status_code == 200:

            with open(path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        else:
            raise Exception('Earnings report download failed')
            

    def get_user_info(self):
        
        r = self.session.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/user/detail')
        
        return json.loads(r.text)

    def get_vendor_numbers(self, contentProviderId):
        
        r = self.session.get('https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/ra/paymentConsolidation/providers/%s/sapVendorNumbers' % contentProviderId)
        
        return json.loads(r.text)

    def get_contentproviderids_and_vendornumbers(self):
        
        contentProviderIds = {}

        userdata = self.get_user_info()
        
        for assoc_acc in userdata['data']['associatedAccounts']:

            contentProviderId = assoc_acc['contentProvider']['contentProviderId']
            
            vendornumberdata = self.get_vendor_numbers(contentProviderId)

            vendorNumbers = []
            
            for item in vendornumberdata['data']:
                vendorNumbers.append(item['sapVendorNumber'])
                
            contentProviderIds[contentProviderId] = vendorNumbers
            
        return contentProviderIds
