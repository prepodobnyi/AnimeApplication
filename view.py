import textwrap
from kivymd.uix.fitimage.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard


def create_card(screen, anime_id, anime_image_title):
    text = textwrap.shorten(anime_image_title[1], width=60, placeholder="...")
    fitimage = FitImage(source=anime_image_title[0], radius=[25,])
    mdlabel = MDLabel(text=text, size_hint=(1, .4), font_style='Caption')
    card = MDCard(fitimage, mdlabel,
                  focus_behavior=True,
                  on_release=lambda *args: screen.manager.get_screen('search').return_selected_anime(fitimage, anime_image_title[1] , *args),
                  id=anime_id,
                  orientation="vertical",
                  size_hint=(None, None),
                  radius=[25, 25, 4, 4],
                  ripple_behavior=True,
                  size=('125dp', '277dp'))
    return card

def add_all_ongoing(self,all_anime,*args,):
    self.ids.all_anime_bar.clear_widgets()
    self.ids.scroll_all_anime.scroll_y = 1
    
    self.all_anime = all_anime
    self.manager.current = 'all_anime'
    self.batch_size = 10
    self.current_index = 0
    for i in range(self.current_index, min(self.current_index + self.batch_size, len(self.all_anime))):
        anime_id, anime_image_title = list(self.all_anime.items())[i]
        card = create_card(self, anime_id, anime_image_title)
        self.ids.all_anime_bar.add_widget(card)
    self.current_index += self.batch_size

def add_all_pupular(self,all_anime,*args,):
    self.ids.all_anime_bar.clear_widgets()
    self.ids.scroll_all_anime.scroll_y = 1
    self.manager.current = 'all_anime'
    all_anime = self.popular_thred1.join() 
    self.all_anime = all_anime
    self.batch_size = 10
    self.current_index = 0
    for i in range(self.current_index, min(self.current_index + self.batch_size, len(self.all_anime))):
        anime_id, anime_image_title = list(self.all_anime.items())[i]
        card = create_card(self, anime_id, anime_image_title)
        self.ids.all_anime_bar.add_widget(card)
    self.current_index += self.batch_size