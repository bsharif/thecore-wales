# -*- coding: utf-8 -*-
# try something like
import datetime
from gluon.tools import prettydate

@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster') or auth.has_membership('medic_user'))
def get_user_name(user_id):
    user_record = db(db.auth_user.id==user_id).select().first()
    first_name = user_record.first_name
    last_name = user_record.last_name
    full_name = str(first_name +" " + last_name)
    return full_name

@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster') or auth.has_membership('medic_user'))
def index():
    all_posts = db(db.inbox_posts).select(orderby=~db.inbox_posts.created_on)
    most_recent_post = db(db.inbox_posts).select(orderby=~db.inbox_posts.created_on).first()
    return locals()

@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster') or auth.has_membership('medic_user'))
def view():
    post_id = int(request.args(0))
    inbox_post_record = db(db.inbox_posts.id==post_id).select().first()
    # user_name = "test" 
    category_record = db(db.inbox_categories.id==inbox_post_record.category).select().first()
    advanced_options=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True

    return locals()


@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster') or auth.has_membership('medic_user'))
def view_category():
    category_id = int(request.args(0))
    category_name = db(db.inbox_categories.id==category_id).select().first()
    all_posts = db(db.inbox_posts.category==category_id).select(orderby=db.inbox_posts.created_on)

    return locals()



@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster'))
def new_post():
    form = SQLFORM(db.inbox_posts)
    if auth.has_membership('ecg_poster'):
        form.vars.category = 2
    if form.process().accepted:
        response.flash = 'Posted!'
        redirect(URL('inbox','index'))
    return locals()


@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster'))
def new_category():
    form = SQLFORM(db.inbox_categories)
    if form.process().accepted:
        response.flash = 'New category created'
        redirect(URL('inbox','index'))
    return locals()

 

@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster') or auth.has_membership('medic_user'))
def inbox_sidebar():
    most_recent_post = db(db.inbox_posts).select(orderby=db.inbox_posts.created_on).first()
    blog_categories = db(db.inbox_categories).select()
    advanced_options=False
    ecg_poster=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True
        if auth.has_membership('ecg_poster'):
            ecg_poster=True

    return locals()


@auth.requires_membership('administrator')
def edit_inbox_post():
    post_id = request.args(0)
    form=SQLFORM(db.inbox_posts, post_id, showid=False)
    if form.process().accepted:
        response.flash = 'Post Updated'
        redirect(URL('view',args=[post_id]))
    return locals()




