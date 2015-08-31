# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

#{{=SPAN(_class="glyphicon glyphicon-globe")}} 
response.logo = A(B(SPAN(_class="glyphicon glyphicon-globe"),' The Core'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href=URL('default','index'),
                  _id="thecore-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ben Sharif <SharifBS@cardiff.ac.uk>'
response.meta.description = 'The Core Wales - The Ultimate Online Resource for Core Medical Trainees in Wales.'
response.meta.keywords = 'core medical training, cmt, wales, clinics, clinic, booking'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
# response.google_analytics_id = 'UA-65368621-1'
response.google_analytics_id = None


#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [(T('The Mess'), False, URL('blog', 'index'), [])]
response.menu += [(T('Clinics'), False, URL('clinics', 'index'), [
            (T('General Info'), False, URL('clinics', 'index'), []),
            (T('Browse Clinics'), False, URL('clinics', 'browse'), []),
            (T('My Sessions'), False, URL('clinics', 'my_sessions'), []),

  ])]
# response.menu += [(T('Clinics'), False, URL('clinics', 'browse'), [])]
#Custom Menu Constructor
def make_menu(records,sub_records,sub_sub_records):
  menu = []
  for record in records:
    sub_menu = []
    for sub_record in sub_records:
      sub_sub_menu = []
      for sub_sub_record in sub_sub_records:
        if sub_sub_record.parent_link == sub_record.id:
          sub_sub_link_tuple = (sub_sub_record.title,False,URL('content','page',args=[sub_sub_record.page_link]),[])
          sub_sub_menu.append(sub_sub_link_tuple)
      if sub_record.parent_link == record.id:
        sub_link_tuple = (sub_record.title,False,URL('content','page',args=[sub_record.page_link]),sub_sub_menu)
        sub_menu.append(sub_link_tuple)
    link_tuple = (record.title,False,URL('content','page',args=[record.page_link]),sub_menu)
    menu.append(link_tuple)
  return menu

#get the level1 and level2 links for the menu
level1_records = db(db.menu_links.hierarchy_position==1).select(db.menu_links.ALL,orderby=db.menu_links.link_position)
level2_records = db(db.menu_links.hierarchy_position==2).select(db.menu_links.ALL,orderby=db.menu_links.link_position)
level3_records = db(db.menu_links.hierarchy_position==3).select(db.menu_links.ALL,orderby=db.menu_links.link_position)

#call make_menu and pass in the records and subrecords 
response.menu+=make_menu(level1_records,level2_records,level3_records)



if auth.has_membership('hospital') or auth.has_membership('administrator') or auth.has_membership('session_lead'):
    response.menu += [
    (T('ADMIN SECTION'), False, URL('#'), [
      (T('New Single Session'), False, URL('clinics', 'new_session'), []),
      (T('New Repeating Session'), False, URL('clinics', 'new_repeating_session'), []),
      (T('Admin Page'), False, URL('clinics', 'admin_page'), []),    
      
      ]),
    
    ]


DEVELOPMENT_MENU = False

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
          (T('This App'), False, '#', [
              (T('Design'), False, URL('admin', 'default', 'design/%s' % app)),
              LI(_class="divider"),
              (T('Controller'), False,
               URL(
               'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
              (T('View'), False,
               URL(
               'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
              (T('DB Model'), False,
               URL(
               'admin', 'default', 'edit/%s/models/db.py' % app)),
              (T('Menu Model'), False,
               URL(
               'admin', 'default', 'edit/%s/models/menu.py' % app)),
              (T('Config.ini'), False,
               URL(
               'admin', 'default', 'edit/%s/private/appconfig.ini' % app)),
              (T('Layout'), False,
               URL(
               'admin', 'default', 'edit/%s/views/layout.html' % app)),
              (T('Stylesheet'), False,
               URL(
               'admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % app)),
              (T('Database'), False, URL(app, 'appadmin', 'index')),
              (T('Errors'), False, URL(
               'admin', 'default', 'errors/' + app)),
              (T('About'), False, URL(
               'admin', 'default', 'about/' + app)),
              ]),
          ('web2py.com', False, '#', [
             (T('Download'), False,
              'http://www.web2py.com/examples/default/download'),
             (T('Support'), False,
              'http://www.web2py.com/examples/default/support'),
             (T('Demo'), False, 'http://web2py.com/demo_admin'),
             (T('Quick Examples'), False,
              'http://web2py.com/examples/default/examples'),
             (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
             (T('Videos'), False,
              'http://www.web2py.com/examples/default/videos/'),
             (T('Free Applications'),
              False, 'http://web2py.com/appliances'),
             (T('Plugins'), False, 'http://web2py.com/plugins'),
             (T('Recipes'), False, 'http://web2pyslices.com/'),
             ]),
          (T('Documentation'), False, '#', [
             (T('Online book'), False, 'http://www.web2py.com/book'),
             LI(_class="divider"),
             (T('Preface'), False,
              'http://www.web2py.com/book/default/chapter/00'),
             (T('Introduction'), False,
              'http://www.web2py.com/book/default/chapter/01'),
             (T('Python'), False,
              'http://www.web2py.com/book/default/chapter/02'),
             (T('Overview'), False,
              'http://www.web2py.com/book/default/chapter/03'),
             (T('The Core'), False,
              'http://www.web2py.com/book/default/chapter/04'),
             (T('The Views'), False,
              'http://www.web2py.com/book/default/chapter/05'),
             (T('Database'), False,
              'http://www.web2py.com/book/default/chapter/06'),
             (T('Forms and Validators'), False,
              'http://www.web2py.com/book/default/chapter/07'),
             (T('Email and SMS'), False,
              'http://www.web2py.com/book/default/chapter/08'),
             (T('Access Control'), False,
              'http://www.web2py.com/book/default/chapter/09'),
             (T('Services'), False,
              'http://www.web2py.com/book/default/chapter/10'),
             (T('Ajax Recipes'), False,
              'http://www.web2py.com/book/default/chapter/11'),
             (T('Components and Plugins'), False,
              'http://www.web2py.com/book/default/chapter/12'),
             (T('Deployment Recipes'), False,
              'http://www.web2py.com/book/default/chapter/13'),
             (T('Other Recipes'), False,
              'http://www.web2py.com/book/default/chapter/14'),
             (T('Helping web2py'), False,
              'http://www.web2py.com/book/default/chapter/15'),
             (T("Buy web2py's book"), False,
              'http://stores.lulu.com/web2py'),
             ]),
          (T('Community'), False, None, [
             (T('Groups'), False,
              'http://www.web2py.com/examples/default/usergroups'),
              (T('Twitter'), False, 'http://twitter.com/web2py'),
              (T('Live Chat'), False,
               'http://webchat.freenode.net/?channels=web2py'),
              ]),
        ]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu()
