from Models import Student, Mark, Teacher, Subject, User
from datetime import datetime
from sqlalchemy import and_
from flask import Blueprint, Response, request, jsonify, json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth
from marshmallow import Schema



engine = create_engine("mysql+pymysql://root:1234@127.0.0.1:3307/lab", echo=True)
session = sessionmaker(bind=engine)
s = session()

student = Blueprint('student', __name__)
teacher = Blueprint('teacher', __name__)
auth = HTTPBasicAuth()

class MarkSchema(Schema):
    class Meta:
        fields = ('MarkId', 'StudentId','SubjectId', 'TeacherId', 'Date', 'Value')


mark_schema = MarkSchema(many=False)
marks_schema = MarkSchema(many=True)

class TeacherSchema(Schema):
    class Meta:
        fields = ('TeacherId', 'Firstname', 'Surname', 'SubjectId')

teacher_schemas = TeacherSchema(many=True)

@teacher.route("/teachers/<int:subjectId>", methods=["GET"])
def GetAllTeachersBySubject(subjectId):
    teachers = s.query(Teacher).filter(Teacher.SubjectId == subjectId).all()
    result_set = teacher_schemas.dump(teachers)
    return jsonify(result_set)

@teacher.route("/teachers", methods=["GET"])
def GetAllTeachers():
    teachers = s.query(Teacher).all()
    result_set = teacher_schemas.dump(teachers)
    return jsonify(result_set)

@auth.verify_password
def verify_password(username, password):
    try:
        user = s.query(User).filter(and_(User.Username == username,
                                         User.Password == password)).first() is not None
        if user:
            return username
    except:
        return None
@auth.get_user_roles
def get_user_roles(username):
    user = s.query(User).filter(User.Username == username).first()
    return user.Status

@student.route("/student/<studentId>", methods=["GET"])
@auth.login_required(role=['user'])
def GetStudentById(studentId):
    current = auth.username()
    if current != studentId:
        return Response(status=403, response='Access denied')
    student = s.query(Student).filter(Student.StudentId == studentId).one()
    student_data = {'StudentId': student.StudentId, 'Firstname': student.Firstname,
                    'Surname': student.Surname, 'GroupId': student.GroupId}
    return jsonify({"Student": student_data})


@teacher.route("/groups", methods=["POST"])
@auth.login_required(role=['admin'])
def AddStudent():
    try:
        StudentId = request.json['StudentId']
        Firstname = request.json['Firstname']
        Surname = request.json['Surname']
        Password = request.json['Password']
        GroupId = request.json['GroupId']

        new_student = Student(StudentId=StudentId, Password=Password, Firstname=Firstname,
                              Surname=Surname, GroupId=GroupId)
        new_user = User(Username=StudentId, Password=Password, Status="user")
        s.add(new_student)
        s.add(new_user)
        s.commit()
        return Response(status=200, response='Success: Student was added')

    except Exception as e:
        return Response(status=403, response='Error: Invalid data')


@teacher.route("/student/<studentId>", methods=["DELETE"])
@auth.login_required(role=['admin'])
def DeleteStudent(studentId):
    student_del = s.query(Student).filter(Student.StudentId == studentId).one()
    user = s.query(User).filter(User.Username == studentId).one()

    s.delete(user)
    s.delete(student_del)
    s.commit()
    return Response(status=200, response='Success: Student was deleted')


@student.route("/student/<studentId>", methods=["PUT"])
@auth.login_required(role=['user'])
def UpdateStudentById(studentId):
    current = auth.username()
    if current != studentId:
        return Response(status=403, response='Access denied')
    student = s.query(Student).filter(Student.StudentId == studentId).one()
    try:
        StudentId = request.json['StudentId']
        Firstname = request.json['Firstname']
        Password = request.json['Password']
        Surname = request.json['Surname']

        student.StudentId = StudentId
        student.Firstname = Firstname
        student.Password = Password
        student.Surname = Surname

        user = s.query(User).filter(User.Username == studentId).one()
        user.Username = StudentId
        user.Password = Password

        s.commit()
    except Exception as e:
        return Response(status=400, response='Error: Invalid data')
    return Response(status=200, response='Success: Student was updated')


@teacher.route("/teachers", methods=["POST"])
@auth.login_required(role="admin")
def AddTeacher():
    try:
        TeacherId = request.json['TeacherId']
        Password = request.json['Password']
        Firstname = request.json['Firstname']
        Surname = request.json['Surname']
        SubjectId = request.json['SubjectId']

        new_teacher = Teacher(TeacherId=TeacherId, Password=Password, Firstname=Firstname,
                              Surname=Surname, SubjectId=SubjectId)

        new_user = User(Username=TeacherId, Password=Password, Status="admin")

        s.add(new_teacher)
        s.add(new_user)
        s.commit()
        return Response(status=200, response='Success: Teacher was added')

    except Exception as e:
        return Response(status=403, response='Error: Invalid data')


@teacher.route("/teachers/<teacherId>", methods=["GET"])
def GetTeacherById(teacherId):
        teacher = s.query(Teacher).filter(Teacher.TeacherId == teacherId).one()
        teacher_data = {'TeacherId': teacher.TeacherId, 'Firstname': teacher.Firstname,
                        'Surname': teacher.Surname, "SubjectId": teacher.SubjectId}
        return jsonify({"Teacher": teacher_data})




@teacher.route("/teachers/<teacherId>", methods=["PUT"])
@auth.login_required(role=["admin"])
def UpdateTeacherById(teacherId):
    current = auth.username()
    if current != teacherId:
        return Response(status=403, response='Access denied')
    teacher = s.query(Teacher).filter(Teacher.TeacherId == teacherId).one()
    user = s.query(User).filter(User.Username == teacherId).one()
    try:
        TeacherId = request.json['TeacherId']
        Password = request.json['Password']
        Firstname = request.json['Firstname']
        Surname = request.json['Surname']
        SubjectId = request.json['SubjectId']

        user.Username = TeacherId
        user.Password = Password

        teacher.TeacherId = TeacherId
        teacher.Password = Password
        teacher.Firstname = Firstname
        teacher.Surname = Surname
        teacher.SubjectId = SubjectId



        s.commit()
    except Exception as e:
        return Response(status=400, response='Error: Invalid data')

    return Response(status=200, response='Success: Teacher was updated')


@teacher.route("/teachers/<teacherId>", methods=["DELETE"])
@auth.login_required(role=["admin"])
def DeleteTeacherById(teacherId):
    current = auth.username()
    if current != teacherId:
        return Response(status=403, response='Access denied')
    teacher = s.query(Teacher).filter(Teacher.TeacherId == teacherId).one()
    user = s.query(User).filter(User.Username == teacherId).one()
    s.delete(user)
    s.delete(teacher)

    s.commit()
    return Response(status=200, response='Success: Teacher was deleted')


@teacher.route("/teacher", methods=["POST"])
@auth.login_required(role=["admin"])
def AddMark():
    try:
        MarkId = request.json['MarkId']
        Date = request.json['Date']
        Value = request.json['Value']
        SubjectId = request.json['SubjectId']
        StudentId = request.json['StudentId']
        TeacherId = request.json['TeacherId']
        current = auth.username()
        if current != TeacherId:
            return Response(status=403, response='Access denied')
        new_mark = Mark(MarkId=MarkId, StudentId=StudentId,
                        SubjectId=SubjectId, TeacherId=TeacherId,
                        Date=datetime.strptime(Date, "%Y-%m-%d"), Value=Value)

        s.add(new_mark)
        s.commit()
        return Response(status=200, response='Success: Mark was added')

    except Exception as e:
        return Response(status=400, response='Error: Invalid data')


@teacher.route("/teacher/<studentId>/<int:markId>", methods=["PUT"])
@auth.login_required(role=["admin"])
def UpdateMarkById(studentId, markId):
    mark = s.query(Mark).filter(and_(Mark.StudentId == studentId, Mark.MarkId == markId)).one()
    try:
        MarkId = request.json['MarkId']
        Date = request.json['Date']
        Value = request.json['Value']
        SubjectId = request.json['SubjectId']
        StudentId = request.json['StudentId']
        TeacherId = request.json['TeacherId']
        current = auth.username()
        if current != TeacherId:
            return Response(status=403, response='Access denied')
        mark.MarkId = MarkId
        mark.Date = datetime.strptime(Date, "%Y-%m-%d")
        mark.Value = Value
        mark.SubjectId = SubjectId
        mark.StudentId = StudentId
        mark.TeacherId = TeacherId

        s.commit()
    except Exception as e:
        return Response(status=400, response='Error: Invalid data')

    return Response(status=200, response='Success: Mark was updated')


@teacher.route("/teacher/<studentId>/<int:markId>/<teacherId>", methods=["DELETE"])
@auth.login_required(role=["admin"])
def DeleteMarkById(studentId, markId, teacherId):
    current = auth.username()
    if current != teacherId:
        return Response(status=403, response='Access denied')
    mark = s.query(Mark).filter(and_(Mark.StudentId == studentId, Mark.MarkId == markId)).one()
    s.delete(mark)
    s.commit()
    return Response(status=200, response='Success: Mark was deleted')


@student.route("/students/<int:subjectId>/<studentId>", methods=["GET"])
@auth.login_required(role=["user"])
def GetAllStudentMarksBySubjectId(subjectId, studentId):
    current = auth.username()
    if current != studentId:
        return Response(status=403, response='Access denied')
    marks = s.query(Mark).filter(and_(Mark.SubjectId == subjectId, Mark.StudentId == studentId)).all()
    result_set = marks_schema.dump(marks)
    return jsonify(result_set)

@student.route("/students/<studentId>", methods = ["GET"])
@auth.login_required(role=["user"])
def GetAllStudentMarks(studentId):
    current = auth.username()
    if current != studentId:
        return Response(status=403, response='Access denied')
    marks = s.query(Mark).filter(Mark.StudentId == studentId).all()
    result_set = marks_schema.dump(marks)
    return jsonify(result_set)
