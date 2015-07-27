# -*- coding: utf-8 -*-
# try something like
import datetime
from gluon.tools import prettydate

def get_user_name(user_id):
    user_record = db(db.auth_user.id==user_id).select().first()
    first_name = user_record.first_name
    last_name = user_record.last_name
    full_name = str(first_name +" " + last_name)
    return full_name


def index():
    all_posts = db(db.blog_posts).select(orderby=~db.blog_posts.created_on)
    most_recent_post = db(db.blog_posts).select(orderby=~db.blog_posts.created_on).first()
    # session.most_recent_post = most_recent_post
    return locals()

def view():
    post_id = int(request.args(0))
    blog_post_record = db(db.blog_posts.id==post_id).select().first()
    user_name = get_user_name(blog_post_record.created_by)
    # user_name = "test" 
    category_record = db(db.blog_categories.id==blog_post_record.category).select().first()
    blog_comment_records = db(db.blog_comments.blog_post==post_id).select(orderby=db.blog_comments.created_on)
    advanced_options=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True

    return locals()


def view_user():
    user_id = int(request.args(0))
    user_name = get_user_name(user_id)
    user_record = db(db.auth_user.id==user_id).select().first()
    all_posts = db(db.blog_posts.created_by==user_id).select(orderby=~db.blog_posts.created_on)
    return locals()

def view_category():
    category_id = int(request.args(0))
    category_name = db(db.blog_categories.id==category_id).select().first()
    all_posts = db(db.blog_posts.category==category_id).select(orderby=db.blog_posts.created_on)

    return locals()

def view_tag():
    tag_id = int(request.args(0))
    tag_name = db(db.blog_tags.id==tag_id).select().first()
    all_posts = db(db.blog_posts.blog_tags.contains(tag_id)).select(orderby=db.blog_posts.created_on)

    return locals()

@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster'))
def new_post():
    form = SQLFORM(db.blog_posts)
    if auth.has_membership('ecg_poster'):
        form.vars.category = 2
    if form.process().accepted:
        response.flash = 'Blog/ECG Posted'
        redirect(URL('blog','index'))
    return locals()

@auth.requires(lambda: auth.has_membership('administrator') or auth.has_membership('ecg_poster'))
def new_tag():
    form = SQLFORM(db.blog_tags)
    if form.process().accepted:
        response.flash = "Tag added"
        redirect(URL('blog','index'))
    return locals()

@auth.requires_login()
def post_comment():
    blog_post_id = request.args(0)
    form = SQLFORM(db.blog_comments,fields=['comment_body'])
    form.vars.blog_post = blog_post_id
    if form.process().accepted:
        response.flash = "Comment posted"
        redirect(URL('view',args=[blog_post_id]))
    
    return locals()
def get_users_list():
    all_posts = db(db.blog_posts).select(db.blog_posts.created_by)
    user_list = []
    for post in all_posts:
        user_list.append(post.created_by)
    user_list = list(set(user_list))
    user_dict = {}
    for user in user_list:
        user_record = db(db.auth_user.id==user).select().first()
        user_name = user_record.first_name + " " + user_record.last_name
        user_dict[user] = user_name
    return user_dict

def blog_sidebar():
    most_recent_post = db(db.blog_posts).select(orderby=db.blog_posts.created_on).first()
    blog_categories = db(db.blog_categories).select()
    blog_tags = db(db.blog_tags).select()
    users_list = get_users_list()
    advanced_options=False
    ecg_poster=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True
        if auth.has_membership('ecg_poster'):
            ecg_poster=True

    return locals()

# def get_blog_tags():
#     all_posts = db(db.blog_posts).select()
#     tags_list = []
#     # for post in all_posts:
#     #     for tag in post.tags:
#     #         tags_list.append(tag)
#     return tags_list



@auth.requires_membership('administrator')
def edit_blog_post():
    post_id = request.args(0)
    form=SQLFORM(db.blog_posts, post_id, showid=False)
    if form.process().accepted:
        response.flash = 'Post Updated'
        redirect(URL('view',args=[post_id]))
    return locals()





# def view_tag():
#     tag_name = request.args(0)
# #     user_record = db(db.auth_user.id==user_id).select().first()
#     blog_posts = db(db.blog_posts.tags.contains(tag_name)).select(db.blog_posts.ALL,orderby=~db.blog_posts.created_on)
#     return locals()

# session.blog_tags = get_blog_tags()
# session.user_dict = get_users_list()
