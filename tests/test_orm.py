import pytest
import models.models as model
from sqlalchemy import text

def test_mapper_can_add_user(session):

    session.execute(text("INSERT INTO user (phone_number) VALUES "
                    '("+34600000000"),'
                    '("+34600000001"),'
                    '("+34600000002")'
                ))
    
    expected = [model.User(1,phone_number="+34600000000"),
                model.User(2,phone_number="+34600000001"),
                model.User(3,phone_number="+34600000002")]
    

    assert session.query(model.User).all() == expected