# -*- coding: utf-8 -*-
# try something like

###################################################
# response.ttt = db((db.page.showinmenu==1)&(db.page.active==1)).select(db.page.id, db.page.menutext, db.page.pageurl, db.page.parent, orderby=db.page.parent|db.page.sort|db.page.menutext)
# response.tttmenu = [dict(),dict()]
# for subpage in response.ttt:
#     response.tttmenu[0][str(subpage.id)] = [subpage.menutext, subpage.pageurl, subpage.parent]

#     if str(subpage.parent) in response.tttmenu[1]:
#         response.tttmenu[1][str(subpage.parent)].append(subpage.id)
#     else:
#         response.tttmenu[1][str(subpage.parent)] = [subpage.id]


# def buildmenu(parent, menu):
#     html = []
#     if menu[1][str(parent)]:

#         for itemid in menu[1][str(parent)]:
#             if str(itemid) in menu[1]:
#                 #children
#                 pageurlarg=str(menu[0][str(itemid)][1])
#                 html.append((str(menu[0][str(itemid)][0]), False, URL('aptcms', 'pages', 'index', args=pageurlarg.split("/")), buildmenu(itemid, menu)))
#             else:
#                 #no children
#                 pageurlarg=str(menu[0][str(itemid)][1])
#                 html.append((str(menu[0][str(itemid)][0]), False, URL('aptcms', 'pages', 'index', args=pageurlarg.split("/"))))
#     return html

# response.menu = buildmenu(0, response.tttmenu)
##############################

# def make_menu(records,sub_records):
# 	menu = []
	
# 	for record in records:
# 		sub_menu = []
# 		for sub_record in sub_records:
# 			if sub_record.parent_link == record.id:
# 				sub_link_tuple = (sub_record.title,False,URL('page',args=[sub_record.page_link]),[])
# 				sub_menu.append(sub_link_tuple)
# 		link_tuple = (record.title,False,URL('page',args=[record.page_link]),sub_menu)
# 		menu.append(link_tuple)
# 	return menu

# def menu_links_new():

# 	level1_records = db(db.menu_links.hierarchy_position==1).select(db.menu_links.ALL,orderby=db.menu_links.link_position)
# 	level2_records = db(db.menu_links.hierarchy_position==2).select(db.menu_links.ALL,orderby=db.menu_links.link_position)
# 	# menu = []
# 	# children_menu = []
# 	# for record in level1_records:
# 	# 	children_records = db((db.menu_links.hierarchy_position==2)&(db.menu_links.parent_link==record.id)).\
# 	# 						select(db.menu_links.ALL,orderby=db.menu_links.link_position)
# 	# 	for children_record in children_records:
# 	# 		children_tuple = (children_record.title, False, URL('page',args=[children_record.page_link],),[]) 
# 	# 		children_menu.append(children_tuple)
# 	# 	test_link = ('HellWorld',False,URL('page'),[])

# 	# 	link_tuple = (record.title, False, URL('page',args=[record.page_link],),children_menu)
# 	# 	menu.append(link_tuple)
# 	menu = make_menu(level1_records,level2_records)
# 	test = "HELLO"
# 	response.menu = menu
# 	return locals()
def generate_links():
	links_dict = {}
	links_dict['all_links'] = {}
	rows = db(db.menu_links).select()
	for row in rows:
		links_dict['all_links'][row.id] = row
	links_dict['level1'] = {}
	links_dict['level2'] = {}
	for row in rows:
		if row.hierarchy_position == 1:
			links_dict['level1'][row.id] = []
		if row.hierarchy_position == 2:
			links_dict['level2'][row.id] = []

	for level1link in links_dict['level1']:
		for row in rows:
			if row.parent_link == level1link:
				links_dict['level1'][level1link].append(row.id)
	for level2link in links_dict['level2']:
		for row in rows:
			if row.parent_link == level2link:
				links_dict['level2'][level2link].append(row.id)

	session.links_dict = links_dict


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
	page_id = 11
	page = db(db.static_pages.id==page_id).select().first()
	generate_links()
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	return locals()


def events_sidebar():

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
	event = db(db.events.id==event_id).select().first()
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	return locals()

def page():
	page_id=request.args(0)
	page = db(db.static_pages.id==page_id).select().first()
	generate_links()
	advanced_options=False
	if auth:
		user_id = auth.user_id
		if auth.has_membership('administrator'):
			advanced_options=True
	return locals()

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