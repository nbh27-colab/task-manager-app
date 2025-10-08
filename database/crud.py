from sqlalchemy.orm import Session


def get_all(db: Session, model):
    return db.query(model).all()


def get_by_id(db: Session, model, item_id: int):
    return db.query(model).filter(model.id == item_id).first()


def create_item(db: Session, model, item_data):
    db_item = model(**item_data.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, model, item_id: int, item_data):
    db_item = db.query(model).filter(model.id == item_id).first()
    if db_item:
        for field, value in item_data.dict().items():
            setattr(db_item, field, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_item(db: Session, model, item_id: int):
    db_item = db.query(model).filter(model.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item