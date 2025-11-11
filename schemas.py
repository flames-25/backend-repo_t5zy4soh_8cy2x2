"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Stuvify Jobs schemas

class Job(BaseModel):
    """
    Jobs collection schema
    Collection name: "job"
    """
    title: str = Field(..., description="Job title")
    department: str = Field(..., description="Department e.g., Engineering, Design")
    location: str = Field(..., description="Location string e.g., Remote, NYC")
    type: Literal["Full-time", "Part-time", "Contract", "Internship", "Freelance"] = Field(
        "Full-time", description="Employment type"
    )
    description: str = Field(..., description="Detailed job description")
    requirements: List[str] = Field(default_factory=list, description="Bullet list of requirements")
    featured: bool = Field(False, description="Whether to highlight in UI")

class Application(BaseModel):
    """
    Applications collection schema
    Collection name: "application"
    """
    job_id: str = Field(..., description="ID of the job being applied to")
    name: str = Field(..., description="Applicant full name")
    email: EmailStr = Field(..., description="Applicant email")
    portfolio: Optional[HttpUrl] = Field(None, description="Portfolio or website URL")
    resume_url: Optional[HttpUrl] = Field(None, description="Link to resume (Drive, Dropbox, etc.)")
    cover_letter: Optional[str] = Field(None, description="Optional cover letter text")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
