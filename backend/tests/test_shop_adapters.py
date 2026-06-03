from fastapi.testclient import TestClient

from app.main import app
from app.services.adapters.offmall import parse_offmall_products
from app.services.adapters.secondstreet import parse_secondstreet_products


client = TestClient(app)


OFFMALL_HTML = """
<div class="itemcolmn_item">
  <a href="https://netmall.hardoff.co.jp/product/6171452/">
    <div class="item-img-square">
      <img src="https://example.com/recolte.jpg" alt="クッキングライスクッカー|レコルト" />
    </div>
    <div class="item-infowrap">
      <div class="item-brand-name">レコルト</div>
      <div class="item-name">クッキングライスクッカー</div>
      <div class="item-code">RCR-2</div>
      <div class="item-price">
        <span class="font-en item-price-en">6,600<span class="item-price-jp">円</span></span>
      </div>
    </div>
  </a>
</div>
"""


SECONDSTREET_HTML = """
<ul>
  <li>
    <a href="/goods/detail/goodsId/2321513159015/shopsId/31740">
      その他ブランド レコルト/ホットプレート/RHP-1 商品の状態 : 中古B ¥4,290
    </a>
  </li>
</ul>
"""


def test_parse_offmall_products_from_search_html():
    products = parse_offmall_products(OFFMALL_HTML)
    assert len(products) == 1
    product = products[0]
    assert product.shop_code == "offmall"
    assert product.external_product_id == "6171452"
    assert product.title == "レコルト クッキングライスクッカー RCR-2"
    assert product.price == 6600
    assert product.product_url == "https://netmall.hardoff.co.jp/product/6171452/"
    assert product.image_url == "https://example.com/recolte.jpg"


def test_parse_secondstreet_products_from_search_html():
    products = parse_secondstreet_products(SECONDSTREET_HTML)
    assert len(products) == 1
    product = products[0]
    assert product.shop_code == "secondstreet"
    assert product.external_product_id == "2321513159015"
    assert "レコルト" in product.title
    assert product.price == 4290
    assert product.product_url == "https://www.2ndstreet.jp/goods/detail/goodsId/2321513159015/shopsId/31740"


def test_run_shop_rejects_unknown_shop():
    response = client.post("/api/crawler/run-shop?user_id=1&shop_code=unknown&keyword=レコルト")
    assert response.status_code == 400
