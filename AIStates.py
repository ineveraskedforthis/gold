from StateTemplates import *
from random import randint

class ActorIdle(State):
    def Enter(agent):
        agent.state = 'idle'

    def Execute(agent):
        pass

class ActorGoLeft(State):
    def Enter(agent):
        agent.set_orientation('L')
        agent.move_tick = 0
        agent.state = 'move_left'

    def Execute(agent):
        agent.move_tick += 1
        if agent.move_tick >= agent.speed:
            agent.move(-1)
            agent.move_tick = 0

class ActorGoRight(State):
    def Enter(agent):
        agent.set_orientation('R')
        agent.move_tick = 0
        agent.state = 'move_right'

    def Execute(agent):
        agent.move_tick += 1
        if agent.move_tick >= agent.speed:
            agent.move(1)
            agent.move_tick = 0


class PeasantIdle(State):
    def Execute(agent):
        tmp = agent.game.get_unrepaired_buildings()
        if tmp != None:
            agent.AI.change_state(PeasantRepairTarget)
            agent.target = tmp

class PeasantRepairTarget(State):
    def Execute(agent):
        if agent.target.repair_status == 'None' or agent.target.dead:
            agent.AI.change_state(PeasantIdle)
        elif agent.dist(agent.target) == 0:
            agent.target.increase_hp(1)
        elif agent.state == 'idle':
            if agent.target.x > agent.x:
                agent.sm.change_state(ActorGoRight)
            else:
                agent.sm.change_state(ActorGoLeft)


class TaxCollectorIdle(State):
    def Execute(agent):
        tmp = agent.game.get_untaxed_building()
        if tmp != None:
            agent.AI.change_state(TaxCollectorTaxTarget)
            tmp.tax_status = 'In process'
            tmp.tax_collector = agent
            agent.target = tmp

class TaxCollectorTaxTarget(State):
    def Execute(agent):
        if agent.target == None or agent.target.dead:
            agent.change_state(TaxCollectorIdle)
            return
        if agent.dist(agent.target) == 0:
            agent.target.transfer_cash(agent, agent.target.cash)
            agent.target.tax_status = 'None'
            agent.sm.change_state(ActorIdle)
            agent.AI.change_state(TaxCollectorReturnCashToCastle)
            agent.target = None
        elif agent.state == 'idle':
            if agent.target.x > agent.x:
                agent.sm.change_state(ActorGoRight)
            else:
                agent.sm.change_state(ActorGoLeft)

class TaxCollectorReturnCashToCastle(State):
    def Execute(agent):
        if agent.dist(agent.game.castle) == 0:
            agent.transfer_cash(agent.game.castle, agent.cash)
            agent.sm.change_state(ActorIdle)
            agent.AI.change_state(TaxCollectorIdle)
        elif agent.state == 'idle':
            agent.sm.change_state(ActorGoLeft)


class EnemyPatrol(State):
    def Execute(agent):
        tmp = agent.game.find_closest_enemy(agent)
        if tmp != None:
            agent.AI.change_state(EnemyAttackClosestEnemy)
        elif  agent.state == 'idle':
            agent.sm.change_state(ActorGoLeft)
        elif agent.state == 'move_left' and -agent.x + agent.patrol_point > agent.patrol_dist:
            agent.sm.change_state(ActorGoRight)
        elif agent.state == 'move_right' and agent.x - agent.patrol_point > agent.patrol_dist:
            agent.sm.change_state(ActorGoLeft)

class EnemyAttackClosestEnemy(State):
    def Execute(agent):
        tmp = agent.game.find_closest_enemy(agent)
        if tmp == None:
            agent.AI.change_state(EnemyPatrol)
        elif agent.dist(tmp) <= agent.get('attack_range'):
            agent.sm.change_state(ActorIdle)
            agent.attack(tmp)
        elif agent.x > tmp.x and (agent.state == 'move_right' or agent.state == 'idle'):
            agent.sm.change_state(ActorGoLeft)
        elif agent.x < tmp.x and (agent.state == 'move_left' or agent.state == 'idle'):
            agent.sm.change_state(ActorGoRight)


class WarriorPatrol(State):
    def Execute(agent):
        tmp = agent.game.find_closest_enemy(agent)
        if tmp != None:
            agent.AI.change_state(WarriorAttackClosestEnemy)
        elif agent.state == 'idle':
            agent.sm.change_state(ActorGoLeft)
        elif agent.state == 'move_left' and -agent.x + agent.patrol_point > agent.patrol_dist:
            agent.sm.change_state(ActorGoRight)
        elif agent.state == 'move_right' and agent.x - agent.patrol_point > agent.patrol_dist:
            agent.sm.change_state(ActorGoLeft)

class WarriorAttackClosestEnemy(State):
    def Execute(agent):
        tmp = agent.game.find_closest_enemy(agent)
        if tmp == None:
            agent.AI.change_state(WarriorPatrol)
        elif agent.dist(tmp) <= agent.get('attack_range'):
            agent.sm.change_state(ActorIdle)
            agent.attack(tmp)
        elif agent.x > tmp.x and (agent.state == 'move_right' or agent.state == 'idle'):
            agent.sm.change_state(ActorGoLeft)
        elif agent.x < tmp.x and (agent.state == 'move_left' or agent.state == 'idle'):
            agent.sm.change_state(ActorGoRight)
