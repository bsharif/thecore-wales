# -*- coding: utf-8 -*-
def get_form_labels():
    form_labels = {'pursure_a_career':'What made you decide to pursue a career in this specialty?','rotation_useful':'What rotations did you do in your training and were any particularly helpful?','enjoy_most':'What do you most enjoy about the specialty?','challenging_aspects':'Are there any aspects of the specialty you find challenging/ frustrating?','typical_patients':'Are there typical patient groups and if so what are they like?','typical_day':'What does the typical day in the life of a  registrar for this specialty involve?','typical_hours':'What are the typical working hours?','part_time_training':'Is there any opportunity for part time training?','teaching_research':'Are there many opportunities for teaching/research/managerial positions within the specialty?','advice':'Do you have any advice for someone considering a career in this specialty?','happy_to_contact':'Would you be happy to be contacted by email by trainees who had any further questions?'}
    return form_labels

def index(): 
    specialty_dict = {} 
    specialty_records = db(db.reg_questionnaire).select()
    for specialty in specialty_records:
        specialty_dict[specialty.specialty_slug] = specialty.specialty
    session.specialty_dict = specialty_dict
    advanced_options=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True
    return locals()


def view():
    specialty = request.args(0)
    specialty_record = db(db.reg_questionnaire.specialty_slug==specialty).select().first()
    advanced_options=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True
    return locals()

@auth.requires_membership('administrator')
def edit_post():
    form_labels = get_form_labels()
    post_id = request.vars.post_id
    form=SQLFORM(db.reg_questionnaire, post_id, 
                 showid=False,
                 labels=form_labels)
    if form.process().accepted:
        response.flash = 'Post Updated'
        redirect(URL('index'))
    return locals()

def add_new():
    form_labels = get_form_labels()
    form = SQLFORM(db.reg_questionnaire,
                  labels=form_labels)
    if form.process().accepted:
        response.flash = 'Record Added'
        redirect(URL('index'))
    return locals()
