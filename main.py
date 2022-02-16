#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2022/02/08 11:37:05
@Author  :   Ayatale 
@Version :   1.1
@Github  :   https://github.com/brx86/
@Desc    :   The main window of the application.
"""

import os, time
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QSize
from server import msgServer, apiServer
from qt_material import apply_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loadUi("ui/qtalk.ui")
        self.runServer()
        # init icons
        self.ui.avatarButton.setIcon(QIcon("ui/avatar.jpg"))
        self.ui.friendsButton.setIcon(QIcon("ui/friends.png"))
        self.ui.chatIcon.setIcon(QIcon("ui/arch.png"))
        self.ui.chatIcon.setIconSize(QSize(36, 36))
        self.ui.emojisButton.setIcon(QIcon("ui/emojis.png"))
        self.ui.fileButton.setIcon(QIcon("ui/file.png"))
        self.ui.sendButton.setIcon(QIcon("ui/send.png"))
        self.ui.chatList.itemClicked.connect(self.selectChat)
        self.ui.sendButton.clicked.connect(self.sendMsg)
        self.ui.inputBox.returnPressed.connect(self.sendMsg)
        self.ui.avatarButton.clicked.connect(self.changeLogo)
        self.ui.msgBox.setReadOnly(True)
        self.ui.show()
        self.chat_dict = dict()
        self.chat_now = str()

    def initChat(self):
        chat_list = [g for g in os.listdir("log") if not g.startswith(".")]
        if len(chat_list) == 0:
            self.ui.inputBox.setReadOnly(True)
        else:
            self.ui.inputBox.setReadOnly(False)

    def runServer(self):
        self.apiServer = apiServer()
        self.msgServer = msgServer()
        self.msgServer.start()
        self.self_info = self.apiServer.get_login_info()
        self.ui.avatarButton.setIcon(QIcon("ui/avator.jpg"))
        self.msgServer.new_msg_signal.connect(self.updateMsg)
        self.msgServer.update_logo_signal.connect(self.changeLogo)
        self.msgServer.close_window_signal.connect(self.ui.close)

    def sendMsg(self):
        stime = time.strftime("%H:%M:%S", time.localtime(time.time()))
        msg = self.ui.inputBox.text()
        gid = self.chat_dict.get(self.chat_now)
        if gid:
            self.ui.inputBox.clear()
            self.apiServer.send_msg(gid, msg)
            release = False
            if release:
                log = f"<small>[{stime}] [{self.self_info[0]}]</small> <b>{self.self_info[1]}</b> :<br>{msg}<br><br>\n"
            else:
                log = f"""
<table width="80%" align="right">
    <tr>
        <td valign="bottom" width="64px">&nbsp;<!--img height="64" src="cache/uid.png" width="64"/--></td>
        <td width="100%">
        <table border="1" width="100%"  bgcolor="#ccff99">
            <tr>
                <td>
                <table width="100%">
                    <tr>
                        <td width="10px">&nbsp;</td>
                        <td><font color="#888888">
                        <table width="100%">
                            <tr>
                                <td width="32px"><sex/></td>
                                <td width="40%">{self.self_info[0]}</td>
                                <td  align=" right">{self.self_info[1]}</td>
                            </tr>
                        </table>
                        </font></td>
                        <td width="10px">&nbsp;</td>
                    </tr>
                    <tr>
                        <td width="10px"></td>
                        <td>
                        <!--table width="100%">
                            <tr>
                                <td align="left">reply_msg</td>
                            </tr>
                        </table-->
                        <table width="100%">
                            <tr>
                                <td align="left">{msg}</td>
                            </tr>
                        </table>
                        <!--table width="100%">
                            <tr>
                                <td align="left">ext_msg</td>
                            </tr>
                        </table-->
                        </td>
                        <td width="10px"></td>
                    </tr>
                    <tr>
                        <td width="10px">&nbsp;</td>
                        <td>
                        <table width="100%">
                            <tr>
                                <td align="right"><font color="#888888">{stime}</font></td>
                            </tr>
                        </table>
                        </td>
                        <td width="10px">&nbsp;</td>
                    </tr>
                </table>
                </td>
            </tr>
        </table>
        </td>
        <td valign="top"><!--img src="ui/role.png" width="32" --><role/>&nbsp;</td>
    </tr>
</table>
</body>
"""
            self.ui.msgBox.append(log)
            self.ui.msgBox.ensureCursorVisible()
            with open(f"log/{gid}", "a") as f:
                f.write(log)

    def updateMsg(self, chat_info, msg):
        # print(msg)
        self.ui.chatTitle.setText(chat_info[1])
        self.ui.chatInfo.setText(str(chat_info[0]))
        if chat_info[1] not in self.chat_dict:
            print(f"New chat: {chat_info}\n")
            self.chat_dict[chat_info[1]] = chat_info[0]
            self.ui.chatList.addItem(chat_info[1])
            if self.ui.chatList.count() == 1:
                self.ui.inputBox.setReadOnly(False)
                self.ui.chatList.setCurrentRow(0)
                self.chat_now = self.ui.chatList.selectedItems()[0].text()
                print(f"First: {self.chat_now}")
        gid = self.chat_dict[self.chat_now]
        if chat_info[0] == int(gid):
            self.ui.msgBox.append(msg)
            self.ui.msgBox.ensureCursorVisible()

    def changeLogo(self, signal="", path=""):
        match signal:
            case "avator":
                print(f"Change avator to {path}")
            case False:
                print("Change avator")
            case _:
                print(f"Error: No such signal: {signal}")

    def selectChat(self):
        chat_new = self.ui.chatList.selectedItems()[0].text()
        if chat_new != self.chat_now:
            print(f"{self.chat_now} -> {chat_new}")
            self.chat_now = chat_new
            gid = self.chat_dict[chat_new]
            self.ui.chatTitle.setText(chat_new)
            self.ui.chatInfo.setText(str(gid))
            with open(f"log/{gid}", "r") as f:
                history = f.read()
            self.ui.msgBox.clear()
            self.ui.msgBox.append(history)
            self.ui.msgBox.ensureCursorVisible()


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("ui/arch.png"))
    apply_stylesheet(app, theme="default_light.xml")
    window = MainWindow()
    app.exec_()
