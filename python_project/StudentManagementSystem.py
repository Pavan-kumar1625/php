class Student:
    def __init__(self,student_id,name,age,grade,course):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.course = course

    def __str__(self):
        return (f"ID: {self.student_id} | Name: {self.name} | Age: {self.age} | Grade: {self.grade} | Course: {self.course}")
    
class StudentManagementSystem:
    def __init__(self):
        self.students = {}

    def add_student(self):
        print("\n ---Add New Student--- ")
        student_id = input("Enter the Student ID: ").strip()
        if student_id in self.students:
            print("Error A student with this Id already present\n")
            return
        name = input("Enter the name : \n").strip()
        try:
            age = int(input("Enter the Age: \n").strip())
        except ValueError:
            print("Age must be the valid Number\n")
            return
        grade = input("Enter the Grade: \n").strip()
        course = input("Enter the Course: \n").strip()

        new_student = Student(student_id,name,age,grade,course)
        self.students[student_id] = new_student
        print(f"success: student {name} added successfully!\n")

    def view_students(self):
        print("\n ---Student Records--- ")
        if not self.students:
            print("No Student records found ")
            return
        for student in self.students.values():
            print(student)

    def search_student(self):
        print("\n ---Search Student--- ")
        student_id = input("Enter the student id : ").strip()

        if student_id in self.students:
            print("Record Found.")
            print(self.students[student_id])
        else:
            print("Error Student id not found ")

    def update_student(self):
        print("\n ---Upadate Student--- ")
        student_id = input("Enter the student id: ").strip()
        if student_id not in self.students:
            print("Error Student id not found.")
            return
        student = self.students[student_id]
        print(f"upadating record student : {student.name}")
        print("Leave blank if you do not want to change in field")

        name = input("Enter the name: ").strip()
        age = input("Enter the Age: ").strip()
        grade = input("Enter the Grade: ").strip()
        course = input("Enter the course: ").strip()

        if name:
            student.name = name
        if age:
            try:
                student.age = int(age)
            except ValueError:
                print("Invalid Age entered keeping old age")
        if grade:
            student.grade = grade
        if course:
            student.course = course
        
        print("Success Student record update successfully!")

    def delete_student(self):
        print("\n ---Delete Student--- ")
        student_id = input("Enter the student id: ").strip()
        if student_id in self.students:
            del self.students[student_id]
            print(f"Success Student ID {student_id} deleted successfully")
        else:
            print("Error student id not found!")
            
def main():
        sms = StudentManagementSystem()

        while True:
            print("\n==============================")
            print(" STUDENT MANAGEMENT SYSTEM")
            print("==============================")
            print("1. Add Student")
            print("2. View All Students")
            print("3. Search Student by ID")
            print("4. Update Student Record")
            print("5. Delete Student")
            print("6. Exit")

            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                sms.add_student()
            elif choice == '2':
                sms.view_students()
            elif choice == '3':
                sms.search_student()
            elif choice == '4':
                sms.update_student()
            elif choice == '5':
                sms.delete_student()
            elif choice == '6':
                print("Exiting Student Management System Goodbye!")
                break
            else:
                print("Invalid choice please enter a number between 1 to 6")
        
if __name__ == "__main__":
        main()
        

