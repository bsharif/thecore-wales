# -*- coding: utf-8 -*-

##IMPORTS#####################
#********REPORTLAB************
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from uuid import uuid4
from cgi import escape
import os
#*************
import datetime
import requests
##############################

def index():
    page_id=82    
    page = db(db.static_pages.id==page_id).select().first()
    advanced_options=False
    if auth:
        user_id = auth.user_id
        if auth.has_membership('administrator'):
            advanced_options=True
    return locals()

def clinics_sidebar():
    
    return locals()


@auth.requires(lambda: auth.has_membership('session_lead') or auth.has_membership('undergrad'))
def new_session():
    #add a new session
    #limited to members of undergrad or session_leads
    #set the hosital field to default to the users default hospital (as per profile)
    db.sessions.hospital.default = auth.user.default_hospital

    form = SQLFORM(db.sessions,
                   labels = {'duration':'Duration (minutes)'},
                   col3={'duration':'Please enter time in minutes'})
    form.vars.session_lead = auth.user_id
    if form.process().accepted:
        response.flash = "Session Added"
        redirect(URL('my_sessions'))
    elif form.errors:
        response.flash = "Errors in form. Please correct them"

    return locals()

@auth.requires_membership('session_lead')
def new_repeating_session():
    #limited to members of undergrad or session_leads
    #this creates a basic outline then lets users enter basic session details and number of session required
    #stores all values in a session.dictionary and redirect to a new page with a dynamically genrated SQL form
    #the new page allows entry of dates
    user_id = auth.user_id
    #start from beginning
    restrict_lead_query = ((db.auth_user.id == db.auth_membership.user_id)&
           ((db.auth_membership.group_id == 2)|(db.auth_membership.group_id == 3)))

    basic_form = SQLFORM.factory(
                Field('hospital','reference hospitals',requires=IS_IN_DB(db,'hospitals.id','%(hospital_name)s'),default=auth.user.default_hospital), #need to add a default option depending on users default hospital
                Field('session_type','reference session_types',requires=IS_IN_DB(db,'session_types.id','%(session_type)s'),default='1'),    #added requires in set from SESSION_TYPES table - currently 4 types available
                Field('session_lead','reference auth_user', default=auth.user_id, readable=False, writable=False, requires=IS_IN_DB(db(restrict_lead_query), db.auth_user.id, '%(first_name)s %(last_name)s (%(email)s)')),
                Field('session_lead_name','string'),
                Field('session_lead_email','string'),
                Field('title','string',requires=IS_NOT_EMPTY()),
                Field('description','text'),
                Field('session_location','string',requires=IS_NOT_EMPTY()),
                Field('duration','integer',requires=IS_NOT_EMPTY()),
                Field('max_attendees','integer',requires=IS_NOT_EMPTY()),
                Field('number_of_sessions','integer',requires=IS_NOT_EMPTY()),
                labels = {'duration':'Duration (minutes)'},
                submit_button='Next')

    if basic_form.process().accepted:
        session.part_one = True
        session.repeating_basic = {}
        session.repeating_basic['hospital'] = basic_form.vars.hospital
        session.repeating_basic['session_type'] = basic_form.vars.session_type
        session.repeating_basic['session_lead'] = auth.user_id
        session.repeating_basic['session_lead_name'] = basic_form.vars.session_lead_name
        session.repeating_basic['session_lead_email'] = basic_form.vars.session_lead_email
        session.repeating_basic['title'] = basic_form.vars.title
        session.repeating_basic['description'] = basic_form.vars.description
        session.repeating_basic['session_location'] = basic_form.vars.session_location
        session.repeating_basic['duration'] = basic_form.vars.duration
        session.repeating_basic['max_attendees'] = basic_form.vars.max_attendees
        session.repeating_basic['number_of_sessions'] = basic_form.vars.number_of_sessions


        redirect(URL('new_repeating_session_dates',vars={'num':basic_form.vars.number_of_sessions}))



    return locals()
@auth.requires_login()
def new_repeating_session_dates():
    import uuid
    user_id = int(auth.user_id)
    uuid_value = uuid.uuid4()
    number = request.vars.num
    if not number:
        session.flash = "Number of sessions not provided!"
        redirect(URL('new_repeating_session'))

    number = int(number)

    #make the SQL form
    fields = []
    for i in range(1,number+1):
        field_name = "session_"+str(i)
        fields.append(Field(field_name,'datetime',requires = IS_DATETIME(format=T('%d-%m-%y %H:%M'),error_message='Must be dd-mm-yy HH:MM')))
    date_form=SQLFORM.factory(
            *fields)


    #process the form
    if date_form.process().accepted:
        for session_key in date_form.vars:
            #date_form.vars is a dict. has a key named id and other keys named session_x
            #we don't want to process the id entry
            if session_key != 'id':
                #get the session date (value) for each session_x key
                session_date = date_form.vars[session_key]

                db.sessions.insert(
                        hospital=session.repeating_basic['hospital'],
                        session_type=session.repeating_basic['session_type'],
                        session_lead=session.repeating_basic['session_lead'],
                        session_lead_name=session.repeating_basic['session_lead_name'],
                        session_lead_email=session.repeating_basic['session_lead_email'],
#                         AUTH.SIG UPDATE> author=user_id,
                        title=session.repeating_basic['title'],
                        description=session.repeating_basic['title'],
                        session_location=session.repeating_basic['session_location'],
                        start_datetime=session_date,
                        duration=session.repeating_basic['duration'],
                        max_attendees=session.repeating_basic['max_attendees'],
                        current_attendees=0,
                        repeating=True,
                        session_active=True,
                        session_full=False,
                        uuid=uuid_value)
                db.commit()
        session.repeating_basic = {}
        redirect(URL('my_sessions'))
    return locals()

# @auth.requires_login()
def view_session():
    session_id = request.vars.s_id
    if not session_id:
        session.flash = "No session ID provided"
        redirect(request.env.http_referer)
    session_record = db(db.sessions.id==session_id).select().first()
    display_fields =['hospital','session_type','session_lead_name','title','description','session_location','start_datetime','duration','max_attendees','attendee_ids']
    display_labels = {'duration':'Durations (mins)','max_attendees':'Maximum Attendees','attendee_ids':'Currently attending','session_lead_name':'Session Lead'}

    advanced_options=False
    if auth:
        if session_record.created_by==auth.user_id:
            advanced_options=True

    form=SQLFORM(db.sessions, session_record,
                 readonly=True,
                 fields=display_fields,
                 labels=display_labels,
                 ignore_rw=True,
                 showid=False)

    if form.process().accepted:
        redirect(URL('my_sessions'))
    return locals()

@auth.requires_login()
def edit_session():
    #edit a session
    #limited to members of undergrad or session_leads or authors
    #undergrad should be able to add students to session manually too
    #note think about email notifcaitons/sms
    user_id = auth.user_id
    session_id = request.vars.s_id

    if not session_id:
        session.flash = "No session ID provided"
#         redirect(request.env.http_referer)

    #get the session record
    session_record = db(db.sessions.id==session_id).select().first()

    #check that the user trying to make a change is either owner/author of session
    #TODO maybe allow anyone with admisntrative/undergrad access to edit any session?
    if (user_id != session_record.created_by) and (user_id != session_record.session_lead):
        session.flash = "Error - you do not have permission to edit this session!"
        redirect(request.env.http_referer)

    form=SQLFORM(db.sessions, session_record, showid=False)
    if form.process().accepted:
            # for user_id in session_record.attendee_ids:
                #TODO test email function on 'modified_by'
                # email_updates = send_email(user_id, "Medboard: Session Updated", session_id, "Session Details Updated")
            session.flash = "Session Updated"
            redirect(URL('my_sessions'))
    return locals()

def browse():
    #visible by anyone
    #lists ongoing sessions - default is ALL unless logged in in which case default is auth_user.default_hospital
    #view should filter and sort etc.
    if auth.user:
        
        default_hospital = get_default_hospital(auth.user.default_hospital)
        display_name = default_hospital['hospital_name']

    hospital_rows = db(db.hospitals).select()
    hospitals_list = {}
    for row in hospital_rows:
        hospitals_list[row.hospital_code] = row.hospital_name

    selected_hospital = request.args(0)
    if (not selected_hospital) and (auth.user):
        selected_hospital = auth.user.default_hospital
        db_selection = (db.sessions.session_active==True)&(db.sessions.hospital==selected_hospital)
        current_hospital = get_default_hospital(selected_hospital)
        current_hospital = current_hospital['hospital_code']
        display_fields = (db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)
    elif (not selected_hospital) and (not auth.user):
        selected_hospital = 'ALL'
        db_selection = db.sessions.session_active==True
        current_hospital = 'ALL'
        display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)
    elif selected_hospital == 'ALL':
        db_selection = db.sessions.session_active==True
        display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)
        current_hospital = 'ALL'
    else:
        hosp_id = db(db.hospitals.hospital_code==selected_hospital).select().first()
        selected_hospital = hosp_id.id
        db_selection = (db.sessions.session_active==True)&(db.sessions.hospital==selected_hospital)
        current_hospital = get_default_hospital(selected_hospital)
        current_hospital = current_hospital['hospital_code']
        display_fields = (db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)

    def status_label(row):
        session_record = db(db.sessions.id==row.id).select().first()
        if session_record.session_full == True:
            return SPAN('FULL',_class="label label-danger")
        elif session_record.session_full == False:
            if session_record.current_attendees == None:
                current_attendees = 0
            else:
                current_attendees = session_record.current_attendees
            spaces_available = session_record.max_attendees - current_attendees
            returned_label = SPAN(SPAN('Spaces available',_class="label label-success"),SPAN(' '),SPAN(str(spaces_available)+" / "+str(session_record.max_attendees),_class="badge"))
            return returned_label

    def sign_up_button(row):
        attendee_ids = row.attendee_ids
        
        if auth.user:
            user_id = auth.user_id
            if user_id in attendee_ids:
                return DIV('Attending',_class="label label-success")
            else:
                return A('Sign Up',_class="btn btn-primary",_href=URL('sign_up',vars={"s_id":row.id}))
        else:
            return A('Sign Up',_class="btn btn-primary",_href=URL('sign_up',vars={"s_id":row.id}))

    grid = SQLFORM.grid(db_selection,
                        fields=display_fields,
                        searchable=False,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        paginate=999,
                        sortable=False,
                        csv=False,
                        user_signature=False,
                        maxtextlength=50,
                        links=[dict(header="Status",body=lambda row: status_label(row)),
                               dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                               dict(header="Sign Up",body=lambda row: sign_up_button(row))],
                       headers={'sessions.start_datetime':"Start Date and Time",'sessions.duration':'Duration (mins)'}
                       )

    if grid.element('table'): grid.element('table')['_id'] = 'data_table' #giving an id to the grid container for datatables JS to know what to target

    return locals()
    
def send_email(session_id):
    # session_id = 37
    user_record = db(db.auth_user.id==auth.user_id).select().first()
    session_record = db(db.sessions.id==session_id).select().first()

    session_lead_name = session_record.session_lead_name
    session_lead_email_address = session_record.session_lead_email
    trainee_name = user_record.first_name + " " + user_record.last_name 
    trainee_email = user_record.email
    email_subject = "TheCore.Wales - Clinic Signup Notification"
    email_html ="<html><h1>TheCore.Wales</h1> <p>Dear " + session_lead_name +",</p><p>This is an notification email from TheCore.Wales.</p><hr> \
                    <p>A trainee has signed up to attend one of your clinic sessions. Details below:</p>  \
                    <p>Session Title: " + str(session_record.title) + \
                    "</p> <p>Session Date and Time: " + str(session_record.start_datetime.strftime('%d-%m-%Y %H:%M')) + \
                    "</p> <p>Session Location: " + str(session_record.session_location) + \
                    "</p> <p>Trainee Name: " + str(trainee_name) + \
                    "</p> <p>Trainee Email: " + str(trainee_email) + \
                    "</p> <p><a href='http://thecore.wales/clinics/view_session?s_id="+\
                    str(session_id)+"'>Click here</a> to view this session's details online</p>" \
                    "<p>NOTE: If for any reason this clinic is cancelled or you need to contact the trainee then you can reply to this message to contact the trainee directly.</p> \
                    <p>Thanks,</p> <p>TheCore.Wales </p></html>"
    # email_html = "<html><h1>TheCore.Wales</h1></html>"

    
    from gluon.tools import Mail
    mail = Mail()
    mail.settings.server = 'smtp.gmail.com'
    mail.settings.sender = 'thecorewales.mail@gmail.com'
    mail.settings.login = 'thecorewales.mail@gmail.com:ionTrate'
    sent_email = mail.send(to=[session_lead_email_address],
          subject=email_subject,
          # If reply_to is omitted, then mail.settings.sender is used
          reply_to=trainee_email,
          message=email_html)

    return locals()



def send_email(session_id, user_id):

    session_lead_name = "Dr Sharif"
    trainee_name = "Dr Trainee"
    session_datetime = "08/09/2015 - 0900"
    trainee_email = "ben.sharif@live.com"
    email_text = "<html> \
    <h1>TheCore.Wales</h1> \
    <h3>Sign Up Notification</h3> \
    <p>Dear " + session_lead_name + "</p> \
    <p>This email is to notify you that " + trainee_name + "has signed up to attend your clinic on the " + session_datetime + "</p> \
    <p>If the trainee is not able to attend for any reason please could you notify them by either \
    replying to this email or contacting them using the email address below:</p>" + trainee_email + "</html>"

    mail_send = mail.send(to=['SharifBS@cardiff.ac.uk'],
          subject='TestMail-TheCore',
          # If reply_to is omitted, then mail.settings.sender is used
          reply_to=trainee_email,
          message=email_text)

    return mail_send

@auth.requires_login()
def sign_up():
    session_id = request.vars.s_id
    user_id = auth.user_id
    session_record = db(db.sessions.id==session_id).select().first()
    if not session_id:
        session.flash = "No session ID provided"
        redirect(request.env.http_referer)


    #get number and ids of people already signed up
    number_of_attendees = session_record.current_attendees
    current_attendee_ids = session_record.attendee_ids  #get ids of people already signed up

    #ensure user trying to sign up is not session_lead
    if session_record.session_lead == user_id:
        session.flash = 'You are the lead for this session. You cannot sign up.'
        redirect((request.env.http_referer) or (URL('browse')))
    elif session_record.created_by == user_id:
        session.flash = 'You are the author of this session. You cannot sign up.'
        redirect((request.env.http_referer) or (URL('browse')))
    elif user_id in session_record.attendee_ids:
        session.flash = 'You are already signed up. Thanks!'
        redirect((request.env.http_referer) or (URL('browse')))
    elif session_record.session_full ==  True:
        session.flash = 'Sorry, this session is full!'
        redirect((request.env.http_referer) or (URL('browse')))
    else:
        #perform operations to add current user to list and increment total by 1
        current_attendee_ids.append(user_id)
        number_of_attendees += 1

        #make datebase updates
        session_record.update_record(attendee_ids=current_attendee_ids)
        session_record.update_record(current_attendees=number_of_attendees)

        #if we now reached the max number of attendees then flip the switch to full
        if number_of_attendees == session_record.max_attendees:
            session_record.update_record(session_full=True)

        #send email
        email_success = send_email(session_id)
        session.flash = "Thanks for signing up. The session lead has been sent an email notifying them of your attendence"
        redirect(URL('clinics','browse'))
    return locals()

@auth.requires_login()
def remove_from_session(session_id, user_id):

    #GET THE CURRENT RECORD, ATTENDEE LIST AND NUMBER OF ATTENDEES
    session_record = db(db.sessions.id==session_id).select().first()
    attendee_list = session_record.attendee_ids
    current_attendees = session_record.current_attendees
    removal_status ="NotRemoved"
#     #check that the user_id is in listed as currently attending this session
    if user_id not in session_record.attendee_ids:
        removal_status = "NotInList"
    else:
        #IF SESSSION IF CURRENTLY FULL THEN SWITCH TO NOT FULL
        #(AS ONCE THIS USER QUITS THERE WILL BE ONE MORE SPACE)
        if session_record.session_full==True:
            session_record.update_record(session_full=False)

        #SUBTRACT ONE USER FROM NUMBERS
        current_attendees -= 1
        session_record.update_record(current_attendees=current_attendees)

        #REMOVE USER ID FROM ATTENDEE IDs
        attendee_list.remove(user_id)
        session_record.update_record(attendee_ids=attendee_list)
        removal_status = "Removed"
    return removal_status

@auth.requires_login()
def quit_session():
    #GET VARS
    session_id = request.vars.s_id
    user_id = auth.user_id
    session_record = db(db.sessions.id==session_id).select(db.sessions.repeating).first()
    if not session_id:
        session.flash = "No session ID provided"
        redirect(request.env.http_referer)

    removal_status = remove_from_session(session_id, user_id)
    if removal_status == "Removed":
        session.flash = "You have been removed from the session"
    elif removal_status == "NotInList":
        session.flash = "You are not listed as being signed up to this session."
    else:
        session.flash = "Error. You have not been removed from the session"
    redirect(URL('my_sessions'))

    return locals()

@auth.requires_login()
def quit_repeating_session():
    #GET VARS
    session_id = request.vars.s_id
    user_id = auth.user_id
    if not session_id:
        session.flash = "No session ID provided"
        redirect(request.env.http_referer)
    session_record = db(db.sessions.id==session_id).select().first()

    #layout options for grid
    display_fields = (db.sessions.title,db.sessions.start_datetime)
    field_headers = {'sessions.start_datetime':"Start Date and Time"}
    #get any other records with same UUID and display in grid

    grid = SQLFORM.grid((db.sessions.attendee_ids.contains(user_id))&(db.sessions.uuid==session_record.uuid),
                        selectable = lambda ids : redirect(URL('default', 'remove_from_repeating', vars=dict(s_id=ids))),
                        fields=display_fields,
                        headers=field_headers,
                        searchable=False,
                        create=False,
                        editable=False,
                        deletable=False,
                        csv=False,
                       details=False)
    return locals()

@auth.requires_login()
def remove_from_repeating():
    session_ids = request.vars.s_id
    user_id = auth.user_id
    if not session_ids:
        redirect(URL('my_sessions'))
        session.flash = "Please try again. Remember to tick the boxes of sessions you want to leave"
    else:
        for id in session_ids:
            removal_status = remove_from_session(id, user_id)
        redirect(URL('my_sessions'))
        session.flash = "Sucessfully removed from selected session(s)"
    return locals()

@auth.requires_login()
def cancel_session():
    session_id = request.vars.s_id
    user_id = auth.user_id
    is_owner = check_if_owner(session_id, user_id)
    if is_owner:
        session_record = db(db.sessions.id==session_id).select().first()
        if session_record.session_active == False:
            session.flash = "Session already cancelled"
            redirect(URL('my_sessions'))
        elif session_record.repeating:
            redirect(URL('cancel_repeating_session',vars={"s_id":session_id}))
        else:
            session_record.update_record(session_active=False)
            #TODO >>>>>>>>>> SEND EMAIL UPDATE TO SIGNED UP USERS
            session.flash = "Session cancelled"
            redirect(URL('my_sessions'))
    else:
        session.flash = "You are not authorised to cancel this session."
        redirect(URL('my_sessions'))

    return locals()

@auth.requires_login()
def cancel_repeating_session():
    #GET VARS
    session_id = request.vars.s_id
    user_id = auth.user_id
    is_owner = check_if_owner(session_id, user_id)
    if is_owner:
        session_record = db(db.sessions.id==session_id).select().first()

        #layout options for grid
        display_fields = (db.sessions.title,db.sessions.start_datetime)
        field_headers = {'sessions.start_datetime':"Start Date and Time"}
        #get any other records with same UUID and display in grid

        grid = SQLFORM.grid(db.sessions.uuid==session_record.uuid,
                            selectable = lambda ids : redirect(URL('default', 'cancel_repeating', vars=dict(s_id=ids))),
                            fields=display_fields,
                            headers=field_headers,
                            searchable=False,
                            create=False,
                            editable=False,
                            deletable=False,
                            csv=False,
                            details=False
                            )
        return locals()
    
@auth.requires_login()
def cancel_repeating():
    session_ids = request.vars.s_id
    user_id = auth.user_id
    if not session_ids:
        redirect(URL('my_sessions'))
        session.flash = "Please try again. Remember to tick the boxes of sessions you want to leave"
    else:
        for id in session_ids:
            session_record = db(db.sessions.id==id).select().first()
            session_record.update_record(session_active=False)
            ###TODO SEND EMAIL UPDATE TO SIGNED UP USERS
        redirect(URL('my_sessions'))
        session.flash = "Sucessfully cancelled selected session(s)"
    return locals()

@auth.requires_login()
def enable_session():
    session_id = request.vars.s_id
    user_id = auth.user_id
    is_owner = check_if_owner(session_id, user_id)
    now = datetime.datetime.now()
    if is_owner:
        session_record = db(db.sessions.id==session_id).select().first()
        if session_record.session_active == True:
            session.flash = "Session already enabled"
            redirect(URL('my_sessions'))
        elif session_record.start_datetime < now:
            session.flash = "Session datetime is in the past. Please update this before enabling"
            redirect(URL('my_sessions'))

        else:
            session_record.update_record(session_active=True)
            #TODO >>>>>>>>>> SEND EMAIL UPDATE TO SIGNED UP USERS
            session.flash = "Session enabled"
            redirect(URL('my_sessions'))
    else:
        session.flash = "You are not authorised to enable this session."
        redirect(URL('my_sessions'))

    return locals()
    
@auth.requires_login()
def my_sessions():

    user_id = auth.user_id
    default_sort=[db.sessions.start_datetime]
#     display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.session_lead,db.sessions.title,db.sessions.start_datetime)
    display_fields_upcoming = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name)
    display_fields_previous = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name)
    display_fields_lead = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_active)
    display_fields_authored = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_active)
    field_headers = {'sessions.start_datetime':"Start Date and Time"}

    #custom links in extra columns
    def session_status(row):
        if row.session_active == True:
            return SPAN('Enabled',_class="label label-success")
        elif row.session_active == False:
            return SPAN('Disabled',_class="label label-danger")
    def button_options(row):
        if row.session_active == True:
            return A('Disable',_class="btn btn-danger",_href=URL('cancel_session',vars={"s_id":row.id}))
        elif row.session_active == False:
            return A('Enable',_class="btn btn-success",_href=URL('enable_session',vars={"s_id":row.id}))

    links_current=[dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                   dict(header="Leave",body=lambda row: A('Leave Session',_class="btn btn-danger",_href=URL('quit_session',vars={"s_id":row.id})))]
    links_previous=[dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                    dict(header="Feedback",body=lambda row: A('Provide Feedback',_class="btn btn-primary",_href=URL('feedback',vars={"s_id":row.id})))]
    links_authored=[dict(header="Status",body=lambda row: session_status(row)),
                    dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                    dict(header="Edit",body=lambda row: A('Edit',_class="btn btn-info",_href=URL('edit_session',vars={"s_id":row.id}))),
                    dict(header="Print Report",body=lambda row: A('Print Report',_class="btn btn-info",_href=URL('print_session_report',vars={"s_id":row.id}))),
                    dict(header="Change Status",body=lambda row: button_options(row))]
    links_lead=[dict(header="Status",body=lambda row: session_status(row)),
                    dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                    dict(header="Edit",body=lambda row: A('Edit',_class="btn btn-info",_href=URL('edit_session',vars={"s_id":row.id}))),
                    dict(header="Print Report",body=lambda row: A('Print Report',_class="btn btn-info",_href=URL('print_session_report',vars={"s_id":row.id}))),
                    dict(header="Change Status",body=lambda row: button_options(row))]


#     links_current=[dict(header="",body=lambda row: A('Leave Session',_class="btn btn-danger",_name="row1",_onclick="ajax('quit_session',['row1'],'target'"))]   - tried with ajax, didnt work
    #get all current sessions
    upcoming_sessions = SQLFORM.grid(
                                    (db.sessions.attendee_ids.contains(user_id))&(db.sessions.session_active==True),
                                    fields=display_fields_upcoming,
                                    links=links_current,
                                    headers=field_headers,
                                    searchable=False,
                                    create=False,
                                    editable=False,
                                    deletable=False,
                                    csv=False,
                                    details=False,
                                    sortable=False,
                                    maxtextlength=50)


    #get old sessions
    previous_sessions = SQLFORM.grid(
                                    (db.sessions.attendee_ids.contains(user_id))&(db.sessions.session_active==False),
                                    fields=display_fields_previous,
                                    links=links_previous,
                                    headers=field_headers,
                                    searchable=False,
                                    create=False,
                                    editable=False,
                                    deletable=False,
                                    csv=False,
                                    details=False,
                                    sortable=False,
                                    maxtextlength=50,)


    #get sessions that user authored
    authored_sessions = SQLFORM.grid(db.sessions.created_by==user_id,
                                    fields=display_fields_authored,
                                    links=links_authored,
                                    headers=field_headers,
                                    searchable=False,
                                    create=False,
                                    editable=False,
                                    deletable=False,
                                    csv=False,
                                    details=False,
                                    sortable=False,                                     
                                    maxtextlengths={'sessions.hospital' : 100,'sessions.title':100})

    #get sessions that user led
    leader_sessions = SQLFORM.grid(db.sessions.session_lead==user_id,
                                    fields=display_fields_lead,
                                    links=links_lead,
                                    headers=field_headers,
                                    searchable=False,
                                    create=False,
                                    editable=False,
                                    deletable=False,
                                    csv=False,
                                    details=False,
                                    sortable=False,                                   
                                    maxtextlengths={'sessions.hospital' : 100,'sessions.title':100})

    if upcoming_sessions.element('table'): upcoming_sessions.element('table')['_id'] = 'data_table_upcoming' #giving an id to the grid container for datatables JS to know what to target
    if previous_sessions.element('table'): previous_sessions.element('table')['_id'] = 'data_table_previous' #giving an id to the grid container for datatables JS to know what to target
    if leader_sessions.element('table'): leader_sessions.element('table')['_id'] = 'data_table_leader' #giving an id to the grid container for datatables JS to know what to target
    if authored_sessions.element('table'): authored_sessions.element('table')['_id'] = 'data_table_authored' #giving an id to the grid container for datatables JS to know what to target


    return dict(user_id=user_id,upcoming_sessions=upcoming_sessions,previous_sessions=previous_sessions,authored_sessions=authored_sessions,leader_sessions=leader_sessions)

@auth.requires_login()
def feedback():
    user_id = auth.user_id
    session_id = request.vars.s_id
    session_record = db(db.sessions.id==session_id).select().first()
    current_feedback_records = db(db.feedback.session_id==session_id).select()
    feedback_completed = False
    #check if the user already has a feedback record for this session
    #if so set feedback_completed to True to do allow record update rather than new record
    for record in current_feedback_records:
        if user_id == record.user_id:
            feedback_id = record.id
            feedback_record = db(db.feedback.id==feedback_id).select().first()
            feedback_completed = True

    session_form=SQLFORM(db.sessions, session_record,
             readonly=True,
             showid=False)
    current_attendee_ids = session_record.attendee_ids  #get ids of people already signed up

    if user_id not in session_record.attendee_ids:
        feedback_form = None
        session.flash = 'You can\'t leave feedback because you didn\'t sign up to this session.'
        redirect(URL('my_sessions'))
    else:
        if feedback_completed:
            session.flash = 'You already completed a feedback form. You can update it below.'
            feedback_form = SQLFORM(db.feedback, feedback_record, submit_button="Update",
                                    labels={'rate_interesting':'Interesting (1=poor,10=excellent)',
                                    'rate_relevance':'Relevance  (1=poor,10=excellent)',
                                    'rate_teaching':'Teaching Quality  (1=poor,10=excellent)',
                                    'rate_overall':'Overall Rating  (1=poor,10=excellent)',
                                    'rate_confidence':'Has your confidence with this subject improved?'},
                                    showid=False)
        else:
            feedback_form = SQLFORM(db.feedback,
                            labels={'rate_interesting':'Interesting (1=poor,10=excellent)',
                                    'rate_relevance':'Relevance  (1=poor,10=excellent)',
                                    'rate_teaching':'Teaching Quality  (1=poor,10=excellent)',
                                    'rate_overall':'Overall Rating  (1=poor,10=excellent)',
                                    'rate_confidence':'Has your confidence with this subject improved?'})
        feedback_form.vars.session_id = session_id
        feedback_form.vars.user_id = user_id

        if feedback_form.process().accepted:
            session.flash = "Thanks for your feedback!"
            redirect(URL('my_sessions'))



    return locals()

@auth.requires(lambda: auth.has_membership('hospital') or auth.has_membership('undergrad') or auth.has_membership('administrator'))
def admin_page():
    if not request.vars.db_name:
        requested_page = "access_keys"        
    else:
        requested_page = request.vars.db_name


    if requested_page=="hospitals":
        query = db.hospitals
        display_fields = (db.hospitals.hospital_name,db.hospitals.hospital_code)
        additional_links = None
    elif requested_page=="sessions":
        query = db.sessions
        additional_links=None
        display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_full,db.sessions.current_attendees,db.sessions.session_active)
        field_headers = {'sessions.start_datetime':"Start Date and Time"}

        # def session_status(row):
        #     if row.session_active == True:
        #         return SPAN('Enabled',_class="label label-success")
        #     elif row.session_active == False:
        #         return SPAN('Disabled',_class="label label-danger")
        # def button_options(row):
        #     if row.session_active == True:
        #         return A('Disable',_class="btn btn-danger",_href=URL('cancel_session',vars={"s_id":row.id}))
        #     elif row.session_active == False:
        #         return A('Enable',_class="btn btn-success",_href=URL('enable_session',vars={"s_id":row.id}))

        # additional_links=[dict(header="Status",body=lambda row: session_status(row)),
                    # dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                    # dict(header="Edit",body=lambda row: A('Edit',_class="btn btn-info",_href=URL('edit_session',vars={"s_id":row.id}))),
                    # dict(header="Print Report",body=lambda row: A('Print Report',_class="btn btn-info",_href=URL('print_session_report',vars={"s_id":row.id}))),
                    # dict(header="Change Status",body=lambda row: button_options(row))]

        # grid = SQLFORM.grid(db.sessions,
        #                             fields=display_fields,
        #                             links=additional_links,
        #                             headers=field_headers,
        #                             searchable=False,
        #                             create=False,
        #                             editable=False,
        #                             deletable=False,
        #                             csv=False,
        #                             details=False,
        #                             sortable=False,                                     
        #                             maxtextlength=50,)
    elif requested_page=="session_types":
        query = db.session_types
        display_fields = (db.session_types.id, db.session_types.session_type)
        additional_links = None

    elif requested_page=="access_keys":
        query = db.access_keys
        display_fields = (db.access_keys.unique_key,db.access_keys.key_active,db.access_keys.access_level)
        additional_links = None

    elif requested_page=="print_reports":
        query = db.sessions
        display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead_name,db.sessions.session_full,db.sessions.current_attendees)
        additional_links = [dict(header="Print Report",body=lambda row: A('Print Report',_class="btn btn-info",_href=URL('print_session_report',vars={"s_id":row.id})))]
    elif requested_page=="users":
        query = db.auth_user
        display_fields = (db.auth_user.first_name,db.auth_user.last_name,db.auth_user.email,db.auth_user.default_hospital,db.auth_user.access_key)
        additional_links = [dict(header="Print Report",body=lambda row: A('Print Report',_class="btn btn-info",_href=URL('print_user_report',vars={"u_id":row.id})))]
    

    # if requested_page != "sessions":
    grid = SQLFORM.grid(query,
                    searchable=False,
                    create=True,
                    editable=True,
                    deletable=False,
                    details=True,
                    paginate=999,
                    sortable=False,
                    csv=False,
                    user_signature=False,
                    maxtextlength=30,
                    fields=display_fields,
                    links=additional_links,
                   )
    if grid.element('table'): grid.element('table')['_id'] = 'data_table'

    return locals()

def check_if_owner(session_id, user_id):
    session_record = db(db.sessions.id==session_id).select().first()
    if session_record.session_lead == user_id:
        return True
    elif session_record.created_by == user_id:
        return True
    else:
        return False
    



def get_default_hospital(hosp_id):
    #function to get the users deafualt hosputal details from the hospitals table
    #requires a hospital ID to be passed
    #returns a dictionary with full name and 3 letter code
    row = db.hospitals[hosp_id]
#     the above line does the same as this line below but is far shorter
#     row = db(db.hospitals.id==hosp_id).select().first()
    users_hospital = {"hospital_name":row.hospital_name,"hospital_code":row.hospital_code}
    return users_hospital

def export_as_pdf():
    #will pass it text or something
    #use generic.pdf
    #implementation of pyFPDF
    #v.easy to use: https://code.google.com/p/pyfpdf/wiki/Tutorial
    return locals()

def get_me_a_pdf():
    title = "This The Doc Title"
    heading = "First Paragraph"
    text = 'bla '* 10000
    styles = getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename)
    story = []
    story.append(Paragraph(escape(title),styles["Title"]))
    story.append(Paragraph(escape(heading),styles["Heading2"]))
    story.append(Paragraph(escape(text),styles["Normal"]))
    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data

def get_name_by_id(user_id):
    user_record = db(db.auth_user.id==user_id).select().first()
    first_name = user_record.first_name
    last_name = user_record.last_name
    full_name = str(first_name +" " + last_name)
    return full_name

def get_type_by_id(session_type_id):
    type_record = db(db.session_types.id==session_type_id).select().first()
    type_name = str(type_record.session_type)
    return type_name

def get_hospital_by_id(hospital_id):
    hospital_record = db(db.hospitals.id==hospital_id).select().first()
    hospital_name = str(hospital_record.hospital_name)
    return hospital_name

def failed_auth():

    return locals()

def about():

    return locals()

def help():

    return locals()

def access_key():
    access_key = request.vars.access_key
    user_id = auth.user_id
    if access_key:
        form = "Access key processed"
        user_record = db(db.auth_user.id==user_id).select().first()
        user_record.update_record(access_key=access_key)

        #copypasted from db1.py
        user_key = access_key
        access_keys = db(db.access_keys.key_active==True).select()
        for single_key in access_keys:
            if single_key.unique_key == user_key:
                access_level = single_key.access_level
                if access_level == 'session_lead':
                    auth.add_membership(2, user_id)
                elif access_level == 'medic_user':
                    auth.add_membership(3, user_id)
                elif access_level == 'ecg_poster':
                    auth.add_membership(4, user_id)
                elif access_level == 'administrator':
                    auth.add_membership(5, user_id)
        session.flash = "Access key processed"
        redirect(URL('default','index'))

    else:
        form = SQLFORM.factory(
            Field('access_key','string'))
        if form.process().accepted:
            redirect(URL('access_key',vars={'access_key':form.vars.access_key}))
    return locals()

@auth.requires_login()
def unsubscribe_email():
    user_id = auth.user_id
    user_record = db(db.auth_user.id==user_id).select().first()
    
    user_record.update_record(email_notifications=False)
    session.flash="Ubsubscribed from emails"
    redirect(URL("user",args=['profile']))
    
    return locals()

    
    
def print_session_report():
    session_id = request.vars.s_id
    user_id = auth.user_id
    session_record = db(db.sessions.id==session_id).select().first()

    styles = getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename)
    story = []

    title = "Medboard: Session Report - " + session_record.title
    story.append(Paragraph(escape(title),styles["Title"]))

    heading = "Session Details"
    story.append(Paragraph(escape(heading),styles["Heading2"]))

    session_lead = "Session Lead: " + get_name_by_id(session_record.session_lead_name)
    story.append(Paragraph(escape(session_lead),styles["Heading4"]))

    session_type = "Session Type: " + get_type_by_id(session_record.session_type)
    story.append(Paragraph(escape(session_type),styles["Heading4"]))

    hospital_name = "Hospital Name: " + get_hospital_by_id(session_record.hospital)
    story.append(Paragraph(escape(hospital_name),styles["Heading4"]))

    session_location = "Session Location: " + (session_record.session_location)
    story.append(Paragraph(escape(session_location),styles["Heading4"]))

    date = "Date of session: " + str(session_record.start_datetime)
    story.append(Paragraph(escape(date),styles["Heading4"]))

    duration = "Duration (mins): " + str(session_record.duration)
    story.append(Paragraph(escape(duration),styles["Heading4"]))

    if session_record.description:
        description = "Description: " + session_record.description
        story.append(Paragraph(escape(description),styles["Normal"]))

    heading = "Attendee Details"
    story.append(Paragraph(escape(heading),styles["Heading2"]))


    attendees = "Attendees: " + str(session_record.current_attendees) + " / " + str(session_record.max_attendees)
    story.append(Paragraph(escape(attendees),styles["Normal"]))

    story.append(Paragraph(escape("Names"),styles["Heading5"]))
    for attendee_id in session_record.attendee_ids:
        full_name = u"\u2022" + " "  + get_name_by_id(attendee_id)
        story.append(Paragraph(escape(full_name),styles["Normal"]))

    heading = "Feedback"
    story.append(Paragraph(escape(heading),styles["Heading2"]))

    #GET FEEDBACK RECORDS
    feedback_records = db(db.feedback.session_id==session_id).select()
    total_feedback_records = len(feedback_records)

    if total_feedback_records == 0:
        story.append(Paragraph(escape("No feedback yet"),styles["Normal"]))
    else:
        #AVERAGE RATING SECTION
        story.append(Paragraph(escape("Average Ratings"),styles["Heading5"]))
        total_interesting = 0
        total_relevance = 0
        total_teaching = 0
        total_overall = 0
        for record in feedback_records:
            total_interesting += record.rate_interesting
            total_relevance += record.rate_relevance
            total_teaching += record.rate_teaching
            total_overall += record.rate_overall
        avg_interesting = total_interesting / total_feedback_records
        story.append(Paragraph(escape("-- Interesting: " + str(avg_interesting) + "/10"  ),styles["Normal"]))
        avg_relevance = total_relevance / total_feedback_records
        story.append(Paragraph(escape("-- Relevance: " + str(avg_relevance) + "/10"  ),styles["Normal"]))
        avg_teaching = total_teaching / total_feedback_records
        story.append(Paragraph(escape("-- Teaching Quality: " + str(avg_teaching) + "/10"  ),styles["Normal"]))
        avg_overall = total_overall / total_feedback_records
        story.append(Paragraph(escape("-- Overall: " + str(avg_overall) + "/10"  ),styles["Normal"]))

        #FEEDBACK COMMENTS
        story.append(Paragraph(escape("Comments"),styles["Heading5"]))
        story.append(Paragraph(escape("Positive Points"),styles["Normal"]))
        for record in feedback_records:
            if (record.positive_points) and (record.positive_points != ""):
                story.append(Paragraph(escape("-- " + record.positive_points),styles["Normal"]))

        #spacer  - change 0.1 to desired value (0.1 is like a line break)
        story.append(Spacer(1,0.1*inch))

        story.append(Paragraph(escape("Negative Points"),styles["Normal"]))
        for record in feedback_records:
            if (record.negative_points) and (record.negative_points != ""):
                story.append(Paragraph(escape("-- " + record.negative_points),styles["Normal"]))

        story.append(Spacer(1,0.1*inch))

        story.append(Paragraph(escape("Points for Improvement"),styles["Normal"]))
        for record in feedback_records:
            if (record.improvements) and (record.improvements != ""):
                story.append(Paragraph(escape("-- " + record.improvements),styles["Normal"]))


    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data

def print_user_report():
    user_id = request.vars.u_id
    user_record = db(db.auth_user.id==user_id).select().first()
    sessions_attended = db(db.sessions.attendee_ids.contains(user_id)).select()
    
    styles = getSampleStyleSheet()
    tmpfilename=os.path.join(request.folder,'private',str(uuid4()))
    doc = SimpleDocTemplate(tmpfilename)
    story = []

    title = "Medboard: User Report - " + user_record.first_name + " " + user_record.last_name
    story.append(Paragraph(escape(title),styles["Title"]))

    heading = "User Details"
    story.append(Paragraph(escape(heading),styles["Heading2"]))

    user_name = "User Name: " + get_name_by_id(user_id)
    story.append(Paragraph(escape(user_name),styles["Heading4"]))

    user_email = "Email: " + user_record.email
    story.append(Paragraph(escape(user_email),styles["Heading4"]))

    default_hospital = "Default Hospital: " + get_hospital_by_id(user_record.default_hospital)
    story.append(Paragraph(escape(default_hospital),styles["Heading4"]))

    date_of_report = "Date of report: " + str(datetime.datetime.today().strftime('%d %b %Y'))
    story.append(Paragraph(escape(date_of_report),styles["Heading4"]))


    sessions_attended_count = "Sessions Attended: "  + str(len(sessions_attended))
    story.append(Paragraph(escape(sessions_attended_count),styles["Heading2"]))


    story.append(Paragraph(escape("Session Breakdown"),styles["Heading2"]))
    session_types = db(db.session_types).select()
    for session_type in session_types:
        type_name = get_type_by_id(session_type)
        story.append(Paragraph(escape(type_name),styles["Heading3"]))

        for session in sessions_attended:
            if session.session_type == session_type:
                session_detail = session.title + " / " + session.session_location + " / " + str(session.start_datetime.strftime('%d-%m-%Y %H:%M')) + " / " + str(session.duration) + "mins / " + session.session_lead_name
                story.append(Paragraph(escape(session_detail),styles["Normal"]))
        story.append(Spacer(1,0.1*inch))

    story.append(Spacer(1,2*inch))
    doc.build(story)
    data = open(tmpfilename,"rb").read()
    os.unlink(tmpfilename)
    response.headers['Content-Type']='application/pdf'
    return data
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
