# Web UI自动化测试工具（百度搜索）- 修正版
import pytest
import pandas as pd
import os
import time
# ========== 核心修正：Selenium相关导入顺序 + webdriver-manager正确导入 ==========
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ========== 读取测试用例数据 ==========
def get_test_cases():
    """读取Excel中的批量测试用例"""
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_path)
    data_path = os.path.join(project_root, "data", "test_cases.xlsx")

    df = pd.read_excel(data_path)
    # 转换为pytest可识别的参数化格式
    test_cases = []
    for _, row in df.iterrows():
        test_cases.append((row["用例ID"], row["搜索关键词"], row["预期结果（包含关键词）"]))
    return test_cases


# ========== 初始化浏览器驱动 ==========
@pytest.fixture(scope="module")
def driver():
    """全局浏览器驱动，所有用例共用一个浏览器实例"""
    # 自动下载Chrome驱动并初始化
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()  # 窗口最大化
    driver.implicitly_wait(10)  # 隐式等待10秒（元素加载超时）
    yield driver  # 执行测试用例
    driver.quit()  # 所有用例执行完关闭浏览器


# ========== 核心测试用例 ==========
@pytest.mark.parametrize("case_id, keyword, expected", get_test_cases())
def test_baidu_search(driver, case_id, keyword, expected):
    """百度搜索UI自动化测试用例"""
    try:
        # 1. 打开百度首页
        driver.get("https://www.baidu.com")

        # 2. 定位搜索框，输入关键词
        search_box = driver.find_element(By.ID, "kw")
        search_box.clear()  # 清空输入框
        search_box.send_keys(keyword)
        time.sleep(1)  # 模拟用户输入延迟

        # 3. 点击搜索按钮（或按回车）
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)  # 等待搜索结果加载

        # 4. 断言：搜索结果包含预期内容
        page_source = driver.page_source
        assert expected in page_source, f"用例{case_id}失败：未找到预期内容「{expected}」"

        print(f"✅ 用例{case_id}通过：搜索「{keyword}」，验证结果包含「{expected}」")

    except Exception as e:
        # 捕获所有异常，标记用例失败
        pytest.fail(f"用例{case_id}失败：{str(e)}")


# ========== 生成测试报告 ==========
if __name__ == "__main__":
    # 定义报告保存路径
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_path)
    report_path = os.path.join(project_root, "reports", "baidu_test_report.html")

    # 执行pytest并生成HTML报告
    pytest.main([
        __file__,
        "-v",  # 详细输出
        "--html=" + report_path,  # 报告路径
        "--self-contained-html"  # 报告包含所有资源（图片/CSS）
    ])
    print(f"\n📊 测试报告已生成：{report_path}")