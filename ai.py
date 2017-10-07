from flask import Flask, request
from structs import *
import json
import numpy

app = Flask(__name__)

def create_action(action_type, target):
    actionContent = ActionContent(action_type, target.__dict__)
    return json.dumps(actionContent.__dict__)

def create_action_int(action_type, target):
    actionContent = ActionContentInt(action_type, target)
    return json.dumps(actionContent.__dict__)

def create_action_int(action_type, target):
    actionContent = ActionContentInt(action_type, target)
    return json.dumps(actionContent.__dict__)

def create_move_action(target):
    return create_action("MoveAction", target)

def create_attack_action(target):
    return create_action("AttackAction", target)

def create_collect_action(target):
    return create_action("CollectAction", target)

def create_steal_action(target):
    return create_action("StealAction", target)

def create_heal_action():
    return create_action("HealAction", "")

def create_purchase_action(item):
    return create_action("PurchaseAction", item)

def create_upgrade_action():
    return create_action_int("UpgradeAction", item)

def deserialize_map(serialized_map):
    """
    Fonction utilitaire pour comprendre la map
    """
    serialized_map = serialized_map[1:]
    rows = serialized_map.split('[')
    column = rows[0].split('{')
    deserialized_map = [[Tile() for x in range(20)] for y in range(20)]
    for i in range(len(rows) - 1):
        column = rows[i + 1].split('{')

        for j in range(len(column) - 1):
            infos = column[j + 1].split(',')
            end_index = infos[2].find('}')
            content = int(infos[0])
            x = int(infos[1])
            y = int(infos[2][:end_index])
            deserialized_map[i][j] = Tile(content, x, y)

    return deserialized_map

def printMap(map):
    for i in map:
        for j in i:
            print j,
        print()

def moveLeft(player):
    return create_move_action(Point(int(player.Position.X), int(player.Position.Y-1)))
def moveRight(player):
    return create_move_action(Point(int(player.Position.X), int(player.Position.Y+1)))
def moveUp(player):
    return create_move_action(Point(int(player.Position.X-1), int(player.Position.Y)))
def moveDown(player):
    return create_move_action(Point(int(player.Position.X+1), int(player.Position.Y)))

def goto(player, dest):
    current = player.Position
    if dest.X < current.X:
        print 1
        return moveUp(player)
    elif dest.X > current.X:
        print 2
        return moveDown(player)
    if dest.Y < current.Y:
        print 3
        return moveLeft(player)
    elif dest.Y > current.Y:
        print 4
        return moveRight(player)
    print 5
    return create_move_action(Point(current.X, current.Y))


def doCollect(player, dest):
    current = player.Position
    if dest.X < current.X:
        return create_collect_action(Point(current.X - 1, current.Y))
    elif dest.X > current.X:
        return create_collect_action(Point(current.X + 1, current.Y))
    if dest.Y < current.Y:
        return create_collect_action(Point(current.X, current.Y - 1))
    else:
        return create_collect_action(Point(current.X, current.Y + 1))

def isAtHome(player):
    return player.Position.Distance(player.Position, player.HouseLocation)

def findAdjacentWall(pos, myMap):
    adjacentWallPos = (-1, -1)
    for i in range(20):
        for j in range(20):
            tile = myMap[i][j]
            if tile.Content == TileContent.Wall:
                if pos.Distance(pos, Point(tile.X, tile.Y)) == 1:
                    adjacentWallPos = Point(tile.X, tile.Y)
                    return adjacentWallPos
    return adjacentWallPos
    
def fct(player, dest, myMap):
    current = player.Position
    distance = current.Distance(current, dest);

    adjacentWall = findAdjacentWall(player.Position, myMap)
    if adjacentWall != Point(-1, -1):
        return create_attack_action(adjacentWall)
    if player.CarriedRessources != 0 and isAtHome(player) == 0:
        return create_move_action(player.Position)
    if distance > 1 or (distance > 0 and player.CarriedRessources == player.CarryingCapacity):
        print "goto"
        return goto(player, dest)
    elif distance > 0:
        print "collect"
        return doCollect(player, dest)




def bot():
    """
    Main de votre bot.
    """
    map_json = request.form["map"]

    # Player info

    encoded_map = map_json.encode()
    map_json = json.loads(encoded_map)
    p = map_json["Player"]
    #print "player:{}".format(p)
    pos = p["Position"]
    x = pos["X"]
    y = pos["Y"]
    house = p["HouseLocation"]
    player = Player(p["Health"], p["MaxHealth"], Point(x,y),
                    Point(house["X"], house["Y"]), p["Score"],
                    p["CarriedResources"], p["CarryingCapacity"])

    # Map
    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)

    otherPlayers = []

    for players in map_json["OtherPlayers"]:
        player_info = players["Value"]
        p_pos = player_info["Position"]
        player_info = PlayerInfo(player_info["Health"],
                                     player_info["MaxHealth"],
                                     Point(p_pos["X"], p_pos["Y"]))

        otherPlayers.append(player_info)

    #printMap(deserialized_map)
    print("Score: " + str(player.Score))
    print("Pos: " + str(player.Position))

    # Find house and resource
    housePos = Point(-1, -1)
    resourcePos = Point(-1, -1)
    for i in range(20):
        for j in range(20):
            tile = deserialized_map[i][j]
            if tile.Content == TileContent.House:
                housePos = Point(tile.X, tile.Y)
            if tile.Content == TileContent.Resource:
                resourcePos = Point(tile.X, tile.Y)
    if player.CarriedRessources ==  player.CarryingCapacity:
        dest = housePos
    else:
        dest = resourcePos
    action = fct(player, dest, deserialized_map)
    print "action",action
    # return decision
    return action

@app.route("/", methods=["POST"])
def reponse():
    """
    Point d'entree appelle par le GameServer
    """
    return bot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
