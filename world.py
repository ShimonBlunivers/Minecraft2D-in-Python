from tkinter import *
from mobs import Zombie
from player import Player
from PIL import Image,ImageTk
from blocks import *
from inventory import *
from mouse import *
from tools import *
import math
import random


class World:
    
    def __init__(self, world_file, window):
        self.world_position = [0, 0]
        self.window = window
        self.health_symbol = "❤ "
        self.window_width = 1280
        self.window_height = 720
        self.world_time = 0
        self.day = True

        
        self.falldamage_speed = 10
        self.one_block_width = 50
        self.tick = 1000
        self.ground_tiles = []
        self.ladder_tiles = []
        self.blocks = []
        self.materials = []
        self.blocksID = {}
        self.entities = []
        self.items_on_ground = []
        self.mobs = []
        self.zombies = []

        self.world_file = open(world_file + ".txt", "r").read()

        self.world_height_size = len(self.world_file.split("\n"))
        self.world_size = max(len(elem) for elem in self.world_file.split("\n"))
        self.canvas = Canvas(self.window, bg = "#9ef4f7", width = self.window_width, height = self.window_height)

        self.mouse = Mouse(self.window, self)
        self.inventory = Inventory(self)
        self.font_size = 26
        self.stats = Label(self.window, text=f"Health - {self.health_symbol*0}              Time: {self.world_time}", font=("consolas", self.font_size))
        self.stats.pack(side="top", anchor="center")

        self.canvas.pack()


        # WORLD COLORS
        
        self.day_color = "#9ef4f7"
        self.night_color = "#111538"

        self.ground_material = Material("ground", "#54352d", True, 3, self)
        self.bedrock_material = Material("bedrock", "#474747", True, -1 , self)
        self.wood_material = Material("wood", "#a1641f", False, 3, self)
        self.leaf_material = Material("leaf", "#00b359", False, 2, self)
        self.water_material = Material("water", "#4085c9", False, -1, self)
        self.grass_material = Material("grass", "#239441", True, 3, self)
        self.stone_material = Material("stone", "#8d8d8d", True, 4, self)
        self.ladder_material = Material("ladder", "ladder", False, 2, self)

        self.pickaxe_material = ToolMaterial("pickaxe", -1, self)
        self.axe_material = ToolMaterial("axe", -1, self)
        self.sword_material = ToolMaterial("sword", -1, self)

        # TESTING

        self.pickaxe1 = Tool(self, self.pickaxe_material, [400, 1])
        self.axe1 = Tool(self, self.axe_material, [500, 1])
        self.sword1 = Tool(self, self.sword_material, [600, 1])





        self.generate()

        self.main_player = Player("player", self.window, self.canvas, [self.window_width, self.window_height], self)
        self.player_update()
        self.update()
        self.mouse_update()
        self.block_update()
        self.item_ground_update()
        self.stats_text = f"Health - {self.health_symbol*self.main_player.health}                    Time: {self.world_time}"
        self.window.bind("<KeyPress>", self.main_player.key_press)
        self.window.bind("<KeyRelease>", self.main_player.key_release)



    def generate(self):
        file = self.world_file.split("\n")
        for cell in range(len(file)):
            file[cell] = file[cell].split() 
        for column in range(self.world_height_size):
            for row in range(self.world_size):
                    for material in self.materials:
                        try:
                            if material.code == file[column][row]:
                                Block(material, self, [row, column])
                        except:
                            pass

    def update(self):
        self.stats.configure(text=self.stats_text)
        self.main_player.ground_tiles = self.ground_tiles
        self.main_player.ladder_tiles = self.ladder_tiles
        self.main_player.blocks = self.blocks

        if self.world_time == 24:
            self.world_time = 0
        if self.world_time >= 12:
            self.day = False
        else:
            self.day = True
        
        if self.world_time == 0:
            self.canvas.configure(bg = self.day_color)
        elif self.world_time == 12:
            self.canvas.configure(bg = self.night_color)

        if self.day == False:
            chance = random.randint(0,2)
            if chance == 0:
                Zombie(self, [random.randint(-200,1400), -100])

        if self.day:
            for zombie in self.zombies:
                zombie.hit(3)

        self.world_time += 1

        self.window.after(self.tick, self.update)    


    def layer_sort(self):
        self.canvas.tag_raise(self.main_player.player_image)

        for mob in self.mobs:
            self.canvas.tag_raise(mob.object)

        for block in self.blocks:
            if block.material.name == "water":
                self.canvas.tag_raise(block.block_entity)

        self.canvas.tag_raise(self.inventory.GUI)
        for slot in self.inventory.slots:
            self.canvas.tag_raise(slot.slot_GUI)
            if slot.highlighted:
                if slot.highlight != None:
                    if slot.highlight_block != None:
                        self.canvas.tag_raise(slot.highlight_block)
                    self.canvas.tag_raise(slot.highlight)
            if slot.item != None:
                self.canvas.tag_raise(slot.item_GUI)
            self.canvas.tag_raise(slot.slot_number_text)
            if slot.amount_text != None:
                self.canvas.tag_raise(slot.amount_text)
        
        if len(self.mouse.mouse_windows) != 0:
            if self.mouse.mouse_windows[0].background != None:
                self.canvas.tag_raise(self.mouse.mouse_windows[0].background)
            self.canvas.tag_raise(self.mouse.mouse_windows[0].GUI)

    def player_update(self):
        self.layer_sort()
        for mob in self.mobs:
            mob.update()

        if not self.main_player.dead:
            if self.main_player.cooldown > 0:
                self.main_player.cooldown -= 1
            self.stats_text = f"Health - {self.health_symbol*self.main_player.health}                    Time: {self.world_time}"
            if self.main_player.health <= 0:
                self.stats_text = "DIED"
                self.main_player.death()
            
            self.main_player.grounded = False
            player_coords = self.main_player.canvas.coords(self.main_player.player_image)
            self.player_coords = player_coords = self.main_player.canvas.coords(self.main_player.player_image)
            touching = self.canvas.find_overlapping(player_coords[0], player_coords[1] + self.main_player.height - 10, player_coords[0] + self.main_player.width, player_coords[1] + self.main_player.height + self.main_player.fall_speed)
            touching_head = self.canvas.find_overlapping(player_coords[0], player_coords[1], player_coords[0] + self.main_player.width, player_coords[1] + 10 + self.main_player.fall_speed)
            for ground in self.ground_tiles:
                for touch in touching:
                    if touch == ground.block_entity:      
                        self.main_player.grounded = True
                        if self.main_player.fall_speed > self.falldamage_speed:
                            self.main_player.hit(int(self.main_player.fall_speed/self.falldamage_speed))
                        self.main_player.fall_speed = 0
                for touch in touching_head:
                    if touch == ground.block_entity:
                        self.main_player.fall_speed = 0
                        
            if not self.main_player.grounded:
                self.main_player.fall_speed += self.main_player.fall_acceleration
                
            if self.main_player.player_coords[1] + self.main_player.height < self.window_height - self.window_height/4 and self.main_player.fall_speed>0:
                self.main_player.canvas.move(self.main_player.player_image, 0, self.main_player.fall_speed - self.main_player.knockback_force)
            elif self.main_player.fall_speed>0:
                self.world_position[1] -= self.main_player.fall_speed - self.main_player.knockback_force
                for blok in self.entities:
                    self.canvas.move(blok, 0, -self.main_player.fall_speed - self.main_player.knockback_force)

            if self.main_player.player_coords[1] > self.window_height/4 and self.main_player.fall_speed < 0:
                self.main_player.canvas.move(self.main_player.player_image, 0, self.main_player.fall_speed - self.main_player.knockback_force)
            elif self.main_player.fall_speed < 0:
                self.world_position[1] -= self.main_player.fall_speed - self.main_player.knockback_force
                for blok in self.entities:
                    self.canvas.move(blok, 0, -self.main_player.fall_speed - self.main_player.knockback_force)
            self.main_player.control()

            self.window.after(self.main_player.tick, self.player_update)

    def mouse_update(self):
        self.mouse.update()
        for slot in self.inventory.slots:
            slot.update()
        self.window.after(self.mouse.tick, self.mouse_update)

    def item_ground_update(self):
        for item in self.items_on_ground:
            item.update()
        self.window.after(10, self.item_ground_update)

    def block_update(self):

        for blok in self.blocks:
            blok.update()
        self.window.after(10, self.block_update)


