# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()
#***************************************************************
# DEFINE LIST OF HOSPITALS
# USING A DB WILL ALLOW ME TO CREATE AN ADMIN PAGE TO ADD NEW HOSPITALS
db.define_table('hospitals',
                Field('hospital_name','string'),
                Field('hospital_code','string',length=3),   #limit to 3 letter hospital code
                format = '%(hospital_code)s')  #this format string allows us to decide what details of the records to display when referencing this table from elsewhere (eg. on the user sign up form)
#***************************************************************
#DEFINE A DATABASE OF ACCESS KEYS THAT CAN BE USED TO AUTOMATICALLY GIVE HIGHER LEVEL PERMISSIONS
db.define_table('access_keys',
                Field('unique_key','string'),
                Field('key_active','boolean',default=True),
                Field('access_level','string',requires=IS_IN_SET(('session_lead','medic_user','hospital','administrator'))))
#***************************************************************
#ADD CUSTOM FIELDS TO AUTH USER 
#CUSTOM FIELD = DEFAULT HOSPITAL, ACCESS_KEY, EMAIL NOTIFICATIONS
auth.settings.extra_fields['auth_user']= [
    Field('default_hospital','reference hospitals'),
    Field('training_level','string',requires=IS_IN_SET(('F1','F2','CT1','CT2','CT3','SpR','Consultant','Non-training post'))),
    Field('access_key','string'),
    Field('email_notifications','boolean',default=True)]     
# for default hospital choices make reference to the hospitals table defined above - and require that the value equals something from that DB
#***************************************************************
#Make email addresses case insensitive
auth.settings.email_case_sensitive = False

#

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)







## configure email
mail = auth.settings.mailer
# mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
# mail.settings.sender = myconf.take('smtp.sender')
# mail.settings.login = myconf.take('smtp.login')
#>>>>>>email settings
mail.settings.server = 'smtp.gmail.com:465' 
mail.settings.sender = 'medboard.mail@gmail.com'         # your email
mail.settings.login = 'medboard.mail@gmail.com:nhs15hack!'      # your credentials or None


## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#>>>>>>>>>>custom failed auth page
auth.settings.on_failed_authorization =     URL('failed_auth')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)
