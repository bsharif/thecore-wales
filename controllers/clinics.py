def index():
    redirect(URL('clinics','browse'))

    return locals()

def browse():
    #visible by anyone
    #lists ongoing sessions - default is ALL unless logged in in which case default is auth_user.default_hospital
    #view should filter and sort etc.
    if auth.user:
        
        default_hospital = get_default_hospital(auth.user.default_hospital)
        display_name = default_hospital['hospital_name']

    hospital_rows = db(db.hospitals).select()
    hospitals_list = []
    for row in hospital_rows:
        hospitals_list.append(row.hospital_code)

    selected_hospital = request.args(0)
    if (not selected_hospital) and (auth.user):
        selected_hospital = auth.user.default_hospital
        db_selection = (db.sessions.session_active==True)&(db.sessions.hospital==selected_hospital)
        current_hospital = get_default_hospital(selected_hospital)
        current_hospital = current_hospital['hospital_code']
        display_fields = (db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)
    elif (not selected_hospital) and (not auth.user):
        selected_hospital = 'ALL'
        db_selection = db.sessions.session_active==True
        current_hospital = 'ALL'
        display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)
    elif selected_hospital == 'ALL':
        db_selection = db.sessions.session_active==True
        display_fields = (db.sessions.hospital,db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)
        current_hospital = 'ALL'
    else:
        hosp_id = db(db.hospitals.hospital_code==selected_hospital).select().first()
        selected_hospital = hosp_id.id
        db_selection = (db.sessions.session_active==True)&(db.sessions.hospital==selected_hospital)
        current_hospital = get_default_hospital(selected_hospital)
        current_hospital = current_hospital['hospital_code']
        display_fields = (db.sessions.session_type,db.sessions.title,db.sessions.start_datetime,db.sessions.session_lead,db.sessions.session_full,db.sessions.current_attendees,db.sessions.attendee_ids)

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
                        maxtextlengths={'sessions.hospital':50},
                        links=[dict(header="Status",body=lambda row: status_label(row)),
                               dict(header="Details",body=lambda row: A('View',_class="btn btn-default",_href=URL('view_session',vars={"s_id":row.id}))),
                               dict(header="Sign Up",body=lambda row: sign_up_button(row))],
                       headers={'sessions.start_datetime':"Start Date and Time",'sessions.duration':'Duration (mins)'}
                       )

    if grid.element('table'): grid.element('table')['_id'] = 'data_table' #giving an id to the grid container for datatables JS to know what to target

    return locals()

def clinics_sidebar():
    return locals()



def get_default_hospital(hosp_id):
    #function to get the users deafualt hosputal details from the hospitals table
    #requires a hospital ID to be passed
    #returns a dictionary with full name and 3 letter code
    row = db.hospitals[hosp_id]
#     the above line does the same as this line below but is far shorter
#     row = db(db.hospitals.id==hosp_id).select().first()
    users_hospital = {"hospital_name":row.hospital_name,"hospital_code":row.hospital_code}
    return users_hospital