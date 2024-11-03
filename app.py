from flask import Flask, request, redirect, url_for
from flask import render_template, flash, session
from config import Config
from models import db, SysUser, EmployeeInfo, Department, Checkin, Applyoff
from datetime import datetime
import hashlib

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def has_pswd(password, date):
    ps = date + password
    return hashlib.md5(ps.encode()).hexdigest()


# 初始化数据库
with app.app_context():
    db.create_all()
    company = Department.query.filter_by(name=Config.COMAPNY_NAME).first()
    if not company:
        company = Department(name=Config.COMAPNY_NAME)
        db.session.add(company)
        db.session.commit()
    owner = EmployeeInfo.query.filter_by(name=Config.OWNER).first()
    if not owner:
        date = datetime.today().date().strftime('%Y-%m-%d')
        print(date)
        owner = EmployeeInfo(name=Config.OWNER, email=Config.OWNER_EMAIL,
                             position='CEO', salary=Config.OWNER_SALARY,
                             department=company.name, recruited_at=date,
                             sys_username=Config.OWNER_SYSUSERNAME)
        db.session.add(owner)
        db.session.commit()
        owner_account = SysUser(username=owner.sys_username,
                                date=date,
                                password=has_pswd(Config.OWNER_PSWD, date),
                                is_admin='True')
        db.session.add(owner_account)
        db.session.commit()


# 首页路由
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    employees = EmployeeInfo.query.all()
    departments = Department.query.all()
    return render_template('base.html',
                           employees=employees, departments=departments,
                           company_name=Config.COMAPNY_NAME)


# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # print(f"Username: {username}, Password: {password}")
        user = SysUser.query.filter_by(username=username).first()
        if user and user.password == has_pswd(password, user.date):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')


# 注销
@app.route('/logout')
def logout():
    session.clear()
    flash('您已成功注销')
    return redirect(url_for('login'))


# 访问控制：限制未登录用户访问的路由
@app.before_request
def require_login():
    if 'user_id' not in session and request.endpoint not in ['login']:
        return redirect(url_for('login'))


# ========================= 员工管理 =========================

# 查看所有员工
# @app.route('/employees', methods=['GET'])
# def list_employees():
#     employees = EmployeeInfo.query.all()
#     me = SysUser.query.get(session['user_id'])
#     return render_template('employees.html', employees=employees,
#                            company_name=Config.COMAPNY_NAME, is_admin=me.is_admin)
@app.route('/employees', methods=['GET'])
def list_employees():
    search_query = request.args.get('search', '').strip()
    me = SysUser.query.get(session['user_id'])

    # 如果有搜索关键词，则根据姓名、电子邮件或用户名过滤员工
    if search_query:
        employees = EmployeeInfo.query.filter(
            (EmployeeInfo.name.ilike(f"%{search_query}%")) |
            (EmployeeInfo.email.ilike(f"%{search_query}%")) |
            (EmployeeInfo.sys_username.ilike(f"%{search_query}%"))
        ).all()
    else:
        employees = EmployeeInfo.query.all()

    return render_template('employees.html',
                           employees=employees,
                           company_name=Config.COMAPNY_NAME,
                           is_admin=me.is_admin)


# 添加新员工
@app.route('/employee/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        salary = float(request.form['salary'])
        depart = request.form['department']
        recruit_date = request.form['recruited_at']
        # print(recruit_date)
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form['is_admin']

        new_employee = EmployeeInfo(name=name, email=email,
                                    position=position, salary=salary,
                                    department=depart, recruited_at=recruit_date,
                                    sys_username=username)
        db.session.add(new_employee)
        new_user = SysUser(username=username,
                           date=recruit_date,
                           password=has_pswd(password, recruit_date),
                           is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash('员工添加成功')
        return redirect(url_for('list_employees'))

    departments = Department.query.all()
    return render_template('add_employee.html', departments=departments,
                           company_name=Config.COMAPNY_NAME)


# 删除员工
@app.route('/employee/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    employee = EmployeeInfo.query.get(id)
    employee_account = SysUser.query.filter_by(username=employee.sys_username).first()
    if employee:
        db.session.delete(employee)
        db.session.delete(employee_account)
        db.session.commit()
        flash('员工删除成功')
    return redirect(url_for('list_employees'))


@app.route('/employee/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = EmployeeInfo.query.get(id)
    if request.method == 'POST':
        print(request.form)
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.position = request.form['position']
        employee.salary = float(request.form['salary'])
        employee.department = request.form['department']
        employee.recruited_at = request.form['recruited_at']
        employee.sys_username = request.form['username']
        employee_account = SysUser.query.filter_by(username=employee.sys_username).first()
        # employee_account.password = request.form['password']
        if request.form['password']:
            employee_account.password = has_pswd(request.form['password'], employee.recruited_at)
        employee_account.is_admin = request.form['is_admin']

        db.session.commit()
        flash('员工信息修改成功')
        return redirect(url_for('list_employees'))
    departments = Department.query.all()
    return render_template('edit_employee.html', employee=employee, departments=departments,
                           company_name=Config.COMAPNY_NAME)


# ========================= 部门管理 =========================

# 查看所有部门
@app.route('/departments', methods=['GET'])
def list_departments():
    departments = Department.query.all()
    me = SysUser.query.get(session['user_id'])
    return render_template('departments.html', departments=departments,
                           company_name=Config.COMAPNY_NAME, is_admin=me.is_admin)


@app.route('/department/member/<int:depid>', methods=['GET'])
def depart_member(depid):
    department = Department.query.get(depid)
    employees = EmployeeInfo.query.filter_by(department=department.name).all()
    return render_template('department_members.html', department=department, employees=employees,
                           company_name=Config.COMAPNY_NAME)


# 添加新部门
@app.route('/department/add', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        name = request.form['name']

        new_department = Department(name=name)
        db.session.add(new_department)
        db.session.commit()
        flash('部门添加成功')
        return redirect(url_for('list_departments'))

    employees = EmployeeInfo.query.all()
    return render_template('add_department.html', employees=employees,
                           company_name=Config.COMAPNY_NAME)


@app.route('/department/delete/<int:id>', methods=['POST'])
def delete_department(id):
    department = Department.query.get(id)
    if department:
        db.session.delete(department)
        db.session.commit()
        flash('部门删除成功')
    return redirect(url_for('list_departments'))


# ========================= 考勤管理 =========================
# 打卡页面路由
@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        checkin_date = datetime.now().date().strftime('%Y-%m-%d')
        checkin_time = datetime.now().time().strftime('%H:%M:%S')

        # 创建新的考勤记录
        new_checkin = Checkin(employee_id=employee_id, checkin_date=checkin_date, checkin_time=checkin_time)
        db.session.add(new_checkin)
        db.session.commit()
        flash('打卡成功！')
        return redirect(url_for('checkin'))
    me = SysUser.query.get(session['user_id'])
    employees = EmployeeInfo.query.all()
    # return render_template('checkin.html', employees=employees,
    #                        company_name=Config.COMAPNY_NAME)
    return redirect(url_for('list_checkins'))


# 请假申请页面路由
@app.route('/applyoff', methods=['GET', 'POST'])
def applyoff():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        applyoff_date_start = request.form['applyoff_date_start']
        applyoff_date_end = request.form['applyoff_date_end']
        applyoff_reason = request.form['applyoff_reason']

        # 创建新的请假申请记录
        new_applyoff = Applyoff(employee_id=employee_id, applyoff_date_start=applyoff_date_start,
                                applyoff_date_end=applyoff_date_end, applyoff_reason=applyoff_reason, ended='未销假')
        db.session.add(new_applyoff)
        db.session.commit()
        flash('请假申请已提交！')
        return redirect(url_for('applyoff'))
    employees = EmployeeInfo.query.all()
    return render_template('applyoff.html', employees=employees,
                           company_name=Config.COMAPNY_NAME)


# 查看所有考勤记录
@app.route('/checkins', methods=['GET'])
def list_checkins():
    sys_me = SysUser.query.get(session['user_id'])
    me = EmployeeInfo.query.filter_by(sys_username=sys_me.username).first()
    if sys_me.is_admin == 'True' or sys_me.is_admin == '1':
        checkins = Checkin.query.all()
    else:
        checkins = Checkin.query.filter_by(employee_id=me.id).all()
    employees = EmployeeInfo.query.all()
    return render_template('checkins.html', checkins=checkins,
                           company_name=Config.COMAPNY_NAME, is_admin=sys_me.is_admin,
                           me=me, employees=employees)


# 添加考勤记录
@app.route('/checkin/add', methods=['POST'])
def add_checkin():
    employee_id = int(request.form['employee_id'])
    checkin_date = request.form['checkin_date']
    checkin_time = request.form['checkin_time']
    new_checkin = Checkin(employee_id=employee_id, checkin_date=checkin_date, checkin_time=checkin_time)
    db.session.add(new_checkin)
    db.session.commit()
    flash('考勤记录添加成功')
    return redirect(url_for('list_checkins'))


@app.route('/checkin/delete/<int:id>', methods=['POST'])
def delete_checkin(id):
    checkin = Checkin.query.get(id)
    if checkin:
        db.session.delete(checkin)
        db.session.commit()
        flash('考勤记录删除成功')
    return redirect(url_for('list_checkins'))


# ========================= 请假管理 =========================

# 查看所有请假申请
@app.route('/applyoffs', methods=['GET'])
def list_applyoffs():
    sys_me = SysUser.query.get(session['user_id'])
    me = EmployeeInfo.query.filter_by(sys_username=sys_me.username).first()
    employees = EmployeeInfo.query.all()
    if sys_me.is_admin == 'True' or sys_me.is_admin == '1':
        applyoffs = Applyoff.query.all()
    else:
        applyoffs = Applyoff.query.filter_by(employee_id=me.name).all()
    return render_template('applyoffs.html', applyoffs=applyoffs,
                           company_name=Config.COMAPNY_NAME, is_admin=sys_me.is_admin,
                           me=me, employees=employees)


# 添加请假申请
@app.route('/applyoff/add', methods=['GET', 'POST'])
def add_applyoff():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        applyoff_date_start = request.form['applyoff_date_start']
        applyoff_date_end = request.form['applyoff_date_end']
        applyoff_reason = request.form['applyoff_reason']

        new_applyoff = Applyoff(employee_id=employee_id, applyoff_date_start=applyoff_date_start,
                                applyoff_date_end=applyoff_date_end, applyoff_reason=applyoff_reason)
        db.session.add(new_applyoff)
        db.session.commit()
        flash('请假申请添加成功')
        return redirect(url_for('list_applyoffs'))
    return redirect(url_for('list_applyoffs'))


# 销假
@app.route('/applyoff/end/<int:id>', methods=['POST'])
def end_applyoff(id):
    applyoff = Applyoff.query.get(id)
    if applyoff:
        applyoff.ended = '已销假'
        db.session.commit()
        flash('销假成功')
    return redirect(url_for('list_applyoffs'))


if __name__ == '__main__':
    app.run(debug=True)
