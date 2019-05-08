import os

def compare_file_in_folders(the_file, folder_1,folder_2):
    f1 = open(os.path.join(folder_1, the_file)).read()
    f2 = open(os.path.join(folder_2, the_file)).read()

    diff_result = (f1 == f2)

    print (diff_result)
    return diff_result