from typing import List

from algoLibs.converters.converter import StaticConverter
from algoLibs.dao.sql_alchemy_models.order_model import OrderData  # Assuming this is your ORM model

from algoFarmAdapter.order_management.order_requests import Order


# Assuming this is where your business object is defined


class OrderDataConverter(StaticConverter):

    def to_business_object(self, data_object_list: List[OrderData]) -> List[Order]:
        """
        Converts a list of OrderData (SQLAlchemy objects) into a list of Order (business objects).
        """
        business_objects = []
        for order_data in data_object_list:
            business_object = Order(
                id=order_data.id,
                orderid=order_data.orderid,
                variety=order_data.variety,
                ordertype=order_data.ordertype,
                ordertag=order_data.ordertag,
                producttype=order_data.producttype,
                price=order_data.price,
                triggerprice=order_data.triggerprice,
                quantity=order_data.quantity,
                disclosedquantity=order_data.disclosedquantity,
                duration=order_data.duration,
                squareoff=order_data.squareoff,
                stoploss=order_data.stoploss,
                trailingstoploss=order_data.trailingstoploss,
                tradingsymbol=order_data.tradingsymbol,
                transactiontype=order_data.transactiontype,
                exchange=order_data.exchange,
                symboltoken=order_data.symboltoken,
                strategy=order_data.strategy,
                instrumenttype=order_data.instrumenttype,
                strikeprice=order_data.strikeprice,
                optiontype=order_data.optiontype,
                expirydate=order_data.expirydate,
                lotsize=order_data.lotsize,
                cancelsize=order_data.cancelsize,
                averageprice=order_data.averageprice,
                filledshares=order_data.filledshares,
                unfilledshares=order_data.unfilledshares,
                text=order_data.text,
                status=order_data.status,
                orderstatus=order_data.orderstatus,
                updatetime=order_data.updatetime,
                exchtime=order_data.exchtime,
                exchorderupdatetime=order_data.exchorderupdatetime,
                fillid=order_data.fillid,
                filltime=order_data.filltime,
                parentorderid=order_data.parentorderid,
                packageid=order_data.packageid,
                uniqueorderid=order_data.uniqueorderid
            )
            business_objects.append(business_object)
        return business_objects

    def to_data_object(self, business_object_list: List[Order]) -> List[OrderData]:
        """
        Converts a list of Order (business objects) into a list of OrderData (SQLAlchemy objects).
        """
        data_objects = []
        for order in business_object_list:
            data_object = OrderData(
                id=order.id,
                orderid=order.orderid,
                variety=order.variety,
                ordertype=order.ordertype,
                ordertag=order.ordertag,
                producttype=order.producttype,
                price=order.price,
                triggerprice=order.triggerprice,
                quantity=order.quantity,
                disclosedquantity=order.disclosedquantity,
                duration=order.duration,
                squareoff=order.squareoff,
                stoploss=order.stoploss,
                trailingstoploss=order.trailingstoploss,
                tradingsymbol=order.tradingsymbol,
                transactiontype=order.transactiontype,
                exchange=order.exchange,
                symboltoken=order.symboltoken,
                strategy=order.strategy,
                instrumenttype=order.instrumenttype,
                strikeprice=order.strikeprice,
                optiontype=order.optiontype,
                expirydate=order.expirydate,
                lotsize=order.lotsize,
                cancelsize=order.cancelsize,
                averageprice=order.averageprice,
                filledshares=order.filledshares,
                unfilledshares=order.unfilledshares,
                text=order.text,
                status=order.status,
                orderstatus=order.orderstatus,
                updatetime=order.updatetime,
                exchtime=order.exchtime,
                exchorderupdatetime=order.exchorderupdatetime,
                fillid=order.fillid,
                filltime=order.filltime,
                parentorderid=order.parentorderid,
                packageid=order.packageid,
                uniqueorderid=order.uniqueorderid
            )
            data_objects.append(data_object)
        return data_objects
