# -*- coding: utf-8 -*-
# try something like

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