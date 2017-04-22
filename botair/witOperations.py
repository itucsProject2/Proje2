from wit import Wit

def send(request, response):
    print('Sending to user...', response['text'])
def my_action(request):
    print('Received from user...', request['text'])



def sendToWit(messageString):
    access_token = 'DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS'
    actions = {
        'send': send,
        'my_action': my_action,
    }
    client = Wit(access_token = access_token,actions = actions)
    response = client.message(messageString);
    print(response)
    return response
