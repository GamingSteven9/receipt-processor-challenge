# Gets the points from the given "id"
def getPointsFromID(id, ids):
    match id in ids:
            case True:
                return ids[id]
            case _:
                pass