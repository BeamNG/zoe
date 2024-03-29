from sqlalchemy import Column, Integer, String, DateTime, func
from typing import Optional

from ZoeServer.database import Base

"""
class Test(Base):
  __tablename__ = 'tests'

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True, unique=True)
  description = Column(String)

  #default_runtime_environment_id = Column(Integer, ForeignKey("runtime_environments.id"))
  #test_subject_id = Column(Integer, ForeignKey("test_subjects.id"))
  #parent_test_id = Column(Integer, ForeignKey("tests.id"), nullable=True)


class TestTrigger(Base):
  __tablename__ = 'test_triggers'

  id = Column(Integer, primary_key=True, index=True)
  test_id = Column(Integer, ForeignKey("tests.id"))
  #test = relationship("Test", back_populates="tests")

  type = Column(String, index=True) # svn commit filename, comment, manual
  arg1 = Column(String) # filename or comment regexp


class Platform(Base):
  __tablename__ = 'platforms'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True, unique=True) #Windows, Linux...
  updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
  created_at = Column(DateTime, server_default=func.now())

  __mapper_args__ = {"eager_defaults": True}

class Runtime(Base):
  __tablename__ = 'runtimes'
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True, unique=True)

  type = Column(String) # SVN, GIT, STEAM, ZIP, URL
  arg1 = Column(String) # SVN URL, etc
  arg2 = Column(String) # SVN revision, etc

class TestResult(Base):
  __tablename__ = 'test_results'
  id = Column(Integer, primary_key=True, index=True)

  test_id = Column(Integer, ForeignKey("tests.id"))

  overall_result = Column(String) # success, fail

class TestResultArtifact(Base):
  __tablename__ = 'test_result_artifact'

  id = Column(Integer, primary_key=True, index=True)

  test_result_id = Column(Integer, ForeignKey("test_results.id"))

  type = Column(String) # file, json, image, etc
  arg1 = Column(String) # file path, json data, ...


class TestActions(Base):
  __tablename__ = 'test_actions'
  id = Column(Integer, primary_key=True, index=True)

  test_id = Column(Integer, ForeignKey("tests.id"))
  #test = relationship("Test", back_populates="tests")

  type = Column(String) # file, json, image, etc
  arg1 = Column(String) # file path, json data, ...

"""

class ClientData(Base):
  __tablename__ = 'client_data'

  id: Optional[int] = Column(Integer, default=None, primary_key=True, index=True, autoincrement=True)

  # client related
  nodeName: String = Column(String)
  machineUUID: Optional[String] = Column(String, default=None)

  # message related
  type: Optional[String] = Column(String, default=None)
  loglevel: Optional[String] = Column(String, default=None)
  message: Optional[String] = Column(String, default=None)

  # task related
  build_id: Optional[String] = Column(String, default=None)
  task_id: Optional[String] = Column(String, default=None)

  created_at: Optional[String] = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
  extra: Optional[String] = Column(String, default=None)
