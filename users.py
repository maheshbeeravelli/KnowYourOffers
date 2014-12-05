import webapp2
import logging
import os
import datetime
import json
import urllib
import sys
import jinja2
#Custom imports
import datamodel

#Imports from Google Library
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.api import users

path = os.path.join(os.path.dirname(__file__), 'index.html')
admin_template = os.path.join(os.path.dirname(__file__), 'admin.html')
JINJA_ENVIRONMENT =jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'])

class AccountHandler(webapp2.RequestHandler):
  def get(self):
    user=users.get_current_user()
    if user:
      me  = datamodel.Users.gql("WHERE email = :1",user.email())
      ip = self.request.remote_addr
      self.response.write(ip)
    else:
      login_url=users.create_login_url(self.request.uri)
      self.redirect(login_url)
      self.response.out.write("Unable to redirect")
    
class SearchHandler(webapp2.RequestHandler):
  def get(self):
    try:
      query = str(self.request.get('q')).lower()
      stores = db.GqlQuery("SELECT * FROM Stores ORDER BY deals_count desc")
      where_clause = ""
      coupon_is_there = False
      found = False
      if(query):
        for key in ["coupons","coupon"]:
          if key in query:
            where_clause = "WHERE offer_type='Coupon'"
            coupon_is_there = True
            query=query.replace(key,"")
            found=True;
        for key in ["deals","deal"]:
          if key in query:
            found=True;
            query=query.replace(key,"")
            where_clause = "WHERE offer_type='Deal'"
            if(coupon_is_there):
              where_clause=""
        for store in stores:
          key = store.store.lower()
          if key in query:
            found=True;
            query=query.replace(key,"")
            if where_clause!="":
              where_clause = where_clause + "and store='{0}'".format(store.store)
            else:
              where_clause = "WHERE store='{0}'".format(store.store)
      query_build= "SELECT * FROM Offers {0}".format(where_clause)
      offers = db.GqlQuery(query_build)
      total_pages = offers.count()/20
      fetch_page_number=0
      if(self.request.get('page')):
        fetch_page_number=self.request.get('page')
      offers_list = []
      for offer in offers:
        offers_list.append(offer)
      # sorted(offers_list,key=lambda k: k['posted_on'])
      # self.response.write(offers_list[0])
      offers = offers_list
      data_query =[]
      if(query):
        query = ' '.join(query.split())
        for row in offers:
            if query in row.title.lower():
              found=True;
              data_query.append(row)
              offers = data_query
            elif query in row.description.lower():
              found=True;
              data_query.append(row)
              offers = data_query
      if found:
        offers_desc = "All available offers for your query"
      else:
        offers_desc = "Oops no results for your query"
        offers=[]
      today = datetime.date.today()
      # offers_desc = "All available offers for your query"
      # stores.append(db_stores)  # offers_list = [] # for offer in offers: #   offers_list.append(datetime.datetime.now() - offer.posted_on) # offers[offers.key].
      top_stores=[]
      for store in stores:
        top_stores.append(store)
      stores = top_stores
      template_values = {
          'name': "Mahesh",'offers_desc':offers_desc,'offers':offers,'stores':stores,'top_stores':stores[0:5],
          'page_no':int(fetch_page_number),'link':"/?q=",'count_pages':total_pages
      }
      template = JINJA_ENVIRONMENT.get_template('index.html')
      self.response.write(template.render(template_values))
    except Exception as exc:
        self.response.write("Exception:  ")
        self.response.write(exc)
        self.response.write("    Error at Line number:   ")
        self.response.write(sys.exc_traceback.tb_lineno)
        logging.error('There was an error in main form for query:'+self.request.get('q'))
        logging.error(exc)
        logging.error("At line number")
        logging.error(sys.exc_traceback.tb_lineno)
        
class Signin(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            
            greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            greeting = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        self.response.out.write('<html><body>%s</body></html>' % greeting)


app = webapp2.WSGIApplication([
  ('/user/account', AccountHandler),('user/search', SearchHandler)], debug=True)