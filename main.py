from tkinter import *
from world import World

window = Tk()
window.title("majnkemf")
window.resizable(False, False)

main_world = World("world_file", window)


 
window.update()
window.mainloop()