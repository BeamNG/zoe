from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from ZoeServer.database import Base


class SVNRepo(Base):
  __tablename__ = "svn_repos"

  name = Column(String, primary_key=True, index=True)
  uuid = Column(String) # uuid
  last_commit_revision = Column(Integer) # commit_revision
  last_commit_date = Column(DateTime) # commit_date
  last_commit_author = Column(String) # username
  members = Column(JSON)

  commits = relationship("SVNRepoCommit", back_populates="repo")

'''
LogEntry(
  date=datetime.datetime(2021, 10, 8, 14, 51, 2, 259009, tzinfo=tzutc()),
  msg='new libbeamng binaries, no gamengine rebuild required. windows10.dev.2019.v142',
  revision=84529,
  author='jenkins_bot2',
  changelist=[
    ('M', '/trunk/Bin32/libbeamng.x86.dll'),
    ('M', '/trunk/Bin64/libbeamng.x64.dll')
  ]
)
'''
class FeatureTag(Base):
  __tablename__ = "feature_tags"
  id = Column(Integer, primary_key=True, index=True)
  regexp = Column(String)
  output = Column(String)

  #commits = relationship("SVNRepoCommit", back_populates="features")

class SVNRepoCommit(Base):
  __tablename__ = "svn_repo_commits"

  id = Column(String, primary_key=True, index=True, unique=True)
  repo_name = Column(String, ForeignKey("svn_repos.name"))

  date = Column(DateTime)
  msg = Column(String)
  revision = Column(Integer)
  author = Column(String)
  changelist = Column(JSON)

  #features = relationship("FeatureTag", back_populates="commits")

  branch = Column(String, nullable=True)

  repo = relationship("SVNRepo", back_populates="commits")

