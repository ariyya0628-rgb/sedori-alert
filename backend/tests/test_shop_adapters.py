from fastapi.testclient import TestClient

from app.main import app
from app.services.adapters.offmall import parse_offmall_products
from app.services.adapters.secondstreet import parse_secondstreet_products
from app.services.adapters.mandarake import parse_mandarake_products
from app.services.adapters.surugaya import parse_surugaya_products
from app.services.shop_crawler import SHOP_FETCHERS


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


MANDARAKE_HTML = """
<div class="item">
  <a href="/order/detailPage/item?itemCode=1256789012&ref=list&keyword=recolte&lang=ja">
    <img src="//order.mandarake.co.jp/img/1256789012.jpg" alt="レコルト ホットプレート RHP-1" />
    <div class="item-title">レコルト ホットプレート RHP-1</div>
    <div class="price">4,400円</div>
  </a>
</div>
"""


SURUGAYA_HTML = """
<div class="item">
  <p class="title">
    <a href="/product/detail/608123456">レコルト カプセルカッター ボンヌ</a>
  </p>
  <p class="price">中古 3,980円 (税込)</p>
  <img src="//www.suruga-ya.jp/database/pics_light/game/608123456.jpg" alt="レコルト カプセルカッター ボンヌ" />
</div>
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


def test_parse_mandarake_products_from_search_html():
    products = parse_mandarake_products(MANDARAKE_HTML)
    assert len(products) == 1
    product = products[0]
    assert product.shop_code == "mandarake"
    assert product.external_product_id == "1256789012"
    assert product.title == "レコルト ホットプレート RHP-1"
    assert product.price == 4400
    assert product.product_url == "https://order.mandarake.co.jp/order/detailPage/item?itemCode=1256789012&ref=list&keyword=recolte&lang=ja"
    assert product.image_url == "https://order.mandarake.co.jp/img/1256789012.jpg"


def test_parse_surugaya_products_from_search_html():
    products = parse_surugaya_products(SURUGAYA_HTML)
    assert len(products) == 1
    product = products[0]
    assert product.shop_code == "surugaya"
    assert product.external_product_id == "608123456"
    assert product.title == "レコルト カプセルカッター ボンヌ"
    assert product.price == 3980
    assert product.product_url == "https://www.suruga-ya.jp/product/detail/608123456"
    assert product.image_url == "https://www.suruga-ya.jp/database/pics_light/game/608123456.jpg"


def test_run_shop_rejects_unknown_shop():
    response = client.post("/api/crawler/run-shop?user_id=1&shop_code=unknown&keyword=レコルト")
    assert response.status_code == 400


def test_shop_fetchers_include_mandarake_and_surugaya():
    assert "mandarake" in SHOP_FETCHERS
    assert "surugaya" in SHOP_FETCHERS
