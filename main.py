import ast
import paho.mqtt.client as mqtt
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton


class SmartParking(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        count=1
        for i in range(3,-1,-1):
            ob= (self.children[0].children[1].children[0].children[0].children[i].children[0])
            k = 7  # for encoded dict
            for j in range(1,9):
                b1= MDRaisedButton(text=str(count), size_hint = (1, 1))
                b1.md_bg_color = myLab.color['green']
                b1.id="button"+str(count)
                ob.add_widget(b1)
                myLab.enc_dic.update({count:"0"+"1"+"0"+"0"+str(i)+"0"+str(k)}) #for encoded dict
                k -= 1
                count += 1

class myLab(MDApp):
    connect_status = StringProperty("Disconnected")
    connect_status_hint = StringProperty("(Tap to Connect)")
    hold=False
    enc_dic={}
    db_dic={}
    search_result=[]
    obj_list=[]
    client = mqtt.Client("Receiver")

    color = {'blue': (30 / 255.0, 203 / 255.0, 255 / 255.0, 1),
             'red': (225 / 255.0, 52 / 255.0, 30 / 255.0, 1),
             'green': (6 / 255.0, 194 / 255.0, 88 / 255.0, 1)}

    def connection_main(self, widget):
        global obj
        obj=self

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                obj.connect_status = "Connected"
                obj.connect_status_hint = "(Tap to Disconnect)"
                widget.md_bg_color= obj.color['green']
                print("Connected")
            else:
                print("Connection Failed")


        def on_message(client, userdata, message):
            obj.db_dic.update(ast.literal_eval(message.payload.decode("UTF-8")))
            obj.db_dic=dict(sorted(self.db_dic.items()))
            print(obj.db_dic)
            obj.change_status()

        broker_address = "192.168.0.207"
        port = 1883

        obj.client.on_connect = on_connect
        obj.client.on_message = on_message

        if (obj.connect_status == 'Disconnected'):
            obj.client.connect(broker_address, port)
            obj.client.loop_start()
            obj.client.subscribe([("Camera" + str(i), 1) for i in range(1, 9)])

        else:
            obj.client.loop_stop()
            obj.connect_status = "Disconnected"
            obj.connect_status_hint = "(Tap to Connect)"
            widget.md_bg_color = obj.color['red']
            obj.client.disconnect()


    def on_text_validate(self, widget):
        for i,j in list(self.db_dic.items()):
            if j == int(widget.text):
                self.search_result.append(i)
        self.root.children[0].switch_tab("live parking")
        self.on_parking_press(False)

    def on_search_press(self,status):
        self.hold = status
        self.search_result=[]

    def on_parking_press(self,status):
        self.hold = status
        self.change_status()

    def change_status(self):
        if not self.hold:
            for i,j in self.db_dic.items():
                if i in self.search_result:
                    self.obj_list[i-1].md_bg_color = self.color['blue']
                else:
                    if j=="Empty":
                        self.obj_list[i-1].md_bg_color = self.color['green']
                    else:
                        self.obj_list[i-1].md_bg_color = self.color['red']

    def get_obj(self, pno):
        x = self.enc_dic[pno]
        return self.root.children[int(x[0])].children[int(x[1])].children[int(x[2])].children[int(x[3])].children[int(x[4])].children[int(x[5])].children[int(x[6])]

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_hue = "A700"
        return SmartParking()

    def on_start(self):
        self.obj_list=[self.get_obj(i+1) for i in range(32)]

myLab().run()
