"""WebSocket handlers for real-time features."""
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import current_user
from app import app, db
from models import ChatRoom, ChatMessage, ChatMember, User
from datetime import datetime
import json
from sqlalchemy.exc import SQLAlchemyError
from schemas import ChatMessageSchema
from marshmallow.exceptions import ValidationError

socketio = SocketIO(app, cors_allowed_origins="*")

# Active users in video calls
active_calls = {}

def handle_db_error(e):
    """Handle database errors."""
    db.session.rollback()
    emit('error', {'message': 'Database error occurred'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    if not current_user.is_authenticated:
        disconnect()
        return False
    
    try:
        current_user.status = 'online'
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        emit('status_change', {
            'user_id': current_user.id,
            'status': 'online',
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
    except SQLAlchemyError as e:
        handle_db_error(e)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    if current_user.is_authenticated:
        try:
            current_user.status = 'offline'
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            
            # Clean up any active calls
            for room_id in active_calls:
                if current_user.id in active_calls[room_id]:
                    active_calls[room_id].remove(current_user.id)
                    emit('user_left_call', {
                        'user_id': current_user.id,
                        'username': current_user.username
                    }, room=room_id)
            
            emit('status_change', {
                'user_id': current_user.id,
                'status': 'offline',
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)
        except SQLAlchemyError as e:
            handle_db_error(e)

@socketio.on('join_room')
def handle_join_room(data):
    """Handle room joining."""
    try:
        room_id = data['room_id']
        room = ChatRoom.query.get(room_id)
        
        if not room:
            emit('error', {'message': 'Room not found'})
            return
        
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        # Check if user is member of private room
        if room.is_private:
            member = ChatMember.query.filter_by(
                room_id=room_id,
                user_id=current_user.id
            ).first()
            if not member:
                emit('error', {'message': 'Access denied'})
                return
        
        join_room(room_id)
        
        # Add user to room if not already a member
        member = ChatMember.query.filter_by(
            room_id=room_id,
            user_id=current_user.id
        ).first()
        
        if not member:
            member = ChatMember(
                room_id=room_id,
                user_id=current_user.id
            )
            db.session.add(member)
            db.session.commit()
        
        # Get recent messages
        recent_messages = ChatMessage.query.filter_by(room_id=room_id)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(50).all()
        
        # Get active users in room
        active_users = ChatMember.query.filter_by(room_id=room_id)\
            .join(User)\
            .filter(User.status == 'online')\
            .all()
        
        emit('room_joined', {
            'room_id': room_id,
            'messages': [{
                'id': msg.id,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'sender_id': msg.sender_id,
                'sender_name': msg.sender.username,
                'message_type': msg.message_type,
                'file_url': msg.file_url
            } for msg in reversed(recent_messages)],
            'active_users': [{
                'user_id': member.user.id,
                'username': member.user.username,
                'status': member.user.status
            } for member in active_users]
        })
        
        emit('user_joined', {
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_id)
    except SQLAlchemyError as e:
        handle_db_error(e)
    except KeyError:
        emit('error', {'message': 'Invalid request data'})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle room leaving."""
    try:
        room_id = data['room_id']
        leave_room(room_id)
        emit('user_left', {
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_id)
    except KeyError:
        emit('error', {'message': 'Invalid request data'})

@socketio.on('new_message')
def handle_new_message(data):
    """Handle new message in chat."""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        # Validate message data
        schema = ChatMessageSchema()
        validated_data = schema.load(data)
        
        message = ChatMessage(
            content=validated_data['content'],
            room_id=validated_data['room_id'],
            sender_id=current_user.id,
            message_type=validated_data.get('message_type', 'text'),
            file_url=validated_data.get('file_url')
        )
        db.session.add(message)
        db.session.commit()
        
        emit('message', {
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id,
            'sender_name': current_user.username,
            'message_type': message.message_type,
            'file_url': message.file_url
        }, room=validated_data['room_id'])
    except SQLAlchemyError as e:
        handle_db_error(e)
    except ValidationError as e:
        emit('error', {'message': str(e.messages)})

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator."""
    if current_user.is_authenticated:
        try:
            room_id = data['room_id']
            emit('user_typing', {
                'user_id': current_user.id,
                'username': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
        except KeyError:
            emit('error', {'message': 'Invalid request data'})

@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle stop typing indicator."""
    if current_user.is_authenticated:
        try:
            room_id = data['room_id']
            emit('user_stop_typing', {
                'user_id': current_user.id,
                'username': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
        except KeyError:
            emit('error', {'message': 'Invalid request data'})

# Video call signaling with enhanced features
@socketio.on('join_call')
def handle_join_call(data):
    """Handle joining video call."""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        room_id = data['room_id']
        
        # Initialize room in active_calls if not exists
        if room_id not in active_calls:
            active_calls[room_id] = set()
        
        # Add user to active calls
        active_calls[room_id].add(current_user.id)
        
        # Get all active users in call
        active_users = [{
            'user_id': user_id,
            'username': User.query.get(user_id).username
        } for user_id in active_calls[room_id] if user_id != current_user.id]
        
        # Notify others in room
        emit('user_joined_call', {
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room_id)
        
        # Send active users to joining user
        emit('active_call_users', {
            'users': active_users
        })
    except KeyError:
        emit('error', {'message': 'Invalid request data'})
    except SQLAlchemyError as e:
        handle_db_error(e)

@socketio.on('leave_call')
def handle_leave_call(data):
    """Handle leaving video call."""
    if not current_user.is_authenticated:
        return
    
    try:
        room_id = data['room_id']
        if room_id in active_calls and current_user.id in active_calls[room_id]:
            active_calls[room_id].remove(current_user.id)
            
            # Remove room if empty
            if not active_calls[room_id]:
                del active_calls[room_id]
            
            emit('user_left_call', {
                'user_id': current_user.id,
                'username': current_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_id)
    except KeyError:
        emit('error', {'message': 'Invalid request data'})

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    """Handle ICE candidate for WebRTC."""
    if not current_user.is_authenticated:
        return
    
    try:
        target_id = data['target_id']
        candidate = data['candidate']
        emit('ice_candidate', {
            'candidate': candidate,
            'user_id': current_user.id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=target_id)
    except KeyError:
        emit('error', {'message': 'Invalid request data'})

@socketio.on('offer')
def handle_offer(data):
    """Handle WebRTC offer."""
    if not current_user.is_authenticated:
        return
    
    try:
        target_id = data['target_id']
        offer = data['offer']
        emit('offer', {
            'offer': offer,
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=target_id)
    except KeyError:
        emit('error', {'message': 'Invalid request data'})

@socketio.on('answer')
def handle_answer(data):
    """Handle WebRTC answer."""
    if not current_user.is_authenticated:
        return
    
    try:
        target_id = data['target_id']
        answer = data['answer']
        emit('answer', {
            'answer': answer,
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room=target_id)
    except KeyError:
        emit('error', {'message': 'Invalid request data'})

# Error handling
@socketio.on_error()
def error_handler(e):
    """Handle WebSocket errors."""
    print(f'WebSocket error: {str(e)}')
    emit('error', {'message': 'An error occurred'})
