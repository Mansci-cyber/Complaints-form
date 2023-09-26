from resources.auth import RegisterResource, LoginResource
from resources.complaint import ComplaintsResource, ComplaintApproveResource, ComplaintRejectResource

routes = (
    (RegisterResource, "/register"),
    (LoginResource, "/login"),
    (ComplaintsResource, "/complaints"),
    # to do home work single resource for delete
    (ComplaintApproveResource, "/complaints/<int:pk>/approve"),
    (ComplaintRejectResource, "/complaints/<int:pk>/reject")
)
