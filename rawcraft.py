import requests
import json
import base64
from nbt import *
import io
import dill
import os

craftable_item_blacklist = ['HEAT_CORE','TENTACLE_MEAT', 'MAGMA_CHUNK', 'GAZING_PEARL', 'COLOSSAL_EXP_BOTTLE_UPGRADE', 'BEZOS', 'SULPHURIC_COAL', 'HORN_OF_TAURUS']

reforges = {'dirty': 'DIRT_BOTTLE', 
'fabled': 'DRAGON_CLAW',
'gilded': 'MIDAS_JEWEL',
'suspicious': 'SUSPICIOUS_VIAL',
'warped': 'AOTE_STONE',
'withered': 'WITHER_BLOOD',
'bulky': 'BULKY_STONE',
"jerry's": 'JERRY_STONE',
'precise': 'OPTICAL_LENS',
'spiritual': 'SPIRIT_DECOY',
'headstrong': 'SALMON_OPAL',
'candied': 'CANDY_CORN',
'submerged': 'DEEP_SEA_ORB',
'perfect': 'DIAMOND_ATOM',
'reinforced': 'RARE_DIAMOND',
'renowned': 'DRAGON_HORN',
'spiked': 'DRAGON_SCALE',
'hyper': 'ENDSTONE_GEODE',
'giant': 'GIANT_TOOTH',
'jaded': 'JADERALD',
'cubic': 'MOLTEN_CUBE',
'necrotic': 'NECROMANCER_BROOCH',
'empowered': 'SADAN_BROOCH',
'ancient': 'PRECURSOR_GEAR',
'undead': 'PREMIUM_FLESH',
'loving': 'RED_SCARF',
'ridiculous': 'RED_NOSE',
'glistening': 'SHINY_PRISM',
'strengthened': 'SEARING_STONE',
'waxed': 'BLAZE_WAX',
'fortified': 'METEOR_SHARD',
'lucky': 'LUCKY_DICE',
'stiff': 'HARDENED_WOOD',
'chomp': 'KUUDRA_MANDIBLE',
'ambered': 'AMBER_MATERIAL',
'auspicious': 'ROCK_GEMSTONE',
'fleet': 'DIAMONITE',
'heated': 'HOT_STUFF',
'magnetic': 'LAPIS_CRYSTAL',
'mithraic': 'PURE_MITHRIL',
'refined': 'REFINED_AMBER',
'mining reforge': 'PETRIFIED_STARFALL',
'fruitful': 'ONYX',
'moil': 'MOIL_LOG',
'toil': 'TOIL_LOG',
'blessed': 'BLESSED_FRUIT',
'bountiful': 'GOLDEN_BALL',} 
enchantmentTableEnchants = ['bane_of_arthropods', 'efficiency', 'cleave', 'critical', 'cubism', 'ender_slayer', 'execute', 'experience', 'fire_aspect', 'first_strike', 'first_strike', 'giant_killer', 'impaling', 'knockback','lethality','life_steal', 'looting', 'luck', 'mana_steal', 'life_steal', 'prosecute', 'scavenger', 'sharpness', 'smite', 'syphon', 'thunderbolt', 'thunderlord', 'titan_killer', 'triple-strike', 'vampirism', 'venomous', 'vicious', 'chance', 'dragon_tracer', 'flame', 'infinite_quiver', 'piercing', 'power', 'punch', 'snipe', 'aqua_affinity', 'blast_protection', 'depth_strider', 'feather_falling', 'fire_protection', 'frost_walker', 'growth', 'projectile_protection', 'protection', 'thorns', 'experience', 'fortune', 'harvesting', 'rainbow', 'silk_touch', 'smeling_touch', 'angler', 'blessing', 'caster', 'frail', 'looting', 'luck_of_the_sea', 'lure', 'magnet', 'spiked_hook']

essencePrice = {
    'UNDEAD': 1250,
    'GOLD': 3000,
    'DIAMOND': 3000,
    'DRAGON': 2000,
    'ICE': 2000,
    'WITHER': 3500
}

playerItems = []

class auctionHouse():
    def __init__(self) -> None:
        pages = get_auctions()['totalPages']
        self.items = {}
        for i in range(pages - 1):
            for currentauction in get_auctions(i)['auctions']:
                addAuction = True
                if currentauction['bin'] == False:
                    addAuction = False

                itemId = str(decode_inventory_data(currentauction['item_bytes'])[0]['tag']['ExtraAttributes']['id'])

                try:
                    if itemId == "ENCHANTED_BOOK":
                        if not len(decode_inventory_data(currentauction['item_bytes'])[0]['tag']['ExtraAttributes']['enchantments']) >= 2:
                            itemId = str(list(decode_inventory_data(currentauction['item_bytes'])[0]['tag']['ExtraAttributes']['enchantments'])[0].upper())
                        else:
                            addAuction = False
                except:
                    pass



                if addAuction == True:
                    if itemId in list(self.items):
                        addedAuction = False
                        j = 0
                        while addedAuction == False:
                            if self.items[itemId][j]['starting_bid'] >= currentauction['starting_bid']:
                                self.items[itemId].insert(j, currentauction)
                            j = j + 1
                            addedAuction = True
                    else:
                        self.items[itemId] = [currentauction]

            print("Indexing Auction House: " + str(i) + '/' + str(pages))
        print(self.items)      

class sbItem():
    def __init__(self, data) -> None:
        try: 
            self.id = data['tag']['ExtraAttributes']['id'].value
            name = data['tag']['display']['Name'].value.split('§')
        except:
            self.id = 'None'
            self.value = 0
            return

        self.name = data['tag']['display']['Name'].value

        if len(name) >= 1:
            for i in range(len(name)):
                name[i] = name[i][1:]
        self.name = ''.join(name)

        try:
            self.count = data['Count'].value
        except:
            self.count = 1

        try:
            self.rarityUpgrades = data['tag']['ExtraAttributes']['rarity_upgrades'].value
        except:
            pass
        try:
            self.hotPotatoCount = data['tag']['ExtraAttributes']['hot_potato_count'].value
        except:
            pass
        try:
            self.reforge = data['tag']['ExtraAttributes']['modifier'].value
        except:
            pass
        try:
            self.dungeonStars = data['tag']['ExtraAttributes']['dungeon_item_level'].value
        except:
            pass
        try:
            self.uuid = data['tag']['ExtraAttributes']['uuid']
        except:
            pass
        try:
            self.enchantments = {}
            for i in list(data['tag']['ExtraAttributes']['enchantments']):
                self.enchantments[i] = data['tag']['ExtraAttributes']['enchantments'][i].value
        except:
            pass

        try:
            self.value = self.calc_value()
        except:
            self.value = 0

    def calc_value(self):
        global auction
        global itemData
        global bazaarData
        global reforges
        global enchantmentTableEnchants

        try:
            if not self.id in list(bazaarData):
                itemValue = auction.items[str(self.id)][0]['starting_bid'] / decode_inventory_data(auction.items[str(id)][0]['item_bytes'])['Count']
            else:
                itemValue = bazaarData[self.id]['buyPrice']
        except:
            itemValue = 0
        
        value = itemValue

        reforgeValue = 0
        enchantmentValue = 0
        starValue = 0
        hotPotatoBookValue = 0
        fumingPotatoBookValue = 0
        recombValue = 0

        #reforge
        try:
            if self.reforge in list(reforges):
                reforgeValue = auction.items[reforges[self.reforge]][0]['starting_bid']
            value = value + reforgeValue
        except:
            pass 

        #enchantments
        try: 
            for enchantment in list(self.enchantments):
                if not enchantment in enchantmentTableEnchants:
                    enchantmentValue = enchantmentValue + auction.items[enchantment.upper()][0]['starting_bid'] * 2**(self.enchantments[enchantment] - 1)
            value = value + enchantmentValue
        except: 
            pass

        #stars
        try:
            upgradeCount = self.dungeonStars - 1
            while upgradeCount > 0:
                currentEssenceTier = itemData[str(self.id)]['upgrade_costs'][upgradeCount][0]
                if upgradeCount > 4:
                    upgradeCount = 4
                starValue = starValue + essencePrice[currentEssenceTier['essence_type']] * currentEssenceTier['amount']
                upgradeCount = upgradeCount - 1
            value = value + starValue
        except:
            pass

        #hot potato books
        try:
            hotPotatoBookValue = bazaarData['HOT_POTATO_BOOK']['buyPrice'] * max(min(self.hotPotatoCount, 10), 0)
            fumingPotatoBookValue = bazaarData['FUMING_POTATO_BOOK']['buyPrice'] * max(min(self.hotPotatoCount - 10, 5), 0)
            value = value + hotPotatoBookValue + fumingPotatoBookValue
        except:
            pass

        #recombs
        try:
            recombValue = bazaarData['RECOMBOBULATOR_3000']['buyPrice'] * self.rarityUpgrades
            value = value + recombValue
        except:
            pass
        try:
            value = value * self.count
        except:
            self.count = 1
        
        try:
            if not self.name == 'None':
                with open('output.txt', 'a') as f:
                    f.write('name: ' + str(self.count) + 'x ' + str(self.name) + '\n')
                    f.write('item value: ' + str(itemValue) + '\n')
                    f.write('reforgeValue: ' + str(reforgeValue) + '\n')
                    f.write('enchantmentValue: ' + str(enchantmentValue) + '\n')
                    f.write('starValue: ' + str(starValue) + '\n')
                    f.write('hotPotatoBookValue: ' + str(hotPotatoBookValue) + '\n')
                    f.write('fumingPotatoBookValue: ' + str(fumingPotatoBookValue) + '\n')
                    f.write('recombValue: ' + str(recombValue) + '\n')
                    f.write('value: ' +  str(value) + '\n\n')
        except:
            pass
        value = round(value, 1)

        return value

def calc_raw_value(id):
    global bazaarData
    global auction
    if id == 'NECRON_BLADE':
        id = 'NECRON_HANDLE'
    # try:
    if id in list(bazaarData):
        itemValue = bazaarData[id]['buyPrice']
    elif id in list(auction.items):
        itemValue = auction.items[str(id)][0]['starting_bid']
    else:
        itemValue = 0
    # except:
    #     itemValue = 0
    itemValue = round(itemValue, 1)
    return itemValue
        
def get_auctions(page=0):
    data = requests.get(url='http://api.hypixel.net/skyblock/auctions', params={
        'key': API_KEY,
        'page': page
    }).text
    data = json.loads(data)
    return data
    
def get_bazaar():
    rawdata = requests.get(url='https://api.hypixel.net/skyblock/bazaar', params={
        'key': API_KEY,
    }).text
    rawdata = json.loads(rawdata)['products']
    data = {}
    for product in list(rawdata):
        data[product] = rawdata[product]['quick_status']
    return data

def get_items_data():
    rawdata = requests.get(url='https://api.hypixel.net/resources/skyblock/items', params={
        'key': API_KEY,
    }).text
    rawdata = json.loads(rawdata)['items']
    data = {}
    for item in rawdata:
        data[item['id']] = item
        data[item['id']].pop('id')

    return data

def get_player_data(playerName, profile):
    data = requests.get(url='https://sky.shiiyu.moe/api/v2/profile/' + playerName).text
    data = json.loads(data)
    profiles = list(data['profiles'])

    for i in range(len(profiles)):
        if data['profiles'][profiles[i]]['cute_name'] == profile:
            profile_id = data['profiles'][profiles[i]]['profile_id']
    return data['profiles'][profile_id]

def decode_inventory_data(raw):
   data = nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw)))
   return data[0]

def load_item_neu_data_to_file():
    itemNeuData = {}
    files = len(os.listdir('items'))
    fileNumber = 1

    for filename in os.listdir('items'):
        with open('items/' + filename, 'r', encoding="utf8") as f:
            fileContent = f.read()
            fileContent = json.loads(fileContent)
            itemNeuData[filename[: len(filename) - 5]] = fileContent
            print('Item ' + str(fileNumber) + '/' + str(files) + ' Filename: ' + str(filename))
            fileNumber = fileNumber + 1

    json.dump(itemNeuData, open('itemData.txt', 'w'))

def neuData_to_recipe_list(neuData):
    global craftable_item_blacklist
    recipeList = {}

    for item in list(neuData):
        if 'recipe' in list(neuData[item]):
            checkBlacklisted = ['']
            for i in neuData[item]['recipe'].values():
                try:
                    checkBlacklisted.append(i.split(':')[0])
                except:
                    pass

            if not any(x in checkBlacklisted for x in craftable_item_blacklist):
                recipeList[item] = {}
                for craftSpot in list(neuData[item]['recipe']):
                    if neuData[item]['recipe'][craftSpot] != "":
                        craftSpotItem = neuData[item]['recipe'][craftSpot].split(':')[0]
                        craftSpotItem = craftSpotItem.split(';')[0]
                        craftSpotNumber = int(neuData[item]['recipe'][craftSpot].split(':')[1])
                        if craftSpotItem in list(recipeList[item]):
                            recipeList[item][craftSpotItem] = recipeList[item][craftSpotItem] + craftSpotNumber
                        else:
                            recipeList[item][craftSpotItem] = craftSpotNumber
    return recipeList

def calc_item_craft_profit(recipeList):
    craftCost = {}
    
    for item in list(recipeList):
        craftCost[item] = {}
        craftCost[item]['original'] = calc_raw_value(item)
        craftCost[item]['craft'] = 0

        for recipeItem in list(recipeList[item]):
            craftCost[item]['craft'] = craftCost[item]['craft'] + (calc_raw_value(recipeItem) * recipeList[item][recipeItem])

        craftCost[item]['difference'] =  craftCost[item]['original'] - craftCost[item]['craft']

        if craftCost[item]['craft'] != 0:
            craftCost[item]['diffProc'] =  craftCost[item]['original'] / craftCost[item]['craft'] * 100 - 100
        else:
            craftCost[item]['diffProc'] = 0
    return craftCost

def sort_recipe_list_on_price(recipeList, craftCost, minimumValue = 0):
    craftCostInOrder = []

    for item in list(recipeList):
        setInOrder = False
        currentNumber = 0
        while setInOrder == False:
            if len(craftCostInOrder) > currentNumber:
                if craftCostInOrder[currentNumber]['diffProc'] <= craftCost[item]['diffProc'] and not craftCost[item]['craft'] <= minimumValue:
                    tempData = {'id': item}
                    
                    for i in list(craftCost[item]):
                        tempData[i] = craftCost[item][i]
                    craftCostInOrder.insert(currentNumber,tempData)
                    setInOrder = True
                currentNumber = currentNumber + 1
            else: 
                tempData = {'id': item}
                for i in list(craftCost[item]):
                    tempData[i] = craftCost[item][i]
                craftCostInOrder.append(tempData)
                setInOrder = True
    return craftCostInOrder

def print_craft_cost_to_file(recipeList, craftCost, craftCostInOrder):
    global itemData
    
    with open('item_output.txt', 'w') as f:
        currentItem = 0

        for item in craftCostInOrder:
            item = item['id']
            f.write('#' + str(currentItem) + '\n')
            try:
                f.write('Item Name       : ' + str(itemData[item]['name']) + '\n')
            except:
                f.write('Item Name       : ' + item + '\n')
            f.write('Original   Price: ' + str(craftCost[item]['original']) + '\n')
            f.write('Craft      Price: ' + str(craftCost[item]['craft']) + '\n')
            f.write('diff %         %: ' + str(craftCost[item]['diffProc']) + '\n')
            f.write('Items: \n')
            for i in recipeList[item]:
                try:
                    f.write(f"{str(itemData[i]['name']):<25} {': ':>10} {str(calc_raw_value(i)):<10}{' x ':>0} {str(recipeList[item][i])} {'= ':>3} {calc_raw_value(i) * recipeList[item][i]}" + '\n')
                except:
                    f.write(f"{str(i):<25} {': ':>10} {str(calc_raw_value(i)):<10}{' x ':>0} {str(recipeList[item][i])} {'= ':>3} {calc_raw_value(i) * recipeList[item][i]}" + '\n')
            f.write('\n')
            currentItem = currentItem + 1    



load_item_neu_data_to_file()

#playerData = get_player_data(input('What is your Username?: '), input('What is your profile Name?: '))
itemData = get_items_data()
bazaarData = get_bazaar()
neuData = json.load(open('itemData.txt', 'r'))
auction = auctionHouse()
dill.dump(auction, file=open('auctions.txt', 'wb'))
auction = dill.load(open('auctions.txt', 'rb'))


recipeList = neuData_to_recipe_list(neuData)

craftCost = calc_item_craft_profit(recipeList)

craftCostInOrder = sort_recipe_list_on_price(recipeList, craftCost, 600000)

print_craft_cost_to_file(recipeList, craftCost, craftCostInOrder)

