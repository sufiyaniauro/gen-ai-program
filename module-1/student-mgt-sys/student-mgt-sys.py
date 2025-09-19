import sqlite3
import os
import re
from datetime import datetime
import sys

class Student:
    """
    Student class represents a student entity with attributes and validation.
    """
    def __init__(self, student_id=None, name=None, age=None, grade=None, email=None, phone=None, address=None, enrollment_date=None):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.email = email
        self.phone = phone
        self.address = address
        self.enrollment_date = enrollment_date if enrollment_date else datetime.now().strftime('%Y-%m-%d')
    
    def validate(self):
        """Validate student data before saving to database"""
        errors = []
        
        if not self.name or len(self.name) < 2:
            errors.append("Name must be at least 2 characters")
        
        try:
            if int(self.age) < 5 or int(self.age) > 100:
                errors.append("Age must be between 5 and 100")
        except (ValueError, TypeError):
            errors.append("Age must be a valid number")
        
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            errors.append("Invalid email format")
        
        if self.phone and not re.match(r"^\d{10}$", self.phone):
            errors.append("Phone must be 10 digits")
            
        return errors
    
    def to_dict(self):
        """Convert student object to dictionary"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'age': self.age,
            'grade': self.grade,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'enrollment_date': self.enrollment_date
        }
        

class StudentManagementSystem:
    """
    Main class for Student Management System with database operations.
    """
    def __init__(self, db_path='student_database.db'):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize database connection and create tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    grade TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    enrollment_date TEXT
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    date TEXT,
                    status TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS marks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    subject TEXT,
                    score REAL,
                    exam_date TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
    
    def add_student(self, student):
        """Add a new student to the database"""
        errors = student.validate()
        if errors:
            return False, errors
        
        try:
            self.cursor.execute('''
                INSERT INTO students (name, age, grade, email, phone, address, enrollment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student.name, student.age, student.grade, student.email, 
                  student.phone, student.address, student.enrollment_date))
            self.connection.commit()
            return True, ["Student added successfully!"]
        except sqlite3.Error as e:
            return False, [f"Error adding student: {e}"]
    
    def update_student(self, student_id, student_data):
        """Update an existing student's information"""
        student = Student(student_id=student_id, **student_data)
        errors = student.validate()
        if errors:
            return False, errors
        
        try:
            self.cursor.execute('''
                UPDATE students
                SET name=?, age=?, grade=?, email=?, phone=?, address=?, enrollment_date=?
                WHERE student_id=?
            ''', (student.name, student.age, student.grade, student.email,
                  student.phone, student.address, student.enrollment_date, student_id))
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                return True, ["Student updated successfully!"]
            else:
                return False, ["Student not found."]
        except sqlite3.Error as e:
            return False, [f"Error updating student: {e}"]
    
    def delete_student(self, student_id):
        """Delete a student from the database"""
        try:
            self.cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                self.cursor.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))
                self.cursor.execute("DELETE FROM marks WHERE student_id=?", (student_id,))
                self.connection.commit()
                return True, ["Student deleted successfully!"]
            else:
                return False, ["Student not found."]
        except sqlite3.Error as e:
            return False, [f"Error deleting student: {e}"]
    
    def get_all_students(self):
        """Get all students from the database"""
        try:
            self.cursor.execute("SELECT * FROM students ORDER BY name")
            students = []
            for row in self.cursor.fetchall():
                student = Student(
                    student_id=row[0],
                    name=row[1],
                    age=row[2],
                    grade=row[3],
                    email=row[4],
                    phone=row[5],
                    address=row[6],
                    enrollment_date=row[7]
                )
                students.append(student)
            return students
        except sqlite3.Error as e:
            print(f"Error retrieving students: {e}")
            return []
    
    def get_student_by_id(self, student_id):
        """Get a student by their ID"""
        try:
            self.cursor.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
            row = self.cursor.fetchone()
            if row:
                student = Student(
                    student_id=row[0],
                    name=row[1],
                    age=row[2],
                    grade=row[3],
                    email=row[4],
                    phone=row[5],
                    address=row[6],
                    enrollment_date=row[7]
                )
                return student
            return None
        except sqlite3.Error as e:
            print(f"Error retrieving student: {e}")
            return None
    
    def search_students(self, keyword):
        """Search students by name, email, or grade"""
        try:
            search_param = f"%{keyword}%"
            self.cursor.execute("""
                SELECT * FROM students 
                WHERE name LIKE ? OR email LIKE ? OR grade LIKE ?
                ORDER BY name
            """, (search_param, search_param, search_param))
            
            students = []
            for row in self.cursor.fetchall():
                student = Student(
                    student_id=row[0],
                    name=row[1],
                    age=row[2],
                    grade=row[3],
                    email=row[4],
                    phone=row[5],
                    address=row[6],
                    enrollment_date=row[7]
                )
                students.append(student)
            return students
        except sqlite3.Error as e:
            print(f"Error searching students: {e}")
            return []
    
    def mark_attendance(self, student_id, date, status):
        """Mark attendance for a student"""
        try:
            if not self.get_student_by_id(student_id):
                return False, ["Student not found"]
            
            self.cursor.execute("""
                SELECT * FROM attendance 
                WHERE student_id=? AND date=?
            """, (student_id, date))
            
            if self.cursor.fetchone():
                self.cursor.execute("""
                    UPDATE attendance
                    SET status=?
                    WHERE student_id=? AND date=?
                """, (status, student_id, date))
            else:
                self.cursor.execute("""
                    INSERT INTO attendance (student_id, date, status)
                    VALUES (?, ?, ?)
                """, (student_id, date, status))
            
            self.connection.commit()
            return True, ["Attendance marked successfully!"]
        except sqlite3.Error as e:
            return False, [f"Error marking attendance: {e}"]
    
    def add_marks(self, student_id, subject, score, exam_date):
        """Add marks/grades for a student"""
        try:
            if not self.get_student_by_id(student_id):
                return False, ["Student not found"]
            
            try:
                score = float(score)
                if score < 0 or score > 100:
                    return False, ["Score must be between 0 and 100"]
            except ValueError:
                return False, ["Score must be a valid number"]
            
            self.cursor.execute("""
                SELECT * FROM marks 
                WHERE student_id=? AND subject=? AND exam_date=?
            """, (student_id, subject, exam_date))
            
            if self.cursor.fetchone():
                self.cursor.execute("""
                    UPDATE marks
                    SET score=?
                    WHERE student_id=? AND subject=? AND exam_date=?
                """, (score, student_id, subject, exam_date))
            else:
                self.cursor.execute("""
                    INSERT INTO marks (student_id, subject, score, exam_date)
                    VALUES (?, ?, ?, ?)
                """, (student_id, subject, score, exam_date))
            
            self.connection.commit()
            return True, ["Marks added successfully!"]
        except sqlite3.Error as e:
            return False, [f"Error adding marks: {e}"]
    
    def get_student_marks(self, student_id):
        """Get all marks for a student"""
        try:
            self.cursor.execute("""
                SELECT subject, score, exam_date 
                FROM marks 
                WHERE student_id=? 
                ORDER BY exam_date DESC
            """, (student_id,))
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving marks: {e}")
            return []
    
    def get_attendance_report(self, student_id):
        """Get attendance report for a student"""
        try:
            self.cursor.execute("""
                SELECT date, status 
                FROM attendance 
                WHERE student_id=? 
                ORDER BY date DESC
            """, (student_id,))
            
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving attendance: {e}")
            return []
    
    def generate_grade_report(self, student_id):
        """Generate a comprehensive grade report for a student"""
        student = self.get_student_by_id(student_id)
        if not student:
            return None
        
        marks = self.get_student_marks(student_id)
        attendance = self.get_attendance_report(student_id)
        
        return {
            'student': student.to_dict(),
            'marks': marks,
            'attendance': attendance,
            'attendance_percentage': self._calculate_attendance_percentage(attendance),
            'average_score': self._calculate_average_score(marks)
        }
    
    def _calculate_attendance_percentage(self, attendance):
        """Helper method to calculate attendance percentage"""
        if not attendance:
            return 0
            
        present_count = sum(1 for _, status in attendance if status.lower() == 'present')
        return (present_count / len(attendance)) * 100
    
    def _calculate_average_score(self, marks):
        """Helper method to calculate average score"""
        if not marks:
            return 0
            
        total_score = sum(score for _, score, _ in marks)
        return total_score / len(marks)


class CLI:
    """
    Command Line Interface for the Student Management System.
    """
    def __init__(self):
        self.sms = StudentManagementSystem()
    
    def display_menu(self):
        """Display the main menu options"""
        print("\n===== STUDENT MANAGEMENT SYSTEM =====")
        print("1. Add New Student")
        print("2. View All Students")
        print("3. Search Students")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Mark Attendance")
        print("7. Add Marks/Grades")
        print("8. View Student Report")
        print("9. Exit")
        print("=====================================")
    
    def run(self):
        """Run the CLI application"""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-9): ")
            
            if choice == '1':
                self.add_student()
            elif choice == '2':
                self.view_all_students()
            elif choice == '3':
                self.search_students()
            elif choice == '4':
                self.update_student()
            elif choice == '5':
                self.delete_student()
            elif choice == '6':
                self.mark_attendance()
            elif choice == '7':
                self.add_marks()
            elif choice == '8':
                self.view_student_report()
            elif choice == '9':
                print("Exiting Student Management System...")
                self.sms.close_connection()
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    def add_student(self):
        """Collect student information and add to database"""
        print("\n--- Add New Student ---")
        name = input("Enter name: ")
        age = input("Enter age: ")
        grade = input("Enter grade/class: ")
        email = input("Enter email (optional): ")
        phone = input("Enter phone (optional): ")
        address = input("Enter address (optional): ")
        
        student = Student(
            name=name,
            age=age,
            grade=grade,
            email=email,
            phone=phone,
            address=address
        )
        
        success, messages = self.sms.add_student(student)
        for message in messages:
            print(message)
    
    def view_all_students(self):
        """Display all students in the database"""
        print("\n--- All Students ---")
        students = self.sms.get_all_students()
        
        if not students:
            print("No students found.")
            return
            
        self._display_students_table(students)
    
    def search_students(self):
        """Search for students by keyword"""
        keyword = input("\nEnter search keyword (name, email, grade): ")
        students = self.sms.search_students(keyword)
        
        if not students:
            print("No matching students found.")
            return
            
        print(f"\n--- Search Results for '{keyword}' ---")
        self._display_students_table(students)
    
    def update_student(self):
        """Update student information"""
        student_id = input("\nEnter student ID to update: ")
        
        try:
            student_id = int(student_id)
        except ValueError:
            print("Invalid student ID.")
            return
            
        student = self.sms.get_student_by_id(student_id)
        if not student:
            print("Student not found.")
            return
            
        print(f"\n--- Update Student: {student.name} (ID: {student.student_id}) ---")
        print("(Press Enter to keep current value)")
        
        name = input(f"Name [{student.name}]: ") or student.name
        age = input(f"Age [{student.age}]: ") or student.age
        grade = input(f"Grade [{student.grade}]: ") or student.grade
        email = input(f"Email [{student.email}]: ") or student.email
        phone = input(f"Phone [{student.phone}]: ") or student.phone
        address = input(f"Address [{student.address}]: ") or student.address
        
        student_data = {
            'name': name,
            'age': age,
            'grade': grade,
            'email': email,
            'phone': phone,
            'address': address,
            'enrollment_date': student.enrollment_date
        }
        
        success, messages = self.sms.update_student(student_id, student_data)
        for message in messages:
            print(message)
    
    def delete_student(self):
        """Delete a student from the system"""
        student_id = input("\nEnter student ID to delete: ")
        
        try:
            student_id = int(student_id)
        except ValueError:
            print("Invalid student ID.")
            return
            
        student = self.sms.get_student_by_id(student_id)
        if not student:
            print("Student not found.")
            return
            
        confirm = input(f"Are you sure you want to delete {student.name}? (y/n): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return
            
        success, messages = self.sms.delete_student(student_id)
        for message in messages:
            print(message)
    
    def mark_attendance(self):
        """Mark attendance for a student"""
        student_id = input("\nEnter student ID: ")
        
        try:
            student_id = int(student_id)
        except ValueError:
            print("Invalid student ID.")
            return
            
        student = self.sms.get_student_by_id(student_id)
        if not student:
            print("Student not found.")
            return
            
        print(f"\n--- Mark Attendance for {student.name} ---")
        date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print("Select status:")
        print("1. Present")
        print("2. Absent")
        print("3. Late")
        print("4. Excused")
        
        status_choice = input("Enter choice (1-4): ")
        status_map = {'1': 'Present', '2': 'Absent', '3': 'Late', '4': 'Excused'}
        
        if status_choice not in status_map:
            print("Invalid choice.")
            return
            
        status = status_map[status_choice]
        success, messages = self.sms.mark_attendance(student_id, date, status)
        
        for message in messages:
            print(message)
    
    def add_marks(self):
        """Add marks/grades for a student"""
        student_id = input("\nEnter student ID: ")
        
        try:
            student_id = int(student_id)
        except ValueError:
            print("Invalid student ID.")
            return
            
        student = self.sms.get_student_by_id(student_id)
        if not student:
            print("Student not found.")
            return
            
        print(f"\n--- Add Marks for {student.name} ---")
        subject = input("Enter subject: ")
        score = input("Enter score (0-100): ")
        exam_date = input("Enter exam date (YYYY-MM-DD) or press Enter for today: ")
        
        if not exam_date:
            exam_date = datetime.now().strftime('%Y-%m-%d')
        
        success, messages = self.sms.add_marks(student_id, subject, score, exam_date)
        
        for message in messages:
            print(message)
    
    def view_student_report(self):
        """View comprehensive report for a student"""
        student_id = input("\nEnter student ID: ")
        
        try:
            student_id = int(student_id)
        except ValueError:
            print("Invalid student ID.")
            return
            
        report = self.sms.generate_grade_report(student_id)
        if not report:
            print("Student not found.")
            return
            
        student = report['student']
        print(f"\n{'='*50}")
        print(f"STUDENT REPORT - ID: {student['student_id']}")
        print(f"{'='*50}")
        print(f"Name: {student['name']}")
        print(f"Age: {student['age']}")
        print(f"Grade: {student['grade']}")
        print(f"Email: {student['email']}")
        print(f"Phone: {student['phone']}")
        print(f"Address: {student['address']}")
        print(f"Enrollment Date: {student['enrollment_date']}")
        print(f"{'-'*50}")
        
        print("\nATTENDANCE RECORD:")
        if not report['attendance']:
            print("No attendance records found.")
        else:
            attendance_percentage = report['attendance_percentage']
            print(f"Attendance Rate: {attendance_percentage:.1f}%")
            print(f"{'-'*20}")
            for date, status in report['attendance']:
                print(f"{date}: {status}")
        
        print(f"\nACADEMIC RECORD:")
        if not report['marks']:
            print("No academic records found.")
        else:
            avg_score = report['average_score']
            print(f"Average Score: {avg_score:.1f}")
            print(f"{'-'*20}")
            for subject, score, exam_date in report['marks']:
                print(f"{subject}: {score} (Date: {exam_date})")
        
        print(f"{'='*50}")
    
    def _display_students_table(self, students):
        """Helper method to display students in a table format"""
        if not students:
            return
            
        print(f"\n{'ID':<5} {'Name':<20} {'Age':<5} {'Grade':<10} {'Email':<25} {'Phone':<15}")
        print('-' * 80)
        
        for student in students:
            print(f"{student.student_id:<5} {student.name[:18]:<20} {student.age:<5} "
                  f"{student.grade[:8]:<10} {student.email[:23]:<25} {student.phone[:13]:<15}")


if __name__ == "__main__":
    cli = CLI()
    cli.run()
