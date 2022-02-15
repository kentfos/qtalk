# pyqt-talk

## OICQ

1. 新建一个文件夹，cd进入文件夹

    ```shell
    mkdir onebot
    cd onebot
    ```

2. 使用yarn或npm安装oicq（二选一）

    ``` shell
    yarn add oicq@1
    npm i oicq@1
    ```

3. 首次运行oicq，生成配置文件

    ```shell
    node_modules/.bin/oicq
    ```

4. 根据提示修改配置文件 `~/.oicq/config.js`

    启用http与正向ws

    参考范例：https://fars.ee/RDQd/js

5. 再次运行oicq，根据提示输入密码或扫码登陆

    ```shell
    node_modules/.bin/oicq <qq号>
    ```

## QTalk

1. 新建虚拟环境并安装依赖：

    ```shell
    python -m venv .env --upgrade-deps
    source .env/bin/activate
    pip install pyqt5 websocket-client qt_material
    ```

    如果不想创建虚拟环境，可以直接安装依赖（推荐）
    ```shell
    sudo pacman -S python-pyqt5 python-websocket-client
    # qt_material不在arch官方仓库，如果不需要主题可以直接注释掉18、107行
    # 使用pip安装qt_material
    pip install qt_material
    # 或使用aurhelper安装qt_material
    paru -S python-qt-material-git
    ```

2. 运行主程序:

    ```shell
    python main.py
    ```

## 已知问题

1. 所有消息都在同一个窗口（以后会使用多标签页分群组）
2. 由于没搞明白标签页所以暂时没怎么处理发送消息，目前只会发到指定群组（在main.py第93行）
3. pypi的pyqt5对fcitx5的兼容性有问题，如果使用pip安装并使用fcitx5输入法会无法输入中文，请执行以下命令：
    ```shell
    ln -s /usr/lib/qt/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so .env/lib/python3.10/site-packages/PyQt5/Qt5/plugins/platforminputcontexts/
    ```
    其中.env/lib/python3.10/site-packages可以换成你pip安装的实际路径

## ~~画饼~~ Todo

- [x] 通过标签页或侧栏将消息分组
- [x] 处理常见CQ码
- [ ] 私聊收发消息
- [ ] 显示头像
- [x] 显示消息中的图片
- [ ] 显示@、回复
- [ ] 主动@与回复
- [ ] 可下载消息中的文件
- [ ] 可下载群文件
- [ ] 发送图片与文件
- [ ] 系统消息通知
- [ ] 有待补充...