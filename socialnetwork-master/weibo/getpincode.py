from weibo import APIClient
import urllib
import webbrowser #for test
import httplib
import weiboconfig as config

#get the pin code from the redirect_uri
def get_pincode():
    client = APIClient(app_key=config.APP_KEY, app_secret=config.APP_SECRET, redirect_uri=config.CALLBACK_URI)
    url = client.get_authorize_url()
    conn = httplib.HTTPSConnection('api.weibo.com')
    postdata = urllib.urlencode({'client_id':config.APP_KEY,'response_type':'code','redirect_uri':config.CALLBACK_URI, \
            'action':'submit','userId':config.ACCOUNT,'passwd':config.PASSWORD,'isLoginSina':0,'from':'','regCallback':'', \
            'state':'','ticket':'','withOfficalFlag':0})
    conn.request('POST','/oauth2/authorize',postdata,{'Referer':url, 'Content-Type':'application/x-www-form-urlencoded'})
    res = conn.getresponse()
    location = res.getheader('location')
    try:
        code = location.split('=')[1]
        return code
    except:
        print "error"

if __name__ == "__main__":
    print get_pincode()
