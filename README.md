# Description for HW-12

This is a package that contain main module and decorators for dealing with user's contact book with using of classes. 
Was prepared as a homework for unit 12 of Python core course in CoIT school.

Contain classes:
 - AddressBook (which inherits from UserDict)
 - Record (which is responsible for the logic of adding/removing/editing optional fields and storing the mandatory field Name)
 - Field (which will be the parent of all fields)
 - Name (required field with name), Phone (optional field with phone number) and Birthday (optional field with date of birth)
 - To Phone and Birthday were added setters. To Record was added function to count days to nearest birthday. To AddressBook was added pagination iterator.

Command line interface was implemented.
You could use commands to add, change, delete, show all, find contacts.

Pattern was added to arrange the search of matching contacts in phonebook by key-symbols.

All handler functions and executing parser function are covered by decorators for dealing with errors.

Main package with modules is located here  
https://github.com/AndriiBobanych/goit_classes_phonebook_assistance_v3


Author: <b>Andrii Bobanych<b>