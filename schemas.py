"""Validation schemas for GhostSec application."""
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    """User validation schema."""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=20)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        load_only=True
    )
    confirm_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        load_only=True
    )

class LabConfigSchema(Schema):
    """Lab configuration validation schema."""
    name = fields.Str(required=True)
    description = fields.Str()
    type = fields.Str(
        required=True,
        validate=validate.OneOf(['vulnerability', 'network', 'malware', 'crypto'])
    )
    difficulty = fields.Str(
        validate=validate.OneOf(['beginner', 'intermediate', 'advanced'])
    )
    timeout = fields.Int(missing=3600)
    max_attempts = fields.Int(missing=3)

class ChallengeSubmissionSchema(Schema):
    """Challenge submission validation schema."""
    lab_id = fields.Int(required=True)
    challenge_id = fields.Int(required=True)
    solution = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)

class ReportSchema(Schema):
    """Lab report validation schema."""
    lab_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    completion_time = fields.Int()
    score = fields.Int()
    findings = fields.List(fields.Dict())
    recommendations = fields.List(fields.Str())

# Social feature schemas
class PostSchema(Schema):
    """Forum post validation schema."""
    title = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200)
    )
    content = fields.Str(
        required=True,
        validate=validate.Length(min=10)
    )
    category_id = fields.Int(required=True)
    use_markdown = fields.Bool(missing=False)

class CommentSchema(Schema):
    """Forum comment validation schema."""
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000)
    )
    post_id = fields.Int(required=True)

class ProjectSchema(Schema):
    """Project validation schema."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=100)
    )
    description = fields.Str(
        required=True,
        validate=validate.Length(min=10)
    )
    repository_url = fields.URL(allow_none=True)
    is_public = fields.Bool(missing=True)
    technologies = fields.List(fields.Str(), missing=[])

class ChatRoomSchema(Schema):
    """Chat room validation schema."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50)
    )
    description = fields.Str(validate=validate.Length(max=200))
    is_private = fields.Bool(missing=False)
    max_members = fields.Int(missing=50)

class ChatMessageSchema(Schema):
    """Chat message validation schema."""
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000)
    )
    room_id = fields.Int(required=True)
    message_type = fields.Str(
        validate=validate.OneOf(['text', 'image', 'file']),
        missing='text'
    )
    file_url = fields.URL(allow_none=True)

def validate_password_match(data):
    """Validate that password and confirm_password match."""
    if data.get('password') != data.get('confirm_password'):
        raise ValidationError('Passwords must match')

# Add password validation to UserSchema
UserSchema.validators = [validate_password_match]
