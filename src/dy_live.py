import _thread
import binascii
import gzip
import json
import os
import signal
import sys
from src.utils.logger import logger
import re
import time
import requests
import websocket
from protobuf_inspector.types import StandardParser
from google.protobuf import json_format
from proto.dy_pb2 import PushFrame
from proto.dy_pb2 import Response
from proto.dy_pb2 import MatchAgainstScoreMessage
from proto.dy_pb2 import LikeMessage
from proto.dy_pb2 import MemberMessage
from proto.dy_pb2 import GiftMessage
from proto.dy_pb2 import ChatMessage
from proto.dy_pb2 import SocialMessage
from proto.dy_pb2 import RoomUserSeqMessage
from proto.dy_pb2 import UpdateFanTicketMessage
from proto.dy_pb2 import CommonTextMessage
from proto.dy_pb2 import ProductChangeMessage
clientDictSession={}

def onMessage(ws: websocket.WebSocketApp, message: bytes):
    liveRoomId = clientDictSession[ws] # 获取房间ID
    # print(message)
    # 相当于每一条消息
    wssPackage = PushFrame()
    # 将二进制序列化后的数据解析到此消息中
    wssPackage.ParseFromString(message)
    logId = wssPackage.logId
    # 使用gzip压缩
    decompressed = gzip.decompress(wssPackage.payload)
    payloadPackage = Response()
    payloadPackage.ParseFromString(decompressed)
    # 发送ack包
    if payloadPackage.needAck:
        sendAck(ws, logId, payloadPackage.internalExt)
    for msg in payloadPackage.messagesList:
        # 反对分数消息
        if msg.method == 'WebcastMatchAgainstScoreMessage':
            unPackMatchAgainstScoreMessage(msg.payload)
            continue

        # 点赞数
        if msg.method == 'WebcastLikeMessage':
            unPackWebcastLikeMessage(msg.payload)
            continue

        # 成员进入直播间消息
        if msg.method == 'WebcastMemberMessage':
            unPackWebcastMemberMessage(msg.payload)
            continue

        # 礼物消息
        if msg.method == 'WebcastGiftMessage':
            unPackWebcastGiftMessage(msg.payload)
            continue

        # 聊天消息
        if msg.method == 'WebcastChatMessage':
            unPackWebcastChatMessage(msg.payload)
            continue

        # 联谊会消息
        if msg.method == 'WebcastSocialMessage':
            unPackWebcastSocialMessage(msg.payload)
            continue

        # 房间用户发送消息
        if msg.method == 'WebcastRoomUserSeqMessage':
            unPackWebcastRoomUserSeqMessage(msg.payload)
            continue

        # 更新粉丝票
        if msg.method == 'WebcastUpdateFanTicketMessage':
            unPackWebcastUpdateFanTicketMessage(msg.payload)
            continue

        # 公共文本消息
        if msg.method == 'WebcastCommonTextMessage':
            unPackWebcastCommonTextMessage(msg.payload)
            continue

        # 商品改变消息
        if msg.method == 'WebcastProductChangeMessage':
            WebcastProductChangeMessage(msg.payload)
            continue
        logger.info('[onMessage] [待解析方法' + msg.method + '等待解析～] [房间Id：' + liveRoomId + ']')


def unPackWebcastCommonTextMessage(data):
    
    commonTextMessage = CommonTextMessage()
    commonTextMessage.ParseFromString(data)
    data = json_format.MessageToDict(commonTextMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info('[unPackWebcastCommonTextMessage] [] | ' + log)
    return data


def WebcastProductChangeMessage(data):
    commonTextMessage = ProductChangeMessage()
    commonTextMessage.ParseFromString(data)
    data = json_format.MessageToDict(commonTextMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info('[WebcastProductChangeMessage] []  | ' + log)


def unPackWebcastUpdateFanTicketMessage(data):
    updateFanTicketMessage = UpdateFanTicketMessage()
    updateFanTicketMessage.ParseFromString(data)
    data = json_format.MessageToDict(updateFanTicketMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info('[unPackWebcastUpdateFanTicketMessage] []  | ' + log)
    return data


def unPackWebcastRoomUserSeqMessage(data):
    roomUserSeqMessage = RoomUserSeqMessage()
    roomUserSeqMessage.ParseFromString(data)
    data = json_format.MessageToDict(roomUserSeqMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info('[unPackWebcastRoomUserSeqMessage] []| ' + log)
    return data


def unPackWebcastSocialMessage(data):
    socialMessage = SocialMessage()
    socialMessage.ParseFromString(data)
    data = json_format.MessageToDict(socialMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info('[unPackWebcastSocialMessage] [➕直播间关注消息]  | ' + log)
    return data


# 普通消息
def unPackWebcastChatMessage(data):
    chatMessage = ChatMessage()
    chatMessage.ParseFromString(data)
    data = json_format.MessageToDict(chatMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info(
        f'[unPackWebcastChatMessage] | ' + log)
    return data


# 礼物消息
def unPackWebcastGiftMessage(data):
    giftMessage = GiftMessage()
    giftMessage.ParseFromString(data)
    data = json_format.MessageToDict(giftMessage, preserving_proto_field_name=True)
    try:
        gift_name = data.get("gift").get("name")
        nick_name = data.get("user").get("nickName")
        print(gift_name, nick_name)
        # # 对特殊礼物单独统计
        # if gift_name in LIVE_GIFT_LIST:
        #     logger.info(f"抓到特殊礼物了: {gift_name}，用户名：{nick_name}")
        #     GlobalVal.gift_list.append(f"{nick_name}")
        # # 特殊礼物价值依然统计
        # GlobalVal.gift_num += int(data.get("totalCount", 1))
        # GlobalVal.gift_value += (int(data["gift"]["diamondCount"]) * int(data.get("totalCount", 1)))
        # # 将消息发送到我们自己的服务器:websocket链接
        # ws_sender(f"收到礼物: {gift_name}，礼物数量:{GlobalVal.gift_num}，礼物价值: {GlobalVal.gift_value}")
    except Exception as e:
        logger.error(f"解析礼物数据出错: {e}")
    log = json.dumps(data, ensure_ascii=False)
    logger.info(
        f'[unPackWebcastGiftMessage]  ' + log)
    return data


# xx成员进入直播间消息
def unPackWebcastMemberMessage(data):
    global member_num
    memberMessage = MemberMessage()
    memberMessage.ParseFromString(data)
    data = json_format.MessageToDict(memberMessage, preserving_proto_field_name=True)
    # 直播间人数统计
    member_num = int(data.get("memberCount", 0))
    log = json.dumps(data, ensure_ascii=False)
    print("---------------")
    print(data)
    print("---------------")
    
    # logger.info(f'[unPackWebcastMemberMessage]   | ' + log)
    return data


# 点赞
def unPackWebcastLikeMessage(data):
    likeMessage = LikeMessage()
    likeMessage.ParseFromString(data)
    data = json_format.MessageToDict(likeMessage, preserving_proto_field_name=True)

    log = json.dumps(data, ensure_ascii=False)
    logger.info(f'[unPackWebcastLikeMessage] [直播间点赞统计{data["total"]}]  | ' + log)
    return data


# 解析WebcastMatchAgainstScoreMessage消息包体
def unPackMatchAgainstScoreMessage(data):
    matchAgainstScoreMessage = MatchAgainstScoreMessage()
    matchAgainstScoreMessage.ParseFromString(data)
    data = json_format.MessageToDict(matchAgainstScoreMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logger.info('[unPackMatchAgainstScoreMessage] [不知道是啥的消息]  | ' + log)
    return data


# 发送Ack请求
def sendAck(ws, logId, internalExt):
    obj = PushFrame()
    obj.payloadType = 'ack'
    obj.logId = logId
    obj.payloadType = internalExt
    data = obj.SerializeToString()
    ws.send(data, websocket.ABNF.OPCODE_BINARY)
    logger.info('[sendAck] [🌟发送Ack] ')


def onError(ws, error):
    logger.error('[onError] [webSocket Error事件] ')


def onClose(ws, a, b):
    logger.info('[onClose] [webSocket Close事件]')
    # clientDictSession.pop(ws)
    # # 直播结束退出程序
    # pid = os.getpid()  # 获取当前进程的PID
    # os.kill(pid, signal.SIGTERM)


def onOpen(ws):
    _thread.start_new_thread(ping, (ws,))
    liveRoomId = clientDictSession[ws] # 获取房间ID
    logger.info('[onOpen] [webSocket Open事件] [房间Id：' + liveRoomId + ']')


# 发送ping心跳包
def ping(ws):
    liveRoomId = clientDictSession[ws] # 获取房间ID
    while True:
        obj = PushFrame()
        obj.payloadType = 'hb'
        data = obj.SerializeToString()
        ws.send(data, websocket.ABNF.OPCODE_BINARY)
        logger.info('[ping] [💗发送ping心跳] [房间Id：' + liveRoomId + '] ====>')
        time.sleep(10)


def wssServerStart(ttwid:str, liveRoomId:str):
    websocket.enableTrace(False)
    # 拼接获取弹幕消息的websocket的链接
    webSocketUrl = 'wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&internal_ext=internal_src:dim|wss_push_room_id:' + liveRoomId + '|wss_push_did:7188358506633528844|dim_log_id:20230521093022204E5B327EF20D5CDFC6|fetch_time:1684632622323|seq:1|wss_info:0-1684632622323-0-0|wrds_kvs:WebcastRoomRankMessage-1684632106402346965_WebcastRoomStatsMessage-1684632616357153318&cursor=t-1684632622323_r-1_d-1_u-1_h-1&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&debug=false&maxCacheMessageNumber=20&endpoint=live_pc&support_wrds=1&im_path=/webcast/im/fetch/&user_unique_id=7188358506633528844&device_platform=web&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh&browser_platform=MacIntel&browser_name=Mozilla&browser_version=5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36&browser_online=true&tz_name=Asia/Shanghai&identity=audience&room_id=' + liveRoomId + '&heartbeatDuration=0&signature=00000000'
    h = {
        'cookie': 'ttwid=' + ttwid,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    # 创建一个长连接，并开始侦听消息
    ws = websocket.WebSocketApp(
        webSocketUrl, on_message=onMessage, on_error=onError, on_close=onClose,
        on_open=onOpen,
        header=h
    )
    clientDictSession[ws] = liveRoomId
    ws.run_forever()


def parseLiveRoomUrl(url, userSession):
    """
    解析直播的弹幕websocket地址
    :param url:直播地址
    :return:
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
    wssServerStart(ttwid, liveRoomId)

