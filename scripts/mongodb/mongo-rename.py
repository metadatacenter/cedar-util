#!/usr/local/bin/python3

# Created: 2017-Oct-25
# Last update: 2017-Oct-25
# mongo-rename.py: Utility to (1) copy a MongoDB database and (2) swap the content of two MongoDB databases.

# Import the modules needed to run the script.
import sys, os
from pymongo import MongoClient
import uuid

# =======================
#        CONSTANTS
# =======================

MONGO_HOST='localhost'
MONGO_ROOT_USER_NAME='<yourUsername>'
MONGO_ROOT_USER_PASSWORD='<yourPassword>'
menu_actions = {}

# =======================
#        FUNCTIONS
# =======================


def get_mongo_client():
    return MongoClient('mongodb://%s:%s@%s' % (MONGO_ROOT_USER_NAME, MONGO_ROOT_USER_PASSWORD, MONGO_HOST))

# Main menu
def main_menu():
    #os.system('clear')
    print("\nPlease choose an option:")
    print("1. List my MongoDB databases")
    print("2. Create a copy of an existing database")
    print("3. Swap the content of two databases")
    print("4. Exit")
    choice = input(">>  ")
    exec_menu(choice)
    return


# Execute menu
def exec_menu(choice):
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print("Invalid selection, please try again.\n")
            menu_actions['main_menu']()
    return


# Menu to list databases
def choice_list_dbs():
    c = get_mongo_client()
    print('\nList of MongoDB databases at ' + MONGO_HOST + ':')
    for n in c.database_names():
        print('- ' + n)
    main_menu()
    return


# Copy DB (step 1)
def choice_copy_db():
    print("\nEnter the name of the DB that you want to copy:")
    db_name = input(">>  ")
    c = get_mongo_client()
    db_names = c.database_names()
    if db_name in db_names:
        choice_copy_db_step2(c, db_name, db_names)
    else:
        print("Database '" + db_name + "' does not exist! Please try again.")
        exec_menu('2')
    return


# Copy DB (step 2)
def choice_copy_db_step2(c, db_name, db_names):
    print("\nEnter the name of the new database (copy of '" + db_name + "'):")
    db_copy_name = input(">>  ")
    if db_copy_name in db_names:
        print("Database '" + db_copy_name + "' already exists. You cannot overwrite it! Please try again.")
        choice_copy_db_step2(c, db_name, db_names)
    else:
        print('Creating copy of the \'' + db_name + '\' database. New database: \'' + db_copy_name + '\'')
        c.admin.command('copydb', fromdb=db_name, todb=db_copy_name)
        print('Done.')
        exec_menu('main_menu')
    return


# Swap DBs
def choice_swap_dbs():
    c = get_mongo_client()
    print("\nEnter the names of the databases that you want to swap:")
    db1_name = input("database 1 >>  ")
    if db1_name not in c.database_names():
        print("The database '" + db1_name + "' does not exist. Please try again.")
        choice_swap_dbs()
    db2_name = input("database 2 >>  ")
    if db2_name not in c.database_names():
        print("The database '" + db2_name + "' does not exist. Please try again.")
        choice_swap_dbs()
    print("Do you want to swap the content of '" + db1_name + "' and '" + db2_name + "'?")
    swap_confirm = input("Yes/No? ")
    tmp_db_name = 'db_' + str(uuid.uuid1());
    if swap_confirm.lower() == 'yes':
        print('Copying \'' + db1_name + '\' to \'' + tmp_db_name + '\'...')
        c.admin.command('copydb', fromdb=db1_name, todb=tmp_db_name)
        print('Dropping \'' + db1_name + '\'...')
        c.drop_database(db1_name)

        print('Copying \'' + db2_name + '\' to \'' + db1_name + '\'...')
        c.admin.command('copydb', fromdb=db2_name, todb=db1_name)
        print('Dropping \'' + db2_name + '\'...')
        c.drop_database(db2_name)

        print('Copying \'' + tmp_db_name + '\' to \'' + db2_name + '\'...')
        c.admin.command('copydb', fromdb=tmp_db_name, todb=db2_name)
        print('Dropping \'' + tmp_db_name + '\'...')
        c.drop_database(tmp_db_name)

        print('Done.')
        exec_menu('main_menu')
    else:
        exec_menu('main_menu')
    return


# Back to main menu
def back():
    menu_actions['main_menu']()


# Exit program
def exit():
    sys.exit()


# =======================
#    MENUS DEFINITIONS
# =======================

# Menu definition
menu_actions = {
    'main_menu': main_menu,
    '1': choice_list_dbs,
    '2': choice_copy_db,
    '3': choice_swap_dbs,
    '4': exit,
}

# =======================
#      MAIN PROGRAM
# =======================

# Main Program
if __name__ == "__main__":
    # Launch main menu
    main_menu()


