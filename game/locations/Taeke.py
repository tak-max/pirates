import random
import game.display as display
from game import combat, config, crewmate, event
from game.items import Item
import game.location as location


class Island (location.Location):

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "island"
        self.symbol = 'I'
        self.visitable = True
        self.locations = {}
        self.locations["south_cliff"] = south_cliff(self)
        self.locations["east_cliff"] = East_Cliff(self)
        self.locations["tunnel"] = Tunnel(self)
        self.locations["cave"] = Cave(self)
        self.locations["forest"] = Forest(self)
        self.locations["cliff"] = Cliff(self)

        self.starting_location = self.locations["south_cliff"]

    def enter (self, ship):
        display.announce ("arrived at cliff island", pause=False)


class south_cliff (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "south_cliff"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

    def enter (self):
        display.announce (
            "arrive at the seacliff in a rowboat. Your ship is at anchor to the south. Ahead you see a big rockface."
            )

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            display.announce ("You return to your ship.")
            self.main_location.end_visit()
        elif (verb == "north"):
            display.announce ('there seems to be no way to get up the cliff')
        elif (verb == "east"):
            config.the_player.next_loc = self.main_location.locations["east_cliff"]
        elif (verb == "west"):
            display.announce ("You walk all the way around the island on the beach. It's not very interesting.")

class East_Cliff (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "east_cliff"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.verbs['investigate'] = self


    def enter (self):
        display.announce ('You get to a new section of cliff on the east side of the island. You see a hole in the rockface. You may investigate.')


    def process_verb(self, verb, cmd_list, nouns):
        if(verb == "investigate"):
            self.HandleTunnel()
#        if verb(verb == "north" or verb == "east" or verb == "west" or verb == "south"):
#            display.announce('you end up back at your boat.')
#            self.main_location.end_visit()


    # Handles the logic and output for the tunnel
    def HandleTunnel(self):
        display.announce("As you investigate the the hole. It seems to be the entrance to a tunnel")
        choice = display.get_text_input("Do you enter the tunnel?")
        if("yes" in choice.lower()):
            self.EnterTunnel()
        else:
            display.announce("You row away from the tunnel entrance.", pause=False)
    
    def EnterTunnel(self):
        config.the_player.next_loc = self.main_location.locations["tunnel"]
        config.the_player.go = True


class Tunnel (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "tunnel"
        self.verbs['forward'] = self
        self.verbs['back'] = self
        self.verbs['run'] = self
        self.verbs['take'] = self
        self.TunnelCollapsed = False
        self.item_in_skull = GoldTooth() #Treasure from this island


    def enter (self):
        display.announce(
            f"You enter the tunnel and start walking down.\nYou hear a weird crunching as you are walking and then you notice the sound is bones crunching under your feet..."
            )
        if self.item_in_skull != None:
            display.announce('You see somthing glistening.\nYou take a closer look.\n It is a skull with a golden tooth in its mouth.')

    def process_verb(self, verb, cmd_list, nouns):
        if(verb == "investigate"):
            if self.item_in_skull != None:
                display.announce('you can take the golden tooth.')
        if(verb == "run" or verb == "back"):
            display.announce('You go back to your rowboat.')
            config.the_player.next_loc = self.main_location.locations["east_cliff"]
        if(verb == "forward"):
            self.EnterCave()
        if(verb == 'take'):
            if self.item_in_skull == None:
                display.announce ("You don't see anything to take.")
            else:
                display.announce(f"You pull the golden tooth out from the skull.")
                config.the_player.add_to_inventory([self.item_in_skull])
                self.item_in_skull = None
                config.the_player.go = True
                    

    def EnterCave(self):
        config.the_player.next_loc = self.main_location.locations["cave"]


class Cave(location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "cave"
        self.verbs['climb'] = self
        self.verbs['back'] = self
        self.verbs['up'] = self

        self.event_chance = 100
        self.events.append(GiantSpiderEvent())

    def enter(self):
        display.announce('The tunnel opens up into a cave. you hear a hissing sound above your head')

    def process_verb(self, verb, cmd_list, nouns):
        if(verb == "up" or verb == "climb"):
            config.the_player.next_loc = self.main_location.locations["forest"]
        if(verb == "back" or verb == "run"):
            config.the_player.next_loc = self.main_location.locations["tunnel"]



class GiantSpiderEvent (event.Event):

    def __init__ (self):
        self.name = " giant spider attack."

    def process (self, world):
        result = {}
        spider = GiantSpider()
        display.announce("A giant spider leaps from the ceiling and attacks your crew!")
        combat.Combat([spider]).combat()
        display.announce("The giant spider falls to the ground.")
        # Set newevents to an empty list. If I added 'self' to the list, the event would be readded upon completing, effectively making the spider respawn every turn you are in here.
        result["newevents"] = []
        # Set the result message to an empty string, as we are printing our own strings at the right time.
        result["message"] = ""

        display.announce("In the back of the cave you see a pirate stuck in the spiders webs. They seem to be alive.")
        choice = display.get_text_input("Do you help the pirate?")
        if("yes" in choice.lower()):
            display.get_text_input("You cut the web down and free the pirate and he joins your crew.")
            c = crewmate.CrewMate()
            config.the_player.pirates.append (c)
            config.the_player.nouns[c.get_name().lower()] = c
        else:
            display.announce("You leave the pirate.", pause=False)
        choice = display.get_text_input("Do you want to harvest the spiders meat?")
        if("yes" in choice.lower()):
            display.announce('you gain 25 food!')
            config.the_player.ship.food += 25
        else:
            display.announce('you leave the spider')
        display.announce('You see a rope ladder at the back of the cave leading up into the ceiling of the cave')
        return result


class GiantSpider(combat.Monster):

    # Giant spider can bite or slash. Both do the same damage, it's just a flavor difference.
    # 100-110 speed. 64-96 health.
    def __init__ (self):
        attacks = {}
        attacks["bite"] = ["bites",random.randrange(80,100), (5,15)]
        attacks["slash"] = ["slashes",random.randrange(60,80), (5,15)]
        super().__init__("Giant Spider", random.randint(64,96), attacks, 100 + random.randint(0, 10))
        self.type_name = "Giant Spider"

class Forest(location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "forest"
        self.verbs['investigate'] = self
        self.verbs['north'] = self
        self.verbs['east'] = self
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.pedestalused = False

    def enter(self):
        var = True
        if var == True:
            display.announce('The ladder leads to a hole in a forest floor. \nAs the last pirate climbs up the ladder breaks, the other pirates are just able to pull him up.')
            var = False
        display.announce('you see a pedestal with numbers and symbols. You may investigate.')

    

    def process_verb(self, verb, cmd_list, nouns):
        if(verb == "investigate"):
            if self.pedestalused == False:
                display.announce('You walk up to the pedastal and you see symbols and a bowl with shiny pebbles around it.')
                choice = display.get_text_input("Do you want to play the game?")
                if("yes" in choice.lower()):
                    self.HandlePedestal()
                else:
                    ('you leave the pedestal')
        if(verb == "north" or verb == "east" or verb == "west" or verb == "south"):
            config.the_player.next_loc = self.main_location.locations["cliff"]
            

    def HandlePedestal(self):
        num_correct = False
        awnser = random.randint(1,10)
        while num_correct == False:
            try:           
                num = 'lol'

                num = display.get_text_input('How many pebbles do you put in the bowl?')
                num = int(num)

                awnser = random.randint(1,10)

                while num != awnser:
                    if num < awnser:
                        display.announce('the pedastal displays the symbol: ^')
                        num = display.get_text_input('How many pebbles do you put in the bowl?')
                        num = int(num)
                    elif num > awnser:
                        display.announce('the pedastal displays the symbol: v')
                        num = display.get_text_input('How many pebbles do you put in the bowl?')
                        num = int(num)
                    if num == awnser:
                        num_correct = True
                if num == awnser:
                    num_correct = True
            except:
                display.announce('That is not a number.')
                
        if num_correct == True:
            self.pedestalused = True
            display.announce('The pedastal says:\nYou win. Do which you disire:\nA - jeweled crown\nB - a long rope.')
            choice = display.get_text_input("which do you choose?")
            if("a" in choice.lower()):
                config.the_player.add_to_inventory([jeweled_crown()])
            elif("b" in choice.lower()):
                config.the_player.add_to_inventory([rope()])
            



class GoldTooth(Item):
    def __init__(self):
        super().__init__("gold tooth", 50)

class jeweled_crown(Item):
    def __init__(self):
            super().__init__("jeweled crown", 1000)

class rope(Item):
    def __init__(self):
        super().__init__("rope", 5)

class Cliff(location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "cliff"
        self.verbs['investigate'] = self
        self.verbs['north'] = self
        self.verbs['east'] = self
        self.verbs['south'] = self
        self.verbs['west'] = self

    def enter(self):
        display.announce('You walk up to the cliff edge.\nYou see your rowboat at the bottom.')
        if "rope" in config.the_player.inventory:
            choice = display.get_text_input('Do you want to climb down with your rope?')
            if ("yes" in choice.lower()):
                self.main_location.end_visit()
                config.the_player.go = True
                display.announce('you climb down and row back to the ship.')
        else:
            choice = display.get_text_input('Do you want to jump down?')
            if ("yes" in choice.lower()):
                self.main_location.end_visit()
                config.the_player.go = True
                dead = config.the_player.pirates.pop()
                display.announce(f'{dead} falls on the rocks and dies.\nthe rest climb in the rowboat and get back to the ship')
    
    def process_verb(self, verb, cmd_list, nouns):
        if(verb == "north" or verb == "east" or verb == "west" or verb == "south"):
            config.the_player.next_loc = self.main_location.locations["forest"]
                
