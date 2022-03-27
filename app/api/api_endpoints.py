# starting with api endpoints

# the endpoints are defined according to: 
# https://lucid.app/lucidchart/b45b7344-4270-404c-a4c0-877bf494d4cd/edit?invitationId=inv_f2d14e7e-1d22-4665-bf60-711bf47dd067&page=0_0#


# /api/init-assessment : needs gitusername and assessment_tracker details
# uses: 
# app.crud.verify_member # takes in username returns bool # returns userid
# app.crud.initialize_assessment_tracker:
#     initialize assessment , uses username/userid and assessment data like assessment id and commit
# returns bool : True if member verified and assessment initialized

# /api/verify-member : I think endpoints should not be explicitly be made if a simple function can replace it.
#        not needed necessarly can be replaced by app.crud.verify_member


# /api/init-check: 
# /api/update
# /api/approve-assessment
# /api/assign-reviewers
# /api/confirm-reviewer
# /api/deny-reviewer
# /api/check-assessment-status