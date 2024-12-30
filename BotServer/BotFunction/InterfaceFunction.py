import FileCache.FileCacheServer as Fcs
import xml.etree.ElementTree as ET
import Config.ConfigServer as Cs
from OutPut.outPut import op
import requests
import time
import os


def getWechatVideoData(content):
    """
    处理微信视频号 提取objectId objectNonceId
    :param content:
    :return: objectId objectNonceId
    """
    try:
        root = ET.fromstring(content)
        finderFeed = root.find('.//finderFeed')
        objectId = finderFeed.find('./objectId').text
        objectNonceId = finderFeed.find('./objectNonceId').text
        return objectId, objectNonceId
    except Exception as e:
        op(f'[-]: 提取微信视频号ID出现错误, 错误信息: {e}')
        return '', ''


def getAtData(wcf, msg):
    """
    处理@信息
    :param msg:
    :param wcf:
    :return:
    """
    noAtMsg = msg.content
    try:
        root_xml = ET.fromstring(msg.xml)
        atUserListsElement = root_xml.find('.//atuserlist')
        atUserLists = atUserListsElement.text.replace(' ', '').strip().strip(',').split(
            ',') if atUserListsElement is not None else None
        if not atUserLists:
            return '', ''
        atNames = []
        for atUser in atUserLists:
            atUserName = wcf.get_alias_in_chatroom(atUser, msg.roomid)
            atNames.append(atUserName)
        for atName in atNames:
            noAtMsg = noAtMsg.replace('@' + atName, '')
    except Exception as e:
        op(f'[~]: 处理@消息出现小问题, 仅方便开发调试, 不用管此报错: {e}')
        return '', ''
    return atUserLists, noAtMsg.strip()


def getIdName(wcf, Id):
    """
    获取好友或者群聊昵称
    :return:
    """
    name_list = wcf.query_sql("MicroMsg.db",
                              f"SELECT UserName, NickName FROM Contact WHERE UserName = '{Id}';")
    if not name_list:
        return ''
    name = name_list[0]['NickName']
    return name


def getUserPicUrl(wcf, sender):
    """
    获取好友头像下载地址
    :param sender:
    :param wcf:
    :return:
    """
    imgName = str(sender) + '.jpg'
    save_path = Fcs.returnAvatarFolder() + '/' + imgName

    if imgName in os.listdir(Fcs.returnAvatarFolder()):
        return save_path

    headImgData = wcf.query_sql("MicroMsg.db", f"SELECT * FROM ContactHeadImgUrl WHERE usrName = '{sender}';")
    try:
        if headImgData:
            if headImgData[0]:
                bigHeadImgUrl = headImgData[0]['bigHeadImgUrl']
                content = requests.get(url=bigHeadImgUrl, timeout=30).content
                with open(save_path, mode='wb') as f:
                    f.write(content)
                return save_path
    except Exception as e:
        op(f'[-]: 获取好友头像下载地址出现错误, 错误信息: {e}')
        return None


if __name__ == '__main__':
    pass
