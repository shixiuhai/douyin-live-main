import logging
import os

from config import LOG_FILE_SAVE, LOG_FILE_NAME, LOG_LEVEL, LOG_FORMAT

# 第一步：创建文件日志对象
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



# 配置日志文件保存
if LOG_FILE_SAVE:
    file_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
    # 在创建文件处理器时设置 encoding='utf-8'
    file_handler = logging.FileHandler(filename=file_path, mode="a", encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    fmt1 = logging.Formatter(fmt=LOG_FORMAT)
    file_handler.setFormatter(fmt=fmt1)
    logger.addHandler(file_handler)

# 第三步：创建控制台文本处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
fmt1 = logging.Formatter(fmt=LOG_FORMAT)
console_handler.setFormatter(fmt=fmt1)

# 第四步：将控制台日志器、文件日志器，添加进日志器对象中
logger.addHandler(console_handler)

if __name__ == '__main__':
    logger.info("这是一条info消息")
