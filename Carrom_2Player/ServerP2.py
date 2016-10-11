from Utils import *
import time,datetime
import socket
import sys
from thread import *
import os
import pickle
import argparse
from random import gauss

global Vis

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--Visualization', dest="Vis", type=int,
                        default=0,
                        help='Visualization')

parser.add_argument('-p1', '--port1', dest="PORT1", type=int,
                        default=12121,
                        help='Port 1')

parser.add_argument('-p2', '--port2', dest="PORT2", type=int,
                        default=34343,
                        help='Port 2')

parser.add_argument('-rr', '--', dest="RENDER_RATE", type=int,
                        default=10,
                        help='Render every nth frame')

parser.add_argument('-s', '--stochasticity', dest="stochasticity", type=int,
                        default=1,
                        help='Turn Stochasticity on/off')

parser.add_argument('-rs', '--random-seed', dest="RNG_SEED", type=int,
                        default=0,
                        help='Random Seed')


args=parser.parse_args()

RENDER_RATE=args.RENDER_RATE

Vis=args.Vis
PORT1=args.PORT1
PORT2=args.PORT2

HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces


random.seed(args.RNG_SEED)

t=time.time()

global score1
global score2
global Total_Ticks

Total_Ticks=0





global Stochasticity
Stochasticity=args.stochasticity
if Stochasticity==1:
    noise=0.0005
else:
    noise=0

# Handle exceptions here

# Exception handlers here

timeout_msg = "TIMED OUT"
timeout_period = 0.5
def is_Ended(space):
    for shape in space._get_shapes():
        if abs(shape.body.velocity[0])>Static_Velocity_Threshold or abs(shape.body.velocity[1])>Static_Velocity_Threshold:
            return False
    return True

def requestAction(conn1) :
    try : 
        data=conn1.recv(1024)
    except :
        data = timeout_msg
    finally :
        return data
    
def sendState(state,conn1):
    try:
        conn1.send(state)
    except socket.error:
        print "Player timeout"

    return True
    
'''
Play S,A->S'
Input: 
State: {"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}
Action: [Angle,X,Force] Legal Actions: ? If action is illegal, take random action
Player: 1 or 2
Vis: Visualization? Will be handled later
'''


def Play(State,Player,action):
  

    global Vis
    pygame.init()
    clock = pygame.time.Clock()

    if Vis==1:
        screen = pygame.display.set_mode((Board_Size, Board_Size))
        pygame.display.set_caption("Carrom RL Simulation")

    space = pymunk.Space(threaded=True)
    Score = State["Score"]
    prevScore=State["Score"]


    # pass through object // Dummy Object for handling collisions
    passthrough = pymunk.Segment(space.static_body, (0, 0), (0, 0), 5)
    passthrough.collision_type = 2
    passthrough.filter = pymunk.ShapeFilter(categories=0b1000)

    init_space(space)
    init_walls(space)
    Holes=init_holes(space)
    ##added
    BackGround = Background('use_layout.png', [-30,-30])

    Coins=init_coins(space,State["Black_Locations"],State["White_Locations"],State["Red_Location"],passthrough)
    #load_image("layout.jpg")
    Striker=init_striker(space,Board_Size/2+10, passthrough,action, Player)
        
    if Vis==1:
        draw_options = pymunk.pygame_util.DrawOptions(screen)


    Ticks=0
    Foul=False
    Pocketed=[]


    #print "Force: ",1000-+action[2]*1000
    Queen_Pocketed=False
    Queen_Flag=False
    while 1: 
        global score1
        global score2

        if Ticks%RENDER_RATE==0 and Vis==1:
            Local_VIS=True
        else:
            Local_VIS=False

        Ticks+=1
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit(0)

        if Local_VIS==1:
            screen.blit(BackGround.image, BackGround.rect)
            space.debug_draw(draw_options)

        space.step(1/TIME_STEP)
        #print Striker[0].position
        for hole in Holes:
            if dist(hole.body.position,Striker[0].position)<Hole_Radius-Striker_Radius+(Striker_Radius*0.75):
                for shape in space._get_shapes():
                    if shape.color==Striker_Color:
                        Foul=True
                        print "Player " + str(Player) + ": Foul, Striker in hole"
                        space.remove(shape,shape.body)
                        break


        for hole in Holes:
            for coin in space._get_shapes():
                if dist(hole.body.position,coin.body.position)<Hole_Radius-Coin_Radius+(Coin_Radius*0.75):
                    if coin.color == Black_Coin_Color:
                        Score+=1
                        Pocketed.append((coin,coin.body))
                        space.remove(coin,coin.body)
                        if Player==1:
                            Foul=True
                            print "Foul, Player 1 pocketed black"
                    if coin.color == White_Coin_Color:
                        Score+=1
                        Pocketed.append((coin,coin.body))
                        space.remove(coin,coin.body)
                        if Player==2:
                            Foul=True
                            print "Foul, Player 2 pocketed white"
                    if coin.color == Red_Coin_Color:
                        #Score+=3
                        Pocketed.append((coin,coin.body))
                        space.remove(coin,coin.body)
                        Queen_Pocketed=True


        if Local_VIS==1:
            font = pygame.font.Font(None, 25)
            text = font.render("Player 1: "+str(score1)+"     Player 2: "+str(score2)+"     TIME ELAPSED : "+ str(round(time.time()-t,2)) + "s", 1, (10, 10, 10))
            screen.blit(text, (Board_Size/5,Board_Size/10,0,0))
            if Ticks==1:
                length=Striker_Radius+action[2]/500.0 # The length of the line denotes the action
                startpos_x=action[1]
                angle=action[0]
                if Player==2:
                    startpos_y=145
                else:
                    startpos_y=Board_Size - 136
                endpos_x=(startpos_x+cos(angle)*length)
                endpos_y=(startpos_y-(length)*sin(angle))
                pygame.draw.line(screen, (50,255,50), (endpos_x, endpos_y), (startpos_x,startpos_y),3)
                pygame.draw.circle(screen,(50,255,50), (int(endpos_x), int(endpos_y)), 5)
            pygame.display.flip()
            if Ticks==1:
                time.sleep(1)
            clock.tick()
        
        # Do post processing and return the next State
        if is_Ended(space) or Ticks>TICKS_LIMIT:
            State_new={"Black_Locations":[],"White_Locations":[],"Red_Location":[],"Score":0}

            for coin in space._get_shapes():
                    if coin.color == Black_Coin_Color:
                        State_new["Black_Locations"].append(coin.body.position)
                    if coin.color == White_Coin_Color:
                        State_new["White_Locations"].append(coin.body.position)
                    if coin.color == Red_Coin_Color:
                        State_new["Red_Location"].append(coin.body.position)
            if Foul==True:
                for coin in Pocketed:
                    if coin[0].color == Black_Coin_Color:
                        State_new["Black_Locations"].append((400,400))
                        Score-=1
                    if coin[0].color == White_Coin_Color:
                        State_new["White_Locations"].append((400,400))
                        Score-=1
                    if coin[0].color == Red_Coin_Color:
                        State_new["Red_Location"].append((400,400))
                        #Score-=3

            if (Queen_Pocketed==True and Foul==False):
                if len(State_new["Black_Locations"]) + len(State_new["White_Locations"]) == 18:
                    print "The queen cannot be the first to be pocketed: Player ", Player
                    State_new["Red_Location"].append((400,400))
                else:
                    if Score-prevScore>0:
                        Score+=3
                        print "Queen pocketed and covered in one shot"
                    else:
                        Queen_Flag=True

            
            print "Player " + str(Player) + ": Turn ended in ", Ticks, " Ticks"
            State_new["Score"]=Score
            global Total_Ticks
            Total_Ticks+=Ticks

            return State_new,Queen_Flag



def don():
    s1.close()
    conn1.close()

    s2.close()
    conn2.close()
    print "Done, Closing Connection"
    sys.exit()



def transform_state(state):
    t_state={}
    t_state["White_Locations"]=[]
    t_state["Black_Locations"]=[]
    t_state["Red_Location"]=[]
    t_state["Score"]=state["Score"]
    for pos in state["White_Locations"]:
        t_state["White_Locations"].append((pos[0],800-pos[1]))
    for pos in state["Black_Locations"]:
        t_state["Black_Locations"].append((pos[0],800-pos[1]))
    for pos in state["Red_Location"]:
        t_state["Red_Location"].append((pos[0],800-pos[1]))
    return t_state

def transform_action(action):
    
    return (2*3.14 - action[0],action[1],action[2])



def tuplise(s) :
    try:
        return (round(float(s[0]),4),round(float(s[1]),4),round(float(s[2]),4))
    except:
        print "Invalid action, Taking Random"
        return (random.random()*2*3.14,random.random(),random.random())
# There is a min force with which you hit the striker: You cant give up turn: Ask sir is correct
 
#SAMIRAN:IMPLEMENT last response of the agents are emplty.. account for that also
def validate(action) :
    #print "Action Recieved: ",action
    angle=action[0]
    position=action[1]
    force=action[2]
    if angle<0 or angle >3.14*2 or (angle<3.14*1.75 and angle>3.14*1.25):
        print "Invalid Angle, taking random angle"
        angle=random.random()*3.14
    if position<0 or position>1:
        print "Invalid position, taking random position"
        position=random.random()    
    if force<0 or force>1:
        print "Invalid force, taking random position"
        force=random.random()  
    global Stochasticity
       
    angle=float(max(min(float(action[0]) + gauss(0,noise*360),360),0))
    position=170+(float(max(min(float(action[1]) + gauss(0,noise),1),0))*(460))
    force=MIN_FORCE+float(max(min(float(action[2]) + gauss(0,noise),1),0))*MAX_FORCE

    action=(angle,position,force)
    return action

if __name__ == '__main__':


    s1=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s1.bind((HOST, PORT1))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s1.listen(1)
    conn1,addr1=s1.accept()
    conn1.settimeout(timeout_period);


    s2=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s2.bind((HOST, PORT2))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s2.listen(1)
    conn2,addr2=s2.accept()
    conn2.settimeout(timeout_period);

    global score1
    global score2

    winner = 0
    reward1 = 0
    score1 = 0
    reward2 = 0
    score2 = 0

    State={'White_Locations': [(400,368),(437,420), (372,428),(337,367), (402,332), (463,367), (470,437), (405,474), (340,443)], 'Red_Location': [(400, 403)], 'Score': 0, 'Black_Locations': [(433,385),(405,437), (365,390), (370,350), (432,350), (467,402), (437,455), (370,465), (335,406)]}
    next_State=State

    it=1
    
    while it<200: # Number of Chances given to each player
     
        if it>150:
            global Vis
            Vis=1 # To Be removed

        it+=1

        prevScore = next_State["Score"]
        sendState(str(next_State) + ";REWARD" + str(reward1),conn1)
        s=requestAction(conn1)
        if not s :#response empty
            print "No response from player 1"
            winner=2
            break
        elif s == timeout_msg:
            print "Timeout from player 1"
            winner=2
            break
        else :
            action=tuplise(s.replace(" ","").split(','))
        next_State,Queen_Flag=Play(next_State,1,validate(action))
        print "Coins: ", len(next_State["Black_Locations"]),"B ", len(next_State["White_Locations"]),"W ",len(next_State["Red_Location"]),"R"

        reward1 = next_State["Score"] - prevScore
        prevScore = next_State["Score"]
        score1 = score1 + reward1
        if Queen_Flag:

            print "Pocketed Queen, pocket any coin in this turn to cover it"
            prevScore = next_State["Score"]

            sendState(str(next_State) + ";REWARD" + str(reward1),conn1)
            s=requestAction(conn1)
            if not s :#response empty
                print "No response from player 1"
                winner=2
                break
            elif s == timeout_msg:
                print "Timeout from player 1"
                winner=2
                break
            else :
                action=tuplise(s.replace(" ","").split(','))
            next_State,Queen_Flag=Play(next_State,1,validate(action))
            print "Coins: ", len(next_State["Black_Locations"]),"B ", len(next_State["White_Locations"]),"W ",len(next_State["Red_Location"]),"R"


            reward1 = next_State["Score"] - prevScore
            if reward1>0:
                score1+=3
                print "Sucessfully covered the queen"
            else:
                print "Could not cover the queen"
                next_State["Red_Location"].append((400,400))
            prevScore = next_State["Score"]
            score1 = score1 + reward1



        if len(next_State["Black_Locations"])==0 or len(next_State["White_Locations"])==0:
            break

        sendState(str(transform_state(next_State))+";REWARD" + str(reward2),conn2)
        s=requestAction(conn2)
        if not s: #response empty
            print "No response from Player 2";
            winner=1
            break
        elif s == timeout_msg:
            print "Timeout from Player 2";
            winner = 1
            break
        else :
            action=transform_action(tuplise(s.replace(" ","").split(',')))



        next_State,Queen_Flag=Play(next_State,2,validate(action))
        print "Coins: ", len(next_State["Black_Locations"]),"B ", len(next_State["White_Locations"]),"W ",len(next_State["Red_Location"]),"R"

        reward2 = next_State["Score"] - prevScore
        score2 = score2 + reward2
        if Queen_Flag:

            prevScore = next_State["Score"]
            print "Pocketed Queen, pocket any coin in this turn to cover it"
            sendState(str(transform_state(next_State))+";REWARD" + str(reward2),conn2)
            s=requestAction(conn2)
            if not s: #response empty
                print "No response from Player 2";
                winner=1
                break
            elif s == timeout_msg:
                print "Timeout from Player 2";
                winner = 1
                break
            else :
                action=transform_action(tuplise(s.replace(" ","").split(',')))

            next_State,Queen_Flag=Play(next_State,2,validate(action))
            print "Coins: ", len(next_State["Black_Locations"]),"B ", len(next_State["White_Locations"]),"W ",len(next_State["Red_Location"]),"R"


            reward2 = next_State["Score"] - prevScore
            if reward2>0:
                score2+=3
                print "Successfully covered the queen"
            else:
                print "Could not cover the queen"
                next_State["Red_Location"].append((400,400))
            score2 = score2 + reward2
        
        print "P1 score: ",score1," P2 score: ", score2, " Turn "+str(it)
        print "Coins: ", len(next_State["Black_Locations"]),"B ", len(next_State["White_Locations"]),"W ",len(next_State["Red_Location"]),"R"
        if len(next_State["Black_Locations"])==0 or len(next_State["White_Locations"])==0:
            break

    if winner==2:
        print "Player 1 Timeout"
    elif winner==1:
        print "Player 2 Timeout"           
    if winner == 0 :
        if len(next_State["White_Locations"])==0:
            if len(next_State["Red_Location"])>0:
                winner=2
            else:
                winner=1
            msg = "Winner is Player " + str(winner)
        elif len(next_State["Black_Locations"])==0:
            if len(next_State["Red_Location"])>0:
                winner=1
            else:
                winner=2
            msg = "Winner is Player " + str(winner)
        else:
            msg = "Draw"

    try:
        print msg
    except NameError:
        pass
    
    f=open("logS2.txt","a")
    f.write(str(it)+" "+str(round(time.time()-t,0))+" "+str(winner)+" "+str(score1)+" "+str(score2)+"\n")
    f.close()
    don()


