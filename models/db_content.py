# -*- coding: utf-8 -*-
from plugin_ckeditor import CKEditor
 
ckeditor = CKEditor(db)
 
ckeditor.define_tables()

# db.define_table('cms_demo', 
# 	Field('title', length=255), 
# 	Field('is_public', 'boolean', default=True), 
# 	Field('full_text', 'text', widget=ckeditor.widget)
# 	)
# db.cms_demo.drop()

db.define_table('static_pages',
	Field('title', length=255, requires=IS_NOT_EMPTY()), 
	Field('is_public', 'boolean', default=True, readable=False, writable=False), 
	Field('page_content', 'text', widget=ckeditor.widget),
	auth.signature,
	format='%(title)s - %(id)s'
	)

db.define_table('menu_links',
	Field('title', length=255), 
	Field('page_link','reference static_pages'),
	Field('hierarchy_position','integer',requires=IS_IN_SET(['1','2','3'])),
	Field('link_position','integer'),
	Field('parent_link','reference menu_links'),
	auth.signature,
	format='%(title)s - %(id)s'
	)

db.menu_links.parent_link.requires=IS_EMPTY_OR(IS_IN_DB(db,db.menu_links.id,'%(title)s - %(id)s'))

db.define_table('events',
	Field('title','string',requires=IS_NOT_EMPTY()),
	Field('description','text',requires=IS_NOT_EMPTY(),widget=ckeditor.widget),
	Field('event_location','string',requires=IS_NOT_EMPTY()),
	Field('event_venue','string',requires=IS_NOT_EMPTY()),
	Field('event_date','date'),
	Field('event_start_time','time',requires=IS_TIME(error_message='Must be HH:MM:SS!')),
	Field('event_end_time','time',requires=IS_TIME(error_message='Must be HH:MM:SS!')),
	Field('info_link','string',requires=IS_URL(error_message='Must be a URL')),
	Field('is_public','boolean',default=True),
	auth.signature
	)

db.events.event_date.requires = IS_DATETIME(format=T('%d-%m-%y'),error_message='Must be dd-mm-yy')



