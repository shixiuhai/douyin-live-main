import logging
from src import dy_live
import requests
import re
import json
import asyncio
import websockets
from urllib.parse import parse_qs
from src.utils.logger import logger
import threading

userDictSession={}
clientDictThreads = {}

def get_liveRoomId_ttwid(url:str)->tuple:
    """
    通过url 提取 房间ID 和 ttwid
    """
    h = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'cookie': '__ac_nonce=0638733a400869171be51',
    }
    res = requests.get(url=url, headers=h)
    data = res.cookies.get_dict()
    ttwid = data['ttwid']
    res = res.text
    res_room = re.search(r'roomId\\":\\"(\d+)\\"', res)
    # 获取直播主播的uid和昵称等信息
    live_room_search = re.search(r'owner\\":(.*?),\\"room_auth', res)
    # 如果没有获取到live_room信息，很有可能是直播已经关闭了，待优化
    live_room_res = live_room_search.group(1).replace('\\"', '"')
    live_room_info = json.loads(live_room_res)
    logger.info(f"主播账号信息: {live_room_info}")
    print(f"主播账号信息: {live_room_info}")
    # 直播间id
    liveRoomId = res_room.group(1)
    return (liveRoomId, ttwid)

async def handle_client(websocket, path):
    # 解析查询字符串参数
    params = params = parse_qs(path[2:])
    print(f"Client connected with parameters: {params}")

    try:
        async for message in websocket:
            print(f"Received message from client: {message}")

            # 在这里处理接收到的消息

            # 例如，回复客户端
            response_message = f"Server received: {message}"
            await websocket.send(response_message)
            print(f"Sent message to client: {response_message}")

    finally:
        # 客户端断开连接时执行清理工作
        print("Client disconnected")

async def start_server(host, port):
    # 启动 WebSocket 服务器
    server = await websockets.serve(
        handle_client,
        host,
        port
    )
    print(f"WebSocket server started at ws://{host}:{port}")

    # 保持服务器运行
    await server.wait_closed()

if __name__ == '__main__':
    # 日志配置
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.ERROR)
    # dy_live.parseLiveRoomUrl("https://live.douyin.com/544995324917")
    # 设置服务器的主机和端口
    server_host = "127.0.0.1"
    server_port = 8765

    # 启动 WebSocket 服务器
    asyncio.run(start_server(server_host, server_port))
