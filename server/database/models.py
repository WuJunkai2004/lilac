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
    id = AutoField()
    username = CharField(unique=True)
    password_hash = CharField()
    avatar = ForeignKeyField(Image, null=True, column_name="avatar", backref="users")
    session_token = CharField(unique=True, null=True)
    token_expires_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "users"


class MoodType(BaseModel):
    id = AutoField()
    name = CharField(unique=True)
    color_code = CharField(null=True)
    element_type = CharField(null=True)

    class Meta:  # type: ignore
        table_name = "mood_types"


class Letter(BaseModel):
    id = AutoField()
    user_id = ForeignKeyField(User, backref="letters")
    content = TextField(null=True)
    image = ForeignKeyField(Image, null=True, column_name="image", backref="letters")
    mood_type = ForeignKeyField(
        MoodType, null=True, column_name="mood_type", backref="letters"
    )
    latitude = FloatField()
    longitude = FloatField()
    location = CharField()
    likes_count = IntegerField(default=0)
    view_count = IntegerField(default=0)
    is_public = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "letters"
        indexes = ((("user_id",), False),)
        constraints = [Check("content IS NOT NULL OR image IS NOT NULL")]


class LetterLike(BaseModel):
    id = AutoField()
    user_id = ForeignKeyField(User, backref="letter_likes")
    letter_id = ForeignKeyField(Letter, backref="likes")

    class Meta:  # type: ignore
        table_name = "letter_likes"
        indexes = ((("user_id", "letter_id"), True),)


class MoodEntry(BaseModel):
    id = AutoField()
    user_id = ForeignKeyField(User, backref="mood_entries")
    mood_type_id = ForeignKeyField(MoodType, backref="mood_entries")
    log_date = DateField()
    is_public = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "mood_entries"
        indexes = ((("user_id", "log_date"), True),)


class AIFeedback(BaseModel):
    id = AutoField()
    mood_entry_id = ForeignKeyField(MoodEntry, backref="ai_feedback", unique=True)
    review_content = TextField()
    rec_activity = TextField(null=True)
    rec_food = TextField(null=True)
    rec_location = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "ai_feedback"


class ChatSession(BaseModel):
    id = AutoField()
    user_id = ForeignKeyField(User, backref="chat_sessions")
    session_type = CharField()  # 'daily' or 'long-term'
    conversation_id = CharField(null=True, unique=True)  # Store ID from Agent service
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:  # type: ignore
        table_name = "chat_sessions"
        indexes = ((("id", "conversation_id"), True),)
        constraints = [Check("session_type IN ('daily', 'long-term')")]


class ChatMessage(BaseModel):
    id = AutoField()
    session_id = ForeignKeyField(ChatSession, backref="messages")
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
    content = TextField(null=True)
    image_url = CharField(null=True)
    mood_id = IntegerField(null=True)
    latitude = FloatField()
    longitude = FloatField()
    location = CharField()
    likes_count = IntegerField()
    view_count = IntegerField()
    created_at = DateTimeField()
    username = CharField()
    avatar_url = CharField(null=True)

    class Meta:  # type: ignore
        table_name = "v_public_letter_flow"
        primary_key = False


class UserProfile(BaseModel):
    user_id = IntegerField()
    username = CharField()
    avatar = IntegerField(null=True)
    letter_count = IntegerField()
    total_likes = IntegerField()
    mood_day_count = IntegerField()

    class Meta:  # type: ignore
        table_name = "v_user_profile"
        primary_key = False
