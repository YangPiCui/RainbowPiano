from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen,SwapTransition,ScreenManager
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty
from kivy.uix.screenmanager import SwapTransition
import shutil
from kivy.storage.jsonstore import JsonStore
from kivy.core.text import Label as CoreLabel
import os
import math
from kivy.utils import platform
from kivymd.uix.snackbar import Snackbar
from kivy.uix.filechooser import FileChooserListView
import json

import webbrowser 
from kivy.graphics import PushMatrix, PopMatrix, Translate

from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from functools import partial
import numpy as np
import pygame   #for play sound only 
from kivy.clock import Clock

from kivy.metrics import dp
from kivy.uix.colorpicker import ColorPicker
Config.set('graphics', 'fullscreen', '0')
Config.write()
from kivy.core.window import Window
pera_keys=1
class ColoredLabel(Label):
    def __init__(self, background_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = background_color
        
        with self.canvas.before:
            Color(*self.background_color)  # Set the background color
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
class BorderedBoxLayout(BoxLayout):
    def __init__(self, border_color=(0, 0, 0, 1), border_width=2, **kwargs):
        super().__init__(**kwargs)
        self.border_color = border_color
        self.border_width = border_width
        
        with self.canvas.after:  # Draw the border after other widgets are drawn
            Color(*self.border_color)
            self.border = Line(width=self.border_width)
        
        self.bind(pos=self._update_border, size=self._update_border)

    def _update_border(self, *args):
        # Update the border's position and size
        self.border.rectangle = (*self.pos, *self.size)

class ColoredBoxLayout(ButtonBehavior,MDBoxLayout):
    def __init__(self, background_color=(1, 1, 1, 1),tone=None,layout=None,bk=None, **kwargs):
        super().__init__(**kwargs)
        self._background_color = background_color
        self.active_color = (0, 1, 0, 1)  # Green
        self.active = False
        self.tune = tone
        self.elevation= 10
        self.layout=layout
        self.md_bg_color= self._background_color
        print(self.tune)
        global pera_keys
        self.app=MDApp.get_running_app()
        if self.app.white_key:
            self.radius=[0,0,8,8]
        elif self.app.black_key:
            if self.tune=="0A":
                self.radius=[0,0,0,8]
            elif self.tune=="8C":
                self.radius=[0,0,8,8]
            elif self.tune=="7B":
                self.radius=[0,0,8,0]
            elif bk=="full":
                self.radius==[0,0,0,0]
            elif bk=="black":
                self.radius=[0,0,8,8]
            elif bk=="h1":
                self.radius=[0,0,8,0]
            elif bk=="h2":
                self.radius=[0,0,0,8]
        else:
            if self.tune and self.tune[-1]!='#' and self.tune[-1]!='a':
                in_c= self.app.piano_notes.index(self.tune)
                if in_c==0:
                    self.radius=[0,0,0,8]
                elif in_c==87:
                    self.radius=[0,0,8,8]
                else:
                    in_a=in_c-1
                    in_b = in_c+1
                    tr=0
                    tl=0
                    br=0
                    bl=0
                    if self.app.piano_notes[in_b][-1]=='#':
                        br=0
                    else:
                        br=8
                    if self.app.piano_notes[in_a][-1]=='#':
                        bl=0
                    else:
                        bl=8
                    self.radius=[tr,tl,br,bl]
            if self.tune and self.tune[-1]=='a':
                if pera_keys==1:
                    self.radius=[0,0,8,0]
                    pera_keys=2
                else:
                    self.radius=[0,0,0,8]
                    pera_keys=1
            if self.tune and self.tune[-1]=='#':
                self.radius=[0,0,8,8]
            
            


        # with self.canvas.before:
        #     self.color = Color(*self._background_color)
        #     self.rect = Rectangle(size=self.size, pos=self.pos)
        # self.bind(size=self._update_rect, pos=self._update_rect)
       
    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def set_background_color(self, color):
        # Update the color in the canvas
        self._background_color = color
        self.md_bg_color= self._background_color
        
        #self.color.rgba = color
class MainScreen(Screen):
    def sustain_sound(self):
        app=MDApp.get_running_app()
        
        if self.ids.sustain_img.source=="images/sustainoff.png":
            self.ids.sustain_img.source = "images/sustainon.png"
            app.sustain_tune = True
        else:
            self.ids.sustain_img.source="images/sustainoff.png"
            app.sustain_tune = False
       
    pass

class MySlider(Slider):
    pass

class Equalizer:
    def __init__(self):
        self.bands = 10
        self.min_freq = 20
        self.max_freq = 20000
        self.app=MDApp.get_running_app()
        
        self.gains = self.app.main_gain
        

        self.calculate_band_frequencies()
        
    def calculate_band_frequencies(self):
        self.frequencies = np.logspace(np.log10(self.min_freq), np.log10(self.max_freq), self.bands + 1)
    
    def set_gain(self, band, gain):
        self.gains[band] = gain
    
    def apply_eq(self, audio_data, sample_rate):
        fft_data = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
        
        for i in range(self.bands):
            low, high = self.frequencies[i], self.frequencies[i+1]
            mask = (freqs >= low) & (freqs < high)
            fft_data[mask] *= self.gains[i]
        
        eq_audio = np.fft.irfft(fft_data)
        return eq_audio.astype(np.int16)

    def get_band_range(self, band):
        return self.frequencies[band], self.frequencies[band + 1]
class EqualizerPopup(Popup):
    def create_popup(self):
        self.app=MDApp.get_running_app()
        
        # Equalizer
        self.equalizer = Equalizer()
        eq_layout = BoxLayout(size_hint=(1, 1))
        self.eq_sliders = []
        for i in range(10):
            freq_range = self.equalizer.get_band_range(i)
            slider = EqualizerSlider(i, freq_range)
            slider.slider.bind(value=self.update_equalizer)
            
            eq_layout.add_widget(slider)
            self.eq_sliders.append(slider.slider)
        self.ids.slide_hold.add_widget(eq_layout)
    def dismiss_dia(self):
        self.dismiss()
    def reset(self):
        for u in self.eq_sliders:
            u.value = 1.0
            
        self.app.main_gain=np.ones(10)
        self.equalizer.gains = self.app.main_gain
    def change_eqstate(self):
        self.app.equalizer=self.ids.eq_switch.active
        
    def update_equalizer(self, instance, value):
        band = self.eq_sliders.index(instance)
        self.equalizer.set_gain(band, value)
        

class EqualizerSlider(BoxLayout):
    def __init__(self, band, freq_range, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.band = band
        self.app=MDApp.get_running_app()
        
        self.low_freq, self.high_freq = freq_range
        freq = self.low_freq * (self.high_freq / self.low_freq) ** (self.app.main_gain[self.band] / 2)
        
        self.slider = Slider(min=0, max=2, value=float(self.app.main_gain[self.band]), orientation='vertical')
        self.label = Label(text=f'{self.format_freq(freq)}', font_size='10sp',size_hint_y= None,height=20)
   
        self.slider.bind(value=self.update_label)
        self.add_widget(self.slider)
        self.add_widget(self.label)
    @staticmethod
    def format_freq(freq):
        if freq >= 1000:
            return f'{freq/1000:.1f}kHz'
        else:
            return f'{freq:.0f}Hz'
    def update_label(self, instance, value):
        freq = self.low_freq * (self.high_freq / self.low_freq) ** (value / 2)
        self.label.text = f'{self.format_freq(freq)}'
class LabelPopup(Popup):
    #keys_label
    def write_custom(self):

        self.app=MDApp.get_running_app()
        if len(self.app.custom_label.keys())==12:
            self.ids.lbl_1.text=self.app.custom_label["C"]
            self.ids.lbl_2.text=self.app.custom_label["C#"]
            self.ids.lbl_3.text=self.app.custom_label["D"]
            self.ids.lbl_4.text=self.app.custom_label["D#"]
            self.ids.lbl_5.text=self.app.custom_label["E"]
            self.ids.lbl_6.text=self.app.custom_label["F"]
            self.ids.lbl_7.text=self.app.custom_label["F#"]
            self.ids.lbl_8.text=self.app.custom_label["G"]
            self.ids.lbl_9.text=self.app.custom_label["G#"]
            self.ids.lbl_10.text=self.app.custom_label["A"]
            self.ids.lbl_11.text=self.app.custom_label["A#"]
            self.ids.lbl_12.text=self.app.custom_label["B"]
        if self.app.keys_label!=None:

            if self.app.keys_label=="Notes":
                self.ids.f_4.active=True
            elif isinstance( self.app.keys_label,dict): #==self.app.custom_label:
                self.ids.f_6.active=True
            elif self.app.keys_label[0]=="1":
                self.ids.f_1.active=True
            elif self.app.keys_label[0]=="A":
                self.ids.f_2.active=True
            elif self.app.keys_label[0]=="a":
                self.ids.f_3.active=True
            
        else:
            self.ids.f_5.active=True
    def apply_changes(self):
        
        if self.ids.f_1.active:
            self.dismiss()
            self.app.keys_label=["1","2","3","4","5","6","7"]
            self.app.update_visiblekeys()
        elif self.ids.f_2.active:
            
            self.app.keys_label=["A","B","C","D","E","F","G"]
            self.app.update_visiblekeys()
            self.dismiss()
        elif self.ids.f_3.active:
            self.app.keys_label=["a","b","c","d","e","f","g"]
            self.app.update_visiblekeys()
            self.dismiss()
            
        elif self.ids.f_4.active:
            self.app.keys_label="Notes"
            self.app.update_visiblekeys()
            self.dismiss()
            
        elif self.ids.f_5.active:
            self.app.keys_label = None
            self.app.update_visiblekeys()
            self.dismiss()
            
        elif self.ids.f_6.active:
            # if len(self.ids.lbl_1.text)>3 or len(self.ids.lbl_2.text)>3 or len(self.ids.lbl_3.text)>3 or len(self.ids.lbl_4.text)>3 or len(self.ids.lbl_5.text)>3 or len(self.ids.lbl_6.text)>3 or len(self.ids.lbl_7.text)>3:
            #     self.ids.error_msg.text="In custom label you can add 3 latter maximum."
            #else:
            self.app.custom_label={
                "C":self.ids.lbl_1.text,
                "C#":self.ids.lbl_2.text,
                "D":self.ids.lbl_3.text,
                "D#":self.ids.lbl_4.text,
                "E":self.ids.lbl_5.text,
                "F":self.ids.lbl_6.text,
                "F#":self.ids.lbl_7.text,
                "G":self.ids.lbl_8.text,
                "G#":self.ids.lbl_9.text,
                "A":self.ids.lbl_10.text,
                "A#":self.ids.lbl_11.text,
                "B":self.ids.lbl_12.text,
                
                }
            self.app.keys_label=self.app.custom_label
            self.app.update_visiblekeys()
            self.dismiss()
    def dismiss_dialog(self):
        self.dismiss()
    pass
class ColorPopup(Popup):
    def create_popup(self,action=None):
        self.app=MDApp.get_running_app()
        if(action!=None):
            self.ids.pattern_cls.clear_widgets()
            self.ids.custom_cls.clear_widgets()
        self.main_bx = BoxLayout(orientation="vertical",size_hint_y= None,height=45*12)
        self.custom_bx = BoxLayout(orientation="vertical",size_hint_y= None,height=45*88)
        if(self.app.custom_color_active):
            self.ids.switchy.text = "Deactive"
            self.ids.switchx.text = "Active"
        else:
            self.ids.switchx.text= "Deactive"
            self.ids.switchy.text = "Active"
        v=1
        for i in ["1C","1C#","1D","1D#","1E","1F","1F#","1G","1G#","0A","0A#","0B"]:
            bx2 = BoxLayout(orientation="horizontal",size_hint_y= None,height=40)
            
            lblnum = Label(text=str(v)+'.',size_hint_x= None,width=dp(30))
            vst = i[1:]
            if len(vst)!=2:
                vst=vst+" "

            lbl = Label(text=vst,size_hint_x=None,width=dp(30),)
            lblfree = Label()
            btn = Button(size_hint_x=None,width=dp(30),    background_normal= '',background_color= self.app.notes_color[i],on_release= lambda instance, lbtn=i : self.open_color_picker(instance,lbtn,True))
            
            bx2.add_widget(lblnum)
            bx2.add_widget(lbl)
            bx2.add_widget(lblfree)
            bx2.add_widget(btn)
            
            self.main_bx.add_widget(bx2)
            paddinglbl = Label(size_hint_y=None,height=5)
            self.main_bx.add_widget(paddinglbl)
            
            v+=1
        self.ids.pattern_cls.add_widget(self.main_bx)
        v=1
        for i in list(self.app.custom_color.keys()):
            bx2 = BoxLayout(orientation="horizontal",size_hint_y= None,height=40)
            
            lblnum = Label(text=str(v)+'.',size_hint_x= None,width=dp(30))
            vst = i
            if len(vst)!=2:
                vst=vst+" "

            lbl = Label(text=vst,size_hint_x=None,width=dp(50))
            lblfree = Label()
            btn = Button(size_hint_x=None,width=dp(30),    background_normal= '',background_color= self.app.custom_color[i],on_release= lambda instance, lbtn=i : self.open_color_picker(instance,lbtn,False))
            
            bx2.add_widget(lblnum)
            bx2.add_widget(lbl)
            bx2.add_widget(lblfree)
            bx2.add_widget(btn)
            
            self.custom_bx.add_widget(bx2)
            paddinglbl = Label(size_hint_y=None,height=5)
            self.custom_bx.add_widget(paddinglbl)
            
            v+=1
        self.ids.custom_cls.add_widget(self.custom_bx)
    def open_color_picker(self, instance, btn,frm):
        # Create a ColorPicker widget
        color_picker = ColorPicker()
        #color_picker.bind(color=self.on_color)
        if frm:
            color_picker.color = list(self.app.notes_color[btn])
        else:
            color_picker.color = list(self.app.custom_color[btn])
            
        bx = BoxLayout(orientation='vertical')
        bx3 = BoxLayout(orientation= 'horizontal',size_hint_y= None,height=50)
        btn2 = Button(size_hint= (None,None),text="Apply",height=50,width=120)
        btn2.bind(on_release= lambda instance: self.on_color(instance, color_picker.color,btn,frm))
        lbl = Label(size_hint_y=None,height=10)
        lbl2= Label()
        bx.add_widget(color_picker)
        bx3.add_widget(lbl2)
        bx3.add_widget(btn2)
        bx.add_widget(lbl)
        bx.add_widget(bx3)
        # Create a Popup to hold the ColorPicker
        self.popup = Popup(title="Pick a Color", content=bx, size_hint=(0.8, 0.8))

        # Bind the color picker to update the label text with the selected color
        
        # Open the Popup
        self.popup.open()

    def on_color(self, instance, value,dic_id,frm):
        # Update the label text with the selected color (value is a list of RGBA)
        if(frm):
            self.app.notes_color[dic_id]=value
        else:
            self.app.custom_color[dic_id]=value
            
        self.create_popup(True)
        
        self.popup.dismiss()
        if self.app.color_pattern_active:
            self.app.update_color()
        else:
            self.app.custom_update_color()
    def change_cusmeth(self):
        
        if self.ids.switchx.text=="Active":
            self.app.color_pattern_active=True
            self.app.custom_color_active=False
            self.app.update_color()    
        
        else:
            self.app.color_pattern_active=False
            self.app.custom_color_active=True
            self.app.custom_update_color()
        self.create_popup(True)
        
        pass
    def change_method(self):
        
        if self.ids.switchy.text=="Deactive":
            self.app.color_pattern_active=True
            self.app.custom_color_active=False
            self.app.update_color()    
        
        else:
            self.app.color_pattern_active=False
            self.app.custom_color_active=True
            self.app.custom_update_color()
        
        self.create_popup(True)
    def reset_color(self,action):
        if action=="custom":
            
            self.app.custom_color = self.app.defualt_cus
        else:
            self.app.notes_color= self.app.defualt_pat
        self.app.update_color()    
        self.create_popup(True)
           
class ButtonImg(ButtonBehavior,Image):
    pass
class FileChooserIns(Screen):
    selected_files = StringProperty("Add 88 Notes with note name like 0A.wav add icon image(instrument_name.png or instrument_name.jpg)")
    file_list=[]
    def back_to_main(self):
        self.app=MDApp.get_running_app()
        self.app.screen_switch_mainscreen()
    def add_ins(self):
        a=os.listdir('instruments/')
        max_num=0
        for i in a:
            try:
                b=int(i)
                if b>max_num:
                    max_num=b
            except ValueError:
                pass
        
        self.app=MDApp.get_running_app()
        
        icon_added=False
        note_leave=""
        c=0
        if len(self.file_list)>88:
            for i in self.file_list:
                if ".png" in i or ".jpg" in i:
                    icon_added=True
                if ".wav" in i:
                    c+=1
                
                    note_find=False
                        
                    for j in self.app.piano_notes:
                        if j in i:
                            note_find=True
                    if note_find==False:
                        note_leave="miss"
            if icon_added==False:
                self.ids.error_msg.text="Please add icon file with instrument name(name.png or name.jpg)"
            elif note_leave!="":
                self.ids.error_msg.text="you "+note_leave+ " notes. please add like name A0.wav"
            elif  c<88:
                self.ids.error_msg.text="Please select all notes(.wav)"
            else:
                destination_directory="instruments/"+str(max_num+1)
                os.makedirs(destination_directory, exist_ok=True)
                for i in self.file_list:
                    destination_file = os.path.join(destination_directory, os.path.basename(i))
                    try:
                        shutil.copy(i, destination_file)
                        Snackbar(
                            text=f"Instrument added successfully",
                            snackbar_x="10dp",
                            snackbar_y="10dp",
                            size_hint_x=(
                                Window.width - (dp(10) * 2)
                            ) / Window.width
                        ).open()
                    except FileNotFoundError:
                        pass
                    except PermissionError:
                        pass
                    except Exception as e:
                        Snackbar(
                            text=f"An error occurred: {e}",
                            snackbar_x="10dp",
                            snackbar_y="10dp",
                            size_hint_x=(
                                Window.width - (dp(10) * 2)
                            ) / Window.width
                        ).open()
                self.app.screen_switch_mainscreen()


                pass

            
        

        else:
            self.ids.error_msg.text="Please select all notes with icon"
    def select_files(self, *args):
        selected = args[1]  # The second argument of on_selection contains the list of selected files
        if selected:
            self.file_list=list(selected)
            if len(list(selected))!=0:
                self.ids.ins_data.height=0
                self.ids.ins_data.text=''
                self.ids.scroll_view.height=60
                self.ids.main_box.clear_widgets()
                for i in list(selected):
                    self.ids.main_box.add_widget(Label(text="  "+str(selected.index(i)+1)+".    "+str(i),size_hint_y=None,height=24,text_size= (self.width, None),halign= 'left'))
            else:
                self.ids.ins_data.height=60
                self.ids.ins_data.text=self.selected_files
                self.ids.scroll_view.height=0
                self.file_list=[]
                
        else:
            self.selected_files = "Add 88 Notes with note name like 0A.wav add icon image(instrument_name.png or instrument_name.jpg)"
            self.file_list=[]
            self.ids.ins_data.height=0
            self.ids.ins_data.text=self.selected_files
            self.ids.scroll_view.height=60
            
            
class InstrumentPopup(Popup):
    def create_popup(self):
        self.app=MDApp.get_running_app()
        self.ids.ins_container.cols= self.app.window_width//300
        list_ins={}
        self.ins_id=[]
        self.selected_ins={}
        for f in os.listdir('instruments'):
            try:
                l = os.listdir('instruments/'+f)
                if len(l)>88:
                    list_ins[f]=l      
            except:
                pass
        
        for i in list_ins.keys():
            for v in list_ins[i]:
                if v.endswith(('.png', '.jpg')):
                    name = v.split('.')
                    
                    back_cls = (40/255,40/255,40/255,1)
                    if self.app.selected_instrument==i:
                        back_cls = (150/255,150/255,150/255,1)
                        self.selected_ins={}
                        self.selected_ins[i]=v
                    ab = ColoredBoxLayout(orientation='vertical',size_hint= (None,None),width=200,height=300,background_color=back_cls,padding=10,on_press = lambda ins, vid=i,ns=v: self.change_ins(vid,ns))
                    img = Image(source="instruments/"+i+"/"+v)
                    lbl = Label(text=name[0],size_hint_y= None,height=30)
                    ab.add_widget(img)
                    ab.add_widget(lbl)
                    self.ids.ins_container.ids[i]=ab
                    self.ids.ins_container.add_widget(ab)
                    self.ins_id.append(i)
        ab = ColoredBoxLayout(orientation='vertical',size_hint= (None,None),width=200,height=300,background_color=(40/255,40/255,40/255,1),padding=10,on_release = lambda ins: self.add_custom())
        img = Label(text="+",bold=True,font_size=64)
        lbl = Label(text="Add Custom \nInstruments",font_size=22,size_hint_y= None,height=30)
        ab.add_widget(img)
        ab.add_widget(lbl)
        self.ids.ins_container.add_widget(ab)
                    
    def add_custom(self):
        self.dismiss()
        self.app.screen_switch_chosefile()
    def change_ins(self,vid,name):
        self.selected_ins={}
        self.selected_ins[vid]=name
        for i in self.ins_id:
            if i==vid:
                self.ids.ins_container.ids[i].set_background_color((150/255,150/255,150/255,1))
            else:
                self.ids.ins_container.ids[i].set_background_color((40/255,40/255,40/255,1))
    def dismiss_dia(self):
        self.dismiss()
    def apply_changes(self):
        ins_id = list(self.selected_ins.keys())[0]
        name = self.selected_ins[ins_id]
        self.app.selected_instrument=ins_id
        self.app.instrument_img= "instruments/"+ins_id+"/"+name
        self.app.instrument_icon()
        self.app.load_sample()
        self.dismiss()
        
    pass    
class MyPopup(Popup):
    def dec_number(self):
        app=MDApp.get_running_app()
            
        num = int(self.ids.number_row.text)
        if(num!=1):
            num=num-1
            app.numberof_row= str(num)
            app.update_piano(num,None)
        

        self.ids.number_row.text = str(num)
    def inc_number(self):
        app=MDApp.get_running_app()
            
        num = int(self.ids.number_row.text)
        if(num!=10):
            num=num+1
            app.numberof_row= str(num)
            
            app.update_piano(num,None)
        
        self.ids.number_row.text = str(num)
    def change_white(self):
        app=MDApp.get_running_app()
        if self.ids.switch.active:
            app.white_key=True
            app.black_key=False
            self.ids.switch2.active=False
            app.whitekeys_only('w')
        else:
            app.white_key=False
            app.update_piano(int(self.ids.number_row.text),'w')
    def change_black(self):
        app=MDApp.get_running_app()
        if self.ids.switch2.active:
            app.black_key=True
            app.white_key=False
            self.ids.switch.active=app.white_key
            app.evenback_keys('b')
           
        else:
            app.black_key=False
            app.update_piano(int(self.ids.number_row.text),'b')
        
    def visible_keys(self,opration):
        app=MDApp.get_running_app()
        keys = int(self.ids.visible_key.text)
        if opration:
            if keys!=88:
                keys+=1
                
        else:
            if keys!=6:
                keys-=1
                
        app.visible_keys = str(keys)
        app.wid = app.window_width/keys -0.05
        self.ids.visible_key.text=str(keys)
        app.update_visiblekeys()
       # app.update_piano(int(self.ids.number_row.text),'k')
        
        pass
    def keyboard_lock(self):
        lock = self.ids.switch3.active
        app=MDApp.get_running_app()
        app.keyboard_lock= lock
        app.lock_mode()
        #app.update_piano(int(self.ids.number_row.text))
        
    pass
class PaddingLabel(Label):
    pass

class PianoApp(MDApp):
    def __init__(self):
        super(PianoApp, self).__init__()
        self.screen= Screen()
        
        self.sm= ScreenManager()
        self.visible_keys = self.retrieve_data("visible_keys") if self.retrieve_data("visible_keys") is not None else "25"
        self.window_width, self.window_height = Window.size
        self.wid = self.window_width / int(self.visible_keys) - 0.05
            
        self.numberof_row=self.retrieve_data("numberof_row") if self.retrieve_data("numberof_row") is not None else "1"
        self.keyboard_lock=self.retrieve_data("keyboard_lock") if self.retrieve_data("keyboard_lock") is not None else False
        
        self.custom_color_active=self.retrieve_data("custom_color_active") if self.retrieve_data("custom_color_active") is not None else False
        self.color_pattern_active=self.retrieve_data("color_pattern_active") if self.retrieve_data("color_pattern_active") is not None else True
        self.sustain_tune = self.retrieve_data("sustain_tune") if self.retrieve_data("sustain_tune") is not None else False
        self.selected_instrument=self.retrieve_data("selected_instrument") if self.retrieve_data("selected_instrument") is not None else "1"
        self.equalizer = self.retrieve_data("equalizer") if self.retrieve_data("equalizer") is not None else False
        
        self.save_scroll= self.retrieve_data("save_scroll") if self.retrieve_data("save_scroll") is not None else  {"0":27/(88-int(self.visible_keys)),"1":27/(88-int(self.visible_keys))}
        self.main_gain = np.array(self.retrieve_data("main_gain")) if self.retrieve_data("main_gain") is not None else np.ones(10)
        select_files = [f for f in os.listdir('instruments/1') if f.endswith(('.png', '.jpg')) ]
        self.instrument_img = "instruments/1/"+select_files[0]
        self.pre_music=0
        self.keys_label=self.retrieve_data("keys_label")
        
        self.custom_label=self.retrieve_data("custom_label") if self.retrieve_data("custom_label") is not None else {"C":"C","C#":"C#","D":"D","D#":"D#","E":"E","F":"F","F#":"F#","G":"G","G#":"G#","A":"A","A#":"A#","B":"B"}
        self.first_note = ['x','y','x','s']
        self.f_label = [0,1,1]
        self.m_label = [ 0,0,0,
                        0,1,2,0,1,0,1,2,0,2,0,1,
                        0,1,2,0,1,0,1,2,0,2,0,1,
                        0,1,2,0,1,0,1,2,0,2,0,1
                        ,0,1,2,0,1,0,1,2,0,2,0,1
                        ,0,1,2,0,1,0,1,2,0,2,0,1
                        ,0,1,2,0,1,0,1,2,0,2,0,1
                        ,0,1,2,0,1,0,1,2,0,2,0,1
                        
                        
                        ]
        self.mid_note = ['x','y','x','y','x','s','x','y','x','y','x','y','x','s']
        self.piano_notes = [
           "0A","0A#","0B",
           "1C","1C#","1D","1D#","1E","1F","1F#","1G","1G#","1A","1A#","1B",
           "2C","2C#","2D","2D#","2E","2F","2F#","2G","2G#","2A","2A#","2B",
           "3C","3C#","3D","3D#","3E","3F","3F#","3G","3G#","3A","3A#","3B",
           "4C","4C#","4D","4D#","4E","4F","4F#","4G","4G#","4A","4A#","4B",
           "5C","5C#","5D","5D#","5E","5F","5F#","5G","5G#","5A","5A#","5B",
           "6C","6C#","6D","6D#","6E","6F","6F#","6G","6G#","6A","6A#","6B",
           "7C","7C#","7D","7D#","7E","7F","7F#","7G","7G#","7A","7A#","7B",
           "8C"
        
            ]
        self.notes_color =self.retrieve_data("notes_color") if self.retrieve_data("notes_color") is not None else {
            "0A":(98/255.0,0,0,1),
            "0A#":(139/255.0,0,0,1),
            "0B":(177/255,0,0,1),
            "1C":(213/255.0,0,0,1),
            "1C#":(248/255.0,0,0,1),
            "1D":(255/255.0,145/255.0,0,1),
            "1D#":(240/255.0,255.0/255.0,0,1),
            "1E":(115/255,255/255,0,1),
            "1F":(0,255/255,181/255,1),
            "1F#":(0,113/255,255/255,1),
            "1G":(109/255,0,251/255,1),
            "1G#":(97/255,0,97/255,1)
        }


        self.defualt_pat={  "0A":(98/255.0,0,0,1),
            "0A#":(139/255.0,0,0,1),
            "0B":(177/255,0,0,1),
            "1C":(213/255.0,0,0,1),
            "1C#":(248/255.0,0,0,1),
            "1D":(255/255.0,145/255.0,0,1),
            "1D#":(240/255.0,255.0/255.0,0,1),
            "1E":(115/255,255/255,0,1),
            "1F":(0,255/255,181/255,1),
            "1F#":(0,113/255,255/255,1),
            "1G":(109/255,0,251/255,1),
            "1G#":(97/255,0,97/255,1)
        }
        self.defualt_cus={'0A': [0.5137254901960784, 0, 0.7098039215686275, 1], '0A#': [0, 0.27450980392156865, 1.0, 1], '0B': [0, 1.0, 0.5725490196078431, 1], '1C': [0.6392156862745098, 1.0, 0, 1], '1C#': [1.0, 0.7450980392156863, 0, 1], '1D': [0.9803921568627451, 0, 0, 1], '1D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '1E': [0, 0.27450980392156865, 1.0, 1], '1F': [0, 1.0, 0.5725490196078431, 1], '1F#': [0.6392156862745098, 1.0, 0, 1], '1G': [1.0, 0.7450980392156863, 0, 1], '1G#': [0.9803921568627451, 0, 0, 1], '1A': [0.5137254901960784, 0, 0.7098039215686275, 1], '1A#': [0, 0.27450980392156865, 1.0, 1], '1B': [0, 1.0, 0.5725490196078431, 1], '2C': [0.6392156862745098, 1.0, 0, 1], '2C#': [1.0, 0.7450980392156863, 0, 1], '2D': [0.9803921568627451, 0, 0, 1], '2D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '2E': [0, 0.27450980392156865, 1.0, 1], '2F': [0, 1.0, 0.5725490196078431, 1], '2F#': [0.6392156862745098, 1.0, 0, 1], '2G': [1.0, 0.7450980392156863, 0, 1], '2G#': [0.9803921568627451, 0, 0, 1], '2A': [0.5137254901960784, 0, 0.7098039215686275, 1], '2A#': [0, 0.27450980392156865, 1.0, 1], '2B': [0, 1.0, 0.5725490196078431, 1], '3C': [0.6392156862745098, 1.0, 0, 1], '3C#': [1.0, 0.7450980392156863, 0, 1], '3D': [0.9803921568627451, 0, 0, 1], '3D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '3E': [0, 0.27450980392156865, 1.0, 1], '3F': [0, 1.0, 0.5725490196078431, 1], '3F#': [0.6392156862745098, 1.0, 0, 1], '3G': [1.0, 0.7450980392156863, 0, 1], '3G#': [0.9803921568627451, 0, 0, 1], '3A': [0.5137254901960784, 0, 0.7098039215686275, 1], '3A#': [0, 0.27450980392156865, 1.0, 1], '3B': [0, 1.0, 0.5725490196078431, 1], '4C': [0.6392156862745098, 1.0, 0, 1], '4C#': [1.0, 0.7450980392156863, 0, 1], '4D': [0.9803921568627451, 0, 0, 1], '4D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '4E': [0, 0.27450980392156865, 1.0, 1], '4F': [0, 1.0, 0.5725490196078431, 1], '4F#': [0.6392156862745098, 1.0, 0, 1], '4G': [1.0, 0.7450980392156863, 0, 1], '4G#': [0.9803921568627451, 0, 0, 1], '4A': [0.5137254901960784, 0, 0.7098039215686275, 1], '4A#': [0, 0.27450980392156865, 1.0, 1], '4B': [0, 1.0, 0.5725490196078431, 1], '5C': [0.6392156862745098, 1.0, 0, 1], '5C#': [1.0, 0.7450980392156863, 0, 1], '5D': [0.9803921568627451, 0, 0, 1], '5D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '5E': [0, 0.27450980392156865, 1.0, 1], '5F': [0, 1.0, 0.5725490196078431, 1], '5F#': [0.6392156862745098, 1.0, 0, 1], '5G': [1.0, 0.7450980392156863, 0, 1], '5G#': [0.9803921568627451, 0, 0, 1], '5A': [0.5137254901960784, 0, 0.7098039215686275, 1], '5A#': [0, 0.27450980392156865, 1.0, 1], '5B': [0, 1.0, 0.5725490196078431, 1], '6C': [0.6392156862745098, 1.0, 0, 1], '6C#': [1.0, 0.7450980392156863, 0, 1], '6D': [0.9803921568627451, 0, 0, 1], '6D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '6E': [0, 0.27450980392156865, 1.0, 1], '6F': [0, 1.0, 0.5725490196078431, 1], '6F#': [0.6392156862745098, 1.0, 0, 1], '6G': [1.0, 0.7450980392156863, 0, 1], '6G#': [0.9803921568627451, 0, 0, 1], '6A': [0.5137254901960784, 0, 0.7098039215686275, 1], '6A#': [0, 0.27450980392156865, 1.0, 1], '6B': [0, 1.0, 0.5725490196078431, 1], '7C': [0.6392156862745098, 1.0, 0, 1], '7C#': [1.0, 0.7450980392156863, 0, 1], '7D': [0.9803921568627451, 0, 0, 1], '7D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '7E': [0, 0.27450980392156865, 1.0, 1], '7F': [0, 1.0, 0.5725490196078431, 1], '7F#': [0.6392156862745098, 1.0, 0, 1], '7G': [1.0, 0.7450980392156863, 0, 1], '7G#': [0.9803921568627451, 0, 0, 1], '7A': [0.5137254901960784, 0, 0.7098039215686275, 1], '7A#': [0, 0.27450980392156865, 1.0, 1], '7B': [0, 1.0, 0.5725490196078431, 1], '8C': [0.6392156862745098, 1.0, 0, 1]}

        self.custom_color = self.retrieve_data("custom_color") if self.retrieve_data("custom_color") is not None else {'0A': [0.5137254901960784, 0, 0.7098039215686275, 1], '0A#': [0, 0.27450980392156865, 1.0, 1], '0B': [0, 1.0, 0.5725490196078431, 1], '1C': [0.6392156862745098, 1.0, 0, 1], '1C#': [1.0, 0.7450980392156863, 0, 1], '1D': [0.9803921568627451, 0, 0, 1], '1D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '1E': [0, 0.27450980392156865, 1.0, 1], '1F': [0, 1.0, 0.5725490196078431, 1], '1F#': [0.6392156862745098, 1.0, 0, 1], '1G': [1.0, 0.7450980392156863, 0, 1], '1G#': [0.9803921568627451, 0, 0, 1], '1A': [0.5137254901960784, 0, 0.7098039215686275, 1], '1A#': [0, 0.27450980392156865, 1.0, 1], '1B': [0, 1.0, 0.5725490196078431, 1], '2C': [0.6392156862745098, 1.0, 0, 1], '2C#': [1.0, 0.7450980392156863, 0, 1], '2D': [0.9803921568627451, 0, 0, 1], '2D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '2E': [0, 0.27450980392156865, 1.0, 1], '2F': [0, 1.0, 0.5725490196078431, 1], '2F#': [0.6392156862745098, 1.0, 0, 1], '2G': [1.0, 0.7450980392156863, 0, 1], '2G#': [0.9803921568627451, 0, 0, 1], '2A': [0.5137254901960784, 0, 0.7098039215686275, 1], '2A#': [0, 0.27450980392156865, 1.0, 1], '2B': [0, 1.0, 0.5725490196078431, 1], '3C': [0.6392156862745098, 1.0, 0, 1], '3C#': [1.0, 0.7450980392156863, 0, 1], '3D': [0.9803921568627451, 0, 0, 1], '3D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '3E': [0, 0.27450980392156865, 1.0, 1], '3F': [0, 1.0, 0.5725490196078431, 1], '3F#': [0.6392156862745098, 1.0, 0, 1], '3G': [1.0, 0.7450980392156863, 0, 1], '3G#': [0.9803921568627451, 0, 0, 1], '3A': [0.5137254901960784, 0, 0.7098039215686275, 1], '3A#': [0, 0.27450980392156865, 1.0, 1], '3B': [0, 1.0, 0.5725490196078431, 1], '4C': [0.6392156862745098, 1.0, 0, 1], '4C#': [1.0, 0.7450980392156863, 0, 1], '4D': [0.9803921568627451, 0, 0, 1], '4D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '4E': [0, 0.27450980392156865, 1.0, 1], '4F': [0, 1.0, 0.5725490196078431, 1], '4F#': [0.6392156862745098, 1.0, 0, 1], '4G': [1.0, 0.7450980392156863, 0, 1], '4G#': [0.9803921568627451, 0, 0, 1], '4A': [0.5137254901960784, 0, 0.7098039215686275, 1], '4A#': [0, 0.27450980392156865, 1.0, 1], '4B': [0, 1.0, 0.5725490196078431, 1], '5C': [0.6392156862745098, 1.0, 0, 1], '5C#': [1.0, 0.7450980392156863, 0, 1], '5D': [0.9803921568627451, 0, 0, 1], '5D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '5E': [0, 0.27450980392156865, 1.0, 1], '5F': [0, 1.0, 0.5725490196078431, 1], '5F#': [0.6392156862745098, 1.0, 0, 1], '5G': [1.0, 0.7450980392156863, 0, 1], '5G#': [0.9803921568627451, 0, 0, 1], '5A': [0.5137254901960784, 0, 0.7098039215686275, 1], '5A#': [0, 0.27450980392156865, 1.0, 1], '5B': [0, 1.0, 0.5725490196078431, 1], '6C': [0.6392156862745098, 1.0, 0, 1], '6C#': [1.0, 0.7450980392156863, 0, 1], '6D': [0.9803921568627451, 0, 0, 1], '6D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '6E': [0, 0.27450980392156865, 1.0, 1], '6F': [0, 1.0, 0.5725490196078431, 1], '6F#': [0.6392156862745098, 1.0, 0, 1], '6G': [1.0, 0.7450980392156863, 0, 1], '6G#': [0.9803921568627451, 0, 0, 1], '6A': [0.5137254901960784, 0, 0.7098039215686275, 1], '6A#': [0, 0.27450980392156865, 1.0, 1], '6B': [0, 1.0, 0.5725490196078431, 1], '7C': [0.6392156862745098, 1.0, 0, 1], '7C#': [1.0, 0.7450980392156863, 0, 1], '7D': [0.9803921568627451, 0, 0, 1], '7D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '7E': [0, 0.27450980392156865, 1.0, 1], '7F': [0, 1.0, 0.5725490196078431, 1], '7F#': [0.6392156862745098, 1.0, 0, 1], '7G': [1.0, 0.7450980392156863, 0, 1], '7G#': [0.9803921568627451, 0, 0, 1], '7A': [0.5137254901960784, 0, 0.7098039215686275, 1], '7A#': [0, 0.27450980392156865, 1.0, 1], '7B': [0, 1.0, 0.5725490196078431, 1], '8C': [0.6392156862745098, 1.0, 0, 1]}

        self.white_key=self.retrieve_data("white_key") if self.retrieve_data("white_key") is not None else False
        
        self.black_key=self.retrieve_data("black_key") if self.retrieve_data("black_key") is not None else True
        if self.white_key:
            self.black_key=False
        self.a=Builder.load_file("main.kv")
        self.update_piano(int(self.numberof_row),'b')
        

    def build(self):    
        Window.bind(on_resize=self.on_window_resize)
        
        
        self.intervals = {}
        self.channels = {}
        
        self.num_channels = 89 
        self.sounds={}
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)
        
        self.load_sample()
        
        return self.a
    def export_jsonstore(self):
        store = JsonStore('app.json')
        
        source_path = store.filename
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
            
            from android.storage import primary_external_storage_path
            download_dir = os.path.join(primary_external_storage_path(), 'Download')
        elif platform in ['macosx', 'win']:
            download_dir = os.path.expanduser('~/Downloads')
        else:
            return
        
        
        destination_path = os.path.join(download_dir, 'app.json')
        
        try:
            shutil.copy2(source_path, destination_path)
            Snackbar(
                text=f"File exported successfully to {destination_path}",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()
        except Exception as e:
            Snackbar(
                text=f"Error exporting file: {e}",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()

            
    def show_file_chooser(self, instance):
        self.file_chooser = FileChooserListView()
        self.file_chooser.filters = ['*.json']
        
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE])
            from android.storage import primary_external_storage_path
            self.file_chooser.path = primary_external_storage_path()
        else:
            self.file_chooser.path = os.path.expanduser('~')

        self.file_chooser.bind(on_submit=self.import_selected_file)
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.file_chooser)
        close_button = Button(text='Close', size_hint_y=None, height=50)
        close_button.bind(on_press=self.close_file_chooser)
        layout.add_widget(close_button)
        
        self.file_chooser_popup = Popup(title="Choose JSON file", content=layout, size_hint=(0.9, 0.9))
        self.file_chooser_popup.open()

    def close_file_chooser(self, instance):
        self.file_chooser_popup.dismiss()

    def import_selected_file(self, instance, selection, touch):
        if selection:
            source_path = selection[0]
            self.import_jsonstore(source_path)
        self.file_chooser_popup.dismiss()

    def import_jsonstore(self, source_path):
        store = JsonStore('app.json')
        
        destination_path = store.filename
        
        try:
            # Validate JSON file
            with open(source_path, 'r') as file:
                json.load(file)  # This will raise an exception if the file is not valid JSON
            
            shutil.copy2(source_path, destination_path)
            
            # Reload the JsonStore
            self.store = JsonStore(destination_path)
            Snackbar(
                text=f"File imported successfully from {source_path}",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()
            self.update_setting()
        except json.JSONDecodeError:
            Snackbar(
                text=f"Error: The selected file is not a valid JSON file.",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()

        except Exception as e:
            Snackbar(
                text=f"Error importing file: {e}",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(
                    Window.width - (dp(10) * 2)
                ) / Window.width
            ).open()
    def update_setting(self):
        self.visible_keys = self.retrieve_data("visible_keys") if self.retrieve_data("visible_keys") is not None else "20"
        self.numberof_row=self.retrieve_data("numberof_row") if self.retrieve_data("numberof_row") is not None else "1"
        self.keyboard_lock=self.retrieve_data("keyboard_lock") if self.retrieve_data("keyboard_lock") is not None else False
        
        self.custom_color_active=self.retrieve_data("custom_color_active") if self.retrieve_data("custom_color_active") is not None else False
        self.color_pattern_active=self.retrieve_data("color_pattern_active") if self.retrieve_data("color_pattern_active") is not None else True
        self.sustain_tune = self.retrieve_data("sustain_tune") if self.retrieve_data("sustain_tune") is not None else False
        self.selected_instrument=self.retrieve_data("selected_instrument") if self.retrieve_data("selected_instrument") is not None else "1"
        self.equalizer = self.retrieve_data("equalizer") if self.retrieve_data("equalizer") is not None else False
        
        self.save_scroll= self.retrieve_data("save_scroll") if self.retrieve_data("save_scroll") is not None else  {}
        self.main_gain = np.array(self.retrieve_data("main_gain")) if self.retrieve_data("main_gain") is not None else np.ones(10)
        self.keys_label=self.retrieve_data("keys_label")
        self.custom_label=self.retrieve_data("custom_label") if self.retrieve_data("custom_label") is not None else {"C":"C","C#":"C#","D":"D","D#":"D#","E":"E","F":"F","F#":"F#","G":"G","G#":"G#","A":"A","A#":"A#","B":"B"}
        self.notes_color =self.retrieve_data("notes_color") if self.retrieve_data("notes_color") is not None else {
            "0A":(98/255.0,0,0,1),
            "0A#":(139/255.0,0,0,1),
            "0B":(177/255,0,0,1),
            "1C":(213/255.0,0,0,1),
            "1C#":(248/255.0,0,0,1),
            "1D":(255/255.0,145/255.0,0,1),
            "1D#":(240/255.0,255.0/255.0,0,1),
            "1E":(115/255,255/255,0,1),
            "1F":(0,255/255,181/255,1),
            "1F#":(0,113/255,255/255,1),
            "1G":(109/255,0,251/255,1),
            "1G#":(97/255,0,97/255,1)
        }
        self.custom_color = self.retrieve_data("custom_color") if self.retrieve_data("custom_color") is not None else {'0A': [0.5137254901960784, 0, 0.7098039215686275, 1], '0A#': [0, 0.27450980392156865, 1.0, 1], '0B': [0, 1.0, 0.5725490196078431, 1], '1C': [0.6392156862745098, 1.0, 0, 1], '1C#': [1.0, 0.7450980392156863, 0, 1], '1D': [0.9803921568627451, 0, 0, 1], '1D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '1E': [0, 0.27450980392156865, 1.0, 1], '1F': [0, 1.0, 0.5725490196078431, 1], '1F#': [0.6392156862745098, 1.0, 0, 1], '1G': [1.0, 0.7450980392156863, 0, 1], '1G#': [0.9803921568627451, 0, 0, 1], '1A': [0.5137254901960784, 0, 0.7098039215686275, 1], '1A#': [0, 0.27450980392156865, 1.0, 1], '1B': [0, 1.0, 0.5725490196078431, 1], '2C': [0.6392156862745098, 1.0, 0, 1], '2C#': [1.0, 0.7450980392156863, 0, 1], '2D': [0.9803921568627451, 0, 0, 1], '2D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '2E': [0, 0.27450980392156865, 1.0, 1], '2F': [0, 1.0, 0.5725490196078431, 1], '2F#': [0.6392156862745098, 1.0, 0, 1], '2G': [1.0, 0.7450980392156863, 0, 1], '2G#': [0.9803921568627451, 0, 0, 1], '2A': [0.5137254901960784, 0, 0.7098039215686275, 1], '2A#': [0, 0.27450980392156865, 1.0, 1], '2B': [0, 1.0, 0.5725490196078431, 1], '3C': [0.6392156862745098, 1.0, 0, 1], '3C#': [1.0, 0.7450980392156863, 0, 1], '3D': [0.9803921568627451, 0, 0, 1], '3D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '3E': [0, 0.27450980392156865, 1.0, 1], '3F': [0, 1.0, 0.5725490196078431, 1], '3F#': [0.6392156862745098, 1.0, 0, 1], '3G': [1.0, 0.7450980392156863, 0, 1], '3G#': [0.9803921568627451, 0, 0, 1], '3A': [0.5137254901960784, 0, 0.7098039215686275, 1], '3A#': [0, 0.27450980392156865, 1.0, 1], '3B': [0, 1.0, 0.5725490196078431, 1], '4C': [0.6392156862745098, 1.0, 0, 1], '4C#': [1.0, 0.7450980392156863, 0, 1], '4D': [0.9803921568627451, 0, 0, 1], '4D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '4E': [0, 0.27450980392156865, 1.0, 1], '4F': [0, 1.0, 0.5725490196078431, 1], '4F#': [0.6392156862745098, 1.0, 0, 1], '4G': [1.0, 0.7450980392156863, 0, 1], '4G#': [0.9803921568627451, 0, 0, 1], '4A': [0.5137254901960784, 0, 0.7098039215686275, 1], '4A#': [0, 0.27450980392156865, 1.0, 1], '4B': [0, 1.0, 0.5725490196078431, 1], '5C': [0.6392156862745098, 1.0, 0, 1], '5C#': [1.0, 0.7450980392156863, 0, 1], '5D': [0.9803921568627451, 0, 0, 1], '5D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '5E': [0, 0.27450980392156865, 1.0, 1], '5F': [0, 1.0, 0.5725490196078431, 1], '5F#': [0.6392156862745098, 1.0, 0, 1], '5G': [1.0, 0.7450980392156863, 0, 1], '5G#': [0.9803921568627451, 0, 0, 1], '5A': [0.5137254901960784, 0, 0.7098039215686275, 1], '5A#': [0, 0.27450980392156865, 1.0, 1], '5B': [0, 1.0, 0.5725490196078431, 1], '6C': [0.6392156862745098, 1.0, 0, 1], '6C#': [1.0, 0.7450980392156863, 0, 1], '6D': [0.9803921568627451, 0, 0, 1], '6D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '6E': [0, 0.27450980392156865, 1.0, 1], '6F': [0, 1.0, 0.5725490196078431, 1], '6F#': [0.6392156862745098, 1.0, 0, 1], '6G': [1.0, 0.7450980392156863, 0, 1], '6G#': [0.9803921568627451, 0, 0, 1], '6A': [0.5137254901960784, 0, 0.7098039215686275, 1], '6A#': [0, 0.27450980392156865, 1.0, 1], '6B': [0, 1.0, 0.5725490196078431, 1], '7C': [0.6392156862745098, 1.0, 0, 1], '7C#': [1.0, 0.7450980392156863, 0, 1], '7D': [0.9803921568627451, 0, 0, 1], '7D#': [0.5137254901960784, 0, 0.7098039215686275, 1], '7E': [0, 0.27450980392156865, 1.0, 1], '7F': [0, 1.0, 0.5725490196078431, 1], '7F#': [0.6392156862745098, 1.0, 0, 1], '7G': [1.0, 0.7450980392156863, 0, 1], '7G#': [0.9803921568627451, 0, 0, 1], '7A': [0.5137254901960784, 0, 0.7098039215686275, 1], '7A#': [0, 0.27450980392156865, 1.0, 1], '7B': [0, 1.0, 0.5725490196078431, 1], '8C': [0.6392156862745098, 1.0, 0, 1]}

        self.white_key=self.retrieve_data("white_key") if self.retrieve_data("white_key") is not None else False
        
        self.black_key=self.retrieve_data("black_key") if self.retrieve_data("black_key") is not None else False
        self.update_piano(int(self.numberof_row),'b')
        

    def update_storage(self):
        store = JsonStore('app.json')
        store.put('notes_color', notes_color=self.notes_color)
        store.put('custom_color', custom_color=self.custom_color)
        store.put('custom_color_active', custom_color_active=self.custom_color_active)
        store.put('color_pattern_active', color_pattern_active=self.color_pattern_active)
        
        store.put('sustain_tune', sustain_tune=self.sustain_tune)
        
        
        store.put('numberof_row', numberof_row=self.numberof_row)
        store.put('visible_keys', visible_keys=self.visible_keys)
        store.put('keyboard_lock', keyboard_lock=self.keyboard_lock)
        store.put('white_key', white_key=self.white_key)
        store.put('black_key', black_key=self.black_key)
        
        

        store.put('equalizer', equalizer=self.equalizer)
        store.put('main_gain', main_gain=self.main_gain.tolist())
        
        store.put('selected_instrument', selected_instrument=self.selected_instrument)

        
        store.put('keys_label', keys_label=self.keys_label)
        store.put('custom_label', custom_label=self.custom_label)

        store.put('save_scroll', save_scroll=self.save_scroll)
    def retrieve_data(self,val):
        store = JsonStore('app.json')
        try:
            return store.get(val)[val]
        except:
            return None
        
    def load_sample(self):
        self.samples = {}
        pygame.mixer.set_num_channels(1)
        
        for note in self.piano_notes:
            filename = "instruments/"+self.selected_instrument+"/"+f"{note}.wav"
            try:
                wave_obj = pygame.mixer.Sound(filename)
                audio_data = pygame.sndarray.array(wave_obj)
                self.samples[note] = audio_data.flatten()
            except FileNotFoundError:
                pass
        pygame.mixer.set_num_channels(89)
    def open_link(self,link):
        webbrowser.open(link) 
 
    def screen_switch_chosefile(self):
        self.a.transition=SwapTransition()
        self.a.current = 'FileChooserIns'
    def screen_switch_mainscreen(self):
        self.a.transition=SwapTransition()
        self.a.current = 'MainScreen'
    def on_window_resize(self, window, width, height):
        try:
            self.window_width=width
            self.wid = self.window_width / int(self.visible_keys) - 0.05
            self.update_visiblekeys()
        except:
            pass
    def instrument_icon(self):
        self.a.ids.main_screen.ids.instrument_id.source=self.instrument_img
    def custom_update_color(self):
        for i in self.custom_color.keys():
            for j in self.a.ids.main_screen.ids.keys_container.children:
                for v in j.children[1].children[0].ids:
                    if v==i:

                        j.children[1].children[0].ids[i].set_background_color(self.custom_color[i])
                    elif "half" in v and v[0:3]==i:
                        j.children[1].children[0].ids[v].ids[i].set_background_color(self.custom_color[i])
                        
                        for p in j.children[1].children[0].ids[v].ids['double_container'].ids:
                            j.children[1].children[0].ids[v].ids['double_container'].ids[p].set_background_color(self.custom_color[p[:-1]])
                    elif "half" in v and v[0:2]==i and v[2]=="_":
                        j.children[1].children[0].ids[v].ids[i].set_background_color(self.custom_color[i])
                        for p in j.children[1].children[0].ids[v].ids['double_container'].ids:
                            j.children[1].children[0].ids[v].ids['double_container'].ids[p].set_background_color(self.custom_color[p[:-1]])
             
                        
        self.update_storage()
       
        
    def update_color(self):
        if self.custom_color_active:
            self.custom_update_color()
            return
        
        full_notes_color = {}
        color_keys = list(self.notes_color.keys())
        num_colors = len(color_keys)

        for i, note in enumerate(self.piano_notes):
            color_index = i % num_colors  # Cycle through the colors
            color_key = color_keys[color_index]
            full_notes_color[note] = self.notes_color[color_key]

        
        for i in full_notes_color.keys():
            for j in self.a.ids.main_screen.ids.keys_container.children:
                for v in j.children[1].children[0].ids:
                    if v==i:
                        
                        j.children[1].children[0].ids[i].set_background_color(full_notes_color[i])
                    elif "half" in v and v[0:3]==i:
                        j.children[1].children[0].ids[v].ids[i].set_background_color(full_notes_color[i])
                        for p in j.children[1].children[0].ids[v].ids['double_container'].ids:
                            j.children[1].children[0].ids[v].ids['double_container'].ids[p].set_background_color(full_notes_color[p[:-1]])
                    elif "half" in v and v[0:2]==i and v[2]=="_":
                        j.children[1].children[0].ids[v].ids[i].set_background_color(full_notes_color[i])
                        for p in j.children[1].children[0].ids[v].ids['double_container'].ids:
                            j.children[1].children[0].ids[v].ids['double_container'].ids[p].set_background_color(full_notes_color[p[:-1]])
        
        self.update_storage()
       
          
    def update_visiblekeys(self):
        x=len(self.a.ids.main_screen.ids.keys_container.children)-1
        for i in self.a.ids.main_screen.ids.keys_container.children:
            self.save_scroll[str(x)]=i.children[-1].value
            x-=1
        self.update_piano(int(self.numberof_row),'b')
            
    def lock_mode(self):
        for child in self.a.ids.main_screen.ids.keys_container.children:
            for vchild in child.children:
                if isinstance(vchild, MySlider):
                    if self.keyboard_lock:
                        vchild.opacity = 0
                        vchild.height=0
                    else:
                        vchild.opacity = 1
                        vchild.height= dp(30)
        self.update_storage()
       
    def scroll_piano(self,value,bx,lbl):
        bx.scroll_x= lbl
        x=len(self.a.ids.main_screen.ids.keys_container.children)-1
        for i in self.a.ids.main_screen.ids.keys_container.children:
            self.save_scroll[str(x)]=i.children[-1].value
            x-=1
        self.update_storage()
        
        
        pass
    def stop_all_sounds(self):
        self.release_event=None
        for i in range(self.num_channels):
            channel = pygame.mixer.Channel(i)
            if channel.get_busy():
                if i in self.intervals and self.intervals[i]:
                    pass
                    #self.intervals[i].cancel()
                else:
                    channel.set_volume(1.0-0.008)
                    self.intervals[i] = Clock.schedule_interval(partial(self.fade_out, channel=channel,num=i), 1 / 120)
                
                
                
    def fade_out(self,dt,channel,num):
        if channel.get_busy():
            current_volume = channel.get_volume()
            if current_volume==1.0:
                if self.intervals[num]:
                    self.intervals[num].cancel()
                    self.intervals[num]=None
                
            elif current_volume > 0.01:
                channel.set_volume(current_volume - 0.008)
            
            else:
                channel.set_volume(1.0)
                channel.stop()
                if self.intervals[num]:
                    self.intervals[num].cancel()
                    self.intervals[num]=None
                
                #self.release_event = None
                
                
    def play_sound(self,file_nm):
        # Get the list of all .wav and .mp3 files in the 'instrument' folder
        file_name = ""
        if self.piano_notes[file_nm-1]+".wav" in os.listdir('instruments/'+self.selected_instrument):
            file_name=f"{self.piano_notes[file_nm-1]}.wav"
        else:
            file_name=f"{self.piano_notes[file_nm-1]}.mp3"
        path = "instruments/"+self.selected_instrument+"/"+file_name
        
        file_path = f"{path}"

        channel = pygame.mixer.Channel(file_nm)  
        if channel:
            if self.equalizer:

                equalizerclass = Equalizer()
                audio_data = self.samples[self.piano_notes[file_nm-1]]
                eq_audio = equalizerclass.apply_eq(audio_data, 44100)  # Assuming 44.1kHz sample rate
                sound = pygame.sndarray.make_sound(eq_audio)
                
                channel.set_volume(1.0)
                channel.stop()
                channel.play(sound)
            else:
                if file_path not in self.sounds:
                    self.sounds[file_path] = pygame.mixer.Sound(file_path)
        
                channel.set_volume(1.0)
                channel.stop()
                channel.play(self.sounds[file_path])
        
        
        


    def link_layouts(self,layout1, layout2):
        layout1.partner = layout2
        layout2.partner = layout1
    def touch_down(self,touch,action):
        for i in self.a.ids.main_screen.ids.keys_container.children:
            # Checking which key's row is clicked
            if (touch.pos[0]>=i.pos[0] and touch.pos[0]<=i.pos[0]+i.size[0]) and (touch.pos[1]>=i.pos[1] and touch.pos[1]<=i.pos[1]+i.size[1]):
                if (touch.pos[0]>=i.children[-1].pos[0] and touch.pos[0]<=i.children[-1].pos[0]+i.children[-1].size[0]) and (touch.pos[1]>=i.children[-1].pos[1] and touch.pos[1]<=i.children[-1].pos[1]+i.children[-1].size[1]):
                    return False
                    
                touch.pos = list(touch.pos)
                touch.pos[0]=touch.pos[0]+i.children[1].scroll_x*(i.children[1].children[0].width-i.children[1].width)
            
                key_ids = list(i.children[1].children[0].ids.keys())
                key_ids.reverse()
                
                #Checking which key is Clicked
                num_key = 0
                for v in i.children[1].children[0].children:
                        
                    if (touch.pos[0]>=v.pos[0]+i.pos[0] and touch.pos[0]<=v.pos[0]+v.size[0]+i.pos[0]) and (touch.pos[1]>=v.pos[1]+i.pos[1] and touch.pos[1]<=v.pos[1]+v.size[1]+i.pos[1]):
                        #White keys color
                        if len(v.children)<2 and isinstance(v,BoxLayout):
                            self.update_color()
                            v.set_background_color([108/255,122/255,137/255,1])
                            sub_id = key_ids[num_key]+'a'
                            if action=="down":
                                self.play_sound(88-num_key)
                            elif 88-num_key!=self.pre_music:
                                if self.sustain_tune==False:
                                    self.stop_all_sounds()
                                self.play_sound(88-num_key)
                            self.pre_music = 88-num_key
                            for n in key_ids:
                                if "half" in n:
                                    if sub_id in list(i.children[1].children[0].ids[n].children[0].ids.keys()):
                                        i.children[1].children[0].ids[n].children[0].ids[sub_id].set_background_color([108/255,122/255,137/255,1])
                        elif len(v.children)>=2 and isinstance(v.children[0],Label) and isinstance(v.children[-1],Label):
                            self.update_color()

                            if action=="down":
                                self.play_sound(88-num_key)
                            elif 88-num_key!=self.pre_music:
                                if self.sustain_tune==False:
                                    self.stop_all_sounds()
                                self.play_sound(88-num_key)
                            self.pre_music = 88-num_key
                            
                            v.set_background_color([108/255,122/255,137/255,1])
                                
                                
                        elif isinstance(v,BoxLayout):
                            if (touch.pos[0]>=v.children[-1].pos[0]+i.pos[0] and touch.pos[0]<=v.children[-1].pos[0]+v.children[-1].size[0]+i.pos[0]) and (touch.pos[1]>=v.children[-1].pos[1]+i.pos[1] and touch.pos[1]<=v.children[-1].pos[1]+v.children[-1].size[1]+i.pos[1]):
                                self.update_color()
                                if action=="down":
                                    self.play_sound(88-num_key)
                                elif 88-num_key!=self.pre_music:
                                    if self.sustain_tune==False:
                                        self.stop_all_sounds()
                                    self.play_sound(88-num_key)
                                self.pre_music = 88-num_key
                                v.children[-1].set_background_color([108/255,122/255,137/255,1])
                            else:
                                pera_key = list(v.children[0].ids.keys())
                                for vir in pera_key:
                                    child_pass = v.children[0].ids[vir]
                                    if (touch.pos[0]>=child_pass.pos[0]+i.pos[0] and touch.pos[0]<=child_pass.pos[0]+child_pass.size[0]+i.pos[0]) and (touch.pos[1]>=child_pass.pos[1]+i.pos[1] and touch.pos[1]<=child_pass.pos[1]+child_pass.size[1]+i.pos[1]):
                                        self.update_color()
                                        new_in=self.piano_notes.index(vir[:-1])+1
                                        if action=="down":
                                            self.play_sound(new_in)
                                        elif new_in!=self.pre_music:
                                            if self.sustain_tune==False:
                                                self.stop_all_sounds()
                                            self.play_sound(new_in)
                                        self.pre_music = new_in
                                        
                                        child_pass.set_background_color([108/255,122/255,137/255,1])
                                        vi = vir[:-1]
                                        i.children[1].children[0].ids[vi].set_background_color([108/255,122/255,137/255,1])
                                        for tin in i.children[1].children[0].children:
                                            if len(tin.children)>=2:
                                                if vir in list(tin.children[0].ids.keys()):
                                                    tin.children[0].ids[vir].set_background_color([108/255,122/255,137/255,1])


                    if isinstance(v,BoxLayout):
                        num_key+=1   
              
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def touch_up(self,touch):    
        self.update_color()
        if self.sustain_tune==False:
            self.stop_all_sounds()
        else:
            pass
        pass
    def update_piano(self,num,outcome):
        if outcome=='w' or outcome=='b':
            self.a.ids.main_screen.ids.keys_container.clear_widgets()
        
        if self.white_key:
            self.whitekeys_only(None)
            return
        if self.black_key:
            self.evenback_keys(None)
            return
        
        
        #self.a.ids.main_screen.ids.keys_container.clear_widgets()
        total_ele =len(self.a.ids.main_screen.ids.keys_container.children)
        if total_ele>num:
            for _ in range(total_ele-num):
                if self.a.ids.main_screen.ids.keys_container.children:
                    self.a.ids.main_screen.ids.keys_container.remove_widget(self.a.ids.main_screen.ids.keys_container.children[0])
        
        for t in range(total_ele,num):
            bx = BoxLayout(orientation='vertical')
            scr = 0.0
            if str(t) in self.save_scroll.keys():
                scr=self.save_scroll[str(t)]
            slider = MySlider(value=scr)
            self.a.ids.main_screen.ids.keys_container.ids["peta_container_"+str(t)]=bx
            scroll_v = ScrollView(do_scroll_x=False,do_scroll_y=False,scroll_x=scr)
            slider.bind(value=lambda instance, value, lbu=scroll_v: self.scroll_piano(instance,lbu, float(value)))
            bx2 = BoxLayout(orientation="horizontal",size_hint_x=None,width= self.wid*88.5) #88.5
            bx.ids['hori_con']=bx2
            
            an =0
            exnel_label=0
            for i in self.first_note:
                note = self.piano_notes[an]
                if i=='x':
                    bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,always_release=True,width= self.wid,background_color=(1, 1, 1, 1),tone=note,layout=t,padding=[0,0,0,15]
                                          )
                    
                    if self.keys_label!=None:
                        if self.f_label[an]==1:
                            ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)-(self.wid*1.5/6),self.wid*1.5/6))
                            
                            with ft_main.canvas:
                                Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                            #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                            #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                            n_lbl=''
                            if self.keys_label=="Notes":
                                n_lbl=note
                            elif isinstance(self.keys_label, dict):
                                n_lbl = self.keys_label[note[1:]]
                            else:
                                n_lbl=self.keys_label[exnel_label]
                            exnel_label+=1
                            if exnel_label==7:
                                exnel_label=0

                            ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                            ft.text_size = (ft.width, None)
                            ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                            while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                ft.font_size -= 1
                            
                            ft_main.add_widget(ft)
                            
                            #ft_main.add_widget(ft)
                            bx3.add_widget(ft_main)
                    bx2.ids[note]=bx3
                    bx2.add_widget(bx3)
                    an+=1
                elif i=='y':
                    #black key
                    bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= self.wid,background_color=(0, 0, 0, 1))
                    bx2.ids[note+"_half_container"]=bx3
                    
                    #key full
                    bx4 = ColoredBoxLayout(background_color=(0, 0, 0, 1),tone=note,layout=t)
                    bx3.ids[note]=bx4
                    bx4_1 = BorderedBoxLayout(border_color=(0,0,0,1),border_width=1)
                    bx4.add_widget(bx4_1)
                    #half key
                    bx5 = ColoredBoxLayout(orientation="horizontal",size_hint_y=0.4)
                    bx3.ids["double_container"]=bx5
                    bx6 = ColoredBoxLayout(background_color=(1, 1, 1, 1),tone=self.piano_notes[an-1]+'a',layout=t,
                                           )
                    if self.keys_label!=None:
                        if self.f_label[an]==1:
                            ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)-(self.wid*1.5/2),self.wid*1.5/6))
                            
                            with ft_main.canvas:
                                Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                            #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                          #  ft_main.bind(size=self.update_rect, pos=self.update_rect)
                            n_lbl=''
                            if self.keys_label=="Notes":
                                n_lbl=self.piano_notes[an-1]
                            elif isinstance(self.keys_label, dict):
                                n_lbl = self.keys_label[self.piano_notes[an-1][1:]]
                            else:
                                n_lbl=self.keys_label[exnel_label]
                            exnel_label+=1
                            if exnel_label==7:
                                exnel_label=0

                            ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                            ft.text_size = (ft.width, None)
                            ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                            while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                ft.font_size -= 1
                            
                            ft_main.add_widget(ft)
                            
                            #ft_main.add_widget(ft)
                            bx6.add_widget(ft_main)
                    
                    bx5.ids[self.piano_notes[an-1]+'a']=bx6
                    plbl = ColoredLabel(size_hint_x= None,width=2, background_color=(0, 0, 0, 1),)
                    
                    with plbl.canvas:
                        Color(0, 0, 0, 1)
                        Rectangle(pos=plbl.pos, size=plbl.size)

                    bx7 = ColoredBoxLayout(background_color=(1, 1, 1, 1),tone=self.piano_notes[an+1]+'a',layout=t
                                          )
                    bx5.ids[self.piano_notes[an+1]+'a']=bx7
                    
                    bx3.add_widget(bx4)

                    bx5.add_widget(bx6)
                    bx5.add_widget(plbl)
                    bx5.add_widget(bx7)
                    
                        

                    bx3.add_widget(bx5)
                    


                    bx2.add_widget(bx3)
                    an+=1
                else:
                    p_lb =ColoredLabel(size_hint_x= None,width=2,background_color=(0,0,0,1))

                    bx2.add_widget(p_lb)
                        
                    pass
                
            #an=3
            for j in range(0,7):
                asd_space =1+j*2
                sec_space = 1+j*2
                sec_add=True
                for i in self.mid_note:
                    note = self.piano_notes[an]
                
                    if i=='x':
                        bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= self.wid,background_color=(1, 1, 1, 1),tone=note,layout=t
                                          
                                              )
                        if self.keys_label!=None:
                            if self.m_label[an]==1:
                                ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)-(self.wid*1.5/6)+sec_space*2,self.wid*1.5/6))
                                if sec_add:
                                    sec_space+=1
                                    sec_add=False
                                with ft_main.canvas:
                                    Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                    self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                                #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                                #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                                n_lbl=''
                                if self.keys_label=="Notes":
                                    n_lbl=note
                                elif isinstance(self.keys_label, dict):
                                    n_lbl = self.keys_label[note[1:]]
                            
                                else:
                                    n_lbl=self.keys_label[exnel_label]
                                exnel_label+=1
                                if exnel_label==7:
                                    exnel_label=0

                                ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                                ft.text_size = (ft.width, None)
                                ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                                while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                    ft.font_size -= 1
                                
                                ft_main.add_widget(ft)
                                
                                #ft_main.add_widget(ft)
                                bx3.add_widget(ft_main)
                            if self.m_label[an]==2:
                                ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)+sec_space*2,self.wid*1.5/6))
                                if sec_add:
                                    sec_space+=1
                                    sec_add=False
                                with ft_main.canvas:
                                    Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                    self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                                #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)
                                n_lbl=''
                                if self.keys_label=="Notes":
                                    n_lbl=note
                                elif isinstance(self.keys_label, dict):
                                    n_lbl = self.keys_label[note[1:]]
                            
                                else:
                                    n_lbl=self.keys_label[exnel_label]
                                exnel_label+=1
                                if exnel_label==7:
                                    exnel_label=0

                                #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                                ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                                ft.text_size = (ft.width, None)
                                ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                                while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                    ft.font_size -= 1
                            
                                ft_main.add_widget(ft)
                                
                                #ft_main.add_widget(ft)
                                bx3.add_widget(ft_main)
                        bx2.ids[note]=bx3
                    
                        bx2.add_widget(bx3)
                        an+=1
                    elif i=='y':
                        #black key
                        bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= self.wid,background_color=(0, 0, 0, 1))
                        bx2.ids[note+"_half_container"]=bx3
                    
                        #key full
                        bx4 = ColoredBoxLayout(background_color=(0, 0, 0, 1),tone=note,layout=t,
                                          
                                               )
                        bx3.ids[note]=bx4
                    
                        bx4_1 = BorderedBoxLayout(border_color=(0,0,0,1),border_width=1)
                        bx4.add_widget(bx4_1)
                    
                        #half key
                        bx5 = ColoredBoxLayout(orientation="horizontal",size_hint_y=0.4)
                        bx3.ids["double_container"]=bx5
                    
                        bx6 = ColoredBoxLayout(background_color=(1, 1, 1, 1),tone=self.piano_notes[an-1]+'a',layout=t,
                                           )
                        
                        if self.keys_label!=None:
                            if self.m_label[an]==1:
                                ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)-(self.wid*1.5/2)+asd_space*2,self.wid*1.5/6))
                                asd_space+=1
                                with ft_main.canvas:
                                    Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                    self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                                #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                                #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                                n_lbl=''
                                if self.keys_label=="Notes":
                                    n_lbl=self.piano_notes[an-1]
                                elif isinstance(self.keys_label, dict):
                                    n_lbl = self.keys_label[self.piano_notes[an-1][1:]]
                            
                                else:
                                    n_lbl=self.keys_label[exnel_label]
                                exnel_label+=1
                                if exnel_label==7:
                                    exnel_label=0

                                ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                                ft.text_size = (ft.width, None)
                                ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                                while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                    ft.font_size -= 1
                                
                                ft_main.add_widget(ft)
                                
                                #ft_main.add_widget(ft)
                                bx6.add_widget(ft_main)
                        
                        bx5.ids[self.piano_notes[an-1]+'a']=bx6
                    
                        plbl = ColoredLabel(size_hint_x= None,width=2, background_color=(0, 0, 0, 1))
                        with plbl.canvas:
                            Color(0, 0, 0, 1)
                            Rectangle(pos=plbl.pos, size=plbl.size)

                        bx7 = ColoredBoxLayout(background_color=(1, 1, 1, 1),tone=self.piano_notes[an+1]+'a',layout=t,
                                               )
                        bx5.ids[self.piano_notes[an+1]+'a']=bx7
                    
                        bx3.add_widget(bx4)

                        bx5.add_widget(bx6)
                        bx5.add_widget(plbl)
                        bx5.add_widget(bx7)
                        
                            

                        bx3.add_widget(bx5)
                        


                        bx2.add_widget(bx3)
                        an+=1
                    else:
                        p_lb =ColoredLabel(size_hint_x= None,width=2,background_color=(0,0,0,1))

                        bx2.add_widget(p_lb)
                        pass
                    
                        
            bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= self.wid,background_color=(1, 1, 1, 1),tone=self.piano_notes[-1],layout=t,
                                          
                                  )
            if self.keys_label!=None:
                ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)+7*4+2+self.wid*1.5/6,self.wid*1.5/6))
                
                with ft_main.canvas:
                    Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                    self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                n_lbl=''
                if self.keys_label=="Notes":
                    n_lbl=self.piano_notes[-1]
                elif isinstance(self.keys_label, dict):
                    n_lbl = self.keys_label[self.piano_notes[-1][1:]]
                            
                else:
                    n_lbl=self.keys_label[exnel_label]
                exnel_label+=1
                if exnel_label==7:
                    exnel_label=0

                ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                ft.text_size = (ft.width, None)
                ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                    ft.font_size -= 1
                            
                ft_main.add_widget(ft)
                
                #ft_main.add_widget(ft)
                bx3.add_widget(ft_main)
        
            bx2.ids[self.piano_notes[-1]]=bx3
                    
            bx2.add_widget(bx3)
            
                    


            if self.keyboard_lock:
                slider.opacity = 0
                slider.height=0
            else:
                slider.opacity = 1
                slider.height= dp(30)


            bx.add_widget(slider)
            scroll_v.add_widget(bx2)
            bx.add_widget(scroll_v)
            plbl2 = ColoredLabel(size_hint_y= None,height=4, background_color=(0, 0, 0, 1))
            bx.add_widget(plbl2)       
            self.a.ids.main_screen.ids.keys_container.add_widget(bx)
       # self.save_scroll={}
        self.update_color()
        self.update_storage()
       
    def whitekeys_only(self,outcom):
        if outcom=='w':

            self.a.ids.main_screen.ids.keys_container.clear_widgets()
        num= int(self.numberof_row)
        total_ele =len(self.a.ids.main_screen.ids.keys_container.children)
        if total_ele>num:
            for _ in range(total_ele-num):
                if self.a.ids.main_screen.ids.keys_container.children:
                    self.a.ids.main_screen.ids.keys_container.remove_widget(self.a.ids.main_screen.ids.keys_container.children[0])

        for i in range(total_ele,int(self.numberof_row)):
            bx = BoxLayout(orientation='vertical')
            scr = 0.0
            if str(i) in self.save_scroll.keys():
                scr=self.save_scroll[str(i)]
            
            slider = MySlider(value=scr)

            ######################white keyboard
            scroll_v = ScrollView(do_scroll_x=False,do_scroll_y=False,scroll_x=scr)
            bx2 = BoxLayout(orientation="horizontal",size_hint_x=None,width= (self.wid)*90.8)
            x_cont=0
            exnel_label=0
            for r in self.piano_notes:
                bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= self.wid,background_color=(0.2, 0.6, 0.8, 1),padding=5)
                bx2.ids[r]=bx3
                nt =Label()
                bx3.add_widget(nt)
                
                if self.keys_label!=None:
                    n_lbl=''
                    if self.keys_label=="Notes":
                        n_lbl=r
                    elif isinstance(self.keys_label, dict):
                        n_lbl = self.keys_label[r[1:]]
                            
                    else:
                        n_lbl=self.keys_label[exnel_label]
                    exnel_label+=1
                    if exnel_label==7:
                        exnel_label=0
                    nt2 = Label(text=n_lbl,size_hint_y=None,height=30,halign='center',valign="middle",color=(0,0,0,1))
                    nt2.text_size = (nt2.width, None)
                    if len(n_lbl)==1:
                        nt2.font_size = bx3.width / (len(n_lbl)+1) # Start with an arbitrary value
                    else:
                        nt2.font_size = bx3.width / (len(n_lbl))
                    while nt2.texture_size[1] > nt2.height or nt2.texture_size[0] > nt2.width:
                        nt2.font_size -= 1
                    
                    with nt2.canvas.before:
                        Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                        self.rect = Rectangle(size=(self.wid-self.wid*1.5/5,self.wid-self.wid*1.5/5), pos=(self.wid*x_cont+x_cont*2+self.wid*1.5/10,self.wid*1.5/10+10))
                    #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)
                    bx3.add_widget(nt2)
                else:
                    nt2 = Label(text='',size_hint_y=None,height=20,color=(0,0,0,1),font_size=self.wid/3)
                    bx3.add_widget(nt2)

                
                nt3 = Label(size_hint_y=None,height=15)
                bx3.add_widget(nt3)

                bx2.add_widget(bx3)
                bx2.add_widget(PaddingLabel())
                x_cont+=1
            scroll_v.add_widget(bx2)
            #####################################################
            
            slider.bind(value=lambda instance, value, lbu=scroll_v: self.scroll_piano(instance,lbu, float(value)))
            if self.keyboard_lock:
                slider.opacity = 0
                slider.height=0
            else:
                slider.opacity = 1
                slider.height= dp(30)
            bx.add_widget(slider)
            bx.add_widget(scroll_v)
            plbl2 = ColoredLabel(size_hint_y= None,height=4, background_color=(0, 0, 0, 1))
            bx.add_widget(plbl2)       
            
            self.a.ids.main_screen.ids.keys_container.add_widget(bx)
        #self.update_visiblekeys()
       # self.save_scroll={}
        self.update_color()
        self.update_storage()
       
        pass
    def evenback_keys(self,outcome):
        if outcome=='b':
            self.a.ids.main_screen.ids.keys_container.clear_widgets()
        num= int(self.numberof_row)
        total_ele =len(self.a.ids.main_screen.ids.keys_container.children)
        if total_ele>num:
            for _ in range(total_ele-num):
                if self.a.ids.main_screen.ids.keys_container.children:
                    self.a.ids.main_screen.ids.keys_container.remove_widget(self.a.ids.main_screen.ids.keys_container.children[0])
        for i in range(total_ele,num):
            bx = BoxLayout(orientation='vertical')
            scr = 0.0
            if str(i) in self.save_scroll.keys():
                scr=self.save_scroll[str(i)]
            
            slider = MySlider(value=scr)
            self.a.ids.main_screen.ids.keys_container.ids["peta_container_"+str(i)]=bx
            
            ######################white keyboard
            scroll_v = ScrollView(do_scroll_x=False,do_scroll_y=False,scroll_x=scr)
            bx2 = BoxLayout(orientation="horizontal",size_hint_x=None,width= self.wid*88+self.wid/2)
            bx.ids['hori_con']=bx2
            an =0
            exnel_label=0
            for p in range(0,89):
                note = self.piano_notes[an]
                if(p!=0 and p%2==0 and p!=88):
                    #black key
                    bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= self.wid,background_color=(0, 0, 0, 1))
                    bx2.ids[note+"_half_container"]=bx3
                    
                    #key full
                    bx4 = ColoredBoxLayout(background_color=(0, 0, 0, 1),bk='black')
                    bx3.ids[note]=bx4
                    bx4_1 = BorderedBoxLayout(border_color=(0,0,0,1),border_width=1)
                    bx4.add_widget(bx4_1)
                    
                    #half key
                    bx5 = ColoredBoxLayout(orientation="horizontal",size_hint_y=0.4)
                    bx3.ids["double_container"]=bx5
                    
                    bx6 = ColoredBoxLayout(background_color=(1, 1, 1, 1),bk='h1')
                    if self.keys_label!=None:
                        if p==2 :
                            n_lbl=''
                            if self.keys_label=="Notes":
                                n_lbl=self.piano_notes[an-1]
                            elif isinstance(self.keys_label, dict):
                                n_lbl = self.keys_label[self.piano_notes[an-1][1:]]
                            
                            else:

                                n_lbl=self.keys_label[exnel_label]
                            exnel_label+=1
                            if exnel_label==7:
                                exnel_label=0

                            ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)+self.wid/2-(self.wid*1.5/2),self.wid*1.5/6))
                            
                            with ft_main.canvas:
                                Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                            #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                            #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                            ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                            ft.text_size = (ft.width, None)
                            ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                            while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                ft.font_size -= 1
                            
                            ft_main.add_widget(ft)
                            
                            #ft_main.add_widget(ft)
                            if n_lbl!='':
                                bx6.add_widget(ft_main)
                        

                    
                    
                    
                    bx5.ids[self.piano_notes[an-1]+'a']=bx6
                    
                    plbl = ColoredLabel(size_hint_x= None,width=2, background_color=(0, 0, 0, 1))
                    with plbl.canvas:
                        Color(0, 0, 0, 1)
                        Rectangle(pos=plbl.pos, size=plbl.size)

                    bx7 = ColoredBoxLayout(background_color=(1, 1, 1, 1),bk="h2")
                    if an+1 < len(self.piano_notes):
                        bx5.ids[self.piano_notes[an+1]+'a']=bx7
                    else:
                        bx5.ids[self.piano_notes[an]+'a']=bx7
                        
                    
                    bx3.add_widget(bx4)

                    bx5.add_widget(bx6)
                    bx5.add_widget(plbl)
                    bx5.add_widget(bx7)
                    
                    

                    bx3.add_widget(bx5)
                    


                    bx2.add_widget(bx3)
                   # bx2.add_widget(PaddingLabel())
            
                else:
                    #white key
                    print(note)
                    w=self.wid
                    pading= w/2
                    if p==0:
                        w=w+w/2
                        pading=self.wid/4
                    bx3 =ColoredBoxLayout(orientation="vertical",size_hint_x=None,width= w,background_color=(1, 1, 1, 1),tone=note,bk='full')
                    if self.keys_label!=None:
                        if p!=1:
                            ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)+pading,self.wid*1.5/6))
                            with ft_main.canvas:
                                Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                                self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                            #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                            #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                            n_lbl=''
                            if self.keys_label=="Notes":
                                n_lbl=note
                            elif isinstance(self.keys_label, dict):
                                n_lbl = self.keys_label[note[1:]]
                    
                            else:
                                n_lbl=self.keys_label[exnel_label]
                            exnel_label+=1
                            if exnel_label==7:
                                exnel_label=0

                            ft = Label(text=n_lbl,pos=ft_main.pos,halign='center',color=[0,0,0,1])
                            ft.text_size = (ft.width, None)
                            ft.font_size = ft.height / (len(n_lbl)+2) # Start with an arbitrary value
                            while ft.texture_size[1] > ft.height or ft.texture_size[0] > ft.width:
                                ft.font_size -= 1
                            
                            ft_main.add_widget(ft)
                            
                            #ft_main.add_widget(ft)
                            if n_lbl!='':
                                bx3.add_widget(ft_main)
                        
                           # bx3.add_widget(ft_main)
                        # if p==87:
                        #     ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)-self.wid*1.5/6,self.wid*1.5/6))
                        #     with ft_main.canvas:
                        #         Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                        #         self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                        #     #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                        #     #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                        #     n_lbl=''
                        #     if self.keys_label=="Notes":
                        #         n_lbl=note
                        #     else:
                        #         n_lbl=self.keys_label[exnel_label]
                        #     exnel_label+=1
                        #     if exnel_label==7:
                        #         exnel_label=0

                        #     ft = MDLabel(text=n_lbl,pos=ft_main.pos,halign='center',font_style="Caption")
                        #     ft_main.add_widget(ft)
                            
                        #     #ft_main.add_widget(ft)
                        #     bx3.add_widget(ft_main)
                        # if p==88:
                        #     ft_main = FloatLayout(size_hint= (None, None),size=(self.wid, self.wid),pos= (self.wid*(an)+self.wid*1.5/6,self.wid*1.5/6))
                        #     with ft_main.canvas:
                        #         Color(0, 1, 0, 1)  # green; colors range from 0-1 not 0-255
                        #         self.rect = Rectangle(size=ft_main.size, pos=ft_main.pos)
                        #     #     self.draw_text(ft_main, note+"X", (50,50), font_size=20)

                        #     #ft_main.bind(size=self.update_rect, pos=self.update_rect)
                        #     n_lbl=''
                        #     if self.keys_label=="Notes":
                        #         n_lbl=note
                        #     else:
                        #         n_lbl=self.keys_label[exnel_label]
                        #     exnel_label+=1
                        #     if exnel_label==7:
                        #         exnel_label=0

                        #     ft = MDLabel(text=n_lbl,pos=ft_main.pos,halign='center',font_style="Caption")
                        #     ft_main.add_widget(ft)
                            
                        #     #ft_main.add_widget(ft)
                        #     bx3.add_widget(ft_main)
                        

                    bx2.ids[note]=bx3
                    bx2.add_widget(bx3)
                an+=1
                
                if an==len(self.piano_notes):
                    break

            
            scroll_v.add_widget(bx2)
            #####################################################
            
            slider.bind(value=lambda instance, value, lbu=scroll_v: self.scroll_piano(instance,lbu, float(value)))
            if self.keyboard_lock:
                slider.opacity = 0
                slider.height=0
            else:
                slider.opacity = 1
                slider.height= dp(30)
            bx.add_widget(slider)
            bx.add_widget(scroll_v)
            plbl2 = ColoredLabel(size_hint_y= None,height=4, background_color=(0, 0, 0, 1))
            bx.add_widget(plbl2)       
            
            self.a.ids.main_screen.ids.keys_container.add_widget(bx)
        #self.save_scroll={}
        self.update_color()
        self.update_storage()
       
        

    
   
if __name__ == '__main__':
    PianoApp().run()
