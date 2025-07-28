# 启梦教育平台主应用 - 修复版本
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
import json
import random

# 应用配置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qimeng_education.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/materials', exist_ok=True)
os.makedirs('static/uploads/avatars', exist_ok=True)

# 数据模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200), default='default-avatar.png')
    
    # 关系定义
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('TeacherProfile', backref='user', uselist=False, cascade='all, delete-orphan')

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    native_language = db.Column(db.String(50), default='Vietnamese')
    chinese_level = db.Column(db.String(10), default='HSK1')
    emergency_contact = db.Column(db.String(100))
    
    # 关系定义
    enrollments = db.relationship('CourseEnrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    leave_requests = db.relationship('LeaveRequest', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    speech_records = db.relationship('SpeechPracticeRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')

class TeacherProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(100))
    bio = db.Column(db.Text)
    experience_years = db.Column(db.Integer, default=0)
    qualifications = db.Column(db.Text)
    
    # 关系定义
    courses = db.relationship('Course', backref='teacher', lazy='dynamic', cascade='all, delete-orphan')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(10), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_profile.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    schedule = db.Column(db.Text)
    max_students = db.Column(db.Integer, default=20)
    price = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    
    # 关系定义
    enrollments = db.relationship('CourseEnrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    materials = db.relationship('CourseMaterial', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')

class CourseEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    progress = db.Column(db.Integer, default=0)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    lesson_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=90)
    classroom = db.Column(db.String(50))
    online_link = db.Column(db.String(200))
    status = db.Column(db.String(20), default='scheduled')

class CourseMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    teacher_comment = db.Column(db.Text)
    processed_date = db.Column(db.DateTime)

class SpeechPracticeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    audio_file = db.Column(db.String(200))
    score = db.Column(db.Integer)
    pronunciation_score = db.Column(db.Integer)
    fluency_score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    practice_date = db.Column(db.DateTime, default=datetime.utcnow)

class StudyAbroadCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_country = db.Column(db.String(50), nullable=False)
    original_background = db.Column(db.Text, nullable=False)
    target_university = db.Column(db.String(100), nullable=False)
    target_major = db.Column(db.String(100), nullable=False)
    scholarship_amount = db.Column(db.Float)
    success_story = db.Column(db.Text, nullable=False)
    student_photo = db.Column(db.String(200))
    testimonial = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)

class CampProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    theme = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    max_participants = db.Column(db.Integer, default=30)
    min_age = db.Column(db.Integer, default=12)
    max_age = db.Column(db.Integer, default=25)
    itinerary = db.Column(db.Text)
    includes = db.Column(db.Text)
    excludes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    featured_image = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 多语言支持
def get_language():
    return session.get('language', 'zh')

def set_language(language):
    session['language'] = language

translations = {
    'zh': {
        'home': '首页',
        'chinese_courses': '中文教学',
        'study_abroad': '留学服务',
        'camp': '研学旅行',
        'about': '关于我们',
        'login': '登录',
        'register': '注册',
        'logout': '退出登录',
        'dashboard': '控制面板',
        'welcome': '欢迎',
        'courses': '课程',
        'materials': '学习资料',
        'schedule': '课程表',
        'leave_request': '请假申请',
        'speech_practice': 'AI口语练习',
        'profile': '个人资料',
        'settings': '设置'
    },
    'en': {
        'home': 'Home',
        'chinese_courses': 'Chinese Courses',
        'study_abroad': 'Study Abroad',
        'camp': 'Summer Camp',
        'about': 'About Us',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'dashboard': 'Dashboard',
        'welcome': 'Welcome',
        'courses': 'Courses',
        'materials': 'Materials',
        'schedule': 'Schedule',
        'leave_request': 'Leave Request',
        'speech_practice': 'AI Speech Practice',
        'profile': 'Profile',
        'settings': 'Settings'
    },
    'vi': {
        'home': 'Trang chủ',
        'chinese_courses': 'Khóa học tiếng Trung',
        'study_abroad': 'Du học',
        'camp': 'Trại hè',
        'about': 'Về chúng tôi',
        'login': 'Đăng nhập',
        'register': 'Đăng ký',
        'logout': 'Đăng xuất',
        'dashboard': 'Bảng điều khiển',
        'welcome': 'Chào mừng',
        'courses': 'Khóa học',
        'materials': 'Tài liệu',
        'schedule': 'Lịch học',
        'leave_request': 'Xin nghỉ phép',
        'speech_practice': 'Luyện nói AI',
        'profile': 'Hồ sơ',
        'settings': 'Cài đặt'
    }
}

def _(text):
    lang = get_language()
    return translations.get(lang, {}).get(text, text)

@app.context_processor
def inject_template_vars():
    return {
        'moment': lambda: datetime.now(),
        'current_year': datetime.now().year,
        'current_date': datetime.now().strftime('%Y年%m月%d日'),
        'current_time': datetime.now().strftime('%H:%M'),
        '_': _
    }

# 添加自定义过滤器
@app.template_filter('course_color')
def course_color_filter(level):
    """根据课程级别返回颜色"""
    colors = {
        'HSK1': '#28a745',  # 绿色
        'HSK2': '#17a2b8',  # 青色
        'HSK3': '#ffc107',  # 黄色
        'HSK4': '#fd7e14',  # 橙色
        'HSK5': '#dc3545',  # 红色
        'HSK6': '#6f42c1',  # 紫色
        'oral': '#20c997'   # 青绿色
    }
    return colors.get(level, '#6c757d')  # 默认灰色

# 路由定义
@app.route('/')
def index():
    try:
        featured_courses = Course.query.filter_by(status='active').limit(3).all()
        featured_cases = StudyAbroadCase.query.filter_by(is_featured=True).limit(3).all()
        camp_programs = CampProgram.query.filter_by(status='active').limit(3).all()
    except Exception as e:
        print(f"首页数据加载错误: {e}")
        featured_courses = []
        featured_cases = []
        camp_programs = []
    
    return render_template('index.html', 
                         featured_courses=featured_courses,
                         featured_cases=featured_cases,
                         camp_programs=camp_programs)

@app.route('/set_language/<language>')
def set_language_route(language):
    if language in ['zh', 'en', 'vi']:
        set_language(language)
    return redirect(request.referrer or url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('登录成功！', 'success')
            
            if user.role == 'student':
                return redirect(url_for('student_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误！', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'student')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在！', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册！', 'error')
            return render_template('auth/register.html')
        
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role
            )
            db.session.add(user)
            db.session.flush()  # 获取用户ID
            
            if role == 'student':
                profile = StudentProfile(
                    user_id=user.id,
                    full_name=request.form.get('full_name', username)
                )
                db.session.add(profile)
            elif role == 'teacher':
                profile = TeacherProfile(
                    user_id=user.id,
                    full_name=request.form.get('full_name', username)
                )
                db.session.add(profile)
            
            db.session.commit()
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'error')
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'success')
    return redirect(url_for('index'))

# 课程相关路由
@app.route('/courses')
def courses():
    try:
        courses = Course.query.filter_by(status='active').all()
    except Exception as e:
        print(f"课程页面错误: {e}")
        courses = []
    return render_template('courses/index.html', courses=courses)

@app.route('/chinese_courses')
def chinese_courses():
    try:
        courses = Course.query.filter_by(status='active').all()
        # 获取教师信息
        teachers = []
        teacher_profiles = TeacherProfile.query.all()
        for profile in teacher_profiles:
            teachers.append(profile)
    except Exception as e:
        print(f"中文课程页面错误: {e}")
        courses = []
        teachers = []
    return render_template('courses/chinese_courses.html', courses=courses, teachers=teachers)

# 留学服务路由
@app.route('/study_abroad')
def study_abroad():
    try:
        cases = StudyAbroadCase.query.order_by(StudyAbroadCase.created_date.desc()).all()
    except Exception as e:
        print(f"留学页面错误: {e}")
        cases = []
    return render_template('study_abroad/index.html', cases=cases)

@app.route('/study_abroad/cases')
def study_abroad_cases():
    try:
        cases = StudyAbroadCase.query.order_by(StudyAbroadCase.created_date.desc()).all()
    except Exception as e:
        print(f"留学案例页面错误: {e}")
        cases = []
    return render_template('study_abroad/cases.html', cases=cases)

# 研学旅行路由
@app.route('/camp')
def camp():
    try:
        programs = CampProgram.query.filter_by(status='active').all()
    except Exception as e:
        print(f"研学页面错误: {e}")
        programs = []
    return render_template('camp/index.html', programs=programs)

# 学生系统路由
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.student_profile:
            flash('学生资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        enrollments = CourseEnrollment.query.filter_by(
            student_id=current_user.student_profile.id,
            status='active'
        ).all()
        
        upcoming_lessons = []
        for enrollment in enrollments:
            lessons = Lesson.query.filter(
                Lesson.course_id == enrollment.course_id,
                Lesson.lesson_date >= datetime.now(),
                Lesson.status == 'scheduled'
            ).order_by(Lesson.lesson_date).limit(5).all()
            upcoming_lessons.extend(lessons)
        
        pending_requests = LeaveRequest.query.filter_by(
            student_id=current_user.student_profile.id,
            status='pending'
        ).count()
    except Exception as e:
        print(f"学生仪表盘错误: {e}")
        enrollments = []
        upcoming_lessons = []
        pending_requests = 0
    
    return render_template('student/dashboard.html',
                         enrollments=enrollments,
                         upcoming_lessons=upcoming_lessons,
                         pending_requests=pending_requests)

@app.route('/student/materials')
@login_required
def student_materials():
    if current_user.role != 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.student_profile:
            flash('学生资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        enrollments = CourseEnrollment.query.filter_by(
            student_id=current_user.student_profile.id,
            status='active'
        ).all()
        
        materials = []
        for enrollment in enrollments:
            course_materials = CourseMaterial.query.filter_by(
                course_id=enrollment.course_id,
                is_public=True
            ).all()
            materials.extend(course_materials)
    except Exception as e:
        print(f"学习资料页面错误: {e}")
        materials = []
    
    return render_template('student/materials.html', materials=materials)

@app.route('/student/schedule')
@login_required
def student_schedule():
    if current_user.role != 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.student_profile:
            flash('学生资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        enrollments = CourseEnrollment.query.filter_by(
            student_id=current_user.student_profile.id,
            status='active'
        ).all()
        
        lessons = []
        for enrollment in enrollments:
            course_lessons = Lesson.query.filter_by(
                course_id=enrollment.course_id
            ).order_by(Lesson.lesson_date).all()
            lessons.extend(course_lessons)
            
        # 添加模板中需要的变量
        next_class = None
        today_classes = []
        schedules = lessons  # 使用lessons作为schedules
        
        # 创建周统计数据
        week_stats = {
            'total_classes': len(lessons),
            'attended_classes': 0,
            'upcoming_classes': 0,
            'study_hours': 0
        }
        
        # 计算已上课和待上课的数量
        now = datetime.now()
        for lesson in lessons:
            if lesson.lesson_date < now:
                week_stats['attended_classes'] += 1
                week_stats['study_hours'] += lesson.duration / 60  # 转换为小时
            else:
                week_stats['upcoming_classes'] += 1
                # 找出下一节课
                if next_class is None or (lesson.lesson_date > now and lesson.lesson_date < next_class.lesson_date):
                    next_class = lesson
                    
            # 如果是今天的课，添加到today_classes
            if lesson.lesson_date.date() == now.date():
                today_classes.append(lesson)
                
    except Exception as e:
        print(f"课程表页面错误: {e}")
        lessons = []
        next_class = None
        today_classes = []
        schedules = []
        week_stats = {'total_classes': 0, 'attended_classes': 0, 'upcoming_classes': 0, 'study_hours': 0}
    
    return render_template('student/schedule.html', 
                          lessons=lessons,
                          next_class=next_class,
                          today_classes=today_classes,
                          schedules=schedules,
                          week_stats=week_stats)

@app.route('/student/leave_request', methods=['GET', 'POST'])
@login_required
def student_leave_request():
    if current_user.role != 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    if not current_user.student_profile:
        flash('学生资料不完整，请联系管理员！', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            leave_request = LeaveRequest(
                student_id=current_user.student_profile.id,
                course_id=int(request.form['course_id']),
                lesson_date=datetime.strptime(request.form['lesson_date'], '%Y-%m-%d').date(),
                reason=request.form['reason']
            )
            db.session.add(leave_request)
            db.session.commit()
            flash('请假申请已提交！', 'success')
            return redirect(url_for('student_leave_request'))
        except Exception as e:
            print(f"请假申请错误: {e}")
            flash('提交失败，请重试！', 'error')
    
    try:
        enrollments = CourseEnrollment.query.filter_by(
            student_id=current_user.student_profile.id,
            status='active'
        ).all()
        
        leave_requests = LeaveRequest.query.filter_by(
            student_id=current_user.student_profile.id
        ).order_by(LeaveRequest.request_date.desc()).all()
    except Exception as e:
        print(f"请假页面错误: {e}")
        enrollments = []
        leave_requests = []
    
    return render_template('student/leave_request.html', 
                         enrollments=enrollments, 
                         leave_requests=leave_requests)

@app.route('/student/speech_practice')
@login_required
def student_speech_practice():
    if current_user.role != 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.student_profile:
            flash('学生资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        records = SpeechPracticeRecord.query.filter_by(
            student_id=current_user.student_profile.id
        ).order_by(SpeechPracticeRecord.practice_date.desc()).limit(10).all()
    except Exception as e:
        print(f"口语练习页面错误: {e}")
        records = []
    
    return render_template('student/speech_practice.html', records=records)

@app.route('/student/profile')
@login_required
def student_profile():
    if current_user.role != 'student':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    return render_template('student/profile.html')

# 教师系统路由
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.teacher_profile:
            flash('教师资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        courses = Course.query.filter_by(
            teacher_id=current_user.teacher_profile.id,
            status='active'
        ).all()
        
        today_lessons = []
        for course in courses:
            lessons = Lesson.query.filter(
                Lesson.course_id == course.id,
                Lesson.lesson_date >= datetime.now().replace(hour=0, minute=0, second=0),
                Lesson.lesson_date < datetime.now().replace(hour=23, minute=59, second=59),
                Lesson.status == 'scheduled'
            ).all()
            today_lessons.extend(lessons)
        
        pending_requests = LeaveRequest.query.join(Course).filter(
            Course.teacher_id == current_user.teacher_profile.id,
            LeaveRequest.status == 'pending'
        ).count()
    except Exception as e:
        print(f"教师仪表盘错误: {e}")
        courses = []
        today_lessons = []
        pending_requests = 0
    
    return render_template('teacher/dashboard.html',
                         courses=courses,
                         today_lessons=today_lessons,
                         pending_requests=pending_requests)

@app.route('/teacher/classes')
@login_required
def teacher_classes():
    if current_user.role != 'teacher':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.teacher_profile:
            flash('教师资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        courses = Course.query.filter_by(
            teacher_id=current_user.teacher_profile.id
        ).all()
        
        classes = []
        for course in courses:
            enrollments = CourseEnrollment.query.filter_by(
                course_id=course.id,
                status='active'
            ).all()
            
            class_info = {
                'id': course.id,
                'name': f"{course.name}班",
                'course': course,
                'students': [enrollment.student for enrollment in enrollments],
                'capacity': course.max_students,
                'start_date': course.start_date,
                'end_date': course.end_date
            }
            classes.append(class_info)
    except Exception as e:
        print(f"教师班级页面错误: {e}")
        classes = []
    
    return render_template('teacher/classes.html', classes=classes)

@app.route('/teacher/leave_approval')
@login_required
def teacher_leave_approval():
    if current_user.role != 'teacher':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        if not current_user.teacher_profile:
            flash('教师资料不完整，请联系管理员！', 'error')
            return redirect(url_for('index'))
            
        leave_requests = LeaveRequest.query.join(Course).filter(
            Course.teacher_id == current_user.teacher_profile.id
        ).order_by(LeaveRequest.request_date.desc()).all()
    except Exception as e:
        print(f"请假审批页面错误: {e}")
        leave_requests = []
    
    return render_template('teacher/leave_approval.html', 
                         leave_requests=leave_requests)

@app.route('/teacher/approve_leave/<int:request_id>')
@login_required
def approve_leave(request_id):
    if current_user.role != 'teacher':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        leave_request = LeaveRequest.query.get_or_404(request_id)
        leave_request.status = 'approved'
        leave_request.processed_date = datetime.utcnow()
        db.session.commit()
        flash('请假申请已批准！', 'success')
    except Exception as e:
        print(f"批准请假错误: {e}")
        flash('操作失败！', 'error')
    
    return redirect(url_for('teacher_leave_approval'))

@app.route('/teacher/reject_leave/<int:request_id>')
@login_required
def reject_leave(request_id):
    if current_user.role != 'teacher':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        leave_request = LeaveRequest.query.get_or_404(request_id)
        leave_request.status = 'rejected'
        leave_request.processed_date = datetime.utcnow()
        db.session.commit()
        flash('请假申请已拒绝！', 'success')
    except Exception as e:
        print(f"拒绝请假错误: {e}")
        flash('操作失败！', 'error')
    
    return redirect(url_for('teacher_leave_approval'))

# 管理员路由
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        total_students = User.query.filter_by(role='student').count()
        total_teachers = User.query.filter_by(role='teacher').count()
        total_courses = Course.query.count()
        active_courses = Course.query.filter_by(status='active').count()
    except Exception as e:
        print(f"管理员仪表盘错误: {e}")
        total_students = 0
        total_teachers = 0
        total_courses = 0
        active_courses = 0
    
    return render_template('admin/dashboard.html',
                         total_students=total_students,
                         total_teachers=total_teachers,
                         total_courses=total_courses,
                         active_courses=active_courses)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('权限不足！', 'error')
        return redirect(url_for('index'))
    
    try:
        users = User.query.all()
    except Exception as e:
        print(f"用户管理页面错误: {e}")
        users = []
    
    return render_template('admin/users.html', users=users)

# API路由
@app.route('/api/speech_evaluate', methods=['POST'])
@login_required
def api_speech_evaluate():
    if current_user.role != 'student':
        return jsonify({'error': '权限不足'}), 403
    
    if not current_user.student_profile:
        return jsonify({'error': '学生资料不完整'}), 400
    
    data = request.get_json()
    text = data.get('text', '')
    topic = data.get('topic', '')
    
    # 模拟AI评分
    score = random.randint(70, 95)
    pronunciation_score = random.randint(65, 95)
    fluency_score = random.randint(70, 90)
    
    feedback = f"总体表现良好。发音准确度：{pronunciation_score}分，流利度：{fluency_score}分。"
    
    try:
        record = SpeechPracticeRecord(
            student_id=current_user.student_profile.id,
            topic=topic,
            text_content=text,
            score=score,
            pronunciation_score=pronunciation_score,
            fluency_score=fluency_score,
            feedback=feedback
        )
        
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        print(f"保存口语练习记录错误: {e}")
    
    return jsonify({
        'success': True,
        'score': score,
        'pronunciation_score': pronunciation_score,
        'fluency_score': fluency_score,
        'feedback': feedback
    })

# 错误处理
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# 数据库初始化
def init_db():
    """初始化数据库"""
    with app.app_context():
        try:
            db.create_all()
            print("数据库表创建成功！")
            
            # 创建管理员账户
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@qimeng.edu',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("管理员账户已创建: admin/admin123")
            
            create_sample_data()
        except Exception as e:
            print(f"数据库初始化错误: {e}")

def create_sample_data():
    """创建示例数据"""
    try:
        # 创建示例教师
        if not TeacherProfile.query.first():
            teacher_user = User(
                username='teacher1',
                email='teacher1@qimeng.edu',
                password_hash=generate_password_hash('teacher123'),
                role='teacher'
            )
            db.session.add(teacher_user)
            db.session.flush()
            
            teacher_profile = TeacherProfile(
                user_id=teacher_user.id,
                full_name='李老师',
                specialization='HSK教学',
                bio='拥有10年中文教学经验，专注于HSK考试辅导',
                experience_years=10
            )
            db.session.add(teacher_profile)
            db.session.flush()
            
            # 创建示例课程
            course = Course(
                name='HSK1基础班',
                description='适合零基础学员的HSK1级别课程',
                level='HSK1',
                teacher_id=teacher_profile.id,
                start_date=date(2025, 2, 1),
                end_date=date(2025, 5, 31),
                price=1500.00
            )
            db.session.add(course)
            db.session.flush()
            
            # 创建示例课程
            lessons = [
                Lesson(
                    course_id=course.id,
                    title='第一课：你好',
                    description='基础问候语学习',
                    lesson_date=datetime(2025, 2, 3, 10, 0),
                    classroom='A101'
                ),
                Lesson(
                    course_id=course.id,
                    title='第二课：自我介绍',
                    description='学习如何自我介绍',
                    lesson_date=datetime(2025, 2, 5, 10, 0),
                    classroom='A101'
                )
            ]
            for lesson in lessons:
                db.session.add(lesson)
            
            # 创建示例学习资料
            materials = [
                CourseMaterial(
                    course_id=course.id,
                    title='HSK1词汇表',
                    description='HSK1级别必备词汇',
                    file_path='/static/materials/hsk1_vocab.pdf',
                    file_type='pdf'
                ),
                CourseMaterial(
                    course_id=course.id,
                    title='发音练习音频',
                    description='标准发音示范',
                    file_path='/static/materials/pronunciation.mp3',
                    file_type='audio'
                )
            ]
            for material in materials:
                db.session.add(material)
        
        # 创建示例学生
        if not StudentProfile.query.first():
            student_user = User(
                username='student1',
                email='student1@example.com',
                password_hash=generate_password_hash('student123'),
                role='student'
            )
            db.session.add(student_user)
            db.session.flush()
            
            student_profile = StudentProfile(
                user_id=student_user.id,
                full_name='Nguyen Van A',
                native_language='Vietnamese',
                chinese_level='HSK1'
            )
            db.session.add(student_profile)
            db.session.flush()
            
            # 为学生注册课程
            course = Course.query.first()
            if course:
                enrollment = CourseEnrollment(
                    student_id=student_profile.id,
                    course_id=course.id
                )
                db.session.add(enrollment)
        
        # 创建留学案例
        if not StudyAbroadCase.query.first():
            cases = [
                StudyAbroadCase(
                    student_name='Tran Thi B',
                    student_country='Vietnam',
                    original_background='高中毕业，HSK4水平',
                    target_university='北京大学',
                    target_major='国际关系',
                    scholarship_amount=50000.00,
                    success_story='通过我们的专业指导，成功申请到北京大学国际关系专业，并获得全额奖学金。',
                    testimonial='感谢启梦教育的专业指导，让我实现了留学梦想！',
                    is_featured=True
                ),
                StudyAbroadCase(
                    student_name='Le Van C',
                    student_country='Vietnam',
                    original_background='大专毕业，HSK5水平',
                    target_university='清华大学',
                    target_major='计算机科学',
                    scholarship_amount=30000.00,
                    success_story='在启梦教育的帮助下，成功申请到清华大学计算机科学专业硕士。',
                    testimonial='专业的服务让我的申请过程非常顺利！',
                    is_featured=True
                )
            ]
            for case in cases:
                db.session.add(case)
        
        # 创建夏令营项目
        if not CampProgram.query.first():
            camps = [
                CampProgram(
                    name='北京名校探访营',
                    description='深度探访北京顶尖大学，体验中国文化',
                    theme='university',
                    duration=14,
                    start_date=date(2025, 7, 1),
                    end_date=date(2025, 7, 14),
                    price=3500.00,
                    itinerary='第1-3天：北京大学参观；第4-6天：清华大学体验；第7-10天：文化活动；第11-14天：语言实践'
                ),
                CampProgram(
                    name='上海科技体验营',
                    description='探索中国科技发展，参观知名科技企业',
                    theme='tech',
                    duration=10,
                    start_date=date(2025, 8, 1),
                    end_date=date(2025, 8, 10),
                    price=2800.00,
                    itinerary='第1-2天：复旦大学参观；第3-5天：科技企业参访；第6-8天：创新实验室体验；第9-10天：成果展示'
                )
            ]
            for camp in camps:
                db.session.add(camp)
            
        db.session.commit()
        print("示例数据创建完成！")
        
    except Exception as e:
        db.session.rollback()
        print(f"创建示例数据时出错: {e}")

if __name__ == '__main__':
    import sys
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='启梦教育平台')
    parser.add_argument('--port', type=int, default=8088, help='运行端口')
    args, unknown = parser.parse_known_args()
    
    print("启动启梦教育平台...")
    init_db()
    print(f"服务器启动在 http://127.0.0.1:{args.port}")
    print("默认账户:")
    print("管理员: admin/admin123")
    print("教师: teacher1/teacher123")
    print("学生: student1/student123")
    app.run(debug=True, host='0.0.0.0', port=args.port)
