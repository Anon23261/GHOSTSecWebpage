"""add new learning environments

Revision ID: add_new_learning_environments
Revises: initial
Create Date: 2024-01-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_new_learning_environments'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to User table
    op.add_column('user', sa.Column('malware_points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('pentest_points', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('cpp_points', sa.Integer(), nullable=False, server_default='0'))

    # Create MalwareAnalysisLab table
    op.create_table('malware_analysis_lab',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('malware_type', sa.String(length=50), nullable=False),
        sa.Column('tools_required', sa.Text()),
        sa.Column('environment_setup', sa.Text(), nullable=False),
        sa.Column('analysis_steps', sa.Text(), nullable=False),
        sa.Column('safety_precautions', sa.Text(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('estimated_time', sa.Integer()),
        sa.Column('prerequisites', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create PenTestLab table
    op.create_table('pen_test_lab',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('target_setup', sa.Text(), nullable=False),
        sa.Column('tools_required', sa.Text()),
        sa.Column('methodology', sa.Text(), nullable=False),
        sa.Column('objectives', sa.Text(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('estimated_time', sa.Integer()),
        sa.Column('prerequisites', sa.Text()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create CPPExercise table
    op.create_table('cpp_exercise',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('starter_code', sa.Text()),
        sa.Column('solution', sa.Text(), nullable=False),
        sa.Column('test_cases', sa.Text(), nullable=False),
        sa.Column('memory_constraints', sa.Text()),
        sa.Column('security_focus', sa.Text()),
        sa.Column('points', sa.Integer(), nullable=False),
        sa.Column('hints', sa.Text()),
        sa.Column('order', sa.Integer()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create association tables
    op.create_table('malware_lab_completion',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lab_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('time_taken', sa.Integer()),
        sa.ForeignKeyConstraint(['lab_id'], ['malware_analysis_lab.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'lab_id')
    )

    op.create_table('pentest_lab_completion',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lab_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('time_taken', sa.Integer()),
        sa.ForeignKeyConstraint(['lab_id'], ['pen_test_lab.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'lab_id')
    )

    op.create_table('cpp_exercise_completion',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['cpp_exercise.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'exercise_id')
    )

def downgrade():
    # Drop association tables
    op.drop_table('cpp_exercise_completion')
    op.drop_table('pentest_lab_completion')
    op.drop_table('malware_lab_completion')

    # Drop main tables
    op.drop_table('cpp_exercise')
    op.drop_table('pen_test_lab')
    op.drop_table('malware_analysis_lab')

    # Remove columns from User table
    op.drop_column('user', 'cpp_points')
    op.drop_column('user', 'pentest_points')
    op.drop_column('user', 'malware_points')
