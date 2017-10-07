from flask import Flask, request
from structs import *
import json
import numpy
app = Flask(__name__)

def create_action(action_type, target):
    actionContent = ActionContent(action_type, target.__dict__)
    return json.dumps(actionContent.__dict__)

def create_move_action(target):
    print("Moving to: " + str(target))
    return create_action("MoveAction", target)

def create_attack_action(target):
    return create_action("AttackAction", target)

def create_collect_action(target):
    print("Collecting: " + str(target))
    return create_action("CollectAction", target)

def create_steal_action(target):
    return create_action("StealAction", target)

def create_heal_action():
    return create_action("HealAction", "")

def create_purchase_action(item):
    return create_action("PurchaseAction", item)

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

def isAWall(myMap, point):
    for i in range(20):
        for j in range(20):
            tile = myMap[i][j]
            if tile.X == point.X and tile.Y == point.Y:
                return tile.Content != TileContent.Empty

def moveTowardPos(myMap, currentPos, destPos):
    distance = currentPos.Distance(currentPos, destPos);
    if distance > 1:
        if destPos.X < currentPos.X and not isAWall(myMap, Point(currentPos.X - 1, currentPos.Y)):
            return create_move_action(Point(currentPos.X - 1, currentPos.Y))
        if destPos.X > currentPos.X and not isAWall(myMap, Point(currentPos.X + 1, currentPos.Y)):
            return create_move_action(Point(currentPos.X + 1, currentPos.Y))
        if destPos.Y < currentPos.Y - 1 and not isAWall(myMap, Point(currentPos.X, currentPos.Y - 1)):
            return create_move_action(Point(currentPos.X, currentPos.Y - 1))
        if destPos.Y > currentPos.Y + 1 and not isAWall(myMap, Point(currentPos.X, currentPos.Y + 1)):
            return create_move_action(Point(currentPos.X, currentPos.Y + 1))

def bot():
    """
    Main de votre bot.
    """
    map_json = request.form["map"]

    # Player info

    encoded_map = map_json.encode()
    map_json = json.loads(encoded_map)
    p = map_json["Player"]
    pos = p["Position"]
    x = pos["X"]
    y = pos["Y"]
    house = p["HouseLocation"]
    player = Player(p["Health"], p["MaxHealth"], Point(x,y),
                    Point(house["X"], house["Y"]),
                    p["CarriedResources"], p["CarryingCapacity"])

    # Map
    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)

    """otherPlayers = []

    for player_dict in map_json["OtherPlayers"]:
        for player_name in player_dict.keys():
            player_info = player_dict[player_name]
            p_pos = player_info["Position"]
            player_info = PlayerInfo(player_info["Health"],
                                     player_info["MaxHealth"],
                                     Point(p_pos["X"], p_pos["Y"]))

            otherPlayers.append({player_name: player_info })
            # print player.Position[0]"""
    

    #printMap(deserialized_map)
    
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

    resDistance = resourcePos.Distance(player.Position, resourcePos);
    print("Distance to res: " + str(resDistance))
    print("Player pos: (" + str(player.Position.X) + ", " + str(player.Position.Y) + ")")
    print("House pos: (" + str(housePos.X) + ", " + str(housePos.Y) + ")")
    print("Res pos: (" + str(resourcePos.X) + ", " + str(resourcePos.Y) + ")")
    print("Player carry: " + str(player.CarriedRessources))

    # Move to res
    return moveTowardPos(deserialized_map, player.Position, resourcePos)

@app.route("/", methods=["POST"])
def reponse():
    """
    Point d'entree appelle par le GameServer
    """
    return bot()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
