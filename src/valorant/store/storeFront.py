from typing import List, TYPE_CHECKING
from datetime import datetime
import time

if TYPE_CHECKING:
    from ..session import Session


class SkinOffer:
    def __init__(self, session: "Session", item_ID: str, is_direct_purchase: bool, cost: int, start_time: int):
        self.session = session
        self.item_ID = item_ID
        self.is_direct_purchase = is_direct_purchase
        self.cost = cost
        self.start_time = start_time

    @staticmethod
    def from_json(session: "Session", data: dict) -> "SkinOffer":
        start_time = data["StartDate"].split(".")[0].replace("Z", "")

        timestamp = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        timestamp_time = timestamp.timestamp()

        return SkinOffer(session, data["Rewards"][0]["ItemID"], data["IsDirectPurchase"], list(data["Cost"].values())[0], timestamp_time)


class AccessoryOffer(SkinOffer):
    def __init__(self, item_type: str, amount: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_type = item_type
        self.amount = amount

    @staticmethod
    def from_json(session: "Session", data: dict) -> "AccessoryOffer":
        data = data["Offer"]

        start_time = data["StartDate"].split(".")[0].replace("Z", "")

        timestamp = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        timestamp_time = timestamp.timestamp()

        return AccessoryOffer(data["Rewards"][0]["ItemTypeID"], data["Rewards"][0]["Quantity"], session, data["Rewards"][0]["ItemID"], data["IsDirectPurchase"], list(data["Cost"].values())[0], timestamp_time)


class UpgradeCurrencyOffer(SkinOffer):
    def __init__(self, item_quantity: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_quantity = item_quantity

    @staticmethod
    def from_json(session: "Session", data: dict) -> "UpgradeCurrencyOffer":
        data = data["Offer"]

        start_time = data["StartDate"].split(".")[0].replace("Z", "")

        timestamp = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        timestamp_time = timestamp.timestamp()

        return UpgradeCurrencyOffer(
            data["Rewards"][0]["Quantity"],
            session,
            data["Rewards"][0]["ItemID"],
            data["IsDirectPurchase"],
            list(data["Cost"].values())[0],
            timestamp_time
        )


class BundleItem:
    def __init__(self, session: "Session", item_ID: str, item_type: str, amount: int, base_price: int, currency_ID: str, is_promo_item: bool):
        self.session = session

        self.item_ID = item_ID
        self.item_type = item_type

        self.amount = amount
        self.base_price = base_price
        self.currency_ID = currency_ID

        self.is_promo_item = is_promo_item

    @staticmethod
    def from_json(session: "Session", data: dict) -> "BundleItem":
        return BundleItem(
            session,
            data["Item"]["ItemID"],
            data["Item"]["ItemTypeID"],
            data["Item"]["Amount"],
            data["BasePrice"],
            data["CurrencyID"],
            data["IsPromoItem"]
        )


class BundleOffer:
    def __init__(self, session: "Session", bundle_ID: str, buy_currency_ID: str, expires_time: int, items: List[BundleItem], bundle_price: int, bundle_savings: int):
        self.session = session
        self.bundle_ID = bundle_ID

        self.bundle_price = bundle_price
        self.bundle_savings = bundle_savings
        self.buy_currency_ID = buy_currency_ID

        self.expires_time = expires_time

        self.items = items

    @staticmethod
    def from_json(session: "Session", data: dict) -> "BundleOffer":
        expires_time = time.time() + data["DurationRemainingInSeconds"]

        items_raw = data["Items"]
        items: List[BundleItem] = []

        for item in items_raw:
            items.append(BundleItem.from_json(session, item))

        return BundleOffer(
            session,
            data["DataAssetID"],
            data["CurrencyID"],
            expires_time,
            items,
            data["TotalBaseCost"][data["CurrencyID"]],
            data["TotalDiscountedCost"][data["CurrencyID"]]
        )


class StoreFront:
    def __init__(self, session: "Session", daily_shop: List[SkinOffer], accessory_shop: List[AccessoryOffer], upgrade_currency: List[UpgradeCurrencyOffer], bundles: List[BundleOffer]):
        self.session = session
        self.daily_shop = daily_shop
        self.accessory_shop = accessory_shop
        self.upgrade_currency = upgrade_currency
        self.bundles = bundles

    @staticmethod
    def from_json(session: "Session", data: dict) -> "StoreFront":
        daily_shop_raw: list = data["SkinsPanelLayout"]["SingleItemStoreOffers"]
        accessory_shop_raw = data["AccessoryStore"]["AccessoryStoreOffers"]
        upgrade_currency_raw = data["UpgradeCurrencyStore"]["UpgradeCurrencyOffers"]
        bundles_raw = data["FeaturedBundle"]["Bundles"]

        daily_shop: List[SkinOffer] = []
        accessory_shop: List[AccessoryOffer] = []
        upgrade_currency: List[UpgradeCurrencyOffer] = []
        bundles: List[BundleOffer] = []

        for item in daily_shop_raw:
            daily_shop.append(SkinOffer.from_json(session, item))

        for item in accessory_shop_raw:
            accessory_shop.append(AccessoryOffer.from_json(session, item))

        for item in upgrade_currency_raw:
            upgrade_currency.append(UpgradeCurrencyOffer.from_json(session, item))

        for item in bundles_raw:
            bundles.append(BundleOffer.from_json(session, item))

        return StoreFront(session, daily_shop, accessory_shop, upgrade_currency, bundles)
