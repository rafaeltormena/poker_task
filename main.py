import sys
from statemachine import StateMachine


# CREATE CLASS WITH SOME USEFULL PLAYER INFO
class player(object):

    def __init__(self):
        self.name = ''
        self.stack = 0
        self.floatStack = 0
        self.seat = -1
        self.actualBet = 0
        self.wonPot = 0
        self.balance = 0



# CREATE HAND CLASS WITH OUTPUT INFORMATION
class hand(object):
    
    def __init__(self):
        self.handID = -1
        self.blinds = -1
        self.dateTime = -1
        self.buttonPos = -1
        self.players = []
        self.currency = ''
        self.foldedPreflop = []
        self.foldedFlop = []
        self.foldedTurn = []
        self.foldedRiver = []
        self.totalPot = -1
        self.totalRake = -1
        self.board = ''
        self.cards = []
        


    # add bet amount to specific player
    def addBet(self, name, amount):
        for player in self.players:
            if name == player.name:
                player.actualBet += float(amount[len(self.currency):])
                break



    # add pot won amount to specific player
    def addWon(self, name, amount):
        for player in self.players:
            if name == player.name:
                player.wonPot += float(amount[len(self.currency):])
                break



    # show player from the list if any
    def showFoldedIfAny(self, playerList, header):
        if len(playerList):
            print(header)
            for player in playerList:
                print('- {0}'.format(player))



    # show a list if there are 2+ players that not folded in previous stages of the game
    def showPlayedIfAny(self, playerList, header):
        if len(self.players) > len(playerList) +1:
            print(header)
            for player in self.players:
                if player.name not in playerList:
                    print('- {0}'.format(player.name))



    # outputs all the info
    def show(self):
        
        print('handID: {0}'.format(self.handID))
        print('The Blinds: {0}'.format(self.blinds))
        print('Date and Time: {0}'.format(self.dateTime))
        print('Button position: {0}'.format(self.buttonPos))

        print('Players names, stacks and seats:')
        for player in self.players:
            print('- {0}, {1}, {2}'.format(player.name, player.stack, player.seat))

        self.showFoldedIfAny(self.foldedPreflop, 'Players that folded preflop (if any)')

        self.showPlayedIfAny(self.foldedPreflop, 'Players that played the flop (if any)')

        self.showPlayedIfAny(self.foldedPreflop + self.foldedFlop, 'Players that played the turn (if any)')

        self.showFoldedIfAny(self.foldedTurn, 'Players that folded in the turn (if any)')

        self.showPlayedIfAny(self.foldedPreflop + self.foldedFlop + self.foldedTurn, 'Players that played the river (if any)')
        
        print('Total pot and rake')
        print('- {0}, {1}'.format(self.totalPot, self.totalRake))

        if len(self.board):
            print('The Board (if any)')
            print('- {0}'.format(self.board))

        if len(self.cards):
            print('Players that reach the showdown and theirs hole cards')
            for card in self.cards:
                print(card)

        print('The stack difference of each player after the hand in %  (2 decimal places)')
        for player in self.players:
            player.floatStack = float(player.stack[len(self.currency):])
            
            player.balance = player.wonPot - player.actualBet
            #print('- {:}: {:}, {:}, {:}'.format(player.name, player.stack, player.actualBet, player.wonPot))
        
            print('- {:}: {:}{:.2f} ({:}{:.2f}%)'.format(player.name, self.currency, player.floatStack + player.balance,
                                                      ["", "+"][player.balance > 0],100*player.balance/player.floatStack))

        print('\n')
        # END OF HAND.SHOW()



# --- defining all handlers for the state machine ---

def findState_transitions(txt):
    line = txt[0]

    # avoid reaching here with the wrong sentence (caused by sitting out)
    if line[:4] != "*** ":
        newState = "findState_state"
        return (newState, txt[1:])

    key = line.split()[1:]

    if "HOLE" in key and "CARDS" in key:
        newState = "preflop_state"
    elif "FLOP" in key:
        outputClass.board = line.split('[')[1].split(']')[0]
        newState = "flop_state"
    elif "TURN" in key:
        outputClass.board = outputClass.board + ' ' + line.split('[')[2].split(']')[0]
        newState = "turn_state"
    elif "RIVER" in key:
        outputClass.board = outputClass.board + ' ' + line.split('[')[2].split(']')[0]
        newState = "river_state"
    elif "SHOW" in key and "DOWN" in key:
        newState = "showdown_state"
    elif "SUMMARY" in key:
        newState = "summary_state"
    else:
        newState = "End_state"


    return (newState, txt[1:])



# Function to handle the header state (2 first lines)
def header_transitions(txt):
    line = txt[0]

    # get ID
    aux = line.split('#')
    outputClass.handID = aux[1].split()[0][:-1]

    # get blinds    
    aux = line.split('(')
    outputClass.blinds = aux[1].split(')')[0].split()[0]

    # get datetime    
    aux = line.split('-')
    outputClass.dateTime = aux[1][1:-1]

    # get Button
    line = txt[1]
    aux = line.split('#')
    outputClass.buttonPos = aux[1].split()[0]

    # move to new state
    newState = "Seats_state"
    return (newState, txt[2:])



# Function to handle the seats state (get players name/stack/seat)
def seats_transitions(txt):
    line = txt[0]

    # move to new state
    if line.split()[0] != 'Seat':
        newState = "blinds_state"
        return (newState, txt)


    # get new player
    newPlayer = player()
    aux = line.split()
    
    newPlayer.name = line.split(':')[1].split('(')[0][1:-1]
    newPlayer.stack = line.split('(')[1].split()[0]
    newPlayer.seat = line.split(':')[0].split()[1]
    
    outputClass.players += [newPlayer]
    
    return ("seats_state", txt[1:])



# Function to handle the blinds state (get the currency and blinds value)
def blinds_transitions(txt):

    # get small blind
    line = txt[0]
    auxPlayer = line.split(':')[0]
    auxAmount = line.split('small blind')[1][1:-1]
    
    # get currency
    auxCurrency = ''
    for char in auxAmount:
        if char.isdigit():
            break
        auxCurrency += char
    outputClass.currency = auxCurrency
    outputClass.addBet(auxPlayer, auxAmount)


    # get big blind
    line = txt[1]
    auxPlayer = line.split(':')[0]
    auxAmount = line.split('big blind')[1][1:-1]
    outputClass.addBet(auxPlayer, auxAmount)

    # move to new state
    newState = "findState_state"
    return (newState, txt[2:])



# Function to handle the pre-flop state
def preflop_transitions(txt):
    line = txt[0]

    # move to new state
    if line[:4] == "*** ":
        newState = "findState_state"
        return (newState, txt)

    # get player action
    playerAction(line, outputClass.foldedPreflop)
    
    return ("preflop_state", txt[1:])



# Function to handle the flop state
def flop_transitions(txt):
    line = txt[0]

    # move to new state
    if line[:4] == "*** ":
        newState = "findState_state"
        return (newState, txt)

    # get player action
    playerAction(line, outputClass.foldedFlop)
    
    return ("flop_state", txt[1:])



# Function to handle the turn state
def turn_transitions(txt):
    line = txt[0]

    # move to new state
    if line[:4] == "*** ":
        newState = "findState_state"
        return (newState, txt)

    # get player action
    playerAction(line, outputClass.foldedTurn)
    
    return ("turn_state", txt[1:])



# Function to handle the river state
def river_transitions(txt):
    line = txt[0]

    # move to new state
    if line[:4] == "*** ":
        newState = "findState_state"
        return (newState, txt)

    # get player action
    playerAction(line, outputClass.foldedRiver)
    
    return ("river_state", txt[1:])



# Function to handle the showdown state
def showdown_transitions(txt):
    line = txt[0]

    # move to new state
    if line[:4] == "*** ":
        newState = "findState_state"
        return (newState, txt)

    # get player action
    playerAction(line, [])
    
    return ("showdown_state", txt[1:])



# Function to handle the summary state (get only total pot/rake from here)
def summary_transitions(txt):
    line = txt[0]

    # get total pot and rake info
    if 'Total' in line and 'pot' in line and 'Rake' in line:
    #if line.split()[0] == 'Total' and line.split()[1] == 'pot':
        outputClass.totalPot  = line.split()[2]
        outputClass.totalRake = line.split()[5]
        
    # move to new state (end_state)
    if len(txt) == 1:
        newState = "end_state"
        return (newState, txt)

    return ("summary_state", txt[1:])

# --- END OF: defining all handlers for the state machine ---



# function that process the player action (fold, bet, ...)
def playerAction(text, foldList):

    # check if folded (add to respective list)
    if text.split()[-1] == 'folds':
        foldList += [text.split(':')[0]]

    # check for bet/call/raise
    elif 'bets'   in text:
        auxPlayer = text.split(':')[0]
        auxAmount = text.split('bets')[1][1:-1]
        outputClass.addBet(auxPlayer, auxAmount)
    elif 'calls'  in text:
        auxPlayer = text.split(':')[0]
        auxAmount = text.split('calls')[1][1:-1]
        outputClass.addBet(auxPlayer, auxAmount)
    elif 'raises' in text:
        auxPlayer = text.split(':')[0]
        auxAmount = text.split('raises')[1].split('to')[1][1:-1]
        outputClass.addBet(auxPlayer, auxAmount)

    # check for uncalled bet/collecting bet
    elif 'Uncalled bet' in text and 'returned to' in text:
        auxPlayer = text.split('returned to ')[1][:-1]
        auxAmount = text.split('(')[1].split(')')[0]
        outputClass.addWon(auxPlayer, auxAmount)
    elif 'collected' in text and 'from pot' in text:
        auxPlayer = text.split(' collected')[0]
        auxAmount = text.split('collected ')[1].split(' from pot')[0]
        outputClass.addWon(auxPlayer, auxAmount)
    
    # check for shown cards
    elif 'shows' in text and '[' in text and ']' in text:
        outputClass.cards += ['- {0}: {1}'.format( text.split(':')[0], text.split('[')[1].split(']')[0] )]



# --- MAIN ROUTINE: ---

# create the state machine
m2 = StateMachine()
m2.add_state("FindState_state", findState_transitions)
m2.add_state("Header_state", header_transitions)
m2.add_state("Seats_state", seats_transitions)
m2.add_state("Blinds_state", blinds_transitions)
m2.add_state("Preflop_state", preflop_transitions)
m2.add_state("Flop_state", flop_transitions)
m2.add_state("Turn_state", turn_transitions)
m2.add_state("River_state", river_transitions)
m2.add_state("Showdown_state", showdown_transitions)
m2.add_state("Summary_state", summary_transitions)
m2.add_state("End_state", None, end_state=1)

m2.set_start("Header_state")



# READ THE INPUT FILE AND RUN THE STATE MACHINE FOR EACH VALID INPUT
inputText = []
with open(sys.argv[1], 'r') as f:
    while True:
        line = f.readline()

        # CHECK FOR END OF FILE
        if not line:
            break

        # CHECK FOR INFO IN THE LINE
        if len(line) > 1:
            inputText += [line]
        
        # RUN STATE MACHINE ON BLANK LINE (END OF THE INPUT)
        else:
            if len(inputText):
                # run the state machine
                outputClass = hand()
                m2.run(inputText)

                # show output
                outputClass.show()
            inputText = []
        #sys.stdout.write(line)

# RUN LAST INPUT
if len(inputText):
    # run the state machine
    outputClass = hand()
    m2.run(inputText)

    # show output
    outputClass.show()


