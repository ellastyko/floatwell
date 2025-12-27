from utils.market import match_rule
from abc import ABC, abstractmethod

class StrategyContext:
    def __init__(self, item):
        self.item = item

class BaseStrategy(ABC):

    @abstractmethod
    def applies(self, ctx: StrategyContext) -> bool:
        pass

class KeychainStrategy(BaseStrategy):

    def applies(self, ctx: StrategyContext) -> bool:
        if not ctx.item.get('has_keychain'):
            return False
        return True
        # rules = ctx.filters.get('keychains', {})

        # for ast in ctx.item.get('assets', []):
        #     if ast.get("type") != "keychain":
        #         continue

        #     if 'like' in rules and match_rule(ast.get('name', ''), rules['like']):
        #         return True

        # return False

class PatternStrategy(BaseStrategy):
    def applies(self, ctx: StrategyContext) -> bool:
        return (
            ctx.item.get('has_rare_pattern')
            and ctx.item.get('is_price_acceptable')
        )

class FloatStrategy(BaseStrategy):

    def applies(self, ctx: StrategyContext) -> bool:
        return (
            ctx.item.get('has_rare_float')
            and ctx.item.get('is_price_acceptable')
        )

class StickerStrategy(BaseStrategy):

    def applies(self, ctx: StrategyContext) -> bool:
        return ctx.item.get('has_sticker', False)

STRATEGY_REGISTRY = {
    'pattern':  PatternStrategy,
    'float':    FloatStrategy,
    'keychains': KeychainStrategy,
    'stickers':  StickerStrategy,
}