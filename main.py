import sqlite3
from sqlite3 import Error
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Connect to SQLite database
database_file = "blog.db"


class BlogPost(BaseModel):
  title: str
  content: str


def create_connection():
  conn = None
  try:
    conn = sqlite3.connect(database_file)
    return conn
  except Error as e:
    print(e)
  return conn


def create_table():
  conn = create_connection()
  if conn is not None:
    try:
      query = """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            );
            """
      conn.execute(query)
      conn.commit()
    except Error as e:
      print(e)
    finally:
      conn.close()


@app.on_event("startup")
async def startup_event():
  create_table()


# CORS Configuration
origins = [
  "https://work-wine.vercel.app",  # Replace with your frontend URL
  # Add more allowed origins as needed
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/")
def read_root():
  return {"message": "Welcome to the blog page!"}


@app.get("/posts")
def get_all_posts():
  conn = create_connection()
  if conn is not None:
    try:
      query = "SELECT * FROM posts"
      cursor = conn.execute(query)
      posts = cursor.fetchall()
      return posts
    except Error as e:
      print(e)
    finally:
      conn.close()
  return []


# Rest of your code...


@app.get("/posts/{post_id}")
def get_post(post_id: int):
  conn = create_connection()
  if conn is not None:
    try:
      query = "SELECT * FROM posts WHERE id = ?"
      cursor = conn.execute(query, (post_id, ))
      post = cursor.fetchone()
      if post:
        return post
      else:
        raise HTTPException(status_code=404, detail="Post not found")
    except Error as e:
      print(e)
    finally:
      conn.close()


@app.post("/posts")
def create_post(post: BlogPost):
  conn = create_connection()
  if conn is not None:
    try:
      query = "INSERT INTO posts (title, content) VALUES (?, ?)"
      conn.execute(query, (post.title, post.content))
      conn.commit()
      post_id = conn.lastrowid
      return {"message": "Post created successfully", "post_id": post_id}
    except Error as e:
      print(e)
    finally:
      conn.close()
  return {"message": "Failed to create post"}


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
  conn = create_connection()
  if conn is not None:
    try:
      query = "DELETE FROM posts WHERE id = ?"
      conn.execute(query, (post_id, ))
      conn.commit()
      if conn.total_changes == 1:
        return {"message": f"Post '{post_id}' deleted successfully"}
      else:
        raise HTTPException(status_code=404, detail="Post not found")
    except Error as e:
      print(e)
    finally:
      conn.close()
  return {"message": "Failed to delete post"}
