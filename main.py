# import requests
#
#
# if __name__ == '__main__':
#     url='https://api.bilibili.com/pgc/season/rank/web/list?day=3&season_type=2'
#
#     headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78'}
#     response=requests.get(url=url,headers=headers).text
#     print(response)


import logging
import os
import sqlite3
import datetime
import time
import colorlog

from bs4 import BeautifulSoup
from selenium import webdriver



class ColoredLogger(logging.Logger):
    """
    日志函数用于继承的，没啥用，大家看看就好
    """
    def __init__(self, name, level=logging.DEBUG):
        super().__init__(name, level)

        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        log_filename = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
        log_filepath = os.path.join(log_dir, log_filename)

        handler = colorlog.StreamHandler()  # 输出到终端
        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(asctime)s 丨 %(log_color)s%(levelname)s 丨 %(message)s",
                log_colors={
                    "DEBUG": "blue",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_yellow",
                }
            )
        )

        self.setLevel(level)
        self.addHandler(handler)

        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")  # 输出到文件
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.addHandler(file_handler)


def get_movie_list():
    """
    访问指定Url
    使用bs4解析页面 使用class选择器选择info
    然后对数据进行去冗余部分再去需要的内容后添加进movie_list这列表中
    :return: List
    """
    url = "https://www.bilibili.com/v/popular/rank/movie/"
    driver.get(url)

    page_content = driver.page_source

    soup = BeautifulSoup(page_content, "html.parser")

    elements_with_class = soup.select(".info")

    movie_list = []
    for element in elements_with_class:
        # print(element.text)
        disp = element.text.split('\n')

        cleaned_lines = [line.strip() for line in disp if line.strip()]
        movie_list.append(cleaned_lines)
    # print(movie_list)
    return movie_list


def create_movie_table():
    """
    这函数的作用就是查看data.db数据库文件在不在
    如果在那么就删除，再新建
    如果没有就新建


    :return None
    """
    if not os.path.exists('data.db'):
        logger.info('数据库文件不存在，正在新建')
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE movie
                        (name TEXT, release_date TEXT, amount_play TEXT, likes TEXT)''')

        conn.commit()
        conn.close()
        logger.info('数据库文件and表已创建完成')
    elif os.path.exists('data.db'):
        os.remove('data.db')
        logger.info('数据库已存在，正在删除')
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE movie
                        (name TEXT, release_date TEXT, amount_play TEXT, likes TEXT)''')

        conn.commit()
        conn.close()
        logger.info('数据库文件and表已重新创建完成')

def insert_movie_info(name, release_date, amount_play, likes):
    """
     调用sqlite3库插入数据
    :param name:
    :param release_date:
    :param amount_play:
    :param likes:
    :return: None
    """
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # 插入数据
    cursor.execute("INSERT INTO movie (name, release_date, amount_play, likes) VALUES (?, ?, ?, ?)",
                   (name, release_date, amount_play, likes))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    # 需要播放的电影ID
    # movie_id = input('请输入需要播放的id')  # 举例 ：让子弹飞的网页URL是：https://www.bilibili.com/bangumi/play/ss12548?theme=movie 那么他的id是12548
    movie_id = '12548'
    movie_url = f'https://www.bilibili.com/bangumi/play/ss{movie_id}?theme=movie'
    # 设置一下日志的东西，可以不管哦
    logger = ColoredLogger('text')
    logger.info('初始化ing...')
    # 初始化selenium driver
    driver = webdriver.Chrome()
    # 查看数据库文件存在？
    create_movie_table()
    # 这里是主要部分调用这函数可以获取指定的数据写入数据库中
    for i in get_movie_list():  # 写入sqlite
        insert_movie_info(i[0],i[1],i[2],i[3])
        logger.info(f"插入数据成功，name:{i[0]},date:{i[1]},play:{i[2]},likes:{i[3]}")
        pass

    # 访问电影
    logger.info('数据写入完毕，准备访问目标电影，并且播放10s+')
    driver.get(movie_url)
    start_time = time.time()
    time.sleep(15)
    logger.info(f'播放完毕共用时：{"{:.2f}".format(time.time() - start_time)} 秒')
    driver.close()
    logger.info('运行结束,请回车结束运行')
    input()
