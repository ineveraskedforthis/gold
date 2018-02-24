import sys
import os
import pygame
import random
import tkinter as tk
import copy
from math import sqrt
from GameClasses import *
from StateTemplates import *
from pygame.locals import *
from AIStates import *


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('game')
myfont = pygame.font.SysFont('timesnewroman', 18)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is None:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def get_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

game_background, tmp = load_image('game_background.png')
info_bar_image, info_bar_rect = load_image('info_bar.png')
image_pause_button_idle, tmp = load_image('pause_button_idle.png')
image_pause_button_hovered, tmp = load_image('pause_button_hovered.png')
image_pause_button_pressed, tmp = load_image('pause_button_pressed.png')
image_choose_button_idle, tmp = load_image('choose_fleet_button_idle.png')
image_choose_button_hovered, tmp = load_image('choose_fleet_button_hovered.png')
image_choose_button_pressed, tmp = load_image('choose_fleet_button_pressed.png')
system_image, tmp = load_image('system.png')
system_info_image, tmp = load_image('system_info_image.png')
ground_image, tmp = load_image('ground.png')
castle_image, castle_rect = load_image('castle.png')
house_image, house_rect = load_image('house.png')

BASE_TEXT_COLOR = (210, 210, 210)
GROUND_LEVEL = 390
BASE_DIST_BETWEEN_BUILDINGS = 45


class GameManager(TreeNode):
    def __init__(self):
        TreeNode.__init__(self)
        self.scenes_dict = dict()
        self.main_scene = None
        self.deleted_childs = set()

    def run(self):
        while 1:
            for i in self.deleted_childs:
                self.del_child(i)
            self.deleted_childs.clear()
            event_queue = pygame.event.get()
            for event in event_queue:
                if event.type == QUIT:
                    return
            self.update_current_scene(event_queue)
            pygame.display.update()
            pygame.time.delay(30)

    def update_current_scene(self, events):
        if self.get_len() != 0:
            for i in self.childs:
                if i.interactive:
                    i.update_events(events)
                i.update()
                i.draw()

    def delete_child(self, node):
        self.deleted_childs.add(node)


class InterfaceBlock(TreeNode):
    def __init__(self, rect, background_image, is_interactive = True):
        TreeNode.__init__(self)
        self.rect = rect
        self.background_image = background_image
        self.deleted_childs = set()
        self.interactive = is_interactive

    def update(self):
        for i in self.deleted_childs:
            self.del_child(i)
        self.deleted_childs.clear()
        for i in self.childs:
            i.update()

    def update_events(self, events):
        for i in self.childs:
            i.update_events(events)

    def draw(self):
        screen.blit(self.background_image, self.rect)
        for i in self.childs:
            i.draw()

    def delete_child(self, node):
        self.deleted_childs.add(node)

class Game(InterfaceBlock):
    def __init__(self):
        InterfaceBlock.__init__(self, (0, 0, 500, 500), game_background)
        self.tick = 0
        self.topinfobar = TopInfoBar()
        self.add_node(self.topinfobar)
        self.paused = False
        self.camera = (0, 0)
        self.buildings = set()
        self.actors = set()
        self.infobar = InfoBar()
        self.add_node(self.infobar)
        self.next_building_x = 0
        self.castle = Castle(self, self.next_building_x)
        self.add_buiding(self.castle)
        self.actors.add(Peasant(self, 0))
        self.actors.add(TaxCollector(self, 10))
        self.actors.add(TaxCollector(self, 15))
        self.actors.add(TaxCollector(self, 20))
        self.build_queue = Queue()
        self.build('house')


    def update(self):
        InterfaceBlock.update(self)
        if not self.paused:
            self.tick += 1
            for i in self.buildings:
                i.update()
            for i in self.actors:
                i.update()

    def get_tick(self):
        return self.tick()

    def press_pause_button(self):
        self.paused = not self.paused

    def draw(self):
        screen.blit(self.background_image, self.rect)
        (x, y) = self.camera
        for i in self.buildings:
            if x + 500 >= i.x >= x:
                screen.blit(i.get_image(), i.get_rect(self.camera))
        for i in self.actors:
            if x + 500 >= i.x >= x:
                screen.blit(i.get_image(), i.get_rect(self.camera))
        screen.blit(ground_image, (0, GROUND_LEVEL - y))
        for i in self.childs:
            i.draw()


    def update_events(self, events):
        InterfaceBlock.update_events(self, events)
        (x, y) = self.camera
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                choose_flag = True
                x2, y2 = event.pos[0], event.pos[1]
                for child in self.childs:
                    if pygame.Rect(child.rect).colliderect((x2, y2, 1, 1)):
                        choose_flag = False
                if choose_flag:
                    for i in self.actors:
                        if x + 500 >= i.x >= x:
                            if pygame.Rect(i.get_rect(self.camera)).colliderect((x2, y2, 1, 1)):
                                self.infobar.show_info(i, 'Actor')
                    for i in self.buildings:
                        if x + 500 >= i.x >= x:
                            if pygame.Rect(i.get_rect(self.camera)).colliderect((x2, y2, 1, 1)):
                                self.infobar.show_info(i, 'Building')
            if event.type == KEYUP:
                if event.key == K_UP:
                    self.camera = (x, y - 5)
                if event.key == K_DOWN:
                    self.camera = (x, y + 5)
                if event.key == K_LEFT:
                    self.camera = (x - 5, y)
                if event.key == K_RIGHT:
                    self.camera = (x + 5, y)

    def add_buiding(self, building):
        self.buildings.add(building)
        self.next_building_x += BASE_DIST_BETWEEN_BUILDINGS

    def build(self, building):
        if building == 'house':
            if self.castle.cash >= 200:
                self.add_buiding(House(self, self.next_building_x))
                self.castle.cash -= 200

    def get_untaxed_building(self):
        curr = None
        for i in self.buildings:
            if i.tax_status == 'Can be taxed' and (curr == None or (curr != None and i.cash > curr.cash)):
                curr = i
        return curr

class TopInfoBar(InterfaceBlock):
    def __init__(self):
        InterfaceBlock.__init__(self, info_bar_rect, info_bar_image)
        self.add_node(Button(image_pause_button_idle, image_pause_button_hovered, image_pause_button_pressed, (0, 0, 70, 31), action = lambda: self.parent.press_pause_button()))

    def draw(self):
        InterfaceBlock.draw(self)
        screen.blit(myfont.render('Tick: ' + str(self.parent.tick), True, BASE_TEXT_COLOR), (400, 5))

class InfoBar(InterfaceBlock):
    def __init__(self):
        InterfaceBlock.__init__(self, (0, 400, 500, 500), system_info_image)
        self.system = None

    def show_info(self, obj, type):
        self.clear()
        self.obj = obj
        self.shift = 0
        self.add_node(Label(obj.name, (10, 410)))
        if type == 'Building':
            self.add_node(UpdatingLabel(lambda: 'Cash: ' + str(obj.cash), (10, 430)))
        if obj.name == 'Castle':
            self.add_node(Label('Build:', (150, 410)))
            self.add_node(Label('House', (160, 430)))
            self.add_node(ChooseButton((220, 430, 20, 20), lambda: self.parent.build('house')))

    def update(self):
        InterfaceBlock.update(self)

class Label(InterfaceBlock):
    def __init__(self, text, pos, color = BASE_TEXT_COLOR):
        InterfaceBlock.__init__(self, pos, myfont.render(text, True, color))

class UpdatingLabel(InterfaceBlock):
    def __init__(self, text, pos, color = lambda: BASE_TEXT_COLOR):
        InterfaceBlock.__init__(self, pos, myfont.render(text(), True, color()))
        self.text = text
        self.color = color

    def draw(self):
        screen.blit(myfont.render(self.text(), True, self.color()), self.rect)

class Button(InterfaceBlock):
    def __init__(self, image_idle, image_hovered, image_pressed, rect, text = None, action = lambda: None):
        InterfaceBlock.__init__(self, rect, image_idle)
        self.image = dict()
        self.image['idle'] = image_idle
        self.image['hovered'] = image_hovered
        self.image['pressed'] = image_pressed
        self.rect = pygame.Rect(rect)
        self.status = 'idle'
        self.text = text
        self.action = action
        self.prev_status = 'idle'

    def draw(self):
        screen.blit(self.image[self.status], self.rect)
        if self.text != None:
            screen.blit(myfont.render(self.text, True, (210, 210, 210)), self.rect)

    def update_events(self, events):
        for event in events:
            if event.type == MOUSEMOTION:
                if self.rect.colliderect((event.pos[0], event.pos[1], 1, 1)) and self.status != 'pressed':
                    self.status = 'hovered'
                elif self.status != 'pressed':
                    self.status = 'idle'
            if event.type == MOUSEBUTTONDOWN:
                if self.status == 'hovered':
                    if self.status != 'pressed':
                        self.prev_status = self.status
                    self.status = 'pressed'
            if event.type == MOUSEBUTTONUP:
                if self.status == 'pressed':
                    self.action()
                    self.status = self.prev_status

class ChooseButton(Button):
    def __init__(self, rect, action = lambda: None):
        Button.__init__(self, image_choose_button_idle, image_choose_button_hovered, image_choose_button_pressed, rect, action = action)

class GameObject():
    def __init__(self, game, name = None):
        self.game = game
        self.name = name
        self.attributes = dict()

    def get(self, tag):
        if tag in self.attributes:
            return self.attributes[tag]
        return 0

    def transfer_cash(self, target, amount):
        if self.cash < amount:
            amount = self.cash
        target.cash += amount
        self.cash -= amount


class GameObjectWithImage(GameObject):
    def __init__(self, game, x, image, image_rect, name = None):
        GameObject.__init__(self, game, name)
        self.x = x
        self.image = image
        self.image_rect = image_rect

    def get_rect(self, camera):
        (x, y) = camera
        return Rect(self.x - x, GROUND_LEVEL - self.image_rect.height - y, self.image_rect.width, self.image_rect.height)

    def get_image(self):
        return self.image

    def dist(self, item):
        tmp = self.get_rect(self.game.camera)
        rect = item.get_rect(self.game.camera)
        if tmp.colliderect(rect):
            return 0
        return min(abs(tmp.left - rect.right), abs(tmp.right - rect.left))

class AnimatedGameObject(GameObjectWithImage):
    def __init__(self, game, x, image_prefix, side = 0):
        image, image_rect = load_image(image_prefix + '_idle_0.png')
        GameObjectWithImage.__init__(self, game, x, image, image_rect, name = image_prefix)
        self.animation = dict()
        self.current_animation_tick = 0
        self.current_animation = 'idle'
        self.tick = 0

        file = open(image_prefix + '_animations.txt')
        for i in file.readlines():
            anim_tag = i.split()[0]
            anim_count = int(i.split()[1])
            self.add_animation_from_tag(anim_tag, anim_count)

        self.side = side
        self.orientation = 'R'

    def get_image(self):
        if self.orientation == 'R':
            return self.animation[self.current_animation][self.current_animation_tick]
        return pygame.transform.flip(self.animation[self.current_animation][self.current_animation_tick], True, False)

    def move(self, x):
        self.x += x

    def move_to(self, x):
        self.move(-self.x + x)

    def set_orientation(self, orientation):
        if self.orientation == orientation:
            return
        self.orientation = orientation
        self.image = pygame.transform.flip(self.image, True, False)

    def add_animation(self, tag, list_of_image):
        self.animation[tag] = list_of_image

    def add_animation_from_tag(self, tag, count):
        self.animation[tag] = []
        for i in range(count):
            image, tmp = load_image(self.name + '_' + tag + '_' + str(i) + '.png')
            self.animation[tag].append(image)

    def change_animation(self, tag):
        self.current_animation_tick = 0
        self.current_animation = tag

    def next_image(self):
        self.current_animation_tick += 1
        if self.current_animation_tick >= len(self.animation[self.current_animation]):
            self.current_animation_tick = 0
        return self.animation[self.current_animation][self.current_animation_tick]

    def update(self):
        self.tick += 1
        if self.tick % 5 == 0:
            self.image = self.next_image()
            if self.orientation == 'L':
                self.image = pygame.transform.flip(self.image, True, False)
            self.tick = 0

    def check_collisions_after(self, dist):
        checking_rect = self.get_rect().inflate(dist, 0)
        if self.orientation == 'L':
            checking_rect.move_ip(dist, 0)
        for item in self.scene.Objects:
            if checking_rect.colliderect(item.get_rect()) and item.root.char.side != self.root.char.side:
                self.root.action(item)
                if self.get('pierce') == self.get('max_pierce'):
                    self.destroy()
                else:
                    self.set('pierce', self.get('pierce') + 1)



class Building(GameObjectWithImage):
    def __init__(self, game, x, image, image_rect, name, income):
        GameObjectWithImage.__init__(self, game, x, image, image_rect, name)
        self.cash = 0
        self.income = income
        self.tax_status = 'None'

    def update(self):
        if self.game.tick % 300 == 0:
            self.cash += self.income
            if self.name != 'Castle':
                self.tax_status = 'Can be taxed'

class Castle(Building):
    def __init__(self, game, x):
        Building.__init__(self, game, x, castle_image, castle_rect, 'Castle', 100)
        self.cash = 1000

class House(Building):
    def __init__(self, game, x):
        Building.__init__(self, game, x, house_image, house_rect, 'House', 10)

class Actor(AnimatedGameObject):
    def __init__(self, game, x, image_prefix, side = 0):
        AnimatedGameObject.__init__(self, game, x, image_prefix, side)
        self.speed = 1
        self.sm = StateMachine(self, ActorIdle)
        self.state = 'idle'

    def update(self):
        AnimatedGameObject.update(self)
        self.sm.update()

class AIActor(Actor):
    def update(self):
        Actor.update(self)
        self.AI.update()
        # print(self.AI.curr_state)
        # print(self.sm.curr_state)

class Peasant(AIActor):
    def __init__(self, game, x):
        AIActor.__init__(self, game, x, 'peasant')
        self.AI = StateMachine(self, PeasantIdle)

class TaxCollector(AIActor):
    def __init__(self, game, x):
        AIActor.__init__(self, game, x, 'taxcollector')
        self.AI = StateMachine(self, TaxCollectorIdle)
        self.target = None
        self.cash = 0


Manager = GameManager()
CurrentGame = Game()
Manager.add_node(CurrentGame)
Manager.run()