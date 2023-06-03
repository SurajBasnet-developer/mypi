import pymongo
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Connect to MongoDB
client = MongoClient('mongodb+srv://surajdev:surajdev999@cluster0.9gj5ogk.mongodb.net/test?retryWrites=true&w=majority')
db = client['test']
collection = db['blog']


class BlogPost(BaseModel):
    title: str
    content: str


@app.on_event("startup")
async def startup_event():
    # Create an index on the 'title' field for faster search queries
    collection.create_index("title")


@app.get("/")
def read_root():
    return {"message": "Welcome to the blog page!"}


@app.get("/posts")
def get_all_posts():
    posts = collection.find()
    return list(posts)


@app.get("/posts/{post_id}")
def get_post(post_id: str):
    post = collection.find_one({"_id": pymongo.ObjectId(post_id)})
    if post:
        return post
    else:
        raise HTTPException(status_code=404, detail="Post not found")


@app.post("/posts")
def create_post(post: BlogPost):
    post_data = {"title": post.title, "content": post.content}
    result = collection.insert_one(post_data)
    post_id = str(result.inserted_id)
    return {"message": "Post created successfully", "post_id": post_id}


@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    result = collection.delete_one({"_id": pymongo.ObjectId(post_id)})
    if result.deleted_count == 1:
        return {"message": f"Post '{post_id}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Post not found")


# CORS Configuration
origins = [
    "https://blogapp-tan.vercel.app",  # Replace with your frontend URL
    # Add more allowed origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
