import pytest
from util.hashing import get_password_hash, verify_password


@pytest.mark.parametrize(
    'password',
    [
        'Aa123456!',
        'Русскиеbukv1',
        '',
    ]
)
def test_password_success(password):
    hashed_password = get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert verify_password(password, hashed_password)

@pytest.mark.parametrize(
    "password, wrong_password",
    [
        ("Aa123456!", "Aa456!"),
        ("Aa123456!", "123456!"),
    ],
)
def test_password_wrong(password, wrong_password):
    hashed_password = get_password_hash(wrong_password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert verify_password(password, hashed_password) is False
