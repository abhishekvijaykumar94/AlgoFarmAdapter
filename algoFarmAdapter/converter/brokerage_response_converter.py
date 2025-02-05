from typing import get_type_hints

from algoFarmAdapter import BrokerageResponse


class BrokerageResponseConverter():

    @staticmethod
    def parse_brokerage_response(cls, brokerage_response) ->BrokerageResponse:
        if isinstance(brokerage_response, list):
            return [BrokerageResponseConverter.parse_brokerage_response(cls.__args__[0], item) for item in
                    brokerage_response]
        elif isinstance(brokerage_response, dict):
            field_types = get_type_hints(cls)  # Resolves ForwardRef issue
            return cls(**{k: BrokerageResponseConverter.parse_brokerage_response(field_types[k], v) for k, v in
                          brokerage_response.items()})
        else:
            return brokerage_response