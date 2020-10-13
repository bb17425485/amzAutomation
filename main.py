# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from db import MysqlPool


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    with open("keyword_bak.txt", "a") as file:
        file.write("aaaa\n")

    mp = MysqlPool()
    sql = "insert into tb_bac(abc) values(%s)"
    param = [[1],[1]]
    mp.insertMany(sql,param)






# See PyCharm help at https://www.jetbrains.com/help/pycharm/
