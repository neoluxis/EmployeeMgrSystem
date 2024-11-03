import os


class Config:
    SECRET_KEY = 'nlxlovecandy'  # 为Flask会话设置密钥
    SQLALCHEMY_DATABASE_URI = 'sqlite:///employees.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    COMAPNY_NAME = 'ABC公司'
    OWNER = '张三'
    OWNER_SYSUSERNAME = 'zhangsan123'
    OWNER_EMAIL = 'zhangsan123@abc.com'
    OWNER_PSWD = '123456'
    OWNER_SALARY = 1000000
