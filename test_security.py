import uuid
from app.security import hash_password, verify_password, create_access_token, decode_access_token, new_refresh_token, hash_refresh_token

def test_password_hash():
    p = "A-long-test-password-123!"
    h = hash_password(p)
    assert h != p
    assert verify_password(p, h)
    assert not verify_password("wrong", h)

def test_access_token():
    user_id = uuid.uuid4()
    token = create_access_token(user_id)
    assert decode_access_token(token) == user_id

def test_refresh_token_hash():
    token = new_refresh_token()
    assert hash_refresh_token(token) != token
    assert hash_refresh_token(token) == hash_refresh_token(token)
