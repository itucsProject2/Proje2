from wit import Wit

def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content

def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    """
    Sender function
    """
    # We use the fb_id as equal to session_id
    fb_id = request['session_id']
    text = response['text']
    # send message
    fb_message(fb_id, text)




def my_action(request):
    print('Received from user...', request['text'])


actions = {
    'send': send,
    'receive':my_action,
    
}


# Setup Wit Client
client = Wit(access_token=WIT_TOKEN, actions=actions)






#def sendToWit(messageString):
#    access_token = 'DJE4HFOBMAJO6DMIC2IEZRP5DDRQRZKS'
#    actions = {
#        'send': send,
#        'my_action': my_action,
#    }
#    client = Wit(access_token = access_token,actions = actions)
#    try:
#        resp = client.message(messageString);
#        pprint(resp)
#        return resp
#    except:
#        return('wit.ai integration error')
