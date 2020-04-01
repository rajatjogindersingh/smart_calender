#!/usr/bin/python3.7

if __name__ == "main":
    try:
        from app import app
    except Exception as e:
        print(e)
