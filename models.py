from flask_sqlalchemy import SQLAlchemy
from numpy.ma.extras import unique

db = SQLAlchemy()


class SysUser(db.Model):
    __tablename__ = 'sys_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('employee_info.sys_username'), nullable=False, unique=True)
    date = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.String(5), nullable=False)


class EmployeeInfo(db.Model):
    __tablename__ = 'employee_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sys_username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    recruited_at = db.Column(db.String(10), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(50), db.ForeignKey('departments.name'), nullable=False)


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class Checkin(db.Model):
    __tablename__ = 'checkins'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(80), db.ForeignKey('employee_info.name'), nullable=False)
    checkin_date = db.Column(db.String(10), nullable=False)
    checkin_time = db.Column(db.String(8), nullable=False)


class Applyoff(db.Model):
    __tablename__ = 'applyoffs'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(80), db.ForeignKey('employee_info.name'), nullable=False)
    applyoff_date_start = db.Column(db.String(10), nullable=False)
    applyoff_date_end = db.Column(db.String(10), nullable=False)
    applyoff_reason = db.Column(db.Text, nullable=False)
    ended = db.Column(db.String(5), nullable=False, default='no')
