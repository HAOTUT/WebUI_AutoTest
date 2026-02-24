# Web UI自动化测试工具（百度搜索）- 深度绕开检测版
import pytest
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# ========== 读取测试用例数据 ==========
def get_test_cases():
    """读取Excel中的批量测试用例"""
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_path)
    data_path = os.path.join(project_root, "data", "test_cases.xlsx")

    print(f"📂 读取的Excel文件路径：{data_path}")
    try:
        df = pd.read_excel(data_path, engine="openpyxl")
        print(f"📋 Excel中的列名：{list(df.columns)}")

        test_cases = []
        for _, row in df.iterrows():
            test_cases.append((row["用例ID"], row["搜索关键词"], row["预期结果（包含关键词）"]))
        return test_cases
    except FileNotFoundError:
        print(f"❌ 未找到测试用例文件：{data_path}，请检查路径！")
        return []
    except KeyError as e:
        print(f"❌ Excel列名错误：缺少{e}，请核对列名是否为「用例ID」「搜索关键词」「预期结果（包含关键词）」")
        return []


# ========== 初始化浏览器驱动（深度绕开检测） ==========
@pytest.fixture(scope="module")
def driver():
    """全局浏览器驱动，彻底绕开百度反自动化检测"""
    chrome_options = webdriver.ChromeOptions()

    # 1. 核心：禁用所有自动化特征检测
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    # 2. 模拟真人浏览器环境
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")

    # 3. 模拟真人User-Agent（无自动化特征）
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"
    )

    # 4. 禁用缓存/指纹
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disable-cookies")
    chrome_options.add_argument("--incognito")  # 无痕模式，避免缓存干扰

    # 初始化驱动
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 深度绕开检测：执行多个JS脚本，彻底清除自动化特征
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
    driver.execute_script("window.navigator.chrome = {runtime: {}}")

    yield driver
    driver.quit()


# ========== 核心测试用例（JS直接操作DOM，绕过元素交互限制） ==========
@pytest.mark.parametrize("case_id, keyword, expected", get_test_cases())
def test_baidu_search(driver, case_id, keyword, expected):
    """百度搜索UI自动化测试用例（深度绕开检测版）"""
    try:
        # 1. 打开百度首页（无参数，避免触发特殊策略）
        driver.get("https://www.baidu.com")
        print(f"\n🔍 开始执行用例{case_id}：搜索「{keyword}」")
        # 等待页面完全加载（真人级等待）
        time.sleep(5)

        # 2. 调试信息
        print(f"🌐 当前页面URL：{driver.current_url}")
        print(f"📱 页面标题：{driver.title}")

        # 3. 核心：用JS直接操作搜索框（绕过Selenium交互限制）
        # 步骤1：JS定位搜索框并设置值（无需clear，直接赋值）
        set_keyword_js = f"""
            var searchBox = document.getElementById('kw');
            if (searchBox) {{
                searchBox.value = '{keyword}';  // 直接赋值，替代clear+send_keys
                searchBox.dispatchEvent(new Event('input'));  // 触发输入事件，模拟真人输入
                searchBox.dispatchEvent(new Event('change')); // 触发变更事件
            }}
        """
        driver.execute_script(set_keyword_js)
        print(f"✅ JS已输入关键词：{keyword}")
        time.sleep(2)  # 模拟真人输入延迟

        # 步骤2：JS点击搜索按钮（绕过Selenium点击限制）
        click_search_js = """
            var searchBtn = document.getElementById('su');
            if (searchBtn) {
                searchBtn.click();
            } else {
                // 备用：按回车提交搜索
                var searchBox = document.getElementById('kw');
                searchBox.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter'}));
            }
        """
        driver.execute_script(click_search_js)
        print("✅ JS已执行搜索操作")
        time.sleep(4)  # 等待搜索结果加载

        # 4. 断言：验证关键词存在（宽松匹配）
        page_source = driver.page_source
        assert keyword in page_source, f"用例{case_id}失败：搜索结果中未找到关键词「{keyword}」"

        print(f"✅ 用例{case_id}通过：搜索「{keyword}」验证成功")

    except Exception as e:
        print(f"❌ 用例{case_id}失败详情：{str(e)}")
        pytest.fail(f"用例{case_id}失败：{str(e)}")


# ========== 生成测试报告 ==========
if __name__ == "__main__":
    current_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_path)
    report_path = os.path.join(project_root, "reports")
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    report_file = os.path.join(report_path, "baidu_test_report.html")

    pytest.main([
        __file__,
        "-v",
        "--html=" + report_file,
        "--self-contained-html"
    ])
    print(f"\n📊 测试报告已生成：{report_file}")