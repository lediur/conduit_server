from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite connects to file-based database along the path "data/conduit.db"
# engine = create_engine('sqlite:///data/conduit.db', convert_unicode=True)
engine = create_engine('sqlite:///data/conduit.db', convert_unicode=True)

db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base(bind=engine)
Base.query = db.query_property()

def init_db():
  # Import relevant modules
  import app.models
  
  # Drop all tables
  print 'Drop all tables'
  Base.metadata.drop_all(bind=engine)

  # Create all tables
  print 'Create all tables'
  Base.metadata.create_all(bind=engine)