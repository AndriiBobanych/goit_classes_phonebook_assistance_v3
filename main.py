from collections import UserDict
from datetime import datetime
import pickle

from decorators import parser_error_handler, command_error_handler

commands_dict = {
    "hello",
    "add contact",
    "add phone",
    "add birthday",
    "change phone",
    "delete contact",
    "delete phone",
    "delete birthday",
    "days to birthday",
    "phone",
    "find",
    "show all",
    "good bye",
    "close",
    "exit",
}


class Field:
    def __init__(self, value: str):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    pass


class Phone(Field):
    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value):
        phone_number = (
            value.strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        if phone_number.isdigit() and phone_number.startswith("380") and len(phone_number) == 12:
            self._value = "+" + phone_number
        else:
            self._value = None
            print(f"Entered number '{value}' is not valid. Please use format: '+38-0XX-XXX-XX-XX'")


class Birthday(Field):
    @property
    def value(self) -> datetime.date:
        return self._value

    @value.setter
    def value(self, value):
        try:
            self._value = datetime.strptime(value, "%d-%m-%Y").date()
        except ValueError:
            print(f"Entered {value} is not correct date. Please use format: 'dd-mm-yyyy'")

    def __repr__(self):
        return datetime.strftime(self._value, "%d-%m-%Y")


class Record:

    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phone = [phone] if phone is not None else []
        self.birthday = birthday

    def add_to_phone_field(self, phone_number: Phone):
        self.phone.append(phone_number)

    def add_to_birthday_field(self, birthday: Birthday):
        self.birthday = birthday

    def change_in_phone_field(self, old_number: Phone, new_number: Phone):
        try:
            self.phone.remove(old_number)
            self.phone.append(new_number)
        except ValueError:
            print(f"Contact does not contain such phone number: {old_number}")

    def delete_from_phone_field(self, phone: Phone):
        try:
            self.phone.remove(phone)
        except ValueError:
            print(f"Contact does not contain such phone number: {phone}")

    def delete_from_birthday_field(self):
        self.birthday.value = None

    def find_in_phone_field(self, find_phone: str):
        for phone in self.phone:
            if phone.value == find_phone:
                return phone
        return None

    def days_to_birthday(self):
        current_date = datetime.now()
        if self.birthday is not None:
            birthday: datetime.date = self.birthday.value.date()
            next_birthday = datetime(year=current_date.year, month=birthday.month, day=birthday.day).date()
            if next_birthday < current_date:
                next_birthday = datetime(
                    year=next_birthday.year + 1,
                    month=next_birthday.month,
                    day=next_birthday.day,
                )
            return (next_birthday - current_date).days
        return None

    def match_pattern(self, pattern):
        if str(pattern).lower() in str(self.name.value).lower():
            return True
        for phone in self.phone:
            if pattern in phone.value:
                return True
        return False

    def __repr__(self):
        if self.birthday.value is not None:
            return f"name: {self.name.value}; number: {' '.join(phone.value for phone in self.phone)}; " \
                   f"birthday: {self.birthday.value}"
        else:
            return f"Name: {self.name.value}; Number: {' '.join(phone.value for phone in self.phone)}"


class AddressBook(UserDict):
    __book_name = "address_book.pickle"

    def __enter__(self):
        self.__restore()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__save()

    def __restore(self):
        try:
            with open(self.__book_name, "rb+") as file:
                book = pickle.load(file)
                self.data.update(book)
        except Exception:
            print("Book is not restored!")

    def __save(self):
        try:
            with open(self.__book_name, "wb+") as file:
                pickle.dump(self.data, file, protocol=pickle.HIGHEST_PROTOCOL)
                print("Book was successfully saved!")
        except Exception:
            print("Some problems arose.")

    def add_new_contact(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        new_contact = Record(name=name, phone=phone, birthday=birthday)
        self.data[name.value] = new_contact

    # def delete_contact(self, name: Name):
    #     try:
    #         self.data.pop(name.value)
    #     except ValueError:
    #         return None

    def __iter__(self):
        self.page = 0
        self._items_per_page = 20
        return self

    def __next__(self):
        records = list(self.data.items())
        start_index = self.page * self._items_per_page
        end_index = (self.page + 1) * self._items_per_page
        self.page += 1
        if len(records) > end_index:
            to_return = records[start_index:end_index]
        else:
            if len(records) > start_index:
                to_return = records[start_index:len(records)]
            else:
                to_return = records[:-1]
        return [{record[1]: record[0]} for record in to_return]

    def find_by_name(self, name):
        try:
            return self.data[str(name).lower().capitalize()]
        except KeyError:
            return None

    # def find_by_phone(self, phone):
    #     for record in self.data.values():
    #         if phone in [number.value for number in record.phone]:
    #             return record
    #         else:
    #             return None

    def find_by_pattern(self, pattern):
        matched_contacts = []
        for record in self.data.values():
            if record.match_pattern(pattern):
                matched_contacts.append(record)
        return matched_contacts


class UserInputParser:

    @parser_error_handler
    def parse_user_input(self, user_input: str) -> tuple[str, list]:
        for command in commands_dict:
            normalized_input = " ".join(user_input.lower().strip().split(" "))
            if normalized_input.startswith(command):
                parser = getattr(self, "_" + command.replace(" ", "_"))
                return parser(user_input=normalized_input)
        raise ValueError

    def _hello(self, user_input: str):
        return "hello", []

    def _add_contact(self, user_input: str):
        username, number, *birthday = user_input.lstrip("add contact").strip().split(" ")
        if len(username) > 0 and len(number) > 0:
            username = username.capitalize()
            return "add contact", [username, number, *birthday]
        else:
            raise ValueError

    def _add_phone(self, user_input: str):
        username, number = user_input.lstrip("add phone").strip().split(" ")
        if len(username) > 0 and len(number) > 0:
            username = username.capitalize()
            return "add phone", [username, number]
        else:
            raise ValueError

    def _add_birthday(self, user_input: str):
        username, birthday = user_input.lstrip("add birthday").strip().split(" ")
        if len(username) > 0 and len(birthday) > 0:
            username = username.capitalize()
            return "add birthday", [username, birthday]
        else:
            raise ValueError

    def _change_phone(self, user_input: str):
        username, old_number, new_number = user_input.lstrip("change phone").strip().split(" ")
        if len(username) > 0 and len(old_number) > 0 and len(new_number) > 0:
            username = username.capitalize()
            return "change phone", [username, old_number, new_number]
        else:
            raise ValueError

    def _delete_contact(self, user_input: str):
        input_list = user_input.lstrip("delete contact").strip().split(" ")
        username = input_list[0]
        if len(username) > 0:
            username = username.capitalize()
            return "delete contact", [username]
        else:
            raise ValueError

    def _delete_phone(self, user_input: str):
        username, number = user_input.lstrip("delete phone").strip().split(" ")
        if len(username) > 0 and len(number) > 0:
            username = username.capitalize()
            return "delete phone", [username, number]
        else:
            raise ValueError

    def _delete_birthday(self, user_input: str):
        input_list = user_input.lstrip("delete birthday").strip().split(" ")
        username = input_list[0]
        if len(username) > 0:
            username = username.capitalize()
            return "delete birthday", [username]
        else:
            raise ValueError

    def _days_to_birthday(self, user_input: str):
        input_list = user_input.lstrip("days to birthday").strip().split(" ")
        username = input_list[0]
        if len(username) > 0:
            username = username.capitalize()
            return "days to birthday", [username]
        else:
            raise ValueError

    def _phone(self, user_input: str):
        input_list = user_input.lstrip("phone").strip().split(" ")
        username = input_list[0]
        if len(username) > 0:
            username = username.capitalize()
            return "phone", [username]
        else:
            raise ValueError

    def _find(self, user_input: str):
        input_list = user_input.lstrip("find").strip().split(" ")
        pattern = input_list[0]
        if len(pattern) > 0:
            return "find", [pattern]
        else:
            raise ValueError

    def _show_all(self, user_input: str):
        if user_input.lower().strip() == "show all":
            return "show all", []
        else:
            raise ValueError

    def _exit(self, user_input: str):
        if user_input.lower().strip() == "good bye":
            return "exit", []
        elif user_input.lower().strip() == "close":
            return "exit", []
        elif user_input.lower().strip() == "exit":
            return "exit", []
        else:
            raise ValueError

    def _good_bye(self, user_input: str):
        return self._exit(user_input)

    def _close(self, user_input: str):
        return self._exit(user_input)


class CommandLineInterface:

    def __init__(self):
        self._book = None
        self._parsers = UserInputParser()

    @staticmethod
    def phone_validity(number: str):
        phone_number = (
            number.strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        if phone_number.isdigit() and phone_number.startswith("380") and len(phone_number) == 12:
            return True
        else:
            return False

    @command_error_handler
    def hello_handler(self, *args):
        return f"Hello, how can I help you?"

    @command_error_handler
    def add_contact_handler(self, username: str, number: str, birthday=None):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            if current_record.find_in_phone_field(number) is not None:
                raise ValueError(f"Contact with name '{username}' and phone {number} already exist in phonebook")
            else:
                user_decision = input(f"Contact with name '{username}' already exist in phonebook. "
                                      f"Do you want to add phone '{number}' to existing record? "
                                      f"Please print 'yes' or 'no': ")
                if user_decision == "yes":
                    current_record.add_to_phone_field(Phone(number))
                else:
                    pass
        else:
            if self.phone_validity(number):
                self._book.add_new_contact(name=Name(username), phone=Phone(number), birthday=Birthday(birthday))
                return f"New contact with name '{username}' and phone '{number}' was added successfully to phonebook"
            else:
                return f"Entered '{number}' is not a phone number.\nPlease use format: '+38-0XX-XXX-XX-XX'"

    @command_error_handler
    def add_phone_handler(self, username: str, number: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            if current_record.find_in_phone_field(number) is not None:
                raise ValueError(f"Contact with name '{username}' and phone {number} already exist in phonebook")
            current_record.add_to_phone_field(Phone(number))
            return f"Phone '{number}' was added successfully to existing contact'{username}'"
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def add_birthday_handler(self, username: str, birthday: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            if current_record.birthday.value is not None:
                user_decision = input(f"In contact with name '{username}' "
                                      f"is already indicated birthday '{current_record.birthday.value}"
                                      f"Do you want to change it? Please print 'yes' or 'no': ")
                if user_decision == "yes":
                    current_record.add_to_birthday_field(birthday=Birthday(birthday))
                    return f"For contact'{username}' birthday was changed successfully to new '{birthday}'"
                else:
                    pass
            current_record.add_to_birthday_field(Birthday(birthday))
            return f"Birthday '{birthday}' was added successfully to contact'{username}'"
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def change_phone_handler(self, username: str, old_number: str, new_number: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            old_phone = current_record.find_in_phone_field(old_number)
            new_phone = Phone(new_number)
            if old_phone is not None:
                if self.phone_validity(old_number) and self.phone_validity(new_number):
                    current_record.change_in_phone_field(old_phone, new_phone)
                    return f"Number for contact '{username}' was changed successfully to '{new_number}'"
                else:
                    return f"Entered '{new_number}' or '{old_number}' is not a phone number.\n" \
                           f"Please use format: '+38-0XX-XXX-XX-XX'"
            else:
                raise ValueError(f"Number '{old_number}' for contact '{username}' "
                                 f"does not exist in phonebook. Please check it again.")
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def delete_contact_handler(self, username: str):
        if self._book.find_by_name(username):
            self._book.pop(username)
            return f"Contact '{username}' was deleted successfully from your phonebook"
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def delete_phone_handler(self, username: str, number: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            phone_to_delete = current_record.find_in_phone_field(number)
            if phone_to_delete is not None:
                if self.phone_validity(number):
                    current_record.delete_from_phone_field(phone_to_delete)
                    return f"Number '{number}' was deleted successfully from contact '{username}'"
                else:
                    return f"Entered '{number}' is not a phone number.\n" \
                           f"Please use format: '+38-0XX-XXX-XX-XX'"
            else:
                raise ValueError(f"Number '{number}' for contact '{username}' "
                                 f"does not exist in phonebook. Please check it again.")
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def delete_birthday_handler(self, username: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            if current_record.birthday.value is not None:
                current_record.delete_from_birthday_field()
                return f"For contact'{username}' birthday was deleted successfully "
            else:
                return f"Contact with name '{username}' does not contain any birthday."
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def days_to_birthday_handler(self, username: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            if current_record.birthday.value is not None:
                current_record.days_to_birthday()
            else:
                return f"Contact with name '{username}' does not contain any birthday."
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def phone_handler(self, username: str):
        if self._book.find_by_name(username):
            current_record: Record = self._book.find_by_name(username)
            return str(current_record)
        else:
            raise ValueError(f"Contact with name '{username}' does not exist in phonebook.")

    @command_error_handler
    def show_all_handler(self, *args):
        if len(self._book) == 0:
            return "Your phonebook is empty yet. Please add new contacts."
        else:
            first_string = "Your phonebook has the following contacts:\n"
            contact_lines = "\n".join(str(record) for record in list(self._book.data.values()))
            return first_string + contact_lines

    @command_error_handler
    def exit_handler(self, *args):
        raise SystemExit("\nThank you for cooperation. Good bye!\nSee you later. Stay safe.\n")

    @command_error_handler
    def find_handler(self, pattern):
        first_string = "The following contacts match the search:\n"
        contact_lines = "\n".join(
            str(record) for record in list(self._book.find_by_pattern(pattern))
        )
        if len(contact_lines) > 0:
            return first_string + contact_lines
        else:
            return "Your phonebook doesn't contain the contacts that are matching to search."

    def setup_book(self, book):
        self._book = book

    def run_program(self):

        with AddressBook() as book:
            self.setup_book(book)

            name_input = input("Hello! What is your name?\nPlease enter: ")
            print(f"\n{name_input.lower().capitalize()}, nice to meet you. let's start.\n")

            print("""You can use the following commands for your phonebook:
    //first command - than arguments//
    - hello - to start the process
    - add contact "name" "phone-number" "*birthday" -> to add new contact to your phonebook 
                                                       (*birthday also could be indicated, as option);
    - add phone "name" "phone-number" -> to add a phone for existing contact with this name;
    - add birthday "name" "birthday" -> to set up new (or change existing) birthday for contact with this name;
    - change phone "name" "old-phone" "new-phone" -> to set up new number for contact with this name;
    - delete contact "name" -> to delete the contact with this name from phonebook (if exist);
    - delete phone "name" "phone-number" -> to delete phone from the contact with this name;
    - delete birthday "name" -> to delete the birthday from the contact with this name;
    - days to birthday "name" -> to check how many days are left fot the contact's birthday (if indicated b/d);
    - phone "name" -> to see the phone numbers for the contact with this name (if exist);
    - show all -> to see all contacts in your phonebook (if you have added at least 1);
    - find "name" or "phone" -> to find contacts that are matching to entered key-letters or key-digits;
    - good bye / close / exit -> to finish work and close session;
    """)

            while True:
                user_input = input("Please enter command: ")
                result = self._parsers.parse_user_input(user_input=user_input)
                if len(result) != 2:
                    print(result)
                    continue
                command, arguments = result
                command_handler = getattr(self, command.replace(" ", "_") + "_handler")
                try:
                    command_response = command_handler(*arguments)
                    print(command_response)
                except SystemExit as e:
                    print(str(e))
                    break


if __name__ == "__main__":
    cli = CommandLineInterface()
    cli.run_program()
