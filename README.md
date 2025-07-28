# 启梦教育平台

一个专为越南学生提供中文教学、留学服务和研学旅行的综合教育平台。

## 功能特色

### 🎓 中文教学系统
- HSK各级别课程管理
- 在线学习资料下载
- AI口语练习评测
- 课程表管理
- 请假申请系统

### 🌍 留学服务
- 成功案例展示
- 留学咨询服务
- 奖学金信息

### 🏕️ 研学旅行
- 夏令营项目管理
- 文化体验活动
- 名校探访项目

### 👥 多角色系统
- **学生**: 课程学习、资料下载、口语练习
- **教师**: 班级管理、请假审批、课程安排
- **管理员**: 用户管理、系统配置

## 快速开始

### 1. 环境要求
- Python 3.8+
- Flask 2.3.3
- SQLite 数据库

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动应用
```bash
python app.py
```
或使用启动脚本：
```bash
python run.py
```

### 4. 访问应用
打开浏览器访问: http://127.0.0.1:8088

## 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 教师 | teacher1 | teacher123 |
| 学生 | student1 | student123 |

## 项目结构

```
启梦教育平台/
├── app.py              # 主应用文件
├── run.py              # 启动脚本
├── requirements.txt    # 依赖包列表
├── README.md          # 项目说明
├── instance/          # 数据库文件
├── static/            # 静态资源
│   ├── css/          # 样式文件
│   ├── js/           # JavaScript文件
│   └── uploads/      # 上传文件
└── templates/         # HTML模板
    ├── auth/         # 认证页面
    ├── student/      # 学生页面
    ├── teacher/      # 教师页面
    ├── admin/        # 管理员页面
    ├── courses/      # 课程页面
    ├── study_abroad/ # 留学页面
    └── camp/         # 研学页面
```

## 技术栈

- **后端**: Flask + SQLAlchemy
- **前端**: Bootstrap 5 + jQuery
- **数据库**: SQLite
- **认证**: Flask-Login
- **文件上传**: Werkzeug

## 开发说明

### 数据库初始化
应用首次启动时会自动创建数据库表和示例数据。

### 多语言支持
支持中文、英文、越南语三种语言切换。

### 文件上传
支持课程资料、头像等文件上传功能。

## 许可证

MIT License