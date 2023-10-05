from datetime import date, time
from re import sub
from math import ceil
from secrets import token_hex

# Checks the retailer
def checkRetailer(retailer):
    retailerName = sub('\W', '', retailer) # Use regex to replace all non-alphanumerical character with an empty string, then add 1 point for each alphanumerical character
    points=len(retailerName)
    return points

# Checks the purchase date
def checkPurchaseDate(purchaseDate):
    pDate=int(date.fromisoformat(purchaseDate).strftime('%d')) # The day of purchase
    match pDate % 2: # If the day is an odd number then add 6 points
        case 1:
            points=6
        case _:
            points=0
    return points

# Checks the purchase time
def checkPurchaseTime(purchaseTime):
    pTime=time.fromisoformat(purchaseTime) # The purchase time
    match pTime>time.fromisoformat('14:00:00') and pTime<time.fromisoformat('16:00:00'): # If time is between 2 pm and 4 pm, then add 10 points
        case True:
            points=10
        case _:
            points=0
    return points

# Checks if the total is a round number
def checkTotalRound(total):
    match float(total).is_integer(): # If the total is a round number, then add 50 points
        case True:
            points=50
        case _:
            points=0
    return points

# Checks if the total is a multiple of 0.25
def checkTotalMultiple(total):
    match float(total) % 0.25: # If the total is a multiple of 0.25, then add 25 points
        case 0:
            points=25
        case _:
            points=0
    return points

# Checks how many items are in the receipt
def checkItemsLength(items):
    itemsLength = len(items)
    match itemsLength % 2: # Determine if the number of items in the receipt is a multiple of 2
        case 0:
            points=round((5 * itemsLength / 2)) # If the number of the items is even, then divide the length by 2 to get the number of pairs and then multiply the remainder by 5 to get the points
        case 1:
            points=round((5 * (itemsLength - 1) / 2)) # If the number of the items is odd, subtract one from it to make it a multiple of 2, then divide the number by 2 to get the number of pairs, 
                                                                        # and then multiply the remainder by 5 to get the number of points earned.
        case _:
            points=0
    return points

# Checks if the item descriptions are a multiple of 3 
def checkItemsDescription(items):
    points=0
    for j in items:
        match len(j['shortDescription'].strip()) % 3: # If the trimmed length of an item's description is a multiple of 3, multiply the price by 0.2 and round it up to the nearest integer using ceil(x) 
                                                                    # to get the number of points earned.
            case 0:
                points+=ceil(float(j['price']) * 0.2)
            case _:
                points+=0
    return points

# Determines the amount of points from the receipt
def determinePoints(jDict):
    points=0 # Holds the current amount of points that the receipt currently has
    for i in jDict: # Matches each item in the receipt and peformes the desired function
        match i:
            case 'retailer':
                points+=checkRetailer(jDict[i])
            case 'purchaseDate':
                points+=checkPurchaseDate(jDict[i])
            case 'purchaseTime':
                points+=checkPurchaseTime(jDict[i])
            case 'total':
                points+=checkTotalRound(jDict[i])
                points+=checkTotalMultiple(jDict[i])
            case 'items':
                points+=checkItemsLength(jDict[i])
                points+=checkItemsDescription(jDict[i])
            case _:
                pass
    #print(points)
    return points # Return the total amount of points

# Creates a random ID that is not already in 'ids'
def createRandomID(ids):
    randomid = token_hex(4) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(6) # Generate a random ID
    match (randomid in ids): # If the ID is not already present in 'ids,' assign the points to it. Otherwise, create a new ID until the new one is not in 'ids'
        case False:
            return randomid
        case True:
            while randomid in ids:
                randomid = token_hex(4) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(2) + "-" + token_hex(6) # Generate a new random ID
        case _:
            pass
    pass

# Assigns the points to an ID and add it to 'ids'
def addID(ids, randID, points):
    ids[randID] = points
    return ids