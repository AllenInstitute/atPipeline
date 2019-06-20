import os

def compare_file_in_folders(the_file, folder_1,folder_2):
    print("Checking file: " + the_file)
    print("Folder 1: " + folder_1)
    print("Folder 2: " + folder_2)
 
    try:
        f1 = open(os.path.join(folder_1, the_file)).read()
    except IOError:
        print ("Failed opening/reading the file: " + os.path.join(folder_1, the_file))
        return False

    try:
        f2 = open(os.path.join(folder_2, the_file)).read()
    except IOError:
        print ("Failed opening/reading the file: " + os.path.join(folder_2, the_file))
        return False

    diff_result = (f1.strip()== f2.strip())

    print ("Diff result: " + str(diff_result))
    return diff_result
