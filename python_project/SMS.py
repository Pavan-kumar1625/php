import json
import os
import getpass

DATA_FILE = "students.json"

# Default admin credentials (in production, use salted password hashes)
ADMIN_CREDENTIALS = {
    "admin": "admin123"
}


# DATA PERSISTENCE

def load_students():
    """Load student records from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        print("Warning: Failed to read data file. Starting with an empty dataset.")
        return {}


def save_students(students):
    """Save student records to the JSON file."""
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(students, file, indent=4)
    except IOError as e:
        print(f"Error saving data: {e}")


# INPUT VALIDATION HELPERS

def get_valid_roll(existing_students, must_exist=False):
    """Prompt and validate a roll number."""
    while True:
        roll = input("Enter Roll Number: ").strip()
        if not roll:
            print("Roll number cannot be empty.")
            continue
        
        if must_exist and roll not in existing_students:
            print(f"Error: Roll Number '{roll}' does not exist.")
            return None
        if not must_exist and roll in existing_students:
            print(f"Error: Roll Number '{roll}' already exists.")
            continue
        return roll


def get_valid_name(prompt="Enter Student Name: "):
    """Ensure name is non-empty and alphabetic."""
    while True:
        name = input(prompt).strip()
        if not name:
            print("Name cannot be empty.")
            continue
        if not all(x.isalpha() or x.isspace() for x in name):
            print("Name should only contain letters and spaces.")
            continue
        return name


def get_valid_marks(prompt="Enter Marks (0-100): "):
    """Validate numeric input between 0 and 100."""
    while True:
        val = input(prompt).strip()
        try:
            marks = float(val)
            if 0 <= marks <= 100:
                return marks
            print("Marks must be between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


# CORE CRUD OPERATIONS

def add_student(students):
    print("\n--- Add Student ---")
    roll = get_valid_roll(students, must_exist=False)
    name = get_valid_name()
    marks = get_valid_marks()

    students[roll] = {"name": name, "marks": marks}
    save_students(students)
    print(f"Student '{name}' (Roll: {roll}) added successfully.")


def update_student(students):
    print("\n--- Update Student ---")
    roll = get_valid_roll(students, must_exist=True)
    if not roll:
        return

    current = students[roll]
    print(f"Current Record -> Name: {current['name']}, Marks: {current['marks']}")
    print("Press Enter to keep current value.")

    new_name = input(f"Enter New Name [{current['name']}]: ").strip()
    if new_name:
        while not all(x.isalpha() or x.isspace() for x in new_name):
            print("Name should only contain letters and spaces.")
            new_name = input(f"Enter New Name [{current['name']}]: ").strip()
        current['name'] = new_name

    new_marks_str = input(f"Enter New Marks [{current['marks']}]: ").strip()
    if new_marks_str:
        while True:
            try:
                marks_val = float(new_marks_str)
                if 0 <= marks_val <= 100:
                    current['marks'] = marks_val
                    break
                print("Marks must be between 0 and 100.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            new_marks_str = input("Enter New Marks: ").strip()

    save_students(students)
    print(f"Record for Roll {roll} updated successfully.")


def delete_student(students):
    print("\n--- Delete Student ---")
    roll = get_valid_roll(students, must_exist=True)
    if not roll:
        return

    confirm = input(f"Are you sure you want to delete Roll {roll}? (y/n): ").strip().lower()
    if confirm == 'y':
        del students[roll]
        save_students(students)
        print(f"Record for Roll {roll} deleted.")
    else:
        print("Deletion canceled.")


def search_student(students):
    print("\n--- Search Student ---")
    query = input("Search by Roll Number or Name: ").strip().lower()
    if not query:
        print("Search query cannot be empty.")
        return

    matches = []
    for roll, details in students.items():
        if query == roll.lower() or query in details["name"].lower():
            matches.append((roll, details["name"], details["marks"]))

    if not matches:
        print("No matching records found.")
        return

    print("\n" + "=" * 45)
    print(f"{'Roll No':<12} {'Name':<22} {'Marks':<8}")
    print("=" * 45)
    for roll, name, marks in matches:
        print(f"{roll:<12} {name:<22} {marks:<8.2f}")
    print("=" * 45)


# SORTING & REPORTS

def display_sorted_records(students):
    print("\n--- Sort Records ---")
    if not students:
        print("No student records available.")
        return

    print("1. Sort by Name (A-Z)")
    print("2. Sort by Marks (High to Low)")
    choice = input("Enter choice (1-2): ").strip()

    if choice == "1":
        sorted_list = sorted(students.items(), key=lambda item: item[1]["name"].lower())
    elif choice == "2":
        sorted_list = sorted(students.items(), key=lambda item: item[1]["marks"], reverse=True)
    else:
        print("Invalid choice.")
        return

    print("\n" + "=" * 45)
    print(f"{'Roll No':<12} {'Name':<22} {'Marks':<8}")
    print("=" * 45)
    for roll, data in sorted_list:
        print(f"{roll:<12} {data['name']:<22} {data['marks']:<8.2f}")
    print("=" * 45)


def generate_reports(students):
    print("\n--- Performance Reports ---")
    if not students:
        print("No records available to compute metrics.")
        return

    total_students = len(students)
    marks_list = [data["marks"] for data in students.values()]
    avg_marks = sum(marks_list) / total_students
    highest_mark = max(marks_list)
    lowest_mark = min(marks_list)

    toppers = [f"{data['name']} (Roll: {roll})" for roll, data in students.items() if data["marks"] == highest_mark]

    print("\n" + "-" * 35)
    print(f"Total Enrolled Students : {total_students}")
    print(f"Class Average Marks     : {avg_marks:.2f}")
    print(f"Highest Score           : {highest_mark:.2f}")
    print(f"Lowest Score            : {lowest_mark:.2f}")
    print(f"Topper(s)               : {', '.join(toppers)}")
    print("-" * 35)


# AUTHENTICATION & MAIN MENU

def authenticate():
    """Verify administrator identity."""
    print("=" * 40)
    print("      ADMIN LOGIN REQUIRED")
    print("=" * 40)
    attempts = 3
    while attempts > 0:
        username = input("Username: ").strip()
        # Uses getpass to hide typing where supported; falls back to input
        try:
            password = getpass.getpass("Password: ")
        except Exception:
            password = input("Password: ")

        if ADMIN_CREDENTIALS.get(username) == password:
            print("\nAuthentication successful. Welcome, Admin!\n")
            return True
        else:
            attempts -= 1
            print(f"Invalid credentials. Attempts remaining: {attempts}")

    print("Access denied. Exiting application.")
    return False


def main():
    if not authenticate():
        return

    students = load_students()

    while True:
        print("\n" + "=" * 40)
        print("     STUDENT MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. Add Student Record")
        print("2. Update Student Record")
        print("3. Delete Student Record")
        print("4. Search Student")
        print("5. View Sorted Records")
        print("6. Generate Performance Reports")
        print("7. Exit")
        print("=" * 40)

        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            add_student(students)
        elif choice == "2":
            update_student(students)
        elif choice == "3":
            delete_student(students)
        elif choice == "4":
            search_student(students)
        elif choice == "5":
            display_sorted_records(students)
        elif choice == "6":
            generate_reports(students)
        elif choice == "7":
            print("Changes saved. Goodbye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 7.")


if __name__ == "__main__":
    main()