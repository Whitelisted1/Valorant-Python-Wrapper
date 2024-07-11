from typing import List, TYPE_CHECKING
from datetime import datetime
import time

if TYPE_CHECKING:
    from ..session import Session


class SkinOffer:
    def __init__(self, session: "Session", item_ID: str, is_direct_purchase: bool, cost: int, start_time: int):
        """
        An object that represents a Skin Offer in the store front

        Parameters:
        item_ID (str): The ID of the skin for sale
        is_direct_purchase (bool): Represents if the skin if directly purchasable
        cost (int): The cost of the skin in Valorant Points
        start_time (int): The start time of the offer as a unix timestamp
        """

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
    def __init__(self, item_type: str, quantity: int, *args, **kwargs):
        """
        An object that represents an Accessory Offer in the store front

        Parameters:
        item_type (str): The item type ID
        quantity (int): The number of the objects that are purchased
        *args: additional arguments passed to the SkinOffer init function
        **kwargs: additional keyword arguments passed to the SkinOffer init function
        """

        super().__init__(*args, **kwargs)
        self.item_type = item_type
        self.amount = quantity

    @staticmethod
    def from_json(session: "Session", data: dict) -> "AccessoryOffer":
        data = data["Offer"]

        start_time = data["StartDate"].split(".")[0].replace("Z", "")

        timestamp = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        timestamp_time = timestamp.timestamp()

        return AccessoryOffer(data["Rewards"][0]["ItemTypeID"], data["Rewards"][0]["Quantity"], session, data["Rewards"][0]["ItemID"], data["IsDirectPurchase"], list(data["Cost"].values())[0], timestamp_time)


class UpgradeCurrencyOffer(SkinOffer):
    def __init__(self, quantity: int, *args, **kwargs):
        """
        An object that represents an Upgrade Currency Offer

        Parameters:
        item_quantity (str): The quantity of the item purchased
        *args: additional arguments passed to the SkinOffer init function
        **kwargs: additional keyword arguments passed to the SkinOffer init function
        """

        super().__init__(*args, **kwargs)
        self.quantity = quantity

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
    def __init__(self, session: "Session", item_ID: str, item_type: str, quantity: int, base_price: int, currency_ID: str, is_promo_item: bool):
        """
        An object that represents an item that is part of a bundle

        Parameters:
        session (Session): The Session object
        item_ID (str): The ID of the item that is part of the bundle
        item_type (str): The type of item that is part of the bundle
        quantity (int): The number of this type of item that will be included in the bundle
        base_price (int): The base price of the item if you were to buy it separately from the bundle
        currency_ID (str): The ID of the currency used to buy the bundle item
        is_promo_item (bool): Shows if this item is a promotional item
        """

        self.session = session

        self.item_ID = item_ID
        self.item_type = item_type

        self.amount = quantity
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
    def __init__(self, session: "Session", bundle_ID: str, currency_ID: str, expires_time: int, items: List[BundleItem], bundle_price: int, bundle_savings: int):
        """
        An object that represents a bundle offer

        Parameters:
        session (Session): The Session object
        bundle_ID (str): The ID of the bundle
        currency_ID (str): The ID of the currency used to buy the bundle
        expires_time (int): The time that this bundle expires at
        items (List[BundleItem]): The items that are included in the bundle in the form of the BundleItem object
        bundle_price (int): The price of the bundle (in the currency provided in currency_ID)
        bundle_savings (int): Shows how much is the player saving by buying the bundle instead of all the items individually
        """

        self.session = session
        self.bundle_ID = bundle_ID

        self.bundle_price = bundle_price
        self.bundle_savings = bundle_savings
        self.buy_currency_ID = currency_ID

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
        """
        An object that represents the current storefront

        Parameters:
        session (Session): The current Session
        daily_shop (List[SkinOffer]): The daily skin shop
        accessory_shop (List[AccessoryOffer]): The weekly accessory shop
        upgrade_currency (List[UpgradeCurrencyOffer]): The upgrade currency shop
        bundles (List[BundleOffer]): The bundles that are currency for sale
        """

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
