# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
db.define_table('blog_posts',
                Field('title','string'),
                Field('blog_content','text'),
                Field('tags','list:string'),
                auth.signature)
