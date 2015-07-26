from plugin_ckeditor import CKEditor
 
ckeditor = CKEditor(db)
 
# ckeditor.define_tables()

db.define_table('blog_tags',
    Field('tagname'),
    format='%(tagname)s')

db.define_table('blog_categories',
    Field('category_name'),
    format='%(category_name)s')


db.define_table('blog_posts',
    Field('title'),
    # Field('slug'),
    Field('category','reference blog_categories',requires=IS_IN_DB(db, 'blog_categories.id', '%(category_name)s')),
    Field('body', 'text', widget=ckeditor.widget),
    # Field('blog_content','text'),
    Field('excerpt', 'text'),
    Field('blog_tags', 'list:reference blog_tags'),
    auth.signature,
    format='%(title)s')


# db.blog_posts.drop()
# db.define_table('blog_posts',
#                 Field('title','string'),
                # Field('blog_content','text'),
#                 Field('tags','list:string'),
#                 auth.signature)


db.define_table('blog_comments',
                Field('blog_post', 'reference blog_posts', ondelete = 'NO ACTION'),
                Field('comment_body','text', requires = IS_NOT_EMPTY()),
                auth.signature)

#reg questionnaire
db.define_table('reg_questionnaire',
                Field('specialty_slug','string',requires=IS_SLUG()),
                Field('specialty','string'),
                Field('author','string'),
                Field('email','string'),
                Field('pursure_a_career','text'),
                Field('rotation_useful','text'),
                Field('enjoy_most','text'),
                Field('challenging_aspects','text'),
                Field('typical_patients','text'),
                Field('typical_day','text'),
                Field('typical_hours','text'),
                Field('part_time_training','text'),
                Field('teaching_research','text'),
                Field('advice','text'),
                Field('happy_to_contact','text'),
                auth.signature)
# db.reg_questionnaire.drop()