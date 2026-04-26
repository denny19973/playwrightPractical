import re
import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://demos.bellatrix.solutions/"


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(BASE_URL)
        yield page
        browser.close()


# TC_01：首頁載入
def test_tc01_homepage_load(page):
    expect(page).to_have_url(BASE_URL)
    expect(page.locator("body")).to_be_visible()

    # 商品區（Shop）存在
    expect(page.locator("text=Shop")).to_be_visible()


# TC_02：商品列表顯示
def test_tc02_product_list(page):
    products = page.locator(".products .product")
    expect(products).not_to_have_count(0)

    # 檢查第一個商品有名稱與價格
    first = products.first
    expect(first.locator(".woocommerce-loop-product__title")).to_be_visible()
    expect(first.locator(".price")).to_be_visible()


# TC_03：商品價格格式
def test_tc03_price_format(page):
    prices = page.locator(".price")

    count = prices.count()
    assert count > 0

    for i in range(count):
        text = prices.nth(i).inner_text()
        assert "€" in text
        assert re.search(r"\d+\.\d{2}", text)


# TC_04：加入購物車
def test_tc04_add_to_cart(page):
    add_btn = page.locator("text=Add to cart").first
    add_btn.click()

    # 等待購物車更新
    cart_count = page.locator(".cart-contents .count")
    expect(cart_count).not_to_have_text("0")


# TC_05：加入多個商品
def test_tc05_add_multiple_products(page):
    buttons = page.locator("text=Add to cart")

    buttons.nth(0).click()
    buttons.nth(1).click()

    cart_count = page.locator(".cart-contents .count")
    expect(cart_count).to_contain_text("2")


# TC_06：查看購物車內容
def test_tc06_view_cart(page):
    page.locator("text=Add to cart").first.click()

    page.locator(".added_to_cart").click()

    expect(page).to_have_url(re.compile("cart"))

    items = page.locator(".cart_item")
    expect(items).to_have_count(1)

    expect(items.first).to_contain_text("€")


# TC_07：購物車為空
def test_tc07_empty_cart(page):
    page.locator(".cart-contents").click()

    expect(page).to_have_url(re.compile("cart"))

    empty_msg = page.locator(".cart-empty")
    expect(empty_msg).to_be_visible()


# TC_08：商品詳細頁
def test_tc08_product_detail(page):
    page.locator("text=Read more").first.click()

    expect(page).to_have_url(re.compile("product"))
    expect(page.locator(".product")).to_be_visible()


# TC_09：返回商品頁
def test_tc09_back_to_shop(page):
    page.locator("text=Read more").first.click()

    page.go_back()

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".products")).to_be_visible()


# TC_10：購物流程金額驗證 待修改code


def test_tc10_cart_total(page):
    page.locator("text=Add to cart").first.click()
    page.locator(".added_to_cart").click()

    subtotal_text = page.locator(".cart-subtotal .amount").inner_text()

    total_text = page.locator(".order-total .amount").inner_text()

    # 取出數字
    subtotal = float(re.search(r"\d+\.\d{2}", subtotal_text).group()) + 10
    total = float(re.search(r"\d+\.\d{2}", total_text).group())

    # 驗證金額
    assert subtotal == total
