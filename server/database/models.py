import datetime

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    Check,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)

from server.database.connect import Database


class BaseModel(Model):
    class Meta:
        database = Database()


class Image(BaseModel):
    img_id = AutoField()
    name = TextField()  # 存储图片的名称（如 xxx）
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "images"


class User(BaseModel):
    username = CharField(unique=True)
    password_hash = CharField()
    avatar = ForeignKeyField(Image, null=False, column_name="avatar", backref="users")
    session_token = CharField(unique=True, null=True)
    token_expires_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "users"


class MoodType(BaseModel):
    name = CharField(unique=True)
    color_code = CharField(null=True)
    element_type = CharField(null=True)

    class Meta:  # type: ignore
        table_name = "mood_types"


class Letter(BaseModel):
    user = ForeignKeyField(User, backref="letters")
    content = TextField(null=True)
    image = ForeignKeyField(Image, null=True, column_name="image", backref="letters")
    latitude = FloatField()
    longitude = FloatField()
    location = CharField()
    likes_count = IntegerField(default=0)
    view_count = IntegerField(default=0)
    is_public = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "letters"
        indexes = ((("latitude", "longitude"), False),)


class MoodEntry(BaseModel):
    user = ForeignKeyField(User, backref="mood_entries")
    mood_type = ForeignKeyField(MoodType, backref="mood_entries")
    log_date = DateField()
    is_public = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "mood_entries"
        indexes = (
            (("user", "log_date"), True),
            (("log_date", "user"), False),
        )


class AIFeedback(BaseModel):
    mood_entry = ForeignKeyField(MoodEntry, backref="ai_feedback", unique=True)
    review_content = TextField()
    rec_activity = TextField(null=True)
    rec_food = TextField(null=True)
    rec_location = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "ai_feedback"


class ChatSession(BaseModel):
    user = ForeignKeyField(User, backref="chat_sessions")
    session_type = CharField()  # 'daily' or 'long-term'
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "chat_sessions"
        constraints = [Check("session_type IN ('daily', 'long-term')")]


class ChatMessage(BaseModel):
    session = ForeignKeyField(ChatSession, backref="messages")
    role = CharField()  # 'user' or 'assistant'
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "chat_messages"
        constraints = [Check("role IN ('user', 'assistant')")]


class SchoolMoodSummary(BaseModel):
    mood_name = CharField()
    color_code = CharField()
    element_type = CharField()
    count = IntegerField()
    summary_date = DateField()

    class Meta:  # type: ignore
        table_name = "v_school_mood_summary"
        primary_key = False


class PublicLetterFlow(BaseModel):
    id = IntegerField()
    content = TextField()
    image_url = CharField()
    latitude = FloatField()
    longitude = FloatField()
    location = CharField()
    likes_count = IntegerField()
    view_count = IntegerField()
    created_at = DateTimeField()
    username = CharField()
    avatar_url = CharField()

    class Meta:  # type: ignore
        table_name = "v_public_letter_flow"
        primary_key = False
