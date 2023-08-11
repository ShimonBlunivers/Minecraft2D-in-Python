from tkinter import *
from PIL import Image,ImageTk

class Tooltip:
    def __init__(self, world, slot):
        self.world = world
        self.slot = slot
        self.font_size = 20
        self.GUI = self.world.canvas.create_text(self.world.mouse.position[0], self.world.mouse.position[1], text = self.slot.item, fill="black", anchor = 'nw', font =('consolas', self.font_size))
        if slot.item != None:
            self.background = self.world.canvas.create_rectangle(self.world.canvas.bbox(self.GUI), fill='#dbdbdb', width = 2)
        else:
            self.background = None
        
        self.world.mouse.mouse_windows.append(self)
        self.render()

    def render(self):
        if self.background != None:
            self.world.canvas.moveto(self.GUI ,self.world.mouse.position[0] + self.font_size/4, self.world.mouse.position[1] - self.font_size - self.font_size/2)
            self.world.canvas.moveto(self.background ,self.world.mouse.position[0] + self.font_size/4, self.world.mouse.position[1] - self.font_size - self.font_size/2)
            if self in self.world.mouse.mouse_windows:
                self.world.window.after(10, self.render)

class Inventory:
    def __init__(self, world):
        self.world = world
        self.slots = []
        self.GUI_color = '#adcdff'
        self.slots_number = 10
        self.GUI = self.world.canvas.create_rectangle(0, self.world.window_height - self.world.window_height/6.5, self.world.window_width + 10, self.world.window_height + 10, fill = self.GUI_color, width = 0)
        for i in range(self.slots_number):
            InventorySlot(self.world, self,[(self.world.window_width/self.slots_number)*(i+0.5), self.world.window_height - (self.world.window_height/6.5)/2], i+1)

    
    def select(self, event):
        try:
            key = int(event.keysym) -1
            if 0 <= key <= self.slots_number:
                
                if self.slots[key].highlighted == False:
                    for k in self.slots:
                        k.highlighted = False
                    self.slots[key].highlighted = True

                else:
                    self.slots[key].highlighted = False
        except:
            pass


class InventorySlot:
    def __init__(self, world, inventory, position, slot_number, item = None, amount = 0):
        self.world = world
        self.inventory = inventory
        self.slot_number = slot_number
        self.position = position
        self.item = item
        self.amount = amount
        self.inventory.slots.append(self)
        self.color = '#edf3ff'
        self.size = 100
        self.border_width = 4
        self.item_size = 75
        self.font_size = 20
        self.empty = True
        self.amount_text = None
        self.highlighted = False
        self.highlight = None
        self.highlight_block = None
        self.highlight_dimensions = None

        self.generate()
        self.updateText()

    def generate(self):
        self.slot_GUI = self.world.canvas.create_rectangle(self.position[0] - self.size/2, self.position[1] - self.size/2, self.position[0] + self.size/2, self.position[1] + self.size/2, fill = self.color, width = self.border_width)
        self.slot_number_text = self.world.canvas.create_text(self.position[0] - self.item_size/2 + self.font_size, self.position[1] + self.item_size/2 - self.font_size, text=str(self.slot_number), fill="black", font =('consolas', self.font_size))
        self.highlight_dimensions = self.world.canvas.bbox(self.slot_GUI)
        self.highlight_dimensions = [self.highlight_dimensions[0] + self.border_width, self.highlight_dimensions[1] + self.border_width, self.highlight_dimensions[2] - self.border_width, self.highlight_dimensions[3] - self.border_width]
        
    def showItem(self):
        if self.item != None:
            if self.empty:
                self.item_image = ImageTk.PhotoImage((Image.open(f'{self.item}drop.png')).resize((self.item_size, self.item_size), Image.ANTIALIAS))
                self.item_GUI = self.world.canvas.create_image(self.position[0], self.position[1], image = self.item_image)
                self.updateText()
                self.empty = False
            else:
                self.updateText()

    def updateText(self):
        if self.amount <= 0:
            self.amount = 0
            self.item = None
        self.world.canvas.delete(self.highlight)
        self.world.canvas.delete(self.amount_text)
        self.amount_text = self.world.canvas.create_text(self.position[0] + self.item_size/2 - self.font_size, self.position[1] - self.item_size/2 + self.font_size, text=str(self.amount), fill="black", font =('consolas', self.font_size))
        self.highlight = self.world.canvas.create_rectangle(self.highlight_dimensions[0], self.highlight_dimensions[1], self.highlight_dimensions[2], self.highlight_dimensions[3], fill = '#f7ff5e')
        
    def update(self):
        self.world.canvas.delete(self.highlight_block)
        if self.highlighted and self.item != None and self.world.mouse.distance_from_player < self.world.main_player.range*100:
            x = round(self.world.mouse.position[0]/self.world.one_block_width - 1) + ((self.world.world_position[0]%self.world.one_block_width)/self.world.one_block_width)
            y = round(self.world.mouse.position[1]/self.world.one_block_width - 1) + ((self.world.world_position[1]%self.world.one_block_width)/self.world.one_block_width)

            if self.item in ['pickaxe', 'axe']:
                self.highlight_block = self.world.canvas.create_rectangle(x * self.world.one_block_width, y * self.world.one_block_width, x * self.world.one_block_width + self.world.one_block_width, y * self.world.one_block_width + self.world.one_block_width, outline = 'blue', width = 2 )
            elif self.item == 'sword':
                pass

            else:
                self.highlight_block = self.world.canvas.create_rectangle(x * self.world.one_block_width, y * self.world.one_block_width, x * self.world.one_block_width + self.world.one_block_width, y * self.world.one_block_width + self.world.one_block_width, outline = 'red', width = 2 )