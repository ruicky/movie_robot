

# 爬取测试: 引入待测试的pt parser
from yee.pt.ptpter import PTPTer
def test():
    # 初始化 client
    client = PTPTer(
        cookie = ""
    )
    # 测试空搜索
    client.test_empty_search()
    # 测试免费种
    client.test_free()
    # 测试红种
    client.test_redseed()
    # 多页面测试, 注意检查log中种子数量是否正确，防止漏爬情况
    client.test_regular()



if __name__ == '__main__':
    test();

