from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ZoeServer.config import getSettings

engine = create_engine(
  getSettings().db_url, connect_args={"check_same_thread": False}
)
SessionLocal = (sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False))

Base = declarative_base()

def getDB():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

from ZoeServer.vcs.svn.models import FeatureTag

# recap: (?:foo|bar) - ?: is a non capture group :)

default_featuretags = [
  # search RE, output tag replacement, optional output arg
  [r'(^\/vehicles\/[^\/]*)[\/]*', '$1', '$1'],
  [r'(^\/levels\/[^\/]*)[\/]*', '$1', '$1'],
  [r'^\/ui\/modules\/apps\/([^\/]*)[\/]*', '/uiapp/$1', '$1'],
  [r'^\/(ui)\/', '/ui', '$1'],
  [r'^\/Bin(?:32|64)\/(libbeamng\.(?:x86|x64)\.(?:dll|so))', '/physics', ''],
  [r'^(\/lua\/ge\/.*\.lua)', '/lua/ge', '$1'],
  [r'^(\/lua\/vehicle\/.*\.lua)', '/lua/v', '$1'],
  [r'^\/(Bin64|Bin32|BinLinux)\/', '/binaries', '$1'],
  [r'^\/(flowEditor)\/', '/flowgraph', '$1'],
  [r'^\/(locales)\/', '/i18n', '$1'],
  [r'^\/art\/sound\/', '/audio', '/audio'],
  [r'^\/lua\/common\/jbeam', '/jbeam'],
  [r'^\/lua\/vehicle\/jbeam', '/jbeam'],
]

def insertDefaultData():
  db: Session = next(getDB())
  db.begin()
  for f in default_featuretags:
    ft = FeatureTag()
    ft.regexp = f[0]
    ft.output = f[1]
    db.add(ft)
  db.commit()


def setupDB():
  tables_existing = engine.dialect.has_table(engine.connect(), "svn_repos")

  Base.metadata.create_all(bind=engine)

  if not tables_existing:
    insertDefaultData()
