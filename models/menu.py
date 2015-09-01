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

# response.menu = [(T('The Mess'), False, URL('blog', 'index'), [])]
# response.menu += [(T('Clinics'), False, URL('clinics', 'index'), [
#             (T('General Info'), False, URL('clinics', 'index'), []),
#             (T('Browse Clinics'), False, URL('clinics', 'browse'), []),
#             (T('My Sessions'), False, URL('clinics', 'my_sessions'), []),

#   ])]

response.menu = []
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



#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

if "auth" in locals(): auth.wikimenu()
