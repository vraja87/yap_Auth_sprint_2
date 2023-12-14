"""added oauth

Revision ID: 0422eea0c42d
Revises: 7312d2679153
Create Date: 2023-12-12 18:19:17.194212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0422eea0c42d'
down_revision: Union[str, None] = '7312d2679153'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oauth2_users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('oauth_id', sa.String(), nullable=False),
    sa.Column('provider', sa.String(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['content.users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='content'
    )
    op.create_index(op.f('ix_content_oauth2_users_id'), 'oauth2_users', ['id'], unique=False, schema='content')
    op.drop_constraint('login_histories_user_id_fkey', 'login_histories', schema='content', type_='foreignkey')
    op.create_foreign_key(None, 'login_histories', 'users', ['user_id'], ['id'], source_schema='content', referent_schema='content', ondelete='CASCADE')
    op.drop_constraint('refresh_tokens_user_id_fkey', 'refresh_tokens', schema='content', type_='foreignkey')
    op.create_foreign_key(None, 'refresh_tokens', 'users', ['user_id'], ['id'], source_schema='content', referent_schema='content', ondelete='CASCADE')
    op.drop_constraint('user_roles_user_id_fkey', 'user_roles', schema='content', type_='foreignkey')
    op.drop_constraint('user_roles_role_id_fkey', 'user_roles', schema='content', type_='foreignkey')
    op.create_foreign_key(None, 'user_roles', 'users', ['user_id'], ['id'], source_schema='content', referent_schema='content', ondelete='CASCADE')
    op.create_foreign_key(None, 'user_roles', 'roles', ['role_id'], ['id'], source_schema='content', referent_schema='content', ondelete='CASCADE')
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True), schema='content')
    op.add_column('users', sa.Column('is_oauth2', sa.Boolean(), nullable=True), schema='content')
    op.add_column('users', sa.Column('credentials_updated', sa.Boolean(), nullable=True), schema='content')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'credentials_updated', schema='content')
    op.drop_column('users', 'is_oauth2', schema='content')
    op.drop_column('users', 'email', schema='content')
    op.drop_constraint(None, 'user_roles', schema='content', type_='foreignkey')
    op.drop_constraint(None, 'user_roles', schema='content', type_='foreignkey')
    op.create_foreign_key('user_roles_role_id_fkey', 'user_roles', 'roles', ['role_id'], ['id'], source_schema='content', referent_schema='content')
    op.create_foreign_key('user_roles_user_id_fkey', 'user_roles', 'users', ['user_id'], ['id'], source_schema='content', referent_schema='content')
    op.drop_constraint(None, 'refresh_tokens', schema='content', type_='foreignkey')
    op.create_foreign_key('refresh_tokens_user_id_fkey', 'refresh_tokens', 'users', ['user_id'], ['id'], source_schema='content', referent_schema='content')
    op.drop_constraint(None, 'login_histories', schema='content', type_='foreignkey')
    op.create_foreign_key('login_histories_user_id_fkey', 'login_histories', 'users', ['user_id'], ['id'], source_schema='content', referent_schema='content')
    op.drop_index(op.f('ix_content_oauth2_users_id'), table_name='oauth2_users', schema='content')
    op.drop_table('oauth2_users', schema='content')
    # ### end Alembic commands ###