"""
Base service class with common functionality
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.core.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Base service class with common CRUD operations"""
    
    def __init__(self, model: ModelType):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {e}")
            raise DatabaseError(f"Failed to retrieve {self.model.__name__}")
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filters"""
        try:
            query = db.query(self.model)
            
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to retrieve {self.model.__name__} list")
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            db.rollback()
            raise DatabaseError(f"Failed to create {self.model.__name__}")
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update an existing record"""
        try:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            db.rollback()
            raise DatabaseError(f"Failed to update {self.model.__name__}")
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete a record by ID"""
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            db.rollback()
            raise DatabaseError(f"Failed to delete {self.model.__name__}")
    
    def exists(self, db: Session, **filters) -> bool:
        """Check if a record exists with given filters"""
        try:
            query = db.query(self.model)
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.first() is not None
        except Exception as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to check {self.model.__name__} existence")
