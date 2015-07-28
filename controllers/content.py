# -*- coding: utf-8 -*-
# try something like


def make_menu(records,sub_records,sub_sub_records,current_page):
  menu = []
  # current_page = 45
  for record in records:
    sub_menu = []
    for sub_record in sub_records:
      sub_sub_menu = []
      for sub_sub_record in sub_sub_records:
        if sub_sub_record.parent_link == sub_record.id:
          sub_sub_link_tuple = (sub_sub_record.title,sub_sub_record.page_link==current_page,URL('content','page',args=[sub_sub_record.page_link]),[])
          sub_sub_menu.append(sub_sub_link_tuple)
      if sub_record.parent_link == record.id:
        sub_link_tuple = (sub_record.title,sub_record.page_link==current_page,URL('content','page',args=[sub_record.page_link]),sub_sub_menu)
        sub_menu.append(sub_link_tuple)
    link_tuple = (record.title,record.page_link==current_page,URL('content','page',args=[record.page_link]),sub_menu)
    menu.append(link_tuple)
  return menu

@auth.requires_membership('administrator')
def edit_links():
	fields = (db.menu_links.title,db.menu_links.page_link,db.menu_links.hierarchy_position,db.menu_links.parent_link)
	grid = SQLFORM.grid(db.menu_links,orderby=db.menu_links.hierarchy_position,
						searchable=False,
						create=True,
						editable=True,
						deletable=True,
						details=False,
						paginate=999,
						sortable=True,
						csv=False,
						fields=fields)
	return locals()

def index():
	redirect(URL('default','index'))
	# page_id = 11
	# page = db(db.static_pages.id==page_id).select().first()
	
	# advanced_options=False
	# if auth:
	# 	user_id = auth.user_id
	# 	if auth.has_membership('administrator'):
	# 		advanced_options=True
	return locals()


def events_right_sidebar():

	events = db(db.events).select()
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	return dict(events=events,advanced_options=advanced_options)

def events():
	page_id = 11
	event_id = request.args(0)
	if event_id: redirect(URL('view_event',args=[event_id]))
	all_events = db(db.events.id).select()
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	return locals()

def view_event():
	page_id = 11
	event_id = request.args(0)
	event = db(db.events.id==event_id).select().first()
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	return locals()
@auth.requires_membership('administrator')
def edit_event():
	event_id = request.args(0)
	event = db(db.events.id==event_id).select().first()
	buttons = [DIV(TAG.button('Save',_type="submit",_class="btn btn-primary"), \
    				A('Cancel Edit',_href=URL('view_event',args=[event_id]),_class="btn btn-danger"), \
    				_class="col-sm-9 col-sm-offset-4")]

	form = SQLFORM(db.events, event, buttons=buttons)
	if form.process().accepted:
		response.flash = "Event Edited"
		redirect(URL('view_event',args=[event_id]))
	return locals()

@auth.requires_membership('administrator')
def new_event():
	form = SQLFORM(db.events)
	if form.process().accepted:
		response.flash = "Event Added"
		redirect(URL('view_event',args=[form.vars.id]))
	return locals()


def page():

	#get page content
	page_id=request.args(0)
	page = db(db.static_pages.id==page_id).select().first()
	
	#check if page is a public page and if user has appropriate access
	if not page.is_public:
		if not auth:
			redirect(URL('default','failed_auth'))
		elif not auth.has_membership('hospital') and not auth.has_membership('medic_user') and not auth.has_membership('administrator') and not auth.has_membership('session_lead'):
			redirect(URL('default','failed_auth'))


	#if admin then give admin options
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	

	#get the level1 and level2 links for the menu
	level1_records = db(db.menu_links.hierarchy_position==1).select(db.menu_links.ALL,orderby=db.menu_links.link_position)
	level2_records = db(db.menu_links.hierarchy_position==2).select(db.menu_links.ALL,orderby=db.menu_links.link_position)
	level3_records = db(db.menu_links.hierarchy_position==3).select(db.menu_links.ALL,orderby=db.menu_links.link_position)

	#call make_menu and pass in the records and subrecords 
	current_page = int(page_id)
	side_menu=make_menu(level1_records,level2_records,level3_records,current_page)

	#SIDEBAR LINKS  - downright arrow == &#8627;
	#get the link associated with that page
	menu_link_record = db(db.menu_links.page_link==page_id).select().first()
	#get the parent link for that page (if it exists) - used for heading of sidebar
	parent_link_record = db(db.menu_links.id==menu_link_record.parent_link).select().first()
	menu = side_menu
	if menu_link_record.hierarchy_position == 1:
		parent_link_record = menu_link_record
		sidebar_title = parent_link_record.title
		sidebar = []
	elif menu_link_record.hierarchy_position == 2:
		if parent_link_record:
			sidebar_title = parent_link_record.title
			for i in menu:
				if i[0] == parent_link_record.title:
					sidebar = i[3]
		else:
			parent_link_record == menu_link_record
			sidebar = False
	elif menu_link_record.hierarchy_position == 3:
		sidebar = []
		grandparent_link_record = db(db.menu_links.id==parent_link_record.parent_link).select().first()
		sidebar_title = grandparent_link_record.title
		for i in menu:
			if i[0] == grandparent_link_record.title:
				sidebar = i[3]

	return locals()

@auth.requires_membership('administrator')
def edit_page():
    page_id=request.args(0)
    page = db(db.static_pages.id==page_id).select().first()
    buttons = [DIV(TAG.button('Save',_type="submit",_class="btn btn-primary"), \
    				A('Cancel Edit',_href=URL('page',args=[page_id]),_class="btn btn-danger"), \
    				_class="col-sm-9 col-sm-offset-4")]

    form = SQLFORM(db.static_pages, page, buttons=buttons)
    if form.process().accepted:
        response.flash = "Updated"
        redirect(URL('page',args=[page_id]))
    return locals()

@auth.requires_membership('administrator')
def new_page():
	form = SQLFORM(db.static_pages)
	session.new_page_title = None
	session.new_page_id = None
	if form.process().accepted:
		response.flash = "Add New Page"
		session.new_page_title = form.vars.title
		session.new_page_id = form.vars.id

		redirect(URL('new_link'))
	return locals()

@auth.requires_membership('administrator')
def new_link():
	page_id = request.vars.page_id
	fields = ['hierarchy_position','parent_link']
	form = SQLFORM(db.menu_links,fields=fields)
	form.vars.title = session.new_page_title
	form.vars.page_link = session.new_page_id
	
	if form.process().accepted:
		response.flash = "New Link Added"
		redirect(URL('new_page'))
		session.new_page = None

	return locals()