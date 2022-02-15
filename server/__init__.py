import re, json, time
from os import path

from server.config import WSHOST, TOKEN
from PyQt5.QtCore import pyqtSignal, QThread
from threading import Thread
from urllib.request import urlretrieve as download
from websocket import create_connection, _exceptions


class msgServer(QThread):
    new_msg_signal = pyqtSignal(tuple, str)
    close_window_signal = pyqtSignal()
    update_logo_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.ws = create_connection(f"{WSHOST}/?access_token={TOKEN}")
        self.ws.recv()
        self.ws.recv()
        print(f"Msg server connected! Status: {self.ws.getstatus()}")

    def run(self):
        while True:
            try:
                data = json.loads(self.ws.recv())
                # print('Msg', data)
                msg_type = data.get("message_type")
                if msg_type == "group":
                    gid = data["group_id"]
                    uid = data["user_id"]
                    gname = data["group_name"]
                    chat_info = (gid, gname)
                elif msg_type == "private":
                    uid = data["user_id"]
                    uname = data["user_name"]
                    chat_info = (uid, uname)
                else:
                    print(f"Unknown message type: {msg_type}")
                    continue
                if not path.exists(f"cache/{uid}.png"):
                    self.thread_fetch(
                        f"https://q1.qlogo.cn/g?b=qq&nk={uid}&s=140&timestamp=",
                        f"cache/{uid}.png",
                    )
                mid = data["message_id"]
                stime = time.strftime("%H:%M:%S", time.localtime(data["time"]))
                card = data["sender"]["card"]
                sender = card if card else data["sender"]["nickname"]
                rawmsg = data["raw_message"]
                handled_msg = self.handle_cqmsg(rawmsg)
                # log = f"<small>[{stime}] [{uid}]</small> <b>{sender}</b> :<br>{handled_msg}<br><br>\n"
                release = False
                if release:
                    log = (
                        f'<div><span><img src="cache/{uid}.png" width="32" height="32" style="object-fit:cover;"></span><div>{sender}</div'
                        f"><div><b>{handled_msg}</b></div></div> "
                    )
                else:
                    sex = data["sender"]["sex"]
                    nickname = data["sender"]["nickname"]
                    card_name = data["sender"]["card"]
                    role = "member"  # "admin", "owner"
                    reply_msgid = 0
                    reply_msg = ""
                    ext_msg = ""
                    at_info = ""
                    log = f"""
<table width="80%">
    <tr>
        <td valign="bottom" width="64px">&nbsp;<img height="64" src="cache/{uid}.png" width="64"/></td>
        <td width="100%">
        <table border="1" width="100%">
            <tr>
                <td>
                <table width="100%">
                    <tr>
                        <td width="10px">&nbsp;</td>
                        <td><font color="#888888">
                        <table width="100%">
                            <tr>
                                <td width="32px"><{sex}/></td>
                                <td width="40%">{nickname}</td>
                                <td  align=" right">{card_name}</td>
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
                                <td align="left">{reply_msg}</td>
                            </tr>
                        </table-->
                        <table width="100%">
                            <tr>
                                <td align="left">{handled_msg}</td>
                            </tr>
                        </table>
                        <!--table width="100%">
                            <tr>
                                <td align="left">{ext_msg}</td>
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
        <td valign="top"><!--img src="ui/{role}.png" width="32" --><role/>&nbsp;</td>
    </tr>
</table>
</body>
"""
                print(f"message_id: {mid}")
                self.new_msg_signal.emit(chat_info, log)
                with open(f"log/{chat_info[0]}", "a") as f:
                    f.write(log)
            except _exceptions.WebSocketConnectionClosedException:
                msg = "Connection Closed. Exit after 3 seconds."
                self.new_msg_signal.emit(0, msg)
                self.ws.close()
                time.sleep(3)
                self.close_window_signal.emit()
                return

    def handle_cqmsg(self, rawmsg):
        def cq_to_text(cq_list):
            for cq in cq_list:
                cq_type = cq[0]
                cq_data = cq[1]
                if cq_type == "at":
                    cq_at_user = re.compile(r"text=(.+)").findall(cq_data)
                    if cq_at_user:
                        yield f"{cq_at_user[0]} "
                elif cq_type in ["image", "flash"]:
                    cq_image_name = re.compile(r"file=(.+\.\w+),").findall(cq_data)
                    cq_image_url = re.compile(r"url=(.+)").findall(cq_data)
                    if cq_image_name and cq_image_url:
                        self.thread_fetch(cq_image_url[0], f"cache/{cq_image_name[0]}")
                        if cq_type == "image":
                            yield f'<a href="#cache/{cq_image_name[0]}" target="_blank"><img src="cache/{cq_image_name[0]}" width="300"/></a>'
                        else:
                            yield f'<a href="#cache/{cq_image_name[0]}" target="_blank">[闪照]<br><img src="cache/{cq_image_name[0]}" width="300"/></a>'
                elif cq_type == "face":
                    index = cq_data.index("text=")
                    face_index = re.findall(r"\d+", cq_data)
                    face_name = "{:0>3}".format(face_index[0])
                    yield f"<img src='face/{face_name}' width=24 />[表情: {cq_data[index+5:]}]"
                elif cq_type == "record":
                    yield "[录音] "
                elif cq_type == "video":
                    # yield '<a href="path/to/url">[短视频]</a>'
                    yield "[视频] "
                elif cq_type == "xml":
                    if "条转发消息" in cq_data:
                        index = cq_data.index("条转发消息")
                        yield f"[聊天记录:{cq_data[index - 1 : index + 5]}] "
                elif cq_type == "json":
                    index = cq_data.index("条转发消息")
                    yield f"[聊天记录:{cq_data[index - 1 : index + 5]}] "
                else:
                    yield f"[未知: {cq_type}] "

        rawmsg = (
            rawmsg.replace("&#91;", "[")
            .replace("&#93;", "]")
            .replace("&#44;", ",")
            .replace("\n", "<br>")
        )
        pattern_cq = re.compile(r"\[CQ:(\w+),(.*?)\]")
        cq_list = pattern_cq.findall(rawmsg)
        after_msg = re.sub(r"\[CQ:(\w+),(.*?)\]|[\u2029-\u202e]", "", rawmsg)
        if cq_list:
            if cq_list[0][0] == "json":
                print(rawmsg[14:-1])
                data = json.loads(rawmsg[14:-1])
                prompt = data.get("prompt")
                d = data["meta"].get("detail_1")
                desc = d["desc"] if d else data["meta"]["desc"]
                realurl = d["qqdocurl"] if d else data["meta"]["jumpurl"].split("?")[0]
                return f'{prompt}<br><a href="{realurl}">{desc}</a>'
            return f'{"".join(cq_to_text(cq_list))} {after_msg}'
        return after_msg

    def thread_fetch(self, url, path, signal=""):
        def threadDownload(url, path):
            nonlocal signal
            for t in range(5):
                try:
                    download(url, path)
                    if signal:
                        self.update_logo_signal.emit(signal, path)
                    return
                except:
                    print(f"Download failed. Retrying {t+1}...")
                    time.sleep(1)
            print("Download failed. Exit after 3 seconds.")

        thread = Thread(target=threadDownload, args=(url, path))
        thread.start()


class apiServer(QThread):
    def __init__(self):
        super().__init__()
        self.ws = create_connection(f"{WSHOST}/?access_token={TOKEN}")
        self.ws.recv()
        self.ws.recv()
        print(f"Api server connected! Status: {self.ws.getstatus()}")

    def get_login_info(self):
        send_data = {
            "action": "get_login_info",
            "params": {},
        }
        self.ws.send(json.dumps(send_data))
        data = json.loads(self.ws.recv())
        if data.get("status") == "ok":
            data = data["data"]
            self_id = data["user_id"]
            self_name = data["nickname"]
            avatar_url = f"http://q2.qlogo.cn/headimg_dl?dst_uin={self_id}&spec=100"
            for t in range(5):
                try:
                    download(avatar_url, "ui/avatar.jpg")
                    print(f"Avatar Received. ID: {self_id} Name: {self_name}\n")
                    return self_id, self_name
                except:
                    print(f"Download avatar failed. Retrying {t+1}...")
            print("Download avatar failed. Exit after 5 seconds.")
        else:
            print(f"Avatar Received Failed.\n")

    def get_group_member_list(self, gid):
        send_data = {
            "action": "get_group_member_list",
            "params": {"group_id": gid},
        }
        self.ws.send(json.dumps(send_data))
        data = json.loads(self.ws.recv())
        if data.get("status") == "ok":
            group_member = data["data"]
            return len(group_member)
        else:
            print(f"Get Group Failed.\n")

    def send_msg(self, gid, msg):
        send_data = {
            "action": "send_msg",
            "params": {"message_type": "group", "group_id": gid, "message": msg},
        }
        self.ws.send(json.dumps(send_data))
        data = json.loads(self.ws.recv())
        if data.get("status") == "ok":
            mid = data["data"]["message_id"]
            print(f"Message Sent. ID: {mid}\nMessage: {gid}->{msg}\n")
        else:
            print(f"Message Sent Failed.\n")
