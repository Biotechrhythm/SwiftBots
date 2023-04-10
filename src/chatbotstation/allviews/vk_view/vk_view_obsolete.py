import time, super_view, vk_api, configparser, os
from vk_api.bot_longpoll import VkBotEventType

class VkView():
    def __init__(self, bot):
        super().__init__(bot)
        self.keys = self._load_keys('data.ini')
        try:
          session = vk_api.VkApi(token=keys.public_token, api_version='5.103')
          self.lp = VkBotLongPoll(session, keys.public_id)
          self.pub_api = session.get_api()
        except Exception as e:
          log('!!ERROR!! Critical error in ApiManager!\n'+str(type(e))+'\n'+str(e))
          import os
          os._exit(1)
        self.lp = bot.api.lp

    def _load_keys(self, path):
      config = configparser.ConfigParser()
      config.read(path)
      if 'VkStuff' not in config.sections():
        config.add_section("VkStuff")
        self.log(f'View {self.__name__} has not filled data.ini')
      
      for i in config.items("Names"):
        print(i)
      os._exit(1)

    def listen(self, mode=1):
        if mode == 0:
            pass #quiet start
        elif mode == 1:
            self.sender.report('Бот запущен!')
            self.log('Bot is started. mode %d' % mode) 
        elif mode == 2:
            self.sender.report('Бот перезапущен!')
            self.log('Bot is restarted %d' % mode) 
        elif mode == 3:
            self.log('Bot is restarted %d' % mode)
        try:
            self.__listen__()
        except requests.exceptions.ConnectionError:
            self.log('Connection ERROR in core')
            time.sleep(60)
            self.listen(3)

        except requests.exceptions.ReadTimeout:
            self.log('ReadTimeout (night reboot)')
            time.sleep(60)
            self.listen(3) 
        
        except Exception as e:
            self.sender.report('Exception in Botbase:\n'+str(type(e))+'\n'+str(e))
            self.sender.report('Бот запустится через 5 секунд')
            self.log('!!ERROR!!\nException in Botbase:\n'+str(type(e))+'\n'+str(e))
            time.sleep(5)
            self.listen(2)
    
    def __listen__(self):
        self.log('Listening is started')
        for event in self.lp.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object.message.get('text').lower()
                user_id = str(event.object.message.get('from_id'))

                self.log(f'\nThe message from "{user_id}" is catched: "{message}"')
                self._bot.last_msg = time.time()
                controller = None
                #controllers
                for x in self.controllers:
                    if message in x.cmds:
                        controller = x
                if controller != None:
                    controller.message = message
                    controller.user_id = user_id
                    method = controller.cmds.get(message)
                else:
                    #prefixes in controllers
                    for cont in self.controllers:
                        for pref in cont.prefixes:
                            if message.startswith(pref) and (message == pref or message[len(pref)] == ' '):
                                controller = cont
                                if message == pref:
                                    cont.message = ''
                                else:
                                    cont.message = message[len(pref)+1:]
                                controller.user_id = user_id
                                method = controller.prefixes.get(pref)
                if controller != None:
                    if not callable(method):
                        if user_id in self.keys.oper_ids and user_id != self.keys.admin_id:
                            self.sender.send(user_id,
                                             f'There\'s fatal error! "{str(method)}" from class "{type(controller).__name__}" is not a method or a function!')
                        self.sender.report(f'There\'s fatal error! "{str(method)}" from class "{type(controller).__name__}" is not a method or a function!')
                        self.log(f'!!ERROR!!\nThere\'s fatal error! "{str(method)}" from class "{type(controller).__name__}" is not a method or a function!')
                        continue
                    self.log(f'Method "{method.__name__}" from class "{type(controller).__name__}" is called')
                    try:
                        method(controller)
                    except Exception as e:
                        if user_id in self.keys.oper_ids and user_id != self.keys.admin_id:
                            self.sender.send(user_id,
                                             f'Exception in "{method.__name__}" from "{type(controller).__name__}":\n{str(type(e))}\n{str(e)}')
                        self.sender.report(f'Exception in "{method.__name__}" from "{type(controller).__name__}":\n{str(type(e))}\n{str(e)}')
                        self.log(f'!!ERROR!!\nException in "{method.__name__}" from "{type(controller).__name__}":\n{str(type(e))}\n{str(e)}')
                else:
                    self.unknown_cmd(user_id)

    def unknown_cmd(self, user_id):
        self.log('That\'s unknown command')
        if user_id == self.keys.admin_id:
            self.api.pub_api.messages.markAsRead(group_id=self.keys.public_id,mark_conversation_as_read=1,peer_id=user_id)
        else:
            self.sender.send(user_id, 'Неизвестная команда')

