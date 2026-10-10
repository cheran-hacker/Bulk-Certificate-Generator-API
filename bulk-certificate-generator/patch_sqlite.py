import os

env_path = '.env'
with open(env_path, 'r') as f:
    env_content = f.read()

env_content = env_content.replace('postgresql+psycopg2://postgres:postgres@db:5432/certificates', 'sqlite:///./certificates.db')

with open(env_path, 'w') as f:
    f.write(env_content)

session_path = 'app/db/session.py'
with open(session_path, 'r') as f:
    session = f.read()

if 'connect_args=' not in session:
    session = session.replace(
        'engine = create_engine(settings.database_url, pool_pre_ping=True)',
        'engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {})'
    )
    with open(session_path, 'w') as f:
        f.write(session)

os.system('alembic upgrade head')
