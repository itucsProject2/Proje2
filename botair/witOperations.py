from wit import Wit

def sendToWit(messageString):
    access_token = 'DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS'
    actions ={}
    client = Wit(access_token = access_token,actions = actions)
    response = client.message(messageString);
    print(response)
    return response