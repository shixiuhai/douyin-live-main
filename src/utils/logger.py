import logging
import os

from config import LOG_FILE_SAVE, LOG_FILE_NAME, LOG_LEVEL

# 第一步：创建文件日志对象
logger = logging.getLogger()

# 第二步：创建文件日志处理器，默认 logging 会自己创建一个处理器
file_fmt = "%(asctime)s - %(levelname)s - %(message)s"

# 配置日志文件保存
if LOG_FILE_SAVE:
    file_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
    # 在创建文件处理器时设置 encoding='utf-8'
    file_handler = logging.FileHandler(filename=file_path, mode="a", encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(fmt=file_fmt))
    logger.addHandler(file_handler)

# 第三步：创建控制台文本处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_fmt = "%(asctime)s - %(levelname)s - %(message)s"
fmt1 = logging.Formatter(fmt=console_fmt)
console_handler.setFormatter(fmt=fmt1)

# 第四步：将控制台日志器、文件日志器，添加进日志器对象中
logger.addHandler(console_handler)

if __name__ == '__main__':
    logger.info("这是一条info消息")
