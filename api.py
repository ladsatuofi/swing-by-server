from flask import Flask
import redis 

r = redis.Redis(
    host='hostname',
    port=6379, 
    password='password')