# -*- coding: utf-8 -*-
from uuid import uuid4
#hospitals DATABASE IS DEFINED IN DB.PY (JUST BEFORE AUTH.DB) to allow inclusion of 'extra field' on sign up

#table to store session types
#eg. Theatre, Clinic, etc..
db.define_table('session_types',
                Field('session_type','string'),
                auth.signature,
                format = '%(session_type)s')

#both the hospitals table and session_types table need to be defined before the session table
#MAYBE make some of these fields REQUIRED (eg Title, but not description!)


                        
db.define_table('sessions',
                Field('hospital','reference hospitals'), #default is set in the function that creates the form - eg. new_session()
                Field('session_type','reference session_types'), 

                Field('session_lead','reference auth_user', default=auth.user_id,readable=False, writable=False),
                Field('session_lead_name','string',requires=IS_NOT_EMPTY()),
                Field('session_lead_email','string',requires=IS_EMAIL(error_message="Invalid email address")),
                #author field has been superseded by auth.signature (much more versatile and automatic)
                #Field('author','reference auth_user', default=auth.user_id,writable=False,readable=False),   #need to make add this in production >> readable=False, writable=False
                Field('title','string'),                    #apparently its good practice to define a length for string fields, maybe at production time?
                Field('description','text'),
                Field('session_location','string'),
                Field('start_datetime','datetime'), #datepicker has been updated to match in web2py_ajax
                Field('duration','integer'),
                Field('max_attendees','integer',),
                Field('current_attendees','integer',default=0,readable=False,writable=False),
                Field('attendee_ids','list:reference auth_user',default=[],readable=False,writable=False),   #need to make add this in production >> readable=False, writable=False 
                                                                 #**OR** just maybe not display it? does read/write prevent it being changed from the controller?
                Field('repeating','boolean',readable=False,writable=False),
                Field('session_active','boolean',default=True, readable=False,writable=False),     
                Field('session_full','boolean', default=False,writable=False,readable=False),
                Field('uuid',length=64,default=uuid4(),readable=False,writable=False),
                auth.signature,
                format = '%(id)s')

#VALIDATORS FOR SESSIONS TABLE
db.sessions.hospital.requires = IS_EMPTY_OR(IS_IN_DB(db,'hospitals.id','%(hospital_name)s'))
# db.sessions.session_type.requires
                #below line adds extra features to the SQLFORM (limits etc) but breaks the SQLFORM.grid by displaying IDs (format function doesn't work hmm!)
                #,requires=IS_IN_DB(db,'session_types.id','%(session_type)s',zero=T('Choose one'),error_message="Please choose an option")  
restrict_lead_query = ((db.auth_user.id == db.auth_membership.user_id)&
           ((db.auth_membership.group_id == 2)|(db.auth_membership.group_id == 3)))
db.sessions.session_lead.requires=IS_IN_DB(db(restrict_lead_query), db.auth_user.id, '%(first_name)s %(last_name)s (%(email)s)')

db.sessions.title.requires = IS_NOT_EMPTY()

db.sessions.start_datetime.requires = IS_DATETIME(format=T('%d-%m-%y %H:%M'),error_message='Must be dd-mm-yy HH:MM')
db.sessions.duration.requires = IS_INT_IN_RANGE(5,500,error_message="Enter a time between 5 and 500 minutes")
db.sessions.max_attendees.requires = IS_NOT_EMPTY() 




db.define_table('feedback',
                Field('session_id','reference sessions',readable=False,writable=False),
                Field('user_id','reference auth_user',default=auth.user_id,readable=False,writable=False),
                Field('rate_interesting','integer',requires=IS_INT_IN_RANGE(1,11)),
                Field('rate_relevance','integer',requires=IS_INT_IN_RANGE(1,11)),
                Field('rate_teaching','integer',requires=IS_INT_IN_RANGE(1,11)),
                Field('rate_overall','integer',requires=IS_INT_IN_RANGE(1,11)),
                Field('rate_confidence','integer',requires=IS_IN_SET(['Yes','No','Unsure'])),
                Field('positive_points','text'),
                Field('negative_points','text'),
                Field('improvements','text'),
                auth.signature)

#set format to display user names when referencing auth.id
db.auth_user._format = '%(first_name)s %(last_name)s'

#************************************
#SWITCH SESSIONS TO INACTIVE IF DATE HAS PASSED
#Get current datetime using datetime module.
#Get all session still marked as session_active=True
#If current datetime greater than datetime of session then set session_active to False
from datetime import datetime
now = datetime.now()
rows = db(db.sessions.session_active==True).select()
for row in rows:
    if row.start_datetime < now:
        db.sessions[row.id] = dict(session_active=False)  #this is shortcut DAL code to update a record/field

#************************************
#CHECK IF USER HAS PROVIDED A VALID ACCESS KEY AND PROCESS IT
#KEYS ARE STORED IN db.access_keys
#EACH KEY IS LINKED TO AN ACCESS LEVEL
#IF THE KEY PROVIDED MATCHES ONE IN db.access_keys THEN... 
#ASSIGN USER THE APPROPRIATE ACCESS LEVEL
#WRITTEN AS A FUNCTION TO ALLOW USE AFTER INITAL SIGN UP (eg. if user did not have key initally)
def grant_new_access():
    if auth.user_id:
        user_id = auth.user_id
        user_key = auth.user.access_key
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

grant_new_access()
#****************************************


####************AUTOCOMLETE widget for locations!
#::::::COMMENTS
# First part is working with creating an autocomplete widget
# However it only allows users to enter locations that have been previously created/entered into db
# Needs to be modified to allow entry of new items/items not in the autocomplete
# If that is fixed then the second section works well - it loops through entered locations and adds them to the locations db for future use
# :::::::::::::::::DISABLED FOR NOW
#::::::::::::::::::::::::::::::::::::::::::::
#PART ONE
# db.define_table('locations',
#                 Field('name','string'))
# db.sessions.session_location.widget = SQLFORM.widgets.autocomplete(request, db.locations.name, id_field=db.locations.id)

#PART TWO
# session_rows = db(db.sessions).select()
# location_rows = db(db.locations).select()
# location_found = False
# for session_row in session_rows:
#     location_name = session_row.session_location
#     for location_row in location_rows:
#         if location_name == location_row.name:
#             location_found = True
#     if not location_found:
#         db.locations.insert(name=location_name)
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#to drop a table....
# db.table_name.drop()
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

#TODO On Browse, display full session too??
#TODO Update session report with feedbacks - include confidence improved..!
#TODO Update tables to display in DataTables format (and on repeating sessions etc)
#TODO Fix Browse with default hospital display (if no arg ALL then displaying default hospital but in ALL type format)
#TODO Mark 'active'/'not active' if dates changes from previous to new
#TODO Mark uneditable if in past
#TODO Admin management page
#TODO 2 more print out styles - certificate, student report (incl from admin page)
#TODO About page
# TODO fix ordering disabler if not displaying holpital column - on BROWSE.html
