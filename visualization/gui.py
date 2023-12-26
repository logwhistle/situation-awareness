# import tkinter
#
# import tkinter
# import tkinter.messagebox
#
#
# def session1_subject1():
#     tkinter.messagebox.showinfo("Hello Python", "   开始运行 \n 科目一 情景一")
#
#
# def session1_subject2():
#     tkinter.messagebox.showinfo("Hello Python", "   开始运行 \n 科目一 情景二")
#     print('h')
#     return 2
#
#
# def test():
#     print(5)
#     return 5
#
#
# # button 里面的command就是调用函数，并执行那个函数
# # 如果想要改变按钮的位置，可以增加frame来设置边框、类似于css里面的div
#
# windows = tkinter.Tk()  # 实例化出一个父窗口
# A = tkinter.Label(windows, text='TJU_RHZT', bg='yellow', font=('times new roman', 20), width=20, height=3)
# B = tkinter.Button(activebackground="green", bd=5, font=('Arial', 15), text="start", command=session1_subject1,
#                    width=10, height=3)
# C = tkinter.Button(activebackground="red", text="stop", command=test, bd=5, font=('Arial', 15), width=10, height=3)
#
# A.pack()
# B.pack()
# C.pack()
# windows.mainloop()
#
# a = test()
