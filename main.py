from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Temporary storage for blog posts
posts = []


class BlogPost(BaseModel):
  title: str
  content: str


@app.get("/")
def read_root():
  return {"message": "Welcome to the blog page!"}


@app.get("/posts")
def get_all_posts():
  return posts


@app.get("/posts/{post_id}")
def get_post(post_id: int):
  if post_id < len(posts):
    return posts[post_id]
  else:
    raise HTTPException(status_code=404, detail="Post not found")


@app.post("/posts")
def create_post(post: BlogPost):
  posts.append(post)
  return {"message": "Post created successfully"}


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
  if post_id < len(posts):
    deleted_post = posts.pop(post_id)
    return {"message": f"Post '{deleted_post.title}' deleted successfully"}
  else:
    raise HTTPException(status_code=404, detail="Post not found")


# Configure CORS middleware
origins = [
  "http://localhost:5173",  # Replace with your React application URL
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
