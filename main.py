from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import db_models
from database import SessionLocal, engine
from sqlalchemy.orm import Session


app = FastAPI()

# Create all database tables
db_models.Base.metadata.create_all(bind=engine)

# Dependency to get a database connection
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Pydantic model for Book
class Book(BaseModel):
    title: str = Field(min_length=1, max_length=99)
    author: str = Field(min_length=1, max_length=99)
    description: str = Field(min_length=1, max_length=999)
    rating: int = Field(gt=0, le=6) # 1-5 stars

class BookResponse(Book):
    id: int



@app.get("/", response_model=list[BookResponse])
def read_api(db: Session = Depends(get_db)):
    return db.query(db_models.Books).all()

@app.post("/", response_model=BookResponse)
def create_book(book: Book, db: Session = Depends(get_db)):
    book_model = db_models.Books(title=book.title, author=book.author, 
                                 description=book.description, rating=book.rating)
    db.add(book_model)
    db.commit()
    db.refresh(book_model)
    return book_model # Return the SQLAlchemy model

@app.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: Book, db: Session = Depends(get_db)):
    book_model = db.query(db_models.Books).filter(db_models.Books.id == book_id).first()
    
    if book_model is None: # guard clause
        raise HTTPException(status_code=404, detail="Book not found")

    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating
    db.add(book_model)
    db.commit()
    db.refresh(book_model)
    return book_model
    

@app.delete("/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    affected_rows = db.query(db_models.Books).filter(db_models.Books.id == book_id).delete()
    if affected_rows == 0:  # No rows were deleted
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.commit()
    return {"detail": "Book deleted successfully"}



