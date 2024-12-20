"""Initial migration

Revision ID: 7d1725c0f14a
Create Date: 2024-10-30 04:27:00.838394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d1725c0f14a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('HardCodeAgent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('predefined_type', sa.Enum('replace_text', name='predefinedtype'), nullable=True),
    sa.Column('logic', sa.String(), nullable=True),
    sa.Column('arguments', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Model',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Prompt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Graph',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('model_id', sa.Integer(), nullable=False),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('n', sa.Integer(), nullable=False),
    sa.Column('frequency_penalty', sa.Float(), nullable=False),
    sa.Column('presence_penalty', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['model_id'], ['Model.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('UserToken',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['Client.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'client_id')
    )
    op.create_table('Agent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_type', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('start_log_message', sa.String(), nullable=True),
    sa.Column('finish_log_message', sa.String(), nullable=True),
    sa.Column('graph_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['graph_id'], ['Graph.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Running',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('graph_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'FINISHED', 'FAILED', name='runningstatus'), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['graph_id'], ['Graph.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('AIAgent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prompt_id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('settings_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['Client.id'], ),
    sa.ForeignKeyConstraint(['id'], ['Agent.id'], ),
    sa.ForeignKeyConstraint(['prompt_id'], ['Prompt.id'], ),
    sa.ForeignKeyConstraint(['settings_id'], ['Settings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('CopyingAgent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('base_agent_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['base_agent_id'], ['Agent.id'], ),
    sa.ForeignKeyConstraint(['id'], ['Agent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('DocumentTemplate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('filename', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['Agent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ChatAgent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['AIAgent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('CriticAgent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('criticized_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['criticized_id'], ['AIAgent.id'], ),
    sa.ForeignKeyConstraint(['id'], ['AIAgent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('running_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['running_id'], ['Running.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['DocumentTemplate.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('InputDocuments',
    sa.Column('document_template_id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['Agent.id'], ),
    sa.ForeignKeyConstraint(['document_template_id'], ['DocumentTemplate.id'], ),
    sa.PrimaryKeyConstraint('document_template_id', 'agent_id')
    )
    op.create_table('RequiredDocument',
    sa.Column('document_template_id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['Agent.id'], ),
    sa.ForeignKeyConstraint(['document_template_id'], ['DocumentTemplate.id'], ),
    sa.PrimaryKeyConstraint('document_template_id', 'agent_id')
    )
    op.create_table('Stopword',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['ChatAgent.id'], ),
    sa.PrimaryKeyConstraint('id', 'agent_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Stopword')
    op.drop_table('RequiredDocument')
    op.drop_table('InputDocuments')
    op.drop_table('Document')
    op.drop_table('CriticAgent')
    op.drop_table('ChatAgent')
    op.drop_table('DocumentTemplate')
    op.drop_table('CopyingAgent')
    op.drop_table('AIAgent')
    op.drop_table('Running')
    op.drop_table('Agent')
    op.drop_table('UserToken')
    op.drop_table('Settings')
    op.drop_table('Graph')
    op.drop_table('User')
    op.drop_table('Prompt')
    op.drop_table('Model')
    op.drop_table('HardCodeAgent')
    op.drop_table('Client')
    # ### end Alembic commands ###
