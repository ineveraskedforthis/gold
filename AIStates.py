from StateTemplates import *

class ActorIdle(State):
    def Enter(agent):
        agent.state = 'idle'

    def Execute(agent):
        pass

class ActorGoLeft(State):
    def Enter(agent):
        agent.set_orientation('L')
        agent.move_tick = 0
        agent.state = 'move'

    def Execute(agent):
        agent.move_tick += 1
        if agent.move_tick >= agent.speed:
            agent.move(-1)
            agent.move_tick = 0

class ActorGoRight(State):
    def Enter(agent):
        agent.set_orientation('R')
        agent.move_tick = 0
        agent.state = 'move'

    def Execute(agent):
        agent.move_tick += 1
        if agent.move_tick >= agent.speed:
            agent.move(1)
            agent.move_tick = 0


class PeasantIdle(State):
    def Execute(agent):
        pass

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
        if agent.target == None:
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
