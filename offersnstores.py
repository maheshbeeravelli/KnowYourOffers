import webapp2
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
stores_template = os.path.join(os.path.dirname(__file__), 'stores.html') 
JINJA_ENVIRONMENT =jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'])

def exc_handler(self,obj,exc):
  self.response.write("Mahesh")
class OfferPageJson(webapp2.RequestHandler):
    def get(self):
      try:
        key=self.request.get('key')
        self.response.out.headers['Content-Type']='text/json'
        offer = datamodel.Offers.get(key)
        dict={'link':str(offer.aff_link),'coupon':str(offer.coupon_code)}
        output=json.dumps(dict)
        offer.clicks =offer.clicks+1
        offer.put()
        self.response.out.write(output)
      except Exception as exc:
        self.response.write("Mahesh Exception:")
        self.response.write(exc)
        #exc_handler(self,exc)

class OfferPage(webapp2.RequestHandler):
    def get(self):
      try:
        user = users.get_current_user()
        user_logged = None
        if user:
          user_logged=user.nickname()
        id=self.request.get('oid')
        #self.response.out.headers['Content-Type']='text/json'
        current_offer = datamodel.Offers.get_by_id(int(id)) #datamodel.Offers.get(key)
        #dict={'link':str(offer.aff_link),'coupon':str(offer.coupon_code)}
        #output=json.dumps(dict)
        current_offer.clicks =current_offer.clicks+1
        current_offer.put()
        offers = datamodel.Offers.all()
        stores = datamodel.Stores.all()
        template_values = {
            'name': user_logged,'offers':offers,'current_offer':current_offer,'stores':stores
                          }
          #self.response.out.write(template.render(stores_template, template_values))
        template = JINJA_ENVIRONMENT.get_template('singleoffer.html')
        self.response.write(template.render(template_values))
        #self.response.out.write(output)
      except Exception as exc:
        self.response.write("Exception:")
        self.response.write(exc)

class StorePage(webapp2.RequestHandler):
    def get(self):
      user = users.get_current_user()
      try:
        if user:
          user_logged=user.nickname()
        else:
          user_logged = "Guest"
        stores = db.GqlQuery("SELECT * FROM Stores order by deals_count")
        total_pages = stores.count()/20
        fetch_page_number=0
        if(self.request.get('page')):
          fetch_page_number=self.request.get('page')
        if self.request.get("list"):
          # self.response.write("Inside the list page")
          template_values = {
            'name': user_logged,'stores':stores,'top_stores':stores[0:5]}
          #self.response.out.write(template.render(stores_template, template_values))
          template = JINJA_ENVIRONMENT.get_template('stores.html')
          self.response.write(template.render(template_values))
          return
        store = self.request.get("store")
        type  = self.request.get("type")
        # self.response.write("No List of all stores")
        offers =  db.GqlQuery("SELECT * FROM Offers where store=:1 and enabled=True order by posted_on desc",store)  
        for me in stores:
          if me.store==store:
            me.clicks = me.clicks+1
            me.put()
        # today =  datetime.date.today()
        offers_desc = " {0} - Deals and Coupons".format(store)
        top_stores=[]
        for s in stores:
          top_stores.append(s)
        stores = top_stores
        template_values = {
            'name': "Mahesh",'offers_desc':offers_desc,'offers':offers,'stores':stores,'top_stores':stores,
            'page_no':int(fetch_page_number),'link':"/?q=",'count_pages':total_pages,'current_store':store
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
      except Exception as exc:
        self.response.write("Exception:")
        self.response.write(exc)
        self.response.write(sys.exc_traceback.tb_lineno)

app = webapp2.WSGIApplication([
  ('/offer',OfferPage), ('/store',StorePage),
], debug=True)