#!/usr/bin/env python3
"""
Test enum parsing with Pydantic
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class RoleTypeEnum(str, Enum):
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"


class TestModel(BaseModel):
    role_type: Optional[RoleTypeEnum] = Field(default=RoleTypeEnum.FULL_TIME)

    class Config:
        pass


# Test 1: Value-based parsing
print("Test 1: Parsing with enum value 'Full-time'")
try:
    m1 = TestModel(role_type="Full-time")
    print(f"  Success: {m1.role_type}")
    print(f"  Type: {type(m1.role_type)}")
    print(f"  Value: {m1.role_type.value}")
except Exception as e:
    print(f"  Failed: {e}")

# Test 2: Name-based parsing
print("\nTest 2: Parsing with enum name 'FULL_TIME'")
try:
    m2 = TestModel(role_type="FULL_TIME")
    print(f"  Success: {m2.role_type}")
    print(f"  Type: {type(m2.role_type)}")
except Exception as e:
    print(f"  Failed: {e}")

# Test 3: Default
print("\nTest 3: Using default")
try:
    m3 = TestModel()
    print(f"  Success: {m3.role_type}")
    print(f"  Type: {type(m3.role_type)}")
    print(f"  Value: {m3.role_type.value}")
except Exception as e:
    print(f"  Failed: {e}")

# Test 4: No value provided
print("\nTest 4: No value provided (None)")
try:
    m4 = TestModel(role_type=None)
    print(f"  Success: {m4.role_type}")
    print(f"  Type: {type(m4.role_type)}")
except Exception as e:
    print(f"  Failed: {e}")
