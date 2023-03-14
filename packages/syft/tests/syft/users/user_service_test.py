# stdlib
from typing import List
from typing import Tuple

# third party
import pytest
from result import Err
from result import Ok

# syft absolute
from syft.core.node.new.context import AuthedServiceContext
from syft.core.node.new.context import NodeServiceContext
from syft.core.node.new.context import UnauthedServiceContext
from syft.core.node.new.credentials import SyftVerifyKey
from syft.core.node.new.credentials import UserLoginCredentials
from syft.core.node.new.response import SyftError
from syft.core.node.new.response import SyftSuccess
from syft.core.node.new.uid import UID
from syft.core.node.new.user import ServiceRole
from syft.core.node.new.user import User
from syft.core.node.new.user import UserPrivateKey
from syft.core.node.new.user import UserView


@pytest.fixture
def authed_context(admin_user, worker):
    context = AuthedServiceContext(credentials=admin_user.verify_key, node=worker)
    return context


@pytest.fixture
def node_context(worker):
    context = NodeServiceContext(node=worker)
    return context


@pytest.fixture
def unauthed_context(guest_create_user, worker):
    login_credentials = UserLoginCredentials(
        email=guest_create_user.email, password=guest_create_user.password
    )
    context = UnauthedServiceContext(login_credentials=login_credentials, node=worker)
    return context


def test_userservice_create_when_user_exists(
    monkeypatch, user_service, authed_context, guest_create_user
):
    def mock_get_by_email(email):
        return Ok(guest_create_user.to(User))

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    response = user_service.create(authed_context, guest_create_user)
    assert isinstance(response, SyftError)
    expected_error_message = (
        f"User already exists with email: {guest_create_user.email}"
    )
    assert expected_error_message == response.message


def test_userservice_create_error_on_get_by_email(
    monkeypatch, user_service, authed_context, guest_create_user
):
    def mock_get_by_email(email):
        return Err(f"No user exists with given email: {email}")

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    response = user_service.create(authed_context, guest_create_user)
    assert isinstance(response, SyftError)
    expected_error_message = mock_get_by_email(guest_create_user.email).err()
    assert response.message == expected_error_message


def test_userservice_create_success(
    monkeypatch, user_service, authed_context, guest_create_user
):
    def mock_get_by_email(email):
        return Ok(None)

    expected_user = guest_create_user.to(User)
    expected_output = expected_user.to(UserView)

    def mock_set(user):
        return Ok(expected_user)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    monkeypatch.setattr(user_service.stash, "set", mock_set)
    response = user_service.create(authed_context, guest_create_user)
    assert isinstance(response, UserView)
    assert response.to_dict() == expected_output.to_dict()


def test_userservice_create_error_on_set(
    monkeypatch, user_service, authed_context, guest_create_user
):
    def mock_get_by_email(email):
        return Ok(None)

    expected_error_msg = "Failed to set user."

    def mock_set(user):
        return Err(expected_error_msg)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    monkeypatch.setattr(user_service.stash, "set", mock_set)
    response = user_service.create(authed_context, guest_create_user)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_view_error_on_get_by_uid(
    monkeypatch, user_service, authed_context
):
    uid_to_view = UID()
    expected_error_msg = f"Failed to get uid: {uid_to_view}"

    def mock_get_by_uid(uid):
        return Err(expected_error_msg)

    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)
    response = user_service.view(authed_context, uid_to_view)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_view_user_not_exists(monkeypatch, user_service, authed_context):
    uid_to_view = UID()
    expected_error_msg = f"No user exists for given: {uid_to_view}"

    def mock_get_by_uid(uid):
        return Ok(None)

    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)
    response = user_service.view(authed_context, uid_to_view)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_view_user_success(
    monkeypatch, user_service, authed_context, guest_user
):
    uid_to_view = guest_user.id
    expected_output = guest_user.to(UserView)

    def mock_get_by_uid(uid):
        return Ok(guest_user)

    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)
    response = user_service.view(authed_context, uid_to_view)
    assert isinstance(response, UserView)
    assert response == expected_output


def test_userservice_get_all_success(
    monkeypatch, user_service, authed_context, guest_user, admin_user
):
    expected_output = [guest_user, admin_user]

    def mock_get_all():
        return Ok(expected_output)

    monkeypatch.setattr(user_service.stash, "get_all", mock_get_all)
    response = user_service.get_all(authed_context)
    assert isinstance(response, List)
    assert len(response) == len(expected_output)
    assert response == expected_output


def test_userservice_get_all_error(monkeypatch, user_service, authed_context):
    expected_output_msg = "No users exists"

    def mock_get_all():
        return Err("")

    monkeypatch.setattr(user_service.stash, "get_all", mock_get_all)
    response = user_service.get_all(authed_context)
    assert isinstance(response, SyftError)
    assert response.message == expected_output_msg


def test_userservice_search(monkeypatch, user_service, authed_context, guest_user):
    def mock_find_all(**kwargs):
        for key, _ in kwargs.items():
            if hasattr(guest_user, key):
                return Ok([guest_user])
            return Err("Invalid kwargs")

    monkeypatch.setattr(user_service.stash, "find_all", mock_find_all)

    expected_output = [guest_user.to(UserView)]

    # Search via id
    response = user_service.search(authed_context, id=guest_user.id)
    assert isinstance(response, List)
    assert response == expected_output

    # Search via email
    response = user_service.search(authed_context, email=guest_user.email)
    assert isinstance(response, List)
    assert response == expected_output

    # Search via name
    response = user_service.search(authed_context, name=guest_user.name)
    assert isinstance(response, List)
    assert response == expected_output

    # Search via verify_key
    response = user_service.search(authed_context, verify_key=guest_user.verify_key)
    assert isinstance(response, List)
    assert response == expected_output

    # Search via multiple kwargs
    response = user_service.search(
        authed_context, name=guest_user.name, email=guest_user.email
    )
    assert isinstance(response, List)
    assert response == expected_output


def test_userservice_search_with_invalid_kwargs(user_service, authed_context):
    # Search with invalid kwargs
    response = user_service.search(authed_context, role=ServiceRole.GUEST)
    assert isinstance(response, SyftError)
    assert "Invalid Search parameters" in response.message


def test_userservice_update_get_by_uid_fails(
    monkeypatch, user_service, authed_context, update_user
):
    random_uid = UID()
    get_by_uid_err_msg = "Invalid UID"
    expected_error_msg = (
        f"Failed to find user with UID: {random_uid}. Error: {get_by_uid_err_msg}"
    )

    def mock_get_by_uid(uid):
        return Err(get_by_uid_err_msg)

    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)

    response = user_service.update(
        authed_context, uid=random_uid, user_update=update_user
    )
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_update_no_user_exists(
    monkeypatch, user_service, authed_context, update_user
):
    random_uid = UID()
    expected_error_msg = f"No user exists for given UID: {random_uid}"

    def mock_get_by_uid(uid):
        return Ok(None)

    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)

    response = user_service.update(
        authed_context, uid=random_uid, user_update=update_user
    )
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_update_success(
    monkeypatch, user_service, authed_context, guest_user, update_user
):
    def mock_get_by_uid(uid):
        return Ok(guest_user)

    def mock_update(user):
        guest_user.name = update_user.name
        guest_user.email = update_user.email
        return Ok(guest_user)

    monkeypatch.setattr(user_service.stash, "update", mock_update)
    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)

    resultant_user = user_service.update(
        authed_context, uid=guest_user.id, user_update=update_user
    )
    assert isinstance(resultant_user, UserView)
    assert resultant_user.email == update_user.email
    assert resultant_user.name == update_user.name


def test_userservice_update_fails(
    monkeypatch, user_service, authed_context, guest_user, update_user
):
    update_error_msg = "Failed to reach server."
    expected_error_msg = (
        f"Failed to update user with UID: {guest_user.id}. Error: {update_error_msg}"
    )

    def mock_get_by_uid(uid):
        return Ok(guest_user)

    def mock_update(user):
        return Err(update_error_msg)

    monkeypatch.setattr(user_service.stash, "update", mock_update)
    monkeypatch.setattr(user_service.stash, "get_by_uid", mock_get_by_uid)

    response = user_service.update(
        authed_context, uid=guest_user.id, user_update=update_user
    )
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_delete_failure(monkeypatch, user_service, authed_context):
    id_to_delete = UID()
    expected_error_msg = f"No user exists for given id: {id_to_delete}"

    def mock_delete_by_uid(uid):
        return Err(expected_error_msg)

    monkeypatch.setattr(user_service.stash, "delete_by_uid", mock_delete_by_uid)

    response = user_service.delete(context=authed_context, uid=id_to_delete)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_delete_success(monkeypatch, user_service, authed_context):
    id_to_delete = UID()
    expected_output = SyftSuccess(message=f"ID: {id_to_delete} deleted")

    def mock_delete_by_uid(uid):
        return Ok(expected_output)

    monkeypatch.setattr(user_service.stash, "delete_by_uid", mock_delete_by_uid)

    response = user_service.delete(context=authed_context, uid=id_to_delete)
    assert isinstance(response, SyftSuccess)
    assert response == expected_output


def test_userservice_user_verify_key(monkeypatch, user_service, guest_user):
    def mock_get_by_email(email):
        return Ok(guest_user)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)

    response = user_service.user_verify_key(email=guest_user.email)
    assert response == guest_user.verify_key


def test_userservice_user_verify_key_invalid_email(monkeypatch, user_service, faker):
    email = faker.email()
    expected_output = SyftError(message=f"No user with email: {email}")

    def mock_get_by_email(email):
        return Err("No user found")

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)

    response = user_service.user_verify_key(email=email)
    assert response == expected_output


def test_userservice_admin_verify_key_error(monkeypatch, user_service):
    expected_output = "Invalid Role"

    def mock_get_by_role(role):
        return Err(expected_output)

    monkeypatch.setattr(user_service.stash, "get_by_role", mock_get_by_role)

    response = user_service.admin_verify_key()
    assert isinstance(response, SyftError)
    assert response.message == expected_output


def test_userservice_admin_verify_key_success(monkeypatch, user_service, admin_user):
    def mock_get_by_role(role):
        return Ok(admin_user)

    monkeypatch.setattr(user_service.stash, "get_by_role", mock_get_by_role)

    response = user_service.admin_verify_key()
    assert isinstance(response, SyftVerifyKey)
    assert response == admin_user.verify_key


def test_userservice_register_user_exists(
    monkeypatch, user_service, node_context, guest_create_user
):
    def mock_get_by_email(email):
        return Ok(guest_create_user)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    expected_error_msg = f"User already exists with email: {guest_create_user.email}"

    response = user_service.register(node_context, guest_create_user)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_register_error_on_get_email(
    monkeypatch, user_service, node_context, guest_create_user
):
    expected_error_msg = "Failed to get email"

    def mock_get_by_email(email):
        return Err(expected_error_msg)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)

    response = user_service.register(node_context, guest_create_user)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_register_success(
    monkeypatch, user_service, node_context, guest_create_user, guest_user
):
    def mock_get_by_email(email):
        return Ok(None)

    def mock_set(user):
        return Ok(guest_user)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    monkeypatch.setattr(user_service.stash, "set", mock_set)

    expected_msg = f"{guest_create_user.email} User successfully registered !!!"
    expected_private_key = guest_user.to(UserPrivateKey)

    response = user_service.register(node_context, guest_create_user)
    assert isinstance(response, Tuple)

    syft_success_response, user_private_key = response
    assert isinstance(syft_success_response, SyftSuccess)
    assert syft_success_response.message == expected_msg

    assert isinstance(user_private_key, UserPrivateKey)
    assert user_private_key == expected_private_key


def test_userservice_register_set_fail(
    monkeypatch, user_service, node_context, guest_create_user
):
    def mock_get_by_email(email):
        return Ok(None)

    expected_error_msg = "Failed to connect to server."

    def mock_set(user):
        return Err(expected_error_msg)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    monkeypatch.setattr(user_service.stash, "set", mock_set)

    response = user_service.register(node_context, guest_create_user)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_exchange_credentials(
    monkeypatch, user_service, unauthed_context, guest_user
):
    def mock_get_by_email(email):
        return Ok(guest_user)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    expected_user_private_key = guest_user.to(UserPrivateKey)

    response = user_service.exchange_credentials(unauthed_context)
    assert isinstance(response, UserPrivateKey)
    assert response == expected_user_private_key


def test_userservice_exchange_credentials_invalid_user(
    monkeypatch, user_service, unauthed_context, guest_user
):
    def mock_get_by_email(email):
        return Ok(None)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    expected_error_msg = (
        f"No user exists with {guest_user.email} and supplied password."
    )

    response = user_service.exchange_credentials(unauthed_context)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg


def test_userservice_exchange_credentials_get_email_fails(
    monkeypatch, user_service, unauthed_context, guest_user
):
    get_by_email_error = "Failed to connect to server."

    def mock_get_by_email(email):
        return Err(get_by_email_error)

    monkeypatch.setattr(user_service.stash, "get_by_email", mock_get_by_email)
    expected_error_msg = f"Failed to retrieve user with {guest_user.email} with error: {get_by_email_error}"

    response = user_service.exchange_credentials(unauthed_context)
    assert isinstance(response, SyftError)
    assert response.message == expected_error_msg
