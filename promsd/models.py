from peewee import Model, SqliteDatabase, TextField, IntegerField, ForeignKeyField
import config

db = SqliteDatabase(config.DATABASE)


# Database models
class BaseModel(Model):
    class Meta:
        database = db


class Job(BaseModel):
    name = TextField()
    port = IntegerField()


class Target(BaseModel):
    host = TextField()
    job = ForeignKeyField(Job, backref='jobs')


class Label(BaseModel):
    target = ForeignKeyField(Target, backref='labels')
    label = TextField()
    value = TextField()

    class Meta:
        indexes = (
            # create a unique on target/label
            (('target', 'label',), True),
        )
