from tkinter import *
from PIL import Image,ImageTk
import math

class ToolMaterial:
    def __init__(self, name, durability, world):

        self.hex_color = False

        self.code = ''
        self.name = name
        self.isTool = True
        self.texture_drop = Image.open(f'{self.name}drop.png')
        self.stack = 1
        self.damage = 0
        self.durability = durability
        
        if self.name.lower() == 'pickaxe':
            self.code = 'p'
        elif self.name.lower() == 'axe':
            self.code = 'a'
        elif self.name.lower() == 'sword':
            self.code = 's'
            self.damage = 1


        world.materials.append(self)


class Tool:
    def __init__(self, world, tool_material, spawn_position):
        self.world = world
        self.spawn_position = spawn_position
        self.tool_material = tool_material
        self.size = 40
        self.inventory = self.world.inventory
        self.isTool = True
        self.drop_image = ImageTk.PhotoImage((self.tool_material.texture_drop).resize((self.size, self.size), Image.ANTIALIAS))
        self.bounce_speed_limit = 50
        self.fall_speed = 5
        self.y_speed = 0
        self.grounded = False

        self.entity = world.canvas.create_image(self.spawn_position[0], self.spawn_position[1], anchor=NW, image=self.drop_image)
        self.world.entities.append(self.entity)
        self.real_position = [self.spawn_position[0], self.spawn_position[1]]
        self.position = self.world.canvas.coords(self.entity)
        self.world.items_on_ground.append(self)


    def update(self):
        self.position = self.world.canvas.coords(self.entity)
        self.distance_from_player = round(math.hypot((self.position[0]+self.size/2) - self.world.player_coords[0]-self.world.main_player.width/2, (self.position[1]+self.size/2) - self.world.player_coords[1]-self.world.main_player.height/2))

        if self.distance_from_player > (self.world.main_player.range*100/3):
            
            self.grounded = False
            touching = self.world.canvas.find_overlapping(self.real_position[0], self.real_position[1], self.real_position[0] + self.world.one_block_width, self.real_position[1] + self.world.one_block_width + self.size)
            
            for ground in self.world.ground_tiles:
                if ground.block_entity in touching: 
                    self.grounded = True
            if self.grounded:
                self.y_speed += 1
                self.world.canvas.move(self.entity, 0, (abs(self.y_speed)-self.bounce_speed_limit/2)/10)
                if self.y_speed >= self.bounce_speed_limit:
                    self.y_speed = -self.bounce_speed_limit
            else:
                self.world.canvas.move(self.entity, 0, self.fall_speed)
                self.real_position[1] += self.fall_speed
        else:
            speed = 5
            if (self.position[0]+self.size/2) < (self.world.player_coords[0]+self.world.main_player.width/2):
                self.world.canvas.move(self.entity, speed, 0)
                self.real_position[0] += speed
            else:
                self.world.canvas.move(self.entity, -speed, 0)
                self.real_position[0] -= speed
            
            if (self.position[1]+self.size/2) < (self.world.player_coords[1]+self.world.main_player.height/2):
                self.world.canvas.move(self.entity, 0, speed)
                self.real_position[1] += speed
            else:
                self.world.canvas.move(self.entity, 0, -speed)
                self.real_position[1] -= speed

        if self.distance_from_player < (self.world.main_player.range*100/5):
            self.destroy()
            self.pick_up_block()


    def destroy(self):
        self.world.canvas.delete(self.entity)
        self.world.items_on_ground.remove(self)
        self.world.entities.remove(self.entity)

    def pick_up_block(self):
        
        for slot in self.inventory.slots:
            if slot.item == self.tool_material.name and slot.amount < self.tool_material.stack:
                slot.amount += 1
                slot.showItem()
                return
            elif slot.item == None:
                slot.item = self.tool_material.name
                slot.amount = 1
                slot.showItem()
                return