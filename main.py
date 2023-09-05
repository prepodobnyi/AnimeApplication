from kivymd.app import MDApp
import kivy
kivy.require('2.2.1')
from kivy.uix.screenmanager import ScreenManager, Screen
from threading import Thread
from functools import partial
from kivy.clock import Clock
from kivymd.uix.button.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.core.window import Window
from kivymd.uix.fitimage.fitimage import FitImage
from kivy.metrics import dp
from anime_parser import *
from view import *
import textwrap
token = '447d179e875efe44217f20d1ee2146be'



class NewThread(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
    def run(self):
        if self._target != None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
  
class ScrollHorizontalOnY(ScrollView):
    def on_scroll_move(self, touch):
        super().on_scroll_move(touch)
        touch.ud['sv.handled']['y'] = False 
        
  
class VerticallScroll(ScrollView):
    def on_scroll_stop(self, touch, check_children=True):
        super().on_scroll_stop(touch, check_children=False)

class SearchScreen(Screen,FocusBehavior):
    ongoing_bar = ObjectProperty()
    popular_bar = ObjectProperty()
    all_anime_bar = ObjectProperty()
    mainboxl = ObjectProperty()
    def __init__(self, **kw):
        super(SearchScreen,self).__init__(**kw)
        self.ongoing_thred = NewThread(target=get_shiki_ongoing)
        self.ongoing_thred.daemon = True
        self.ongoing_thred.start()
        self.popular_thred = NewThread(target=get_shiki_popular) 
        Window.bind(on_key_down=self.on_key_down)

    def on_key_down(self, window, key, *args):
        if key == 276:  # Код клавиши "влево"
            # Перемещаем фокус на предыдущий виджет
            self.manager.current = 'parametr'
        elif key == 275:  # Код клавиши "вправо"
            # Перемещаем фокус на следующий виджет
            print("work")
            
    def loading_ongoing(self,*args): 
        if not self.ongoing_thred.is_alive():
            ongoings = self.ongoing_thred.join()
            self.max_len = 20
            for anime_id,anime_image_title in ongoings.items():
                if self.max_len > 0:
                    self.max_len -=1
                    card = create_card(self, anime_id, anime_image_title)
                    self.ongoing_bar.add_widget(card)
            mdlabel = MDLabel(text="ЕЩЁ", halign="center", font_style='Caption')
            button = MDCard(mdlabel,
                               id='add_all_ongoing',
                               size=('125dp', '277dp'),
                               size_hint=(None, None),
                               radius=[25, 25, 4, 4],
                               on_release=lambda *args: self.manager.get_screen('all_anime').add_all_ongoing(ongoings, *args))
            
            self.ongoing_bar.add_widget(button)       
            Clock.unschedule(self.loading_ongoing)
            self.popular_thred.daemon = True
            self.popular_thred.start()

    def loading_popular(self,*args): 
        if self.popular_thred.ident and not self.popular_thred.is_alive():
            popular = self.popular_thred.join()
            self.max_len = 20
            for anime_id,anime_image_title in popular.items():
                if self.max_len > 0:
                    self.max_len -=1
                    card = create_card(self, anime_id, anime_image_title)
                    self.popular_bar.add_widget(card)

            mdlabel = MDLabel(text="ЕЩЁ", halign="center", font_style='Caption')
            button = MDCard(mdlabel,
                               id='add_all_popular',
                               size=('125dp', '277dp'),
                               size_hint=(None, None),
                               radius=[25, 25, 4, 4],
                               on_release=lambda *args: self.manager.get_screen('all_anime').add_all_pupular(popular, *args))
            self.popular_bar.add_widget(button)
            Clock.unschedule(self.loading_popular)
    
    def search_anime(self):
        (get_link_anime(self.ids.search_field.text))    
    
    def return_selected_anime(self,fitimage,anime_title,*args,):
        
        self.shiki_data = get_shiki_data(str(args[0].id))
        print(self.shiki_data)
        description = textwrap.shorten(self.shiki_data['descript'], width=695, placeholder="...")
        self.manager.get_screen('parametr').ids.label.text = str(anime_title)
        self.manager.get_screen('parametr').ids.description.text = str(description)
        self.manager.get_screen('parametr').ids.score.text = str(f"Score: {self.shiki_data['score']}")
        
        self.manager.get_screen('parametr').ids.title_image.source = fitimage.source
        self.manager.current = 'parametr'
        
        
class AllAnimeScreen(Screen):
    from view import add_all_ongoing, add_all_pupular
    width_dp = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popular_thred1 = NewThread(target=get_shiki_popular, args=(1,))
        self.popular_thred1.daemon = True
        self.popular_thred1.start()
        self.current_index = 0
        width, height = Window.size
        self.width_dp = int(dp((width) - 645) / 4)
        

    def load_more_cards(self, *args):
    # проверка, достиг ли пользователь конца скролла
        
        if self.ids.scroll_all_anime.scroll_y > 0:
            return
        if self.current_index >= len(self.all_anime):
            return 
        # добавление новой порции карточек
        last_visible_widget = self.ids.all_anime_bar.children[0]
        for i in range(self.current_index, min(self.current_index + self.batch_size, len(self.all_anime))):
            anime_id, anime_image_title = list(self.all_anime.items())[i]
            card = create_card(self, anime_id, anime_image_title)
            self.ids.all_anime_bar.add_widget(card)
        self.current_index += self.batch_size
        self.ids.scroll_all_anime.scroll_to(last_visible_widget)
            

class ChoiceParametrScreen(Screen):
    pass

class WatchAnimeScreen(Screen):
    pass


class AnimeAPP(MDApp):
    def check_key(self, *args):
        print(*args)

    def on_joy_button_down(self, win, stickid, buttonid):
        print('button_down', stickid, buttonid)

    #Вверх 1 11
    #Вниз 1 12
    #Влево 1 13
    #Вправо 1 14
    #Ок 1 0
    #Назад 1 4


    def build(self):
        
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        self.theme_cls.theme_style = "Dark"
        sm = ScreenManager()
        sm.add_widget(SearchScreen(name='search'))
        Clock.schedule_interval(sm.get_screen('search').loading_ongoing, 1)
        Clock.schedule_interval(sm.get_screen('search').loading_popular, 1)
        sm.add_widget(ChoiceParametrScreen(name='parametr'))
        sm.add_widget(WatchAnimeScreen(name='watch_anime'))
        sm.add_widget(AllAnimeScreen(name='all_anime'))
        Clock.schedule_interval(sm.get_screen('all_anime').load_more_cards, 2)
        return sm

if __name__ == '__main__':
    animr_app = AnimeAPP()
    
    animr_app.run()
    
    
    
    