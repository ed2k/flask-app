# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


# Alias common SQLAlchemy names
relationship = relationship

Base = declarative_base()
Model = Base

