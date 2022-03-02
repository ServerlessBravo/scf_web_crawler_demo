from web_crawler.index import main_handler as inner_main_handler


def main_handler(event, context):
    return inner_main_handler(event, context)