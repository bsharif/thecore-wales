# -*- coding: utf-8 -*-
    
# *****************************
# FEATURE PLANS
# *****************************
#Testing server to github

# 1. View Sessions
#     No login req
#     Filter by: Hospital, Type
#     Sort by: Duration, Start, Spaces

# 2. Sign Up to sessions
#     Need user account
#     Users should pick default hospital
# Everyone should automatically be member of student group by default
# For example use auth.settings.everybody_group_id = 5 to make every new user a member of group 5 on sign-up

    
# 3. View My Sessions
#     Ability for users to view sessions they have signed up to
#     Links to provide feedback
#     Remove self from sessions
    
# 4. Add New Sessions
#     Req. a Doctor / Admin account - if Dr account then author is user by default
#     Ability for Admin account to set session lead as a doctor already in db
#     To PROGRAMATICALLY add users to different groups see: http://web2py.com/books/default/chapter/29/09/access-control#Authorization
#     Summary: Use auth.add_membership(group_id, user_id) to add user_id to group_id (if not user_id then default is current logged in user

# 5. Add Repeating Sessions
#     Seperate data entry form
#     Initally minimal area, to enter all the basics
#     Then next page shows multiple boxes to set multiple date/times
#     Then need a function to insert copies of the record for the dates entered
#     SET THE REPEATING boolean to TRUE
    
# 6. Edit sessions
#     Can edit time/date and other details
#     And can delete session entirely
#     Send email notification for all changes? Or only if deleted?
#     Or give user the option to send email update?
    
# 6. Doctor Account
#     Ability to recieve feedback
#     Email notifications
#     Print/Export PDF of feedback
    
# 7. Feedback page
#     Linked to from the MySessions page for users
#     Need to find an example of feedback page
#     Advanced feature - allow users to design their own / choose from multiple feedback sheets
    
# 8. Admin account
#     Manage all sessions
#     Add users to sessions manually - email notifications too
#     Print reports per user etc (PDF)
# Can use SQLFORM.grid to manage other users (and accounts too)
    
# 9. Hospital account
#     Display list of wards and opening times so student can find more learning oppurtunities
