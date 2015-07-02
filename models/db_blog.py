db.define_table('blog_posts',
                Field('title','string'),
                Field('blog_content','text'),
                Field('tags','list:string'),
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