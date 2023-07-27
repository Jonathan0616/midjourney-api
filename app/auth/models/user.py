from tortoise import fields

from app.utils.db import BaseModel


class User(BaseModel):
    # main
    phone = fields.CharField(max_length=20, unique=True)
    hashed_password = fields.CharField(max_length=100, nullable=False)

    # profile
    nickname = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=50, null=True)
    avatar = fields.CharField(max_length=255, null=True)
    gender = fields.IntField(
        default=0, description="1->male 2->female 0->secret"
    )
    hobbies = fields.CharField(max_length=255, null=True)
    motto = fields.CharField(max_length=255, null=True)
    birthdate = fields.DateField()
    last_login_datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        table = "user"
