from inventory import *
import math
from blocks import *

class Mouse:

    def __init__(self, window, world):
        self.world = world
        self.window = window
        self.tick = 4
        self.position = [0, 0]
        self.window.bind('<Motion>', self.check_position)
        self.world.window.bind("<Button-1>", self.hit)
        self.world.window.bind("<Button-3>", self.place)
        self.distance_from_player = 0
        self.mouse_on_inventory_slot = False
        self.mouse_windows = []
        self.hitCooldown = 20



    def update(self):
        self.distance_from_player = math.hypot(self.position[0] - self.world.player_coords[0] - self.world.main_player.width/2, self.position[1] - self.world.player_coords[1] - self.world.main_player.height/3)

    def check_position(self,event):
        self.mouse_on_inventory_slot = False
        self.position = [event.x, event.y]
        touching = self.world.canvas.find_overlapping(self.world.mouse.position[0], self.world.mouse.position[1], self.world.mouse.position[0], self.world.mouse.position[1])
        for touch in touching:
            for slot in self.world.inventory.slots:
                if slot.slot_GUI == touch:
                    self.mouse_on_inventory_slot = True
                    if len(self.mouse_windows) == 0:
                        Tooltip(self.world, slot)

        if self.mouse_on_inventory_slot == False:
            for window in self.mouse_windows:
                self.world.canvas.delete(window.GUI)
                self.world.canvas.delete(window.background)
                self.mouse_windows = []

    def hit(self, event):

        tool = None

        for slot in self.world.inventory.slots:
            if slot.highlighted == True:
                selected_slot = slot
        try:
            for material in self.world.materials:
                if material.name == selected_slot.item:
                    tool = material.code
                    toolObj = material
        except:
            pass
        

        touching = self.world.canvas.find_overlapping(self.world.mouse.position[0], self.world.mouse.position[1], self.world.mouse.position[0], self.world.mouse.position[1])
        if self.distance_from_player < self.world.main_player.range*100:
            for touch in touching:
                if touch in self.world.blocksID:
                    if self.world.blocksID[touch].material.code in 'GgS' and tool == 'p' or self.world.blocksID[touch].material.code in 'wl' and tool == 'a' or self.world.blocksID[touch].material.code in 'L':
                        self.world.blocksID[touch].health -= 1
                        self.world.blocksID[touch].calm_cycles = 0
                        if len(self.world.blocksID[touch].hit_textures) != 0:
                            for x in self.world.blocksID[touch].hit_textures:
                                self.world.blocksID[touch].world.canvas.delete(x)
                                self.world.blocksID[touch].hit_textures.remove(x)
                                self.world.entities.remove(x)
                        if self.world.blocksID[touch].health > 0:
                            if self.world.blocksID[touch].health == self.world.blocksID[touch].max_health -1:
                                hit = self.world.blocksID[touch].material.hit1
                            if self.world.blocksID[touch].health == self.world.blocksID[touch].max_health -2:
                                hit = self.world.blocksID[touch].material.hit2
                            if self.world.blocksID[touch].health == self.world.blocksID[touch].max_health -3:
                                hit = self.world.blocksID[touch].material.hit3
                            self.world.blocksID[touch].hit_texture = self.world.blocksID[touch].world.canvas.create_image(self.world.canvas.coords(touch)[0],self.world.canvas.coords(touch)[1], anchor=NW, image=hit)
                            self.world.blocksID[touch].hit_textures.append(self.world.blocksID[touch].hit_texture)
                            self.world.entities.append(self.world.blocksID[touch].hit_texture)
            for mob in self.world.mobs:
                if mob.object in touching:
                    
                    if toolObj.damage > 0:
                        if self.world.main_player.cooldown == 0:
                            self.world.main_player.cooldown = self.hitCooldown
                            mob.hit(toolObj.damage)


    def place(self, event):
        if self.distance_from_player < self.world.main_player.range*100:
            selected_material = None
            selected_slot = None
            
            for slot in self.world.inventory.slots:
                if slot.highlighted == True:
                    selected_slot = slot
            if selected_slot != None and selected_slot.amount > 0:
                x = round(self.world.mouse.position[0]/self.world.one_block_width - 1) + ((self.world.world_position[0]%self.world.one_block_width)/self.world.one_block_width)
                y = round(self.world.mouse.position[1]/self.world.one_block_width - 1) + ((self.world.world_position[1]%self.world.one_block_width)/self.world.one_block_width)
                cancel = False
                touching = self.world.canvas.find_overlapping(x*self.world.one_block_width + 1, y*self.world.one_block_width + 1, x*self.world.one_block_width + self.world.one_block_width - 1, y*self.world.one_block_width + self.world.one_block_width - 1)

                if self.world.main_player.player_image in touching:
                    cancel = True

                for blok in self.world.blocks:
                    if blok.block_entity in touching:
                        cancel = True

                if cancel == False:
                    for material in self.world.materials:
                        if material.name == selected_slot.item:
                            selected_material = material
                            if selected_material.isTool:
                                cancel = True
                    if cancel == False:

                        selected_slot.amount -= 1
                        selected_slot.updateText()
                        
                        newBlock = Block(selected_material, self.world, [x, y])





