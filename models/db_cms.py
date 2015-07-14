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
	Field('title', length=255), 
	Field('is_public', 'boolean', default=True), 
	Field('page_content', 'text', widget=ckeditor.widget),
	auth.signature,
	format='%(title)s - %(id)s'
	)

db.define_table('menu_links',
	Field('title', length=255), 
	Field('page_link','reference static_pages'),
	Field('hierarchy_position','integer',requires=IS_IN_SET(['1','2','3'])),
	Field('parent_link','reference menu_links'),
	auth.signature,
	format='%(title)s - %(id)s'
	)

db.menu_links.parent_link.requires=IS_EMPTY_OR(IS_IN_DB(db,db.menu_links.id,'%(title)s - %(id)s'))

# db.static_pages.drop()
# db.menu_links.drop()