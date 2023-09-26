import os
from unittest.mock import patch

from constants import TEMP_FILES_PATH
from managers.complaint import ComplaintManager
from models import RoleType, Complaint, TransactionModel, State
from services.s3 import S3Service
from services.wise import WiseService
from tests.base import TestRESTAPIBase, generate_token, mock_uuid
from tests.facroty import UserFactory, ComplaintFactory, TransactionFactory
from utils.helpers import encoded_photo


class TestComplaintSchema(TestRESTAPIBase):
    def test_required_fields_missing_raises(self):
        user = UserFactory(role=RoleType.complainer)
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {}
        res = self.client.post("/complaints", headers=headers, json=data)

        assert res.status_code == 400
        assert res.json == {
            "message": {
                'amount': ['Missing data for required field.'],
                'description': ['Missing data for required field.'],
                'photo': ['Missing data for required field.'],
                'photo_extension': ['Missing data for required field.'],
                'title': ['Missing data for required field.'],
            }
        }

    def test_amount_is_less_than_100(self):
        user = UserFactory(role=RoleType.complainer)
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {

            "description": "test desc",
            "photo_extension": "png",
            "photo": encoded_photo,
            "title": "Test",

        }

        data["amount"] = 55
        res = self.client.post("/complaints", headers=headers, json=data)
        assert res.status_code == 400
        assert res.json == {
            'message': {'amount': ['Must be greater than or equal to 100.']}
        }


class TestComplaints(TestRESTAPIBase):
    @patch("uuid.uuid4", mock_uuid)
    @patch.object(
        ComplaintManager,
        "issue_transaction",
        return_velue=None,
    )
    @patch.object(S3Service, "upload_file", return_value="some_url.com")
    def test_create_complaints(self, mock_s3_upload, mocked_transaction):
        complaints = Complaint.query.all()
        assert len(complaints) == 0

        transactions = TransactionModel.query.all()
        assert len(transactions) == 0

        user = UserFactory(role=RoleType.complainer)
        token = generate_token(user)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {
            "description": "test desc",
            "photo_extension": "png",
            "photo": encoded_photo,
            "title": "Test",
            "amount": 505
        }

        res = self.client.post("/complaints", headers=headers, json=data)

        complaints = Complaint.query.all()
        assert len(complaints) == 1
        assert res.status_code == 201
        assert res.json["photo_url"] == "some_url.com"
        assert res.json["status"] == State.pending.value

        expected_photo_name = f"{mock_uuid()}.{data['photo_extension']}"
        expected_file_path = os.path.join(TEMP_FILES_PATH, expected_photo_name)
        mock_s3_upload.assert_called_once_with(expected_file_path, expected_photo_name)

        full_name = f"{user.first_name} {user.last_name}"
        mocked_transaction.assert_called_once_with(
            data["amount"],
            full_name,
            user.iban,
            complaints[0].id
        )

    @patch.object(WiseService, "fund_transfer", return_value=None)
    def test_approver_complaints(self, mock_fund_transfer):
        approver = UserFactory(role=RoleType.approver)
        complainer = UserFactory()

        token = generate_token(approver)

        complaint = ComplaintFactory(user_id=complainer.id)
        transaction = TransactionFactory(complaint_id=complaint.id)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        complaints = Complaint.query.all()
        assert len(complaints) == 1
        assert complaints[0].status == State.pending

        url = f"/complaints/{complaint.id}/approve"

        res = self.client.get(url, headers=headers)
        assert res.status_code == 200

        complaints = Complaint.query.all()
        assert len(complaints) == 1
        assert complaints[0].status == State.approved

        mock_fund_transfer.assert_called_once_with(transaction.transfer_id)
