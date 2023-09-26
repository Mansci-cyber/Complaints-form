from models import RoleType
from tests.base import generate_token, TestRESTAPIBase
from tests.facroty import UserFactory


class TestLoginAndAuthorizationRequired(TestRESTAPIBase):
    def test_auth_is_required(self):
        all_guarded_urls = [
            ("GET", "/complaints"),
            ("POST", "/complaints"),
            ("GET", "/complaints/1/approve"),
            ("GET", "/complaints/1/reject"),
        ]
        for method, url in all_guarded_urls:
            if method == "GET":
                res = self.client.get(url)
            elif method == "POST":
                res = self.client.post(url)
            elif method == "PUT":
                res = self.client.put(url)
            else:
                res = self.client.delete(url)

            assert res.status_code == 401
            assert res.json == {'message': 'Invalid or missing token'}

    def test_permission_required_create_complaint_requires_complainer(self):
        user = UserFactory(role=RoleType.approver)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.post("/complaints", headers=headers)
        assert res.status_code == 403
        assert res.json == {"message": "You do not have permission!"}

        user = UserFactory(role=RoleType.admin)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.post("/complaints", headers=headers)
        assert res.status_code == 403
        assert res.json == {"message": "You do not have permission!"}

    def test_permission_required_approve_reject_complaint_requires_approvers(self):
        user = UserFactory(role=RoleType.approver)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/complaints/1/approve", headers=headers)
        assert res.status_code == 403
        assert res.json == {"message": "You do not have permission!"}

        res = self.client.get("/complaints/1/reject", headers=headers)
        assert res.status_code == 403
        assert res.json == {"message": "You do not have permission!"}

        user = UserFactory(role=RoleType.complainer)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/complaints/1/approve", headers=headers)
        assert res.status_code == 403
        assert res.json == {"message": "You do not have permission!"}

        res = self.client.get("/complaints/1/reject", headers=headers)
        assert res.status_code == 403
        assert res.json == {"message": "You do not have permission!"}
