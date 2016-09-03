from plugin_ckeditor import CKEditor
 
ckeditor = CKEditor(db)
 
# ckeditor.define_tables()

db.define_table('inbox_tags',
    Field('tagname'),
    format='%(tagname)s')

db.define_table('inbox_categories',
    Field('category_name'),
    format='%(category_name)s')


db.define_table('inbox_posts',
    Field('title'),
    Field('category','reference inbox_categories',requires=IS_IN_DB(db, 'inbox_categories.id', '%(category_name)s')),
    Field('body', 'text', widget=ckeditor.widget),
    # Field('slug'),
    # Field('inbox_content','text'),
    # Field('excerpt', 'text'),
    auth.signature,
    format='%(title)s')


